"""
Deepfake Detection Service using EfficientNet.
Classifies images as real or potentially manipulated.
"""
import io
import time
from typing import Tuple, Dict
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from loguru import logger

from app.config import settings


class DeepfakeDetectorService:
    """Service for detecting deepfake/manipulated images."""
    
    _instance = None
    _model = None
    _transform = None
    _device = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the deepfake detector service."""
        if self._model is None:
            self._setup_transform()
            self._load_model()
    
    def _setup_transform(self) -> None:
        """Setup image preprocessing transforms."""
        self._transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def _load_model(self) -> None:
        """Load the EfficientNet classifier model."""
        logger.info("Loading EfficientNet-B0 deepfake detection model...")
        
        try:
            # Determine device
            if torch.cuda.is_available() and settings.device == "cuda":
                self._device = torch.device("cuda")
            else:
                self._device = torch.device("cpu")
            logger.info(f"Using device: {self._device}")
            
            # Load EfficientNet-B0 pretrained on ImageNet
            # In production, this would be fine-tuned on a deepfake dataset
            self._model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
            
            # Modify classifier for binary classification (real vs fake)
            num_features = self._model.classifier[1].in_features
            self._model.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(num_features, 256),
                nn.ReLU(),
                nn.Dropout(p=0.3),
                nn.Linear(256, 2)  # 2 classes: real, fake
            )
            
            # Check for pretrained deepfake weights
            weights_path = settings.models_dir / "deepfake_detector.pth"
            if weights_path.exists():
                logger.info(f"Loading pretrained weights from {weights_path}")
                checkpoint = torch.load(weights_path, map_location=self._device)
                self._model.load_state_dict(checkpoint)
            else:
                logger.warning(
                    "No pretrained deepfake weights found. Using ImageNet weights. "
                    "Model will provide baseline predictions only."
                )
            
            self._model = self._model.to(self._device)
            self._model.eval()
            
            logger.info("✅ Deepfake detection model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load deepfake detector: {e}")
            raise
    
    def _preprocess_image(self, image_data: bytes) -> torch.Tensor:
        """Preprocess image for model inference."""
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        tensor = self._transform(image).unsqueeze(0)
        return tensor.to(self._device)
    
    def _analyze_frequency_domain(self, image_data: bytes) -> Dict:
        """
        Analyze image in frequency domain for manipulation artifacts.
        Deepfakes often have distinctive frequency patterns.
        """
        try:
            image = Image.open(io.BytesIO(image_data)).convert("L")  # Grayscale
            img_array = np.array(image, dtype=np.float32)
            
            # Compute 2D FFT
            fft = np.fft.fft2(img_array)
            fft_shift = np.fft.fftshift(fft)
            magnitude = np.abs(fft_shift)
            
            # Analyze frequency distribution
            h, w = magnitude.shape
            center_y, center_x = h // 2, w // 2
            
            # Low, mid, and high frequency regions
            low_freq = magnitude[center_y-20:center_y+20, center_x-20:center_x+20].mean()
            mid_freq = magnitude[center_y-50:center_y+50, center_x-50:center_x+50].mean()
            high_freq = magnitude.mean()
            
            # Ratio analysis (deepfakes often have unusual ratios)
            freq_ratio = low_freq / (high_freq + 1e-8)
            
            return {
                "low_freq_energy": float(low_freq),
                "mid_freq_energy": float(mid_freq),
                "high_freq_energy": float(high_freq),
                "freq_ratio": float(freq_ratio),
                "suspicious_frequency": bool(freq_ratio > 100)  # Convert to Python bool
            }
        except Exception as e:
            logger.warning(f"Frequency analysis failed: {e}")
            return {}
    
    async def detect(self, image_data: bytes) -> Tuple[bool, float, str, Dict]:
        """
        Detect if an image is real or potentially manipulated.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Tuple of (is_real, confidence, verdict, details)
        """
        start_time = time.time()
        logger.info("Analyzing image for deepfake artifacts...")
        
        try:
            # Preprocess and run inference
            input_tensor = self._preprocess_image(image_data)
            
            with torch.no_grad():
                outputs = self._model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                
                # Index 0 = fake, Index 1 = real (convention)
                fake_prob = probabilities[0][0].item()
                real_prob = probabilities[0][1].item()
            
            # Frequency domain analysis for additional signals
            freq_analysis = self._analyze_frequency_domain(image_data)
            
            # Combine signals
            combined_fake_score = fake_prob
            if freq_analysis.get("suspicious_frequency", False):
                combined_fake_score = min(1.0, combined_fake_score + 0.1)
            
            # Determine result
            is_real = combined_fake_score < settings.deepfake_threshold
            confidence = real_prob if is_real else fake_prob
            
            # Generate verdict
            if is_real:
                if confidence > 0.9:
                    verdict = "High confidence: Image appears authentic"
                elif confidence > 0.7:
                    verdict = "Moderate confidence: Image likely authentic"
                else:
                    verdict = "Low confidence: Image possibly authentic"
            else:
                if confidence > 0.9:
                    verdict = "High confidence: Image appears manipulated"
                elif confidence > 0.7:
                    verdict = "Moderate confidence: Image possibly manipulated"
                else:
                    verdict = "Low confidence: Minor manipulation indicators"
            
            processing_time = time.time() - start_time
            
            details = {
                "real_probability": round(real_prob, 4),
                "fake_probability": round(fake_prob, 4),
                "frequency_analysis": freq_analysis,
                "processing_time_seconds": round(processing_time, 3),
                "model_used": "EfficientNet-B0",
                "threshold": settings.deepfake_threshold
            }
            
            logger.info(f"✅ Analysis complete: {'REAL' if is_real else 'FAKE'} (confidence: {confidence:.2%})")
            
            return is_real, confidence, verdict, details
            
        except Exception as e:
            logger.error(f"Deepfake detection failed: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None


# Create singleton instance
deepfake_detector_service = DeepfakeDetectorService()
