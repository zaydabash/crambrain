"""
Search service with hybrid BM25 + vector search
"""

import logging
import math
from typing import List, Optional, Dict, Any
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

            # BM25 keyword search
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
                    chunk_id=result["id"],
                    chunk_type=metadata.get("chunk_type", "text"),
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
        """BM25 keyword search over all stored chunks"""
        try:
            chunks = await self.chroma_store.get_all_chunks(doc_id=doc_id)
            if not chunks:
                return []

            query_terms = [t for t in query.lower().split() if t]
            if not query_terms:
                return []

            k1 = 1.5
            b = 0.75

            term_freqs: List[Dict[str, int]] = []
            doc_lengths: List[int] = []
            doc_freq: Dict[str, int] = {}

            for chunk in chunks:
                tokens = chunk["text"].lower().split()
                doc_lengths.append(len(tokens))

                tf: Dict[str, int] = {}
                for token in tokens:
                    tf[token] = tf.get(token, 0) + 1
                term_freqs.append(tf)

                for term in query_terms:
                    if tf.get(term, 0) > 0:
                        doc_freq[term] = doc_freq.get(term, 0) + 1

            n_docs = len(chunks)
            avg_doc_length = sum(doc_lengths) / n_docs if n_docs else 0

            scored_results = []
            for chunk, tf, doc_len in zip(chunks, term_freqs, doc_lengths):
                score = 0.0
                for term in query_terms:
                    f = tf.get(term, 0)
                    if f == 0:
                        continue
                    df = doc_freq.get(term, 0)
                    idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)
                    denom = f + k1 * (1 - b + b * (doc_len / avg_doc_length if avg_doc_length else 1))
                    if denom:
                        score += idf * (f * (k1 + 1)) / denom

                if score > 0:
                    scored_results.append({
                        "id": chunk["id"],
                        "text": chunk["text"],
                        "metadata": chunk["metadata"],
                        "score": score,
                    })

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
            vector_scores = {r["id"]: 1.0 / (i + 1) for i, r in enumerate(vector_results)}
            bm25_scores = {r["id"]: 1.0 / (i + 1) for i, r in enumerate(bm25_results)}

            results_by_id: Dict[str, Dict[str, Any]] = {}
            for r in vector_results + bm25_results:
                results_by_id.setdefault(r["id"], r)

            combined_scores = {
                rid: vector_scores.get(rid, 0) + bm25_scores.get(rid, 0)
                for rid in results_by_id
            }

            sorted_ids = sorted(combined_scores.keys(), key=lambda k: combined_scores[k], reverse=True)

            results = []
            for rid in sorted_ids[:top_k]:
                result = results_by_id[rid]
                result["score"] = combined_scores[rid]
                results.append(result)

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
