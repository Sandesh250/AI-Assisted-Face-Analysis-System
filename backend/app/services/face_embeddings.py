"""
Face Embedding and Matching Service using FaceNet-PyTorch and FAISS.
Generates face embeddings and performs similarity search.
"""
import io
import json
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from PIL import Image
import faiss
from loguru import logger
import torch
import cv2

from app.config import settings
from app.models.schemas import FaceMatch


class FaceEmbeddingService:
    """Service for face embedding generation and similarity matching."""
    
    _instance = None
    _initialized = False
    _model_loaded = False
    _faiss_index = None
    _face_database = {}  # Maps index ID to face info
    _embedding_dim = 512  # FaceNet InceptionResnetV1 embedding dimension
    
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
        """Load DeepFace ArcFace model and MTCNN for face detection."""
        logger.info("Loading DeepFace ArcFace model...")
        
        try:
            from facenet_pytorch import MTCNN
            from deepface import DeepFace
            
            # Disable TF logs
            import os
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3" 
            
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"Using device: {self.device}")
            
            # Face detection (MTCNN)
            self.mtcnn = MTCNN(
                keep_all=False, 
                select_largest=True, 
                device=self.device,
                post_process=True  # Returns normalized tensor
            )
            
            # Load DeepFace model (warmup)
            # We don't need to hold the model instance as DeepFace manages it singleton-style
            # But checking if it loads is good.
            try:
                # Mock call to load model into memory
                dummy_img = np.zeros((112, 112, 3), dtype=np.uint8)
                DeepFace.build_model("ArcFace")
                logger.info("✅ DeepFace ArcFace model loaded successfully")
                self._deepface_ready = True
            except Exception as e:
                logger.error(f"DeepFace ArcFace load failed: {e}")
                raise e
            
            self._model_loaded = True
            
        except ImportError as e:
            logger.error(f"Required libraries not installed: {e}")
            self._model_loaded = False
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            self._model_loaded = False
    
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
            # Use Inner Product (Cosine Similarity) with normalized vectors
            self._faiss_index = faiss.IndexFlatIP(self._embedding_dim)
            self._face_database = {}
        
        logger.info("✅ FAISS index initialized")
    
    async def get_embedding(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Generate face embedding from image.
        """
        if not self._model_loaded:
            logger.warning("Model not loaded, returning random embedding")
            return np.random.randn(self._embedding_dim).astype(np.float32)
        
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            
            # Detect and crop face (returns Tensor [3, 160, 160] or None)
            # MTCNN automatically crops and normalizes
            face_tensor = self.mtcnn(image)
            
            if face_tensor is None:
                logger.warning("No face detected in image")
                return None
            
            # Convert face tensor to numpy array for DeepFace
            # MTCNN returns [C, H, W] tensor, convert to [H, W, C] BGR image
            face_img = face_tensor.permute(1, 2, 0).cpu().numpy()
            
            # Convert from [-1, 1] to [0, 255] and RGB to BGR
            face_img = ((face_img + 1) * 127.5).astype(np.uint8)
            face_img = cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
            
            # Generate embedding with DeepFace
            # enforce_detection=False because we already detected face with MTCNN
            from deepface import DeepFace
            embedding_objs = DeepFace.represent(
                img_path=face_img, 
                model_name="ArcFace", 
                enforce_detection=False, 
                detector_backend="skip",
                align=False  # Already cropped/aligned by MTCNN (roughly)
            )
            
            if not embedding_objs:
                logger.warning("No embedding returned by DeepFace")
                return None
                
            embedding = np.array(embedding_objs[0]["embedding"])
            
            # Normalize embedding (DeepFace ArcFace usually returns normalized, but ensure it)
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    async def add_to_database(self, image_data: bytes, face_id: str, name: str, 
                              image_path: str) -> bool:
        """Add a face to the database."""
        embedding = await self.get_embedding(image_data)
        
        if embedding is None:
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
        """Search for similar faces in the database."""
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
        
        matches = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:
                continue
                
            face_info = self._face_database.get(str(idx), {})
            
            # Convert inner product to similarity percentage
            # For normalized vectors, inner product = cosine similarity
            similarity = float(dist)
            similarity_percentage = max(0.0, min(100.0, similarity * 100))
            
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
        return self._faiss_index.ntotal if self._faiss_index else 0

    def is_loaded(self) -> bool:
        return self._model_loaded


# Create singleton instance
face_embedding_service = FaceEmbeddingService()
