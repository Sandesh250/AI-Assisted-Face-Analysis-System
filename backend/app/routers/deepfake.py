"""
Deepfake Detection API Router.
Handles image verification for manipulation detection.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger

from app.config import settings
from app.models.schemas import DeepfakeVerificationResponse, ErrorResponse
from app.services.deepfake_detector import deepfake_detector_service


router = APIRouter()


@router.post(
    "/deepfake/verify",
    response_model=DeepfakeVerificationResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Verify image authenticity",
    description="Analyze an image to detect potential deepfake or manipulation."
)
async def verify_image(
    file: UploadFile = File(..., description="Image file to verify (JPG, PNG, WebP)")
):
    """
    Verify if an image is real or potentially manipulated.
    
    - **file**: Image file to analyze
    
    Returns verification result with confidence score and analysis details.
    
    ⚠️ **Disclaimer**: AI detection is not 100% accurate. Results should be
    verified by human experts and should not be used as definitive evidence.
    """
    # Validate file extension
    if file.filename:
        extension = f".{file.filename.split('.')[-1].lower()}"
        if extension not in settings.allowed_image_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format. Allowed: {settings.allowed_image_extensions}"
            )
    
    try:
        image_data = await file.read()
        
        # Check file size
        if len(image_data) > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        logger.info(f"Analyzing image: {file.filename} ({len(image_data)} bytes)")
        
        # Run detection
        is_real, confidence, verdict, details = await deepfake_detector_service.detect(image_data)
        
        return DeepfakeVerificationResponse(
            is_real=is_real,
            confidence=round(confidence, 4),
            verdict=verdict,
            details=details,
            disclaimer=(
                "⚠️ AI-based detection is not 100% accurate. This result should be "
                "verified by experts and must not be used as the sole basis for any "
                "decision. For educational purposes only."
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deepfake detection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )


@router.get(
    "/deepfake/info",
    summary="Get detection info",
    description="Get information about the deepfake detection system."
)
async def detection_info():
    """Get information about the deepfake detection system."""
    return {
        "model": "EfficientNet-B0",
        "threshold": settings.deepfake_threshold,
        "supported_formats": settings.allowed_image_extensions,
        "max_file_size_mb": settings.max_file_size_mb,
        "disclaimer": (
            "This system uses AI to detect potential image manipulation. "
            "Results are probabilistic and should not be considered definitive. "
            "Always verify with human experts for critical decisions."
        ),
        "limitations": [
            "May have reduced accuracy on heavily compressed images",
            "Novel manipulation techniques may not be detected",
            "High-quality deepfakes may evade detection",
            "Results can be affected by image quality and resolution"
        ]
    }
