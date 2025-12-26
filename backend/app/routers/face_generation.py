"""
Face Generation API Router.
Handles AI-based face sketch generation from descriptions.
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.schemas import (
    GenerateSketchRequest,
    GenerateSketchResponse,
    NLPProcessingRequest,
    ErrorResponse
)
from app.services.face_generator import face_generator_service
from app.services.nlp_processor import nlp_service


router = APIRouter()


@router.post(
    "/generate-sketch",
    response_model=GenerateSketchResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Generate face sketch from description",
    description="Use AI to generate a facial portrait/sketch from a text description."
)
async def generate_sketch(request: GenerateSketchRequest):
    """
    Generate a face sketch/portrait from a text description.
    
    - **description**: Text description of the face
    - **style**: Output style (portrait, sketch, realistic)
    - **attributes**: Pre-extracted facial attributes (optional)
    
    Returns base64-encoded generated image.
    """
    if not request.description or len(request.description.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Description must be at least 10 characters"
        )
    
    try:
        logger.info(f"Generating face with style: {request.style}")
        
        # If attributes not provided, extract them
        attributes = request.attributes
        if attributes is None:
            attributes, _, _ = nlp_service.process_description(request.description)
        
        # Generate face
        image_base64, prompt_used, generation_time = await face_generator_service.generate_face(
            description=request.description,
            attributes=attributes,
            style=request.style
        )
        
        return GenerateSketchResponse(
            image_base64=image_base64,
            prompt_used=prompt_used,
            generation_time_seconds=generation_time
        )
        
    except Exception as e:
        logger.error(f"Face generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Face generation failed: {str(e)}"
        )


@router.post(
    "/generate-from-text",
    response_model=GenerateSketchResponse,
    summary="Generate face from raw text",
    description="Generate a face directly from raw text input."
)
async def generate_from_text(request: NLPProcessingRequest):
    """
    Generate a face sketch from raw text description.
    
    Automatically extracts attributes before generation.
    """
    sketch_request = GenerateSketchRequest(
        description=request.text,
        style="portrait"
    )
    return await generate_sketch(sketch_request)
