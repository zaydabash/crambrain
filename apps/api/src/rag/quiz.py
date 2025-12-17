# apps/api/src/rag/quiz.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QuizService:
    """
    Minimal, safe implementation that won't crash your server.
    It returns grounded-looking items from retrieved snippets.
    You can improve LLM quality later; this gets you deployed now.
    """
    def __init__(self, client: Optional[Any] = None, model: str = "gpt-4o-mini") -> None:
        self.client = client
        self.model = model

    async def generate_quiz(
        self,
        snippets: List[Dict[str, Any]],
        n: int = 10,
    ) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if not snippets:
            return items

        # Create up to n short-answer items from the top snippets
        for i, s in enumerate(snippets[: max(1, min(n, len(snippets)))]):
            text = (s.get("text") or s.get("content") or "").strip()
            page = s.get("page")
            quote = text[:240]
            prompt = f"Based on the notes on page {page}, what is the key idea?"
            answer = quote or "Refer to the cited page."
            items.append(
                {
                    "type": "short-answer",
                    "prompt": prompt,
                    "answer": answer,
                    "page": page,
                    "quote": quote,
                }
            )
        return items

    async def generate_cram_plan(
        self,
        snippets: List[Dict[str, Any]],
        n: int = 10,
        topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns a simple, deterministic cram plan so the endpoint is stable.
        """
        plan: List[Dict[str, Any]] = []
        if not snippets:
            return {"plan": plan}

        for i, s in enumerate(snippets[: max(1, min(n, len(snippets)))]):
            page = s.get("page")
            title = (s.get("headings") or ["Topic"])[0] if isinstance(s.get("headings"), list) else "Topic"
            plan.append(
                {
                    "step": i + 1,
                    "title": f"Review: {title}",
                    "action": "Read the highlighted snippet and summarize in 2 bullets.",
                    "page": page,
                }
            )
        return {"plan": plan}