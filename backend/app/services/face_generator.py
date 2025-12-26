"""
Face Generation Service using Stable Diffusion.
Generates facial portraits from text descriptions.
"""
import base64
import io
import time
from typing import Optional
import torch
from PIL import Image
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from loguru import logger

from app.config import settings
from app.models.schemas import FacialAttributes


class FaceGeneratorService:
    """Service for generating face sketches/portraits from descriptions."""
    
    _instance = None
    _pipeline = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the face generator service."""
        pass  # Lazy loading - model loaded on first use
    
    def _load_model(self) -> None:
        """Load the Stable Diffusion pipeline."""
        if self._pipeline is not None:
            return
            
        logger.info(f"Loading Stable Diffusion model: {settings.stable_diffusion_model}")
        
        try:
            # Determine device and dtype
            if torch.cuda.is_available() and settings.device == "cuda":
                device = "cuda"
                dtype = torch.float16
                logger.info("Using CUDA with float16 precision")
            else:
                device = "cpu"
                dtype = torch.float32
                logger.info("Using CPU with float32 precision")
            
            # Load pipeline with optimizations
            self._pipeline = StableDiffusionPipeline.from_pretrained(
                settings.stable_diffusion_model,
                torch_dtype=dtype,
                safety_checker=None,  # Disable for faster inference
                requires_safety_checker=False
            )
            
            # Use faster scheduler
            self._pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self._pipeline.scheduler.config
            )
            
            self._pipeline = self._pipeline.to(device)
            
            # Enable memory optimizations for CUDA
            if device == "cuda":
                self._pipeline.enable_attention_slicing()
                try:
                    self._pipeline.enable_xformers_memory_efficient_attention()
                    logger.info("xformers memory efficient attention enabled")
                except Exception:
                    logger.warning("xformers not available, using standard attention")
            
            logger.info("✅ Stable Diffusion model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Stable Diffusion: {e}")
            raise
    
    def _build_prompt(self, description: str, attributes: Optional[FacialAttributes] = None, 
                      style: str = "portrait") -> str:
        """
        Build an optimized prompt for face generation.
        
        Args:
            description: Raw text description
            attributes: Pre-extracted facial attributes
            style: Output style (portrait, sketch, realistic)
        """
        # Base prompt elements
        prompt_parts = []
        
        # Style prefix
        style_prefixes = {
            "portrait": "professional portrait photograph of",
            "sketch": "pencil sketch portrait drawing of",
            "realistic": "hyperrealistic photograph of"
        }
        prompt_parts.append(style_prefixes.get(style, style_prefixes["portrait"]))
        
        # Add attributes if provided
        if attributes:
            if attributes.gender:
                prompt_parts.append(f"a {attributes.gender}")
            if attributes.age_range:
                prompt_parts.append(f"aged {attributes.age_range}")
            if attributes.hair_color:
                prompt_parts.append(f"with {attributes.hair_color} hair")
            if attributes.hair_style:
                prompt_parts.append(f"{attributes.hair_style} hairstyle")
            if attributes.facial_hair:
                prompt_parts.append(f"with {attributes.facial_hair}")
            if attributes.face_shape:
                prompt_parts.append(f"{attributes.face_shape} face shape")
            if attributes.glasses:
                prompt_parts.append("wearing glasses")
            if attributes.distinctive_features:
                for feature in attributes.distinctive_features[:2]:  # Limit features
                    prompt_parts.append(f"with {feature}")
        else:
            # Use raw description
            prompt_parts.append(description)
        
        # Quality enhancers
        prompt_parts.extend([
            "front facing",
            "centered composition",
            "neutral background",
            "high quality",
            "detailed face",
            "8k resolution"
        ])
        
        prompt = ", ".join(prompt_parts)
        logger.debug(f"Generated prompt: {prompt}")
        return prompt
    
    def _get_negative_prompt(self, style: str = "portrait") -> str:
        """Get negative prompt to improve output quality."""
        base_negative = [
            "blurry", "low quality", "distorted", "disfigured",
            "bad anatomy", "extra limbs", "mutated hands",
            "ugly", "duplicate", "morbid", "mutilated",
            "poorly drawn face", "mutation", "deformed",
            "bad proportions", "malformed limbs", "missing arms",
            "missing legs", "extra arms", "extra legs", "fused fingers",
            "too many fingers", "long neck", "watermark", "signature"
        ]
        
        if style == "sketch":
            base_negative.extend(["color", "photograph", "realistic"])
        
        return ", ".join(base_negative)
    
    async def generate_face(
        self,
        description: str,
        attributes: Optional[FacialAttributes] = None,
        style: str = "portrait",
        num_inference_steps: int = 25,
        guidance_scale: float = 7.5
    ) -> tuple[str, str, float]:
        """
        Generate a face image from description.
        
        Args:
            description: Text description of the face
            attributes: Pre-extracted facial attributes
            style: Output style (portrait, sketch, realistic)
            num_inference_steps: Number of denoising steps (lower = faster)
            guidance_scale: How closely to follow the prompt
            
        Returns:
            Tuple of (base64_image, prompt_used, generation_time_seconds)
        """
        # Ensure model is loaded
        self._load_model()
        
        start_time = time.time()
        
        # Build prompts
        prompt = self._build_prompt(description, attributes, style)
        negative_prompt = self._get_negative_prompt(style)
        
        logger.info(f"Generating face with style: {style}")
        logger.debug(f"Using prompt: {prompt[:100]}...")
        
        try:
            # Generate image
            with torch.inference_mode():
                result = self._pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=512,
                    width=512,
                )
            
            image = result.images[0]
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            generation_time = time.time() - start_time
            logger.info(f"✅ Face generated in {generation_time:.2f}s")
            
            return image_base64, prompt, generation_time
            
        except Exception as e:
            logger.error(f"Face generation failed: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._pipeline is not None


# Create singleton instance
face_generator_service = FaceGeneratorService()
