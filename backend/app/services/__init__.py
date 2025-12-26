"""Services package."""
from app.services.speech_to_text import speech_service
from app.services.nlp_processor import nlp_service
from app.services.face_generator import face_generator_service
from app.services.deepfake_detector import deepfake_detector_service
from app.services.face_embeddings import face_embedding_service

__all__ = [
    "speech_service",
    "nlp_service", 
    "face_generator_service",
    "deepfake_detector_service",
    "face_embedding_service"
]
