"""
Speech-to-Text API Router.
Handles audio file uploads and transcription.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger

from app.config import settings
from app.models.schemas import TranscriptionResponse, ErrorResponse
from app.services.speech_to_text import speech_service


router = APIRouter()


@router.post(
    "/speech-to-text",
    response_model=TranscriptionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Transcribe audio to text",
    description="Upload an audio file containing a witness description and get text transcription."
)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, M4A, FLAC, OGG)")
):
    """
    Transcribe an audio file to text using OpenAI Whisper.
    
    - **file**: Audio file containing speech description
    
    Returns transcribed text with language detection and duration.
    """
    # Validate file extension
    if file.filename:
        extension = f".{file.filename.split('.')[-1].lower()}"
        if extension not in settings.allowed_audio_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Allowed: {settings.allowed_audio_extensions}"
            )
    
    # Read file content
    try:
        audio_data = await file.read()
        
        # Check file size
        if len(audio_data) > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        logger.info(f"Processing audio file: {file.filename} ({len(audio_data)} bytes)")
        
        # Transcribe
        text, language, duration = await speech_service.transcribe(
            audio_data, 
            file.filename or "audio.wav"
        )
        
        return TranscriptionResponse(
            text=text,
            language=language,
            duration_seconds=duration,
            confidence=1.0  # Whisper doesn't provide per-transcription confidence
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )
