from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
import logging

from core.deps import get_rate_limiter, get_search_service, get_answer_service
from models.types import QueryRequest, QueryResponse, Citation

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    raw_request: Request,
    rate_limiter = Depends(get_rate_limiter),
    search_service = Depends(get_search_service),
    answer_service = Depends(get_answer_service)
):
    """Ask question with strict grounding and clickable citations"""
    try:
        logger.info(f"Processing question: {request.query}")

        await rate_limiter.check_rate_limit(raw_request)
        
        # Search with strict retrieval
        retrieval_results = await search_service.search(
            query=request.query,
            top_k=request.top_k,
            doc_id=request.doc_id
        )
        
        # Validate retrieval quality
        if not retrieval_results:
            return QueryResponse(
                answer="I couldn't find relevant information in your documents to answer this question.",
                citations=[],
                retrieval=[],
                grounding_score=0.0
            )
        
        # Generate grounded answer
        answer_result = await answer_service.generate_answer(
            query=request.query,
            retrieval_results=retrieval_results
        )
        
        # Extract citations with page anchors
        citations = []
        for result in retrieval_results:
            citation = Citation(
                page=result.page,
                text=result.text[:200] + "..." if len(result.text) > 200 else result.text,
                score=result.score,
                doc_id=result.doc_id,
                chunk_id=result.chunk_id,
                bbox_id=result.metadata.get("bbox_id") # Ensure bbox_id is passed if available
            )
            citations.append(citation)
        
        return QueryResponse(
            answer=answer_result.answer,
            citations=citations,
            retrieval=retrieval_results,
            grounding_score=answer_result.grounding_score
        )
        
    except Exception as e:
        logger.error(f"Failed to process question: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")
