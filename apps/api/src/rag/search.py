"""
Search service with hybrid BM25 + vector search
"""

import logging
from typing import List, Optional, Dict, Any
import numpy as np
from rag.store import ChromaStore
from rag.embed import EmbeddingService
from models.types import RetrievalResult

logger = logging.getLogger(__name__)

class SearchService:
    """Hybrid search service combining BM25 and vector search"""
    
    def __init__(self, chroma_store: ChromaStore, embedding_service: EmbeddingService):
        self.chroma_store = chroma_store
        self.embedding_service = embedding_service
    
    async def search(
        self,
        query: str,
        doc_id: Optional[str] = None,
        top_k: int = 10
    ) -> List[RetrievalResult]:
        """Perform hybrid search"""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.embed_text(query)
            
            # Vector search
            vector_results = await self.chroma_store.search(
                query_embedding=query_embedding,
                doc_id=doc_id,
                top_k=top_k * 2  # Get more results for fusion
            )
            
            # BM25 search (simple keyword matching for now)
            bm25_results = await self._bm25_search(query, doc_id, top_k * 2)
            
            # Reciprocal Rank Fusion
            fused_results = self._reciprocal_rank_fusion(
                vector_results, bm25_results, top_k
            )
            
            # Convert to RetrievalResult objects
            retrieval_results = []
            for result in fused_results:
                metadata = result["metadata"]
                retrieval_result = RetrievalResult(
                    doc_id=metadata["doc_id"],
                    page=metadata["page"],
                    bbox_id=metadata.get("bbox_id"),
                    text=result["text"],
                    score=result["score"],
                    preview_url=self._get_preview_url(metadata),
                    source_url=self._get_source_url(metadata)
                )
                retrieval_results.append(retrieval_result)
            
            return retrieval_results
            
        except Exception as e:
            logger.error(f"Failed to perform search: {e}")
            raise
    
    async def _bm25_search(
        self,
        query: str,
        doc_id: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Simple BM25-style keyword search"""
        try:
            # Get all documents from Chroma
            all_results = await self.chroma_store.search(
                query_embedding=[0.0] * 384,  # Dummy embedding
                doc_id=doc_id,
                top_k=1000  # Get many results for BM25 scoring
            )
            
            # Simple keyword scoring
            query_terms = query.lower().split()
            scored_results = []
            
            for result in all_results:
                text = result["text"].lower()
                score = 0
                
                for term in query_terms:
                    if term in text:
                        score += text.count(term)
                
                if score > 0:
                    result["score"] = score
                    scored_results.append(result)
            
            # Sort by score and return top_k
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            return scored_results[:top_k]
            
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Combine results using Reciprocal Rank Fusion"""
        try:
            # Create score maps
            vector_scores = {}
            bm25_scores = {}
            
            for i, result in enumerate(vector_results):
                doc_id = result["metadata"]["doc_id"]
                page = result["metadata"]["page"]
                key = f"{doc_id}:{page}"
                vector_scores[key] = 1.0 / (i + 1)
            
            for i, result in enumerate(bm25_results):
                doc_id = result["metadata"]["doc_id"]
                page = result["metadata"]["page"]
                key = f"{doc_id}:{page}"
                bm25_scores[key] = 1.0 / (i + 1)
            
            # Combine scores
            combined_scores = {}
            all_keys = set(vector_scores.keys()) | set(bm25_scores.keys())
            
            for key in all_keys:
                vector_score = vector_scores.get(key, 0)
                bm25_score = bm25_scores.get(key, 0)
                combined_scores[key] = vector_score + bm25_score
            
            # Sort by combined score
            sorted_keys = sorted(combined_scores.keys(), key=lambda k: combined_scores[k], reverse=True)
            
            # Return top results
            results = []
            for key in sorted_keys[:top_k]:
                # Find the result with this key
                for result in vector_results + bm25_results:
                    doc_id = result["metadata"]["doc_id"]
                    page = result["metadata"]["page"]
                    if f"{doc_id}:{page}" == key:
                        result["score"] = combined_scores[key]
                        results.append(result)
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Reciprocal rank fusion failed: {e}")
            return vector_results[:top_k]  # Fallback to vector results
    
    def _get_preview_url(self, metadata: Dict[str, Any]) -> str:
        """Get preview URL from metadata"""
        preview_urls = metadata.get("preview_urls", "").split(",")
        page = metadata.get("page", 1)
        if preview_urls and len(preview_urls) >= page:
            return preview_urls[page - 1]
        return ""
    
    def _get_source_url(self, metadata: Dict[str, Any]) -> str:
        """Get source URL from metadata"""
        return metadata.get("file_url", "")
