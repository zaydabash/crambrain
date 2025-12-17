"""
Document management router
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from core.deps import get_chroma_store, get_search_service
from rag.store import ChromaStore
from rag.search import SearchService
from models.types import DocumentListResponse, DocumentResponse, SearchResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/docs", response_model=DocumentListResponse)
async def list_documents(
    chroma: ChromaStore = Depends(get_chroma_store)
):
    """List all documents"""
    try:
        documents = await chroma.list_documents()
        return DocumentListResponse(documents=documents)
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

@router.get("/docs/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    chroma: ChromaStore = Depends(get_chroma_store)
):
    """Get document metadata"""
    try:
        document = await chroma.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(**document.dict())
        
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document")

@router.get("/search", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., description="Search query"),
    doc_id: Optional[str] = Query(None, description="Filter by document ID"),
    limit: int = Query(10, description="Number of results"),
    search: SearchService = Depends(get_search_service)
):
    """Lightweight search for UI"""
    try:
        results = await search.search(
            query=q,
            doc_id=doc_id,
            top_k=limit
        )
        
        return SearchResponse(
            query=q,
            results=results,
            total=len(results)
        )
        
    except Exception as e:
        logger.error(f"Failed to search: {e}")
        raise HTTPException(status_code=500, detail="Failed to search")