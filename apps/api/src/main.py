"""
CramBrain API - Full RAG Implementation
Production-ready API with strict grounding, PDF processing, and advanced features
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Core imports
from core.settings import get_settings
from core.logging import setup_logging
import core.deps as deps

# Services
from rag.store import ChromaStore
from rag.embed import EmbeddingService
from rag.search import SearchService
from rag.answer import AnswerService
from rag.quiz import QuizService
from utils.s3 import S3Service
from utils.pdf import PDFProcessor

# Routers
from routers import ingest, chat, quiz, documents

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load settings once (fail fast if required env missing)
settings = get_settings()

def require_api_key(request: Request):
    """Simple API key check using X-API-Key; no-op if API_KEY not set."""
    if settings.api_key:
        header_key = request.headers.get("x-api-key")
        if not header_key or header_key != settings.api_key:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    try:
        logger.info("Initializing services...")
        
        # Chroma vector store
        deps.chroma_store = ChromaStore(settings)
        await deps.chroma_store.initialize()
        
        # Embedding service
        deps.embedding_service = EmbeddingService()
        await deps.embedding_service.initialize()
        
        # S3 service
        deps.s3_service = S3Service(settings)
        
        # PDF processor
        deps.pdf_processor = PDFProcessor(settings)
        
        # Search service
        deps.search_service = SearchService(deps.chroma_store, deps.embedding_service)
        
        # Answer service
        deps.answer_service = AnswerService(deps.search_service, settings.openai_api_key)
        
        # Quiz service
        deps.quiz_service = QuizService(settings, deps.embedding_service)
        
        logger.info("All services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # In production, we want to crash if services fail to initialize
        raise
    finally:
        logger.info("Shutting down services...")

# Create FastAPI app
app = FastAPI(
    title="CramBrain API",
    description="AI-powered study assistant with strict grounding and advanced RAG",
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[Depends(require_api_key)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Include routers
app.include_router(ingest.router, prefix="/v1", tags=["ingest"])
app.include_router(chat.router, prefix="/v1", tags=["chat"])
app.include_router(quiz.router, prefix="/v1", tags=["quiz"])
app.include_router(documents.router, prefix="/v1", tags=["documents"])

# Health check endpoint
@app.get("/health")
@app.get("/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "ok",
            "chroma": "ok" if deps.chroma_store else "not initialized",
            "embeddings": "ok" if deps.embedding_service else "not initialized",
            "s3": "ok" if deps.s3_service else "not initialized"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )