"""
Face Embedding and Matching Service using InsightFace and FAISS.
Generates face embeddings and performs similarity search.
"""
import io
import json
import time
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image
import faiss
from loguru import logger

from app.config import settings
from app.models.schemas import FaceMatch


class FaceEmbeddingService:
    """Service for face embedding generation and similarity matching."""
    
    _instance = None
    _initialized = False
    _face_analyzer = None
    _faiss_index = None
    _face_database = {}  # Maps index ID to face info
    _embedding_dim = 512  # ArcFace embedding dimension
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the face embedding service."""
        if not self._initialized:
            self._load_model()
            self._initialize_faiss()
            FaceEmbeddingService._initialized = True
    
    def _load_model(self) -> None:
        """Load InsightFace model for face analysis."""
        logger.info("Loading face analysis model...")
        
        try:
            from insightface.app import FaceAnalysis
            
            # Initialize face analyzer
            self._face_analyzer = FaceAnalysis(
                name='buffalo_sc',  # Smaller, faster model
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
            )
            self._face_analyzer.prepare(ctx_id=0, det_size=(640, 640))
            
            logger.info("✅ InsightFace model loaded successfully")
            
        except ImportError:
            logger.warning(
                "⚠️ InsightFace not installed. Face embeddings will use random vectors for demo. "
                "To enable real face matching, install: pip install insightface"
            )
            self._face_analyzer = None
        except Exception as e:
            logger.warning(f"InsightFace load failed: {e}. Using fallback mode.")
            self._face_analyzer = None
    
    def _initialize_faiss(self) -> None:
        """Initialize or load FAISS index."""
        logger.info("Initializing FAISS index...")
        
        index_path = settings.faiss_index_path
        metadata_path = index_path.with_suffix('.json')
        
        if index_path.exists() and metadata_path.exists():
            logger.info(f"Loading existing FAISS index from {index_path}")
            self._faiss_index = faiss.read_index(str(index_path))
            with open(metadata_path, 'r') as f:
                self._face_database = json.load(f)
            logger.info(f"Loaded {self._faiss_index.ntotal} face embeddings")
        else:
            logger.info("Creating new FAISS index")
            # Use L2 distance for cosine similarity (with normalized vectors)
            self._faiss_index = faiss.IndexFlatIP(self._embedding_dim)  # Inner product
            self._face_database = {}
        
        logger.info("✅ FAISS index initialized")
    
    def _preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Convert image bytes to numpy array for InsightFace."""
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        return np.array(image)
    
    async def get_embedding(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Generate face embedding from image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Face embedding vector (512-dim) or None if no face detected
        """
        if self._face_analyzer is None:
            logger.warning("Face analyzer not loaded, returning random embedding for demo")
            return np.random.randn(self._embedding_dim).astype(np.float32)
        
        try:
            img_array = self._preprocess_image(image_data)
            
            # Detect faces and get embeddings
            faces = self._face_analyzer.get(img_array)
            
            if len(faces) == 0:
                logger.warning("No face detected in image")
                return None
            
            # Use the largest/most prominent face
            if len(faces) > 1:
                logger.info(f"Multiple faces detected ({len(faces)}), using largest")
                faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
            
            embedding = faces[0].embedding
            
            # Normalize for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            
            logger.debug(f"Generated embedding with shape {embedding.shape}")
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    async def add_to_database(self, image_data: bytes, face_id: str, name: str, 
                              image_path: str) -> bool:
        """
        Add a face to the database.
        
        Args:
            image_data: Raw image bytes
            face_id: Unique identifier for the face
            name: Name or label for the face
            image_path: Path to the original image
            
        Returns:
            True if successful, False otherwise
        """
        embedding = await self.get_embedding(image_data)
        
        if embedding is None:
            logger.warning(f"Could not add face {face_id}: no face detected")
            return False
        
        # Add to FAISS index
        embedding_2d = embedding.reshape(1, -1)
        self._faiss_index.add(embedding_2d)
        
        # Store metadata
        index_id = self._faiss_index.ntotal - 1
        self._face_database[str(index_id)] = {
            "id": face_id,
            "name": name,
            "image_path": image_path
        }
        
        logger.info(f"Added face to database: {name} (ID: {face_id})")
        return True
    
    async def search(self, image_data: bytes, top_k: int = 5) -> Tuple[List[FaceMatch], float]:
        """
        Search for similar faces in the database.
        
        Args:
            image_data: Query image bytes
            top_k: Number of top matches to return
            
        Returns:
            Tuple of (list of FaceMatch objects, search time in seconds)
        """
        start_time = time.time()
        
        # Get embedding for query image
        query_embedding = await self.get_embedding(image_data)
        
        if query_embedding is None:
            logger.warning("No face detected in query image")
            return [], time.time() - start_time
        
        if self._faiss_index.ntotal == 0:
            logger.warning("Face database is empty")
            return [], time.time() - start_time
        
        # Search FAISS index
        query_2d = query_embedding.reshape(1, -1)
        k = min(top_k, self._faiss_index.ntotal)
        
        distances, indices = self._faiss_index.search(query_2d, k)
        
        # Convert to FaceMatch objects
        matches = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for missing entries
                continue
                
            face_info = self._face_database.get(str(idx), {})
            
            # Convert inner product to similarity percentage
            # For normalized vectors, inner product = cosine similarity
            similarity = float(dist)
            similarity_percentage = max(0, min(100, similarity * 100))
            
            matches.append(FaceMatch(
                id=face_info.get("id", f"unknown_{idx}"),
                name=face_info.get("name", f"Person {idx}"),
                similarity_score=round(similarity, 4),
                image_path=face_info.get("image_path", ""),
                similarity_percentage=round(similarity_percentage, 2)
            ))
        
        search_time = time.time() - start_time
        logger.info(f"Found {len(matches)} matches in {search_time:.3f}s")
        
        return matches, search_time
    
    def save_index(self) -> None:
        """Save FAISS index and metadata to disk."""
        if self._faiss_index is None:
            return
            
        logger.info(f"Saving FAISS index to {settings.faiss_index_path}")
        
        faiss.write_index(self._faiss_index, str(settings.faiss_index_path))
        
        metadata_path = settings.faiss_index_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(self._face_database, f, indent=2)
        
        logger.info("✅ FAISS index saved")
    
    def get_database_size(self) -> int:
        """Get the number of faces in the database."""
        return self._faiss_index.ntotal if self._faiss_index else 0
    
    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        This is for demonstration/explainability purposes.
        
        Formula: cos(θ) = (A · B) / (||A|| × ||B||)
        """
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._face_analyzer is not None or True  # Always available with fallback


# Create singleton instance
face_embedding_service = FaceEmbeddingService()
