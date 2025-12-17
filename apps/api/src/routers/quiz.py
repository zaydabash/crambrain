from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any
from datetime import datetime
import logging

from core.deps import get_search_service, get_quiz_service, get_chroma_store
from models.types import QuizRequest, QuizResponse, QuizQuestion

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(
    request: dict = Body(...),
    search_service = Depends(get_search_service),
    quiz_service = Depends(get_quiz_service)
):
    """Generate quiz with multiple question types and spaced repetition"""
    try:
        # Handle both 'n' (from frontend) and 'num_questions' (from model)
        if 'n' in request and 'num_questions' not in request:
            request['num_questions'] = request['n']
        
        # Convert dict to QuizRequest model for validation
        quiz_request = QuizRequest(**request)
        logger.info(f"Generating quiz for doc_id: {quiz_request.doc_id}")
        
        # Get document content for quiz generation by searching
        search_results = await search_service.search(
            query=quiz_request.topic or "general content",
            doc_id=quiz_request.doc_id,
            top_k=20  # More content for quiz generation
        )
        
        if not search_results:
            raise HTTPException(status_code=404, detail="No content found for quiz generation")
        
        # Convert search results to snippets format expected by generate_quiz
        snippets = [
            {
                "text": result.text,
                "page": result.page,
                "content": result.text,
            }
            for result in search_results
        ]
        
        # Generate quiz using the existing generate_quiz method
        num_questions = quiz_request.num_questions
        quiz_items = await quiz_service.generate_quiz(
            snippets=snippets,
            n=num_questions
        )
        
        # Convert quiz items to QuizQuestion format
        questions = [
            QuizQuestion(
                type=item.get("type", "short_answer"),
                prompt=item.get("prompt", ""),
                answer=item.get("answer", ""),
                page=item.get("page", 1),
                quote=item.get("quote", ""),
                options=item.get("options"),
            )
            for item in quiz_items
        ]
        
        return QuizResponse(
            questions=questions,
            doc_id=quiz_request.doc_id,
            generated_at=datetime.utcnow().isoformat(),
            estimated_time=len(questions) * 2  # Estimate 2 minutes per question
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@router.post("/cram-plan")
async def generate_cram_plan(
    request: dict,
    chroma_store = Depends(get_chroma_store),
    quiz_service = Depends(get_quiz_service)
):
    """Generate a 20-minute cram plan"""
    try:
        doc_id = request.get("doc_id")
        time_minutes = request.get("time_minutes", 20)
        
        logger.info(f"Generating {time_minutes}-minute cram plan for doc_id: {doc_id}")
        
        # Get document structure
        doc = await chroma_store.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate study plan
        plan = await quiz_service.generate_cram_plan(
            doc_id=doc_id,
            time_minutes=time_minutes
        )
        
        return {
            "plan": plan,
            "doc_id": doc_id,
            "time_minutes": time_minutes,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate cram plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate cram plan: {str(e)}")

@router.get("/concept-graph/{doc_id}")
async def get_concept_graph(
    doc_id: str,
    chroma_store = Depends(get_chroma_store),
    quiz_service = Depends(get_quiz_service)
):
    """Get concept graph showing topic connections"""
    try:
        logger.info(f"Generating concept graph for doc_id: {doc_id}")
        
        # Get document and analyze concepts
        doc = await chroma_store.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate concept graph
        graph = await quiz_service.generate_concept_graph(doc_id)
        
        return {
            "graph": graph,
            "doc_id": doc_id,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate concept graph: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate concept graph: {str(e)}")
