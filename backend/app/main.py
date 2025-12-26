"""
Multimodal AI System for Suspect Identification with Deepfake Verification.
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from loguru import logger
import sys
import traceback
import os
from pathlib import Path

# Add ffmpeg to PATH if installed via winget
ffmpeg_paths = [
    Path.home() / "AppData/Local/Microsoft/WinGet/Packages",
]
for base_path in ffmpeg_paths:
    if base_path.exists():
        for ffmpeg_dir in base_path.glob("**/bin"):
            if (ffmpeg_dir / "ffmpeg.exe").exists():
                os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")
                break

from app.config import settings
from app.routers import speech, nlp, face_generation, deepfake, face_matching, analysis


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO"
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG"
)


# Model instances (lazy loaded)
models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    logger.info("🚀 Starting Multimodal AI System...")
    logger.info(f"📍 Device: {settings.device}")
    logger.info(f"📁 Data directory: {settings.data_dir}")
    
    # Models are lazy-loaded on first use to reduce startup time
    logger.info("✅ Application started successfully")
    logger.warning("⚠️  DISCLAIMER: This system is for EDUCATIONAL purposes only")
    
    yield
    
    # Cleanup
    logger.info("👋 Shutting down Multimodal AI System...")
    models.clear()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Multimodal AI System for Suspect Identification with Deepfake Verification

⚠️ **Educational Project Disclaimer**: This system is for educational and research purposes only.
It must NOT be used for real-world surveillance or law enforcement.

### Features
- 🎤 Speech-to-Text transcription
- 🧠 NLP-based attribute extraction
- 🎨 AI face sketch generation
- 🔍 Deepfake detection
- 👤 Face similarity matching

### Ethical Guidelines
- Uses only synthetic/public datasets
- Includes bias awareness messaging
- No demographic predictions
- Full transparency in AI decisions
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/static", StaticFiles(directory=str(settings.uploads_dir)), name="static")

# Mount sample faces for displaying in search results
app.mount("/faces", StaticFiles(directory=str(settings.sample_faces_dir)), name="faces")

# Include routers
app.include_router(speech.router, prefix="/api/v1", tags=["Speech-to-Text"])
app.include_router(nlp.router, prefix="/api/v1", tags=["NLP Processing"])
app.include_router(face_generation.router, prefix="/api/v1", tags=["Face Generation"])
app.include_router(deepfake.router, prefix="/api/v1", tags=["Deepfake Detection"])
app.include_router(face_matching.router, prefix="/api/v1", tags=["Face Matching"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Full Analysis"])


# Global exception handler for better error logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and log them."""
    tb_str = traceback.format_exc()
    logger.error(f"Unhandled exception on {request.url.path}: {exc}")
    logger.error(f"Traceback:\n{tb_str}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url.path)
        }
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "device": settings.device,
        "disclaimer": "This system is for EDUCATIONAL purposes only"
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with system information."""
    return {
        "message": "Multimodal AI System for Suspect Identification",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "disclaimer": "⚠️ EDUCATIONAL PROJECT - Not for real-world law enforcement use"
    }
