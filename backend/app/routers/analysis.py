"""
Full Analysis Pipeline API Router.
Combines all modules into a complete workflow.
"""
import time
import base64
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from loguru import logger
from PIL import Image

from app.config import settings
from app.models.schemas import (
    FullAnalysisResponse,
    TranscriptionResponse,
    GenerateSketchResponse,
    DeepfakeVerificationResponse,
    FaceMatchingResponse,
    ErrorResponse
)
from app.services.speech_to_text import speech_service
from app.services.nlp_processor import nlp_service
from app.services.face_generator import face_generator_service
from app.services.deepfake_detector import deepfake_detector_service
from app.services.face_embeddings import face_embedding_service


router = APIRouter()


@router.post(
    "/analyze/audio",
    response_model=FullAnalysisResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Full analysis from audio",
    description="Complete pipeline: Audio → Text → Attributes → Face Generation → Matching"
)
async def analyze_from_audio(
    audio_file: UploadFile = File(..., description="Audio file with description"),
    generate_sketch: bool = Form(default=True, description="Generate face sketch"),
    top_k: int = Form(default=5, ge=1, le=20, description="Number of matches")
):
    """
    Run the complete analysis pipeline from audio input.
    
    1. Transcribe audio to text
    2. Extract facial attributes from text
    3. Generate face sketch from description
    4. Search for similar faces in database
    
    ⚠️ **Educational Project**: Results are AI-generated suggestions only.
    """
    start_time = time.time()
    
    try:
        # Step 1: Transcribe audio
        logger.info("Step 1: Transcribing audio...")
        audio_data = await audio_file.read()
        text, language, duration = await speech_service.transcribe(
            audio_data, 
            audio_file.filename or "audio.wav"
        )
        
        transcription = TranscriptionResponse(
            text=text,
            language=language,
            duration_seconds=duration,
            confidence=1.0
        )
        
        # Step 2: Extract attributes
        logger.info("Step 2: Extracting facial attributes...")
        attributes, _, _ = nlp_service.process_description(text)
        
        # Step 3: Generate sketch (if requested)
        generated_sketch = None
        sketch_image_data = None
        
        if generate_sketch:
            logger.info("Step 3: Generating face sketch...")
            image_base64, prompt_used, gen_time = await face_generator_service.generate_face(
                description=text,
                attributes=attributes,
                style="portrait"
            )
            generated_sketch = GenerateSketchResponse(
                image_base64=image_base64,
                prompt_used=prompt_used,
                generation_time_seconds=gen_time
            )
            
            # Decode for matching
            sketch_image_data = base64.b64decode(image_base64)
        
        # Step 4: Match faces (if sketch was generated)
        face_matches = None
        if sketch_image_data:
            logger.info("Step 4: Matching faces...")
            matches, search_time = await face_embedding_service.search(sketch_image_data, top_k)
            face_matches = FaceMatchingResponse(
                matches=matches,
                query_embedding_generated=True,
                total_database_faces=face_embedding_service.get_database_size(),
                search_time_seconds=search_time
            )
        
        total_time = time.time() - start_time
        logger.info(f"Full analysis complete in {total_time:.2f}s")
        
        return FullAnalysisResponse(
            transcription=transcription,
            attributes=attributes,
            generated_sketch=generated_sketch,
            deepfake_verification=None,  # Not applicable for generated images
            face_matches=face_matches,
            processing_time_seconds=round(total_time, 2),
            disclaimer=(
                "⚠️ This system provides AI-assisted analysis and is NOT definitive "
                "identification. All results are probabilistic and should be verified "
                "by qualified personnel. FOR EDUCATIONAL PURPOSES ONLY."
            )
        )
        
    except Exception as e:
        logger.error(f"Full analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post(
    "/analyze/image",
    response_model=FullAnalysisResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Full analysis from image",
    description="Complete pipeline: Image → Deepfake Check → Face Matching"
)
async def analyze_from_image(
    image_file: UploadFile = File(..., description="Image file to analyze"),
    top_k: int = Form(default=5, ge=1, le=20, description="Number of matches")
):
    """
    Run analysis pipeline from image input.
    
    1. Verify image authenticity (deepfake detection)
    2. Search for similar faces in database
    
    ⚠️ **Educational Project**: Results are AI-generated suggestions only.
    """
    start_time = time.time()
    
    # Validate file
    if image_file.filename:
        extension = f".{image_file.filename.split('.')[-1].lower()}"
        if extension not in settings.allowed_image_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Allowed: {settings.allowed_image_extensions}"
            )
    
    try:
        image_data = await image_file.read()
        
        # Step 1: Deepfake detection
        logger.info("Step 1: Verifying image authenticity...")
        is_real, confidence, verdict, details = await deepfake_detector_service.detect(image_data)
        
        deepfake_result = DeepfakeVerificationResponse(
            is_real=is_real,
            confidence=round(confidence, 4),
            verdict=verdict,
            details=details
        )
        
        # Step 2: Face matching
        logger.info("Step 2: Matching faces...")
        matches, search_time = await face_embedding_service.search(image_data, top_k)
        
        face_matches = FaceMatchingResponse(
            matches=matches,
            query_embedding_generated=True,
            total_database_faces=face_embedding_service.get_database_size(),
            search_time_seconds=search_time
        )
        
        total_time = time.time() - start_time
        logger.info(f"Image analysis complete in {total_time:.2f}s")
        
        return FullAnalysisResponse(
            transcription=None,
            attributes=None,
            generated_sketch=None,
            deepfake_verification=deepfake_result,
            face_matches=face_matches,
            processing_time_seconds=round(total_time, 2),
            disclaimer=(
                "⚠️ This system provides AI-assisted analysis and is NOT definitive "
                "identification. Deepfake detection is probabilistic. All results "
                "should be verified by qualified personnel. FOR EDUCATIONAL PURPOSES ONLY."
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get(
    "/analyze/status",
    summary="Get analysis system status",
    description="Check the status of all analysis modules."
)
async def analysis_status():
    """Get the status of all analysis system components."""
    return {
        "speech_to_text": {
            "model": settings.whisper_model,
            "status": "available"
        },
        "nlp_processor": {
            "model": "spaCy en_core_web_sm",
            "status": "available"
        },
        "face_generator": {
            "model": settings.stable_diffusion_model,
            "status": "available",
            "device": settings.device
        },
        "deepfake_detector": {
            "model": "EfficientNet-B0",
            "status": "available",
            "threshold": settings.deepfake_threshold
        },
        "face_matching": {
            "model": "InsightFace ArcFace",
            "database_size": face_embedding_service.get_database_size(),
            "status": "available"
        },
        "system": {
            "device": settings.device,
            "version": settings.app_version
        },
        "disclaimer": (
            "This is an EDUCATIONAL system. Do not use for real-world "
            "surveillance or law enforcement purposes."
        )
    }
