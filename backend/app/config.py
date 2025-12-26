"""
Configuration management for the Multimodal AI System.
Uses Pydantic Settings for environment-based configuration.
"""
import os
from pathlib import Path
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


# Get base directory
BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    app_name: str = "Multimodal AI Suspect Identification System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Model Settings
    whisper_model: str = "base"
    stable_diffusion_model: str = "runwayml/stable-diffusion-v1-5"
    device: str = "cuda"
    
    # Deepfake Detection Thresholds
    deepfake_threshold: float = 0.5
    
    # Security
    max_file_size_mb: int = 50
    allowed_audio_extensions: List[str] = [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"]
    allowed_image_extensions: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    
    # CORS Settings
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # FAISS Settings
    top_k_results: int = 5
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }
    
    @property
    def base_dir(self) -> Path:
        return BASE_DIR
    
    @property
    def data_dir(self) -> Path:
        path = BASE_DIR / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def models_dir(self) -> Path:
        path = self.data_dir / "models"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def embeddings_dir(self) -> Path:
        path = self.data_dir / "embeddings"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def sample_faces_dir(self) -> Path:
        path = self.data_dir / "sample_faces"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def uploads_dir(self) -> Path:
        path = self.data_dir / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def faiss_index_path(self) -> Path:
        return self.embeddings_dir / "face_index.faiss"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()

