"""
Face Matching API Router.
Handles face similarity search and database management.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from loguru import logger

from app.config import settings
from app.models.schemas import FaceMatchingResponse, ErrorResponse
from app.services.face_embeddings import face_embedding_service


router = APIRouter()


@router.post(
    "/match-faces",
    response_model=FaceMatchingResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Find similar faces",
    description="Upload an image and find similar faces in the database."
)
async def match_faces(
    file: UploadFile = File(..., description="Image file to search with"),
    top_k: int = Query(default=5, ge=1, le=20, description="Number of top matches")
):
    """
    Find faces similar to the uploaded image.
    
    - **file**: Image file containing a face
    - **top_k**: Number of top matches to return (1-20)
    
    Returns list of similar faces with similarity scores.
    
    ⚠️ **Disclaimer**: Face matching provides AI suggestions only,
    not definitive identification. Human verification is required.
    """
    # Validate file
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
        
        logger.info(f"Searching for matches: {file.filename}")
        
        # Perform search
        matches, search_time = await face_embedding_service.search(image_data, top_k)
        
        return FaceMatchingResponse(
            matches=matches,
            query_embedding_generated=True,
            total_database_faces=face_embedding_service.get_database_size(),
            search_time_seconds=round(search_time, 4),
            disclaimer=(
                "⚠️ Face matching provides AI-assisted suggestions only, "
                "not definitive identification. All results should be verified "
                "by qualified personnel. For educational purposes only."
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face matching failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Matching failed: {str(e)}"
        )


@router.post(
    "/add-face",
    summary="Add face to database",
    description="Add a new face to the search database."
)
async def add_face(
    file: UploadFile = File(..., description="Image file containing a face"),
    face_id: str = Query(..., description="Unique identifier for this face"),
    name: str = Query(..., description="Name or label for this face")
):
    """
    Add a face to the database for future matching.
    
    - **file**: Image file containing a face
    - **face_id**: Unique identifier for this face
    - **name**: Name or label for this face
    
    ⚠️ Only use synthetic or properly consented images.
    """
    # Validate file
    if file.filename:
        extension = f".{file.filename.split('.')[-1].lower()}"
        if extension not in settings.allowed_image_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format. Allowed: {settings.allowed_image_extensions}"
            )
    
    try:
        image_data = await file.read()
        
        # Save image to uploads directory
        save_path = settings.uploads_dir / f"{face_id}_{file.filename}"
        with open(save_path, 'wb') as f:
            f.write(image_data)
        
        # Add to database
        success = await face_embedding_service.add_to_database(
            image_data=image_data,
            face_id=face_id,
            name=name,
            image_path=str(save_path)
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Could not detect a face in the image"
            )
        
        # Save index
        face_embedding_service.save_index()
        
        return {
            "success": True,
            "face_id": face_id,
            "name": name,
            "database_size": face_embedding_service.get_database_size()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Adding face failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add face: {str(e)}"
        )


@router.get(
    "/database-stats",
    summary="Get database statistics",
    description="Get information about the face database."
)
async def database_stats():
    """Get statistics about the face database."""
    return {
        "total_faces": face_embedding_service.get_database_size(),
        "embedding_dimension": 512,
        "index_type": "FAISS IndexFlatIP",
        "similarity_metric": "Cosine Similarity",
        "disclaimer": "Database contains only synthetic/public dataset faces for educational purposes."
    }


@router.get(
    "/similarity-explained",
    summary="Explain similarity calculation",
    description="Educational explanation of how face similarity is calculated."
)
async def similarity_explained():
    """
    Educational endpoint explaining face similarity calculation.
    
    Useful for understanding how the system works.
    """
    return {
        "title": "Face Similarity Calculation",
        "overview": (
            "The system uses deep learning to convert faces into numerical vectors "
            "(embeddings) and then compares these vectors using cosine similarity."
        ),
        "steps": [
            {
                "step": 1,
                "name": "Face Detection",
                "description": "Locate and crop the face region from the image"
            },
            {
                "step": 2,
                "name": "Feature Extraction",
                "description": "Use ArcFace neural network to convert face to 512-dimensional vector"
            },
            {
                "step": 3,
                "name": "Normalization",
                "description": "Normalize the vector to unit length for cosine similarity"
            },
            {
                "step": 4,
                "name": "Similarity Search",
                "description": "Use FAISS to efficiently find similar vectors in the database"
            }
        ],
        "formula": {
            "name": "Cosine Similarity",
            "latex": "cos(θ) = (A · B) / (||A|| × ||B||)",
            "range": "0 to 1 (0 = different, 1 = identical)"
        },
        "limitations": [
            "Similarity scores are relative, not absolute measures of identity",
            "Lighting, angle, and image quality affect embedding quality",
            "The system may have reduced accuracy across different demographics"
        ]
    }
