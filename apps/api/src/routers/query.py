"""
Query and answer router
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from core.deps import get_search_service, get_answer_service, get_quiz_service, get_rate_limiter
from rag.search import SearchService
from rag.answer import AnswerService
from rag.quiz import QuizService
from models.types import QueryRequest, QueryResponse, QuizRequest, QuizResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    search: SearchService = Depends(get_search_service),
    answer: AnswerService = Depends(get_answer_service),
    rate_limiter = Depends(get_rate_limiter)
):
    """Ask question with grounded answer and citations"""
    try:
        # Rate limiting
        await rate_limiter.check_rate_limit()
        
        logger.info(f"Processing question: {request.query}")
        
        # Search for relevant chunks
        search_results = await search.search(
            query=request.query,
            doc_id=request.doc_id,
            top_k=request.top_k
        )
        
        if not search_results:
            return QueryResponse(
                answer="I don't have enough context to answer this question. Please upload some documents first.",
                citations=[],
                retrieval=[]
            )
        
        # Generate grounded answer
        answer_result = await answer.generate_answer(
            query=request.query,
            search_results=search_results
        )
        
        return QueryResponse(
            answer=answer_result.answer,
            citations=answer_result.citations,
            retrieval=search_results
        )
        
    except Exception as e:
        logger.error(f"Failed to process question: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    search: SearchService = Depends(get_search_service),
    quiz: QuizService = Depends(get_quiz_service)
):
    """Generate quiz questions from documents"""
    try:
        logger.info(f"Generating quiz for doc_id: {request.doc_id}")
        
        # Get document content for quiz generation
        search_results = await search.search(
            query=request.topic or "general content",
            doc_id=request.doc_id,
            top_k=20  # More content for quiz generation
        )
        
        if not search_results:
            raise HTTPException(status_code=404, detail="No content found for quiz generation")
        
        # Generate quiz
        quiz_result = await quiz.generate_quiz(
            search_results=search_results,
            num_questions=request.n
        )
        
        return QuizResponse(
            questions=quiz_result.questions,
            doc_id=request.doc_id
        )
        
    except Exception as e:
        logger.error(f"Failed to generate quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")