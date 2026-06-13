# apps/api/src/rag/quiz.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "is", "are", "was", "were", "be", "been", "this", "that",
    "these", "those", "as", "by", "from", "at", "it", "its", "into",
    "their", "his", "her", "they", "we", "you", "your", "our",
}


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
        if not snippets:
            return []

        n = max(1, n)
        mcq_n = max(1, round(n * 0.2)) if n > 1 else 0
        cloze_n = max(1, round(n * 0.2)) if n > 2 else 0
        short_n = max(0, n - mcq_n - cloze_n)

        items: List[Dict[str, Any]] = []
        items.extend(self._short_answer_items(snippets, short_n))
        items.extend(self._multiple_choice_items(snippets, mcq_n))
        items.extend(self._cloze_items(snippets, cloze_n))

        return items[:n]

    async def generate_cram_plan(
        self,
        snippets: List[Dict[str, Any]],
        n: int = 10,
        topic: Optional[str] = None,
        time_minutes: int = 20,
    ) -> Dict[str, Any]:
        """
        Returns a simple, deterministic cram plan so the endpoint is stable.
        """
        if not snippets:
            return {"plan": []}

        n = max(1, min(n, len(snippets)))
        minutes_per_section = max(1, time_minutes // n)

        plan: List[Dict[str, Any]] = []
        for i, s in enumerate(snippets[:n]):
            page = s.get("page")
            text = (s.get("text") or s.get("content") or "").strip()
            headings = s.get("headings")
            if isinstance(headings, list) and headings:
                title = headings[0]
            else:
                title = self._truncate(self._first_sentence(text), 60) or f"Page {page}"

            plan.append(
                {
                    "step": i + 1,
                    "title": f"Review: {title}",
                    "action": "Read the highlighted snippet and summarize in 2 bullets.",
                    "page": page,
                    "time_minutes": minutes_per_section,
                }
            )
        return {"plan": plan}

    async def generate_concept_graph(
        self,
        snippets: List[Dict[str, Any]],
        doc_id: Optional[str] = None,
        max_concepts: int = 15,
    ) -> Dict[str, Any]:
        """
        Returns a simple, deterministic concept graph built from frequent
        capitalized terms found in the retrieved snippets, connected by
        page co-occurrence.
        """
        if not snippets:
            return {"nodes": [], "edges": []}

        concept_info: Dict[str, Dict[str, Any]] = {}
        page_concepts: Dict[int, set] = {}

        for s in snippets:
            text = s.get("text") or s.get("content") or ""
            page = s.get("page", 0)
            terms = self._extract_concepts(text)
            page_set = page_concepts.setdefault(page, set())
            for term in terms:
                info = concept_info.setdefault(term, {"pages": set(), "count": 0})
                info["pages"].add(page)
                info["count"] += 1
                page_set.add(term)

        top_concepts = sorted(
            concept_info.items(), key=lambda kv: kv[1]["count"], reverse=True
        )[:max_concepts]
        top_terms = {term for term, _ in top_concepts}

        max_count = max((info["count"] for _, info in top_concepts), default=1)
        nodes = [
            {
                "id": term.lower().replace(" ", "_"),
                "label": term,
                "pages": sorted(info["pages"]),
                "importance": round(info["count"] / max_count, 3),
                "type": "concept",
            }
            for term, info in top_concepts
        ]

        edge_counts: Dict[tuple, int] = {}
        for terms in page_concepts.values():
            page_terms = sorted(t for t in terms if t in top_terms)
            for i in range(len(page_terms)):
                for j in range(i + 1, len(page_terms)):
                    key = (page_terms[i], page_terms[j])
                    edge_counts[key] = edge_counts.get(key, 0) + 1

        max_edge_count = max(edge_counts.values(), default=1)
        edges = [
            {
                "source": a.lower().replace(" ", "_"),
                "target": b.lower().replace(" ", "_"),
                "relationship": "co-occurs",
                "strength": round(count / max_edge_count, 3),
            }
            for (a, b), count in edge_counts.items()
        ]

        return {"nodes": nodes, "edges": edges}

    def _short_answer_items(self, snippets: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if count <= 0:
            return items

        for i in range(count):
            s = snippets[i % len(snippets)]
            text = (s.get("text") or s.get("content") or "").strip()
            page = s.get("page")
            quote = text[:240]
            prompt = f"Based on the notes on page {page}, what is the key idea?"
            answer = quote or "Refer to the cited page."
            items.append(
                {
                    "type": "short_answer",
                    "prompt": prompt,
                    "answer": answer,
                    "page": page,
                    "quote": quote,
                }
            )
        return items

    def _multiple_choice_items(self, snippets: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if count <= 0 or not snippets:
            return items

        for i in range(count):
            idx = i % len(snippets)
            s = snippets[idx]
            text = (s.get("text") or s.get("content") or "").strip()
            page = s.get("page")
            correct = self._first_sentence(text) or text[:120] or "See the cited page."

            distractors: List[str] = []
            for j, other in enumerate(snippets):
                if j == idx:
                    continue
                other_text = (other.get("text") or other.get("content") or "").strip()
                sentence = self._first_sentence(other_text)
                if sentence and sentence != correct and sentence not in distractors:
                    distractors.append(sentence)
                if len(distractors) >= 3:
                    break

            while len(distractors) < 3:
                distractors.append(f"None of the above (option {len(distractors) + 2})")

            items.append(
                {
                    "type": "multiple_choice",
                    "prompt": f"Which statement best matches the content on page {page}?",
                    "answer": correct,
                    "page": page,
                    "quote": text[:240],
                    "options": [correct] + distractors[:3],
                }
            )
        return items

    def _cloze_items(self, snippets: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if count <= 0:
            return items

        for i in range(count):
            s = snippets[i % len(snippets)]
            text = (s.get("text") or s.get("content") or "").strip()
            page = s.get("page")
            sentence = self._first_sentence(text)

            prompt, answer = self._make_cloze(sentence)
            if not prompt:
                prompt = f"The key topic on page {page} is _____."
                answer = "see the cited page"

            items.append(
                {
                    "type": "cloze",
                    "prompt": prompt,
                    "answer": answer,
                    "page": page,
                    "quote": sentence or text[:240],
                }
            )
        return items

    def _first_sentence(self, text: str) -> str:
        if not text:
            return ""

        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        sentence = parts[0] if parts else text
        sentence = sentence.strip()
        if len(sentence) > 200:
            sentence = sentence[:200].rsplit(" ", 1)[0] + "..."
        return sentence

    def _truncate(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(" ", 1)[0] + "..."

    def _make_cloze(self, sentence: str) -> tuple[str, str]:
        if not sentence:
            return "", ""

        words = re.findall(r"[A-Za-z][A-Za-z'-]*", sentence)
        candidates = [w for w in words if len(w) > 4 and w.lower() not in _STOPWORDS]
        if not candidates:
            return "", ""

        target = max(candidates, key=len)
        pattern = re.compile(r"\b" + re.escape(target) + r"\b")
        prompt = pattern.sub("_____", sentence, count=1)
        return prompt, target

    def _extract_concepts(self, text: str) -> List[str]:
        """Extract candidate concept phrases (capitalized words/short phrases)."""
        if not text:
            return []

        candidates = re.findall(r"\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){0,2}\b", text)

        seen: List[str] = []
        for c in candidates:
            c = c.strip()
            if len(c) < 3 or c.lower() in _STOPWORDS:
                continue
            if c not in seen:
                seen.append(c)

        return seen[:10]
