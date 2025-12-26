"""Pydantic models for API requests and responses."""
from typing import Optional, List
from pydantic import BaseModel, Field


class TranscriptionResponse(BaseModel):
    """Response model for speech-to-text transcription."""
    text: str = Field(..., description="Transcribed text from audio")
    language: str = Field(default="en", description="Detected language")
    duration_seconds: float = Field(..., description="Audio duration in seconds")
    confidence: float = Field(default=1.0, description="Transcription confidence")


class FacialAttributes(BaseModel):
    """Extracted facial attributes from text description."""
    age_range: Optional[str] = Field(None, description="Estimated age range (e.g., '25-35')")
    gender: Optional[str] = Field(None, description="Gender (male/female)")
    hair_color: Optional[str] = Field(None, description="Hair color")
    hair_style: Optional[str] = Field(None, description="Hair style (short, long, bald, etc.)")
    facial_hair: Optional[str] = Field(None, description="Facial hair description")
    face_shape: Optional[str] = Field(None, description="Face shape (oval, round, square, etc.)")
    skin_tone: Optional[str] = Field(None, description="Skin tone description")
    glasses: Optional[bool] = Field(None, description="Whether person wears glasses")
    distinctive_features: List[str] = Field(default=[], description="Distinctive features like scars, moles")
    raw_description: str = Field(..., description="Original cleaned description")


class NLPProcessingRequest(BaseModel):
    """Request model for NLP processing."""
    text: str = Field(..., description="Text description to process")


class NLPProcessingResponse(BaseModel):
    """Response model for NLP processing."""
    attributes: FacialAttributes
    entities: List[dict] = Field(default=[], description="Extracted named entities")
    keywords: List[str] = Field(default=[], description="Important keywords")


class GenerateSketchRequest(BaseModel):
    """Request model for face sketch generation."""
    description: str = Field(..., description="Text description of the face")
    style: str = Field(default="portrait", description="Image style: portrait, sketch, realistic")
    attributes: Optional[FacialAttributes] = Field(None, description="Pre-extracted facial attributes")


class GenerateSketchResponse(BaseModel):
    """Response model for face sketch generation."""
    image_base64: str = Field(..., description="Generated image as base64 string")
    prompt_used: str = Field(..., description="Final prompt used for generation")
    generation_time_seconds: float = Field(..., description="Time taken to generate")


class DeepfakeVerificationResponse(BaseModel):
    """Response model for deepfake detection."""
    is_real: bool = Field(..., description="Whether image is classified as real")
    confidence: float = Field(..., description="Confidence score (0-1)")
    verdict: str = Field(..., description="Human-readable verdict")
    details: dict = Field(default={}, description="Additional detection details")
    disclaimer: str = Field(
        default="AI detection is not 100% accurate. Results should be verified by experts.",
        description="Important disclaimer"
    )


class FaceMatch(BaseModel):
    """Single face match result."""
    id: str = Field(..., description="Face database ID")
    name: str = Field(..., description="Name or label")
    similarity_score: float = Field(..., description="Cosine similarity score (0-1)")
    image_path: str = Field(..., description="Path to matched face image")
    similarity_percentage: float = Field(..., description="Similarity as percentage")


class FaceMatchingRequest(BaseModel):
    """Request model for face matching."""
    top_k: int = Field(default=5, description="Number of top matches to return")


class FaceMatchingResponse(BaseModel):
    """Response model for face matching."""
    matches: List[FaceMatch] = Field(default=[], description="List of matched faces")
    query_embedding_generated: bool = Field(default=True, description="Whether embedding was generated")
    total_database_faces: int = Field(default=0, description="Total faces in database")
    search_time_seconds: float = Field(..., description="Time taken for search")
    disclaimer: str = Field(
        default="AI-based matching provides suggestions only, not definitive identification.",
        description="Important disclaimer"
    )


class FullAnalysisRequest(BaseModel):
    """Request model for full pipeline analysis."""
    include_sketch_generation: bool = Field(default=True, description="Whether to generate sketch")
    top_k_matches: int = Field(default=5, description="Number of face matches")


class FullAnalysisResponse(BaseModel):
    """Response model for full analysis pipeline."""
    transcription: Optional[TranscriptionResponse] = None
    attributes: Optional[FacialAttributes] = None
    generated_sketch: Optional[GenerateSketchResponse] = None
    deepfake_verification: Optional[DeepfakeVerificationResponse] = None
    face_matches: Optional[FaceMatchingResponse] = None
    processing_time_seconds: float = Field(..., description="Total processing time")
    disclaimer: str = Field(
        default="⚠️ This system provides AI-assisted analysis and is NOT definitive identification. "
                "Results should be verified by human experts. For educational purposes only.",
        description="System-wide disclaimer"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: str = Field(default="UNKNOWN_ERROR", description="Error code")
