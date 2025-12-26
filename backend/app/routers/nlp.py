"""
NLP Processing API Router.
Handles text processing and attribute extraction.
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.schemas import NLPProcessingRequest, NLPProcessingResponse, ErrorResponse
from app.services.nlp_processor import nlp_service


router = APIRouter()


@router.post(
    "/process-description",
    response_model=NLPProcessingResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Process text description",
    description="Extract facial attributes from a text description using NLP."
)
async def process_description(request: NLPProcessingRequest):
    """
    Process a text description and extract facial attributes.
    
    - **text**: Text description of a person's appearance
    
    Returns extracted facial attributes, entities, and keywords.
    """
    if not request.text or len(request.text.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="Description text must be at least 5 characters"
        )
    
    try:
        logger.info(f"Processing description: {request.text[:50]}...")
        
        attributes, entities, keywords = nlp_service.process_description(request.text)
        
        return NLPProcessingResponse(
            attributes=attributes,
            entities=entities,
            keywords=keywords
        )
        
    except Exception as e:
        logger.error(f"NLP processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


@router.post(
    "/extract-attributes",
    response_model=NLPProcessingResponse,
    summary="Extract facial attributes",
    description="Alias for /process-description endpoint."
)
async def extract_attributes(request: NLPProcessingRequest):
    """Alias endpoint for process_description."""
    return await process_description(request)
