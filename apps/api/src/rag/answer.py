"""
Answer service with strict grounding and citation generation
"""

import logging
from typing import List, Dict, Any
import openai
from rag.search import SearchService
from models.types import AnswerResult, Citation, RetrievalResult

logger = logging.getLogger(__name__)

class AnswerService:
    """Answer service with strict grounding"""
    
    def __init__(self, search_service: SearchService, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.search_service = search_service
        self.openai_api_key = openai_api_key
        self.model = model
        openai.api_key = openai_api_key
    
    async def generate_answer(
        self,
        query: str,
        search_results: List[RetrievalResult]
    ) -> AnswerResult:
        """Generate grounded answer with citations"""
        try:
            if not search_results:
                return AnswerResult(
                    answer="I don't have enough context to answer this question. Please upload some documents first.",
                    citations=[],
                    grounding_score=0.0,
                    retrieval_quality="no_results"
                )
            
            # Prepare context for LLM
            context_parts = []
            for i, result in enumerate(search_results):
                context_parts.append(f"[{i+1}] Page {result.page}: {result.text}")
            
            context = "\n\n".join(context_parts)
            
            # System prompt for strict grounding
            system_prompt = """You are a precise study assistant. Use ONLY the provided CONTEXT from course notes/slides to answer. If the answer isn't in CONTEXT, say you don't know. Every sentence that states a fact must include a source tag like [p.<page>]. Keep answers concise and stepwise when helpful. Never invent citations."""
            
            # User prompt
            user_prompt = f"""QUESTION: {query}

CONTEXT:
{context}

Instructions:
1. Provide a comprehensive answer based on the excerpts
2. Use [p.N] format for page citations (e.g., [p.1], [p.5])
3. Be precise and factual
4. If the answer cannot be found in the excerpts, say so clearly

Answer:"""
            
            # Generate answer
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Extract citations
            citations = self._extract_citations(answer, search_results)
            
            # Calculate grounding score (simplified: based on citation presence and retrieval quality)
            citation_count = len(citations)
            max_possible_citations = min(len(search_results), 5)  # Cap at 5 for score calculation
            grounding_score = min(1.0, (citation_count / max_possible_citations) * 0.8 + 0.2) if max_possible_citations > 0 else 0.0
            
            # Assess retrieval quality based on search result scores
            avg_score = sum(r.score for r in search_results) / len(search_results) if search_results else 0.0
            if avg_score >= 0.8:
                retrieval_quality = "excellent"
            elif avg_score >= 0.6:
                retrieval_quality = "good"
            elif avg_score >= 0.4:
                retrieval_quality = "fair"
            else:
                retrieval_quality = "poor"
            
            return AnswerResult(
                answer=answer,
                citations=citations,
                grounding_score=grounding_score,
                retrieval_quality=retrieval_quality
            )
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise
    
    def _extract_citations(
        self,
        answer: str,
        search_results: List[RetrievalResult]
    ) -> List[Citation]:
        """Extract citations from answer text"""
        citations = []
        
        # Find all [p.N] patterns in the answer
        import re
        page_pattern = r'\[p\.(\d+)\]'
        matches = re.findall(page_pattern, answer)
        
        # Create citation objects
        for page_num in matches:
            page = int(page_num)
            
            # Find the search result for this page
            for result in search_results:
                if result.page == page:
                    citation = Citation(
                        doc_id=result.doc_id,
                        page=page,
                        bbox_id=result.bbox_id,
                        preview_url=result.preview_url,
                        source_url=result.source_url,
                        quote=result.text[:200] + "..." if len(result.text) > 200 else result.text
                    )
                    citations.append(citation)
                    break
        
        return citations
