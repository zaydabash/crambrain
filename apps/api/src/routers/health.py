"""
Health check router
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from core.deps import get_chroma_store, get_s3_service
from rag.store import ChromaStore
from utils.s3 import S3Service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check(
    chroma: ChromaStore = Depends(get_chroma_store),
    s3: S3Service = Depends(get_s3_service)
):
    """Health check endpoint"""
    try:
        # Check Chroma connection
        chroma_status = "ok"
        try:
            await chroma.list_documents()
        except Exception as e:
            chroma_status = f"error: {str(e)}"
        
        # Check S3 connection
        s3_status = "ok"
        try:
            await s3.list_files()
        except Exception as e:
            s3_status = f"error: {str(e)}"
        
        return {
            "status": "ok",
            "time": datetime.utcnow().isoformat(),
            "services": {
                "chroma": chroma_status,
                "s3": s3_status
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "time": datetime.utcnow().isoformat(),
            "error": str(e)
        }