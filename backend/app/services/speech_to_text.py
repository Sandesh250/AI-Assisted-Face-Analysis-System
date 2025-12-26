"""
Speech-to-Text Service using OpenAI Whisper.
Converts audio recordings to text for processing.
"""
import tempfile
from pathlib import Path
from typing import Tuple
import torch
import whisper
from loguru import logger

from app.config import settings


class SpeechToTextService:
    """Service for converting speech audio to text using Whisper."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern for model reuse."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the speech-to-text service."""
        if self._model is None:
            self._load_model()
    
    def _load_model(self) -> None:
        """Load the Whisper model."""
        logger.info(f"Loading Whisper model: {settings.whisper_model}")
        try:
            # Use CUDA if available
            device = "cuda" if torch.cuda.is_available() and settings.device == "cuda" else "cpu"
            logger.info(f"Using device: {device}")
            
            self._model = whisper.load_model(
                settings.whisper_model,
                device=device
            )
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def transcribe(self, audio_data: bytes, filename: str) -> Tuple[str, str, float]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_data: Raw audio file bytes
            filename: Original filename for extension detection
            
        Returns:
            Tuple of (transcribed_text, detected_language, duration_seconds)
        """
        # Save to temporary file for Whisper processing
        suffix = Path(filename).suffix.lower()
        if suffix not in settings.allowed_audio_extensions:
            raise ValueError(f"Unsupported audio format: {suffix}")
        
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        try:
            logger.info(f"Transcribing audio file: {filename}")
            
            # Transcribe with Whisper
            result = self._model.transcribe(
                tmp_path,
                language="en",  # Force English for consistent results
                task="transcribe",
                verbose=False
            )
            
            transcribed_text = result["text"].strip()
            detected_language = result.get("language", "en")
            
            # Calculate duration from segments
            segments = result.get("segments", [])
            duration = segments[-1]["end"] if segments else 0.0
            
            logger.info(f"Transcription complete: {len(transcribed_text)} characters")
            logger.debug(f"Transcribed text: {transcribed_text[:100]}...")
            
            return transcribed_text, detected_language, duration
            
        finally:
            # Cleanup temporary file
            Path(tmp_path).unlink(missing_ok=True)
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None


# Create singleton instance
speech_service = SpeechToTextService()
