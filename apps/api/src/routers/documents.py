from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import logging

from core.deps import get_chroma_store, get_search_service
from models.types import DocumentListResponse, DocumentResponse, SearchResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/docs", response_model=DocumentListResponse)
async def list_documents(
    chroma_store = Depends(get_chroma_store)
):
    """List all documents"""
    try:
        documents = await chroma_store.list_documents()
        return DocumentListResponse(documents=documents)
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/docs/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    chroma_store = Depends(get_chroma_store)
):
    """Get document details"""
    try:
        doc = await chroma_store.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(**doc)
        
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document")

@router.get("/search", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., description="Search query"),
    doc_id: Optional[str] = Query(None, description="Filter by document ID"),
    top_k: int = Query(10, description="Number of results"),
    search_service = Depends(get_search_service)
):
    """Search documents with strict grounding"""
    try:
        results = await search_service.search(
            query=q,
            top_k=top_k,
            doc_id=doc_id
        )
        
        return SearchResponse(
            query=q,
            results=results,
            total=len(results)
        )
        
    except Exception as e:
        logger.error(f"Failed to search documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to search documents")
