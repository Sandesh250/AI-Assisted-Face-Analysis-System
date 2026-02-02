"""
InsightFace ONNX wrapper for face recognition.
Uses pre-built ArcFace ResNet50 model for 512-dim embeddings.
"""
import cv2
import numpy as np
import onnxruntime as ort
from pathlib import Path
from loguru import logger
import requests
from typing import Optional


class InsightFaceONNX:
    """InsightFace ArcFace model using ONNX Runtime."""
    
    def __init__(self, model_path: Optional[Path] = None):
        """Initialize InsightFace ONNX model."""
        self.model_path = model_path or Path(__file__).parent.parent / "data" / "models" / "arcface_r50.onnx"
        self.session = None
        self.input_name = None
        self.output_name = None
        self.input_shape = (112, 112)  # ArcFace input size
        
    def download_model(self):
        """Download ArcFace ResNet50 ONNX model if not exists."""
        if self.model_path.exists():
            logger.info(f"Model already exists at {self.model_path}")
            return
            
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download from InsightFace model zoo
        url = "https://github.com/onnx/models/raw/main/validated/vision/body_analysis/arcface/model/arcfaceresnet100-8.onnx"
        
        logger.info(f"Downloading ArcFace model from {url}...")
        logger.info("This may take a few minutes (~150MB)...")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(self.model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024 * 10) == 0:  # Log every 10MB
                            logger.info(f"Downloaded {downloaded / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB ({progress:.1f}%)")
        
        logger.info(f"✅ Model downloaded to {self.model_path}")
    
    def load_model(self, use_gpu: bool = True):
        """Load ONNX model with ONNX Runtime."""
        if not self.model_path.exists():
            self.download_model()
        
        logger.info(f"Loading InsightFace ArcFace model from {self.model_path}...")
        
        # Configure ONNX Runtime
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_gpu else ['CPUExecutionProvider']
        
        self.session = ort.InferenceSession(str(self.model_path), providers=providers)
        
        # Get input/output names
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
        logger.info(f"✅ InsightFace model loaded successfully")
        logger.info(f"   Input: {self.input_name}, Output: {self.output_name}")
        logger.info(f"   Providers: {self.session.get_providers()}")
    
    def preprocess(self, img: np.ndarray) -> np.ndarray:
        """Preprocess image for ArcFace model."""
        # Resize to 112x112
        img = cv2.resize(img, self.input_shape)
        
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Normalize to [-1, 1]
        img = (img.astype(np.float32) - 127.5) / 127.5
        
        # Transpose to CHW format
        img = np.transpose(img, (2, 0, 1))
        
        # Add batch dimension
        img = np.expand_dims(img, axis=0)
        
        return img
    
    def get_embedding(self, img: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding from image.
        
        Args:
            img: Face image (BGR format, any size)
            
        Returns:
            512-dim normalized embedding or None if failed
        """
        if self.session is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Preprocess
            input_data = self.preprocess(img)
            
            # Run inference
            embedding = self.session.run([self.output_name], {self.input_name: input_data})[0]
            
            # Normalize
            embedding = embedding.flatten()
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}")
            return None


# Singleton instance
insightface_model = InsightFaceONNX()
