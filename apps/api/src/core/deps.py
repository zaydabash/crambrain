"""
Dependency injection for FastAPI
"""

import logging
from typing import Optional
from fastapi import HTTPException, Request
from core.settings import get_settings
from rag.store import ChromaStore
from rag.embed import EmbeddingService
from rag.search import SearchService
from rag.answer import AnswerService
from rag.quiz import QuizService
from utils.s3 import S3Service
from utils.pdf import PDFProcessor

logger = logging.getLogger(__name__)

# Global services
chroma_store: Optional[ChromaStore] = None
embedding_service: Optional[EmbeddingService] = None
search_service: Optional[SearchService] = None
answer_service: Optional[AnswerService] = None
quiz_service: Optional[QuizService] = None
s3_service: Optional[S3Service] = None
pdf_processor: Optional[PDFProcessor] = None

def get_chroma_store() -> ChromaStore:
    """Get Chroma store instance"""
    if chroma_store is None:
        raise HTTPException(status_code=503, detail="Chroma store not initialized")
    return chroma_store

def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance"""
    if embedding_service is None:
        raise HTTPException(status_code=503, detail="Embedding service not initialized")
    return embedding_service

def get_search_service() -> SearchService:
    """Get search service instance"""
    if search_service is None:
        raise HTTPException(status_code=503, detail="Search service not initialized")
    return search_service

def get_answer_service() -> AnswerService:
    """Get answer service instance"""
    if answer_service is None:
        raise HTTPException(status_code=503, detail="Answer service not initialized")
    return answer_service

def get_quiz_service() -> QuizService:
    """Get quiz service instance"""
    if quiz_service is None:
        raise HTTPException(status_code=503, detail="Quiz service not initialized")
    return quiz_service

def get_s3_service() -> S3Service:
    """Get S3 service instance"""
    if s3_service is None:
        raise HTTPException(status_code=503, detail="S3 service not initialized")
    return s3_service

def get_pdf_processor() -> PDFProcessor:
    """Get PDF processor instance"""
    if pdf_processor is None:
        raise HTTPException(status_code=503, detail="PDF processor not initialized")
    return pdf_processor

def get_rate_limiter():
    """Get rate limiter instance"""
    # Simple in-memory rate limiter
    return SimpleRateLimiter()

class SimpleRateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
        self.settings = get_settings()
    
    async def check_rate_limit(self, request: Request):
        """Check if request is within rate limit (simple in-memory, per-IP)."""
        import time
        current_time = time.time()
        window_start = current_time - self.settings.rate_limit_window

        ip = request.client.host if request.client else "unknown"

        # Clean old requests
        self.requests = {
            ip_addr: [req_time for req_time in reqs if req_time > window_start]
            for ip_addr, reqs in self.requests.items()
        }

        ip_requests = self.requests.get(ip, [])
        if len(ip_requests) >= self.settings.rate_limit_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        ip_requests.append(current_time)
        self.requests[ip] = ip_requests