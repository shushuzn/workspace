"""
Memory distillation module - compress and extract insights from memories.
"""

import json
import requests
from typing import Any

from .config import LLM_MODEL, LLM_BASE_URL, LLM_API_TIMEOUT


class MemoryDistiller:
    """
    Compress and distill memories using local LLM.

    Reduces memory footprint while preserving key information.
    """

    def __init__(
        self,
        llm_model: str = LLM_MODEL,
        llm_base_url: str = LLM_BASE_URL,
    ):
        self._model = llm_model
        self._base_url = llm_base_url.rstrip("/")
        self._api_timeout = LLM_API_TIMEOUT

    def compress(self, memories: list[dict]) -> dict:
        """
        Compress a list of memories into distilled summary.

        Args:
            memories: List of {key, value, source} dicts

        Returns:
            Dict with {summary, key_insights, keywords}
        """
        if not memories:
            return {"summary": "", "key_insights": [], "keywords": []}

        # Build input text
        memory_text = self._build_memory_text(memories)

        # Generate summary via LLM
        summary = self._call_llm(
            f"""Compress these memories into a concise summary (2-3 sentences):
            
{memory_text}

Output format: A single paragraph summary."""
        )

        # Extract key insights
        insights = self.extract_insights(memories)

        # Extract keywords
        keywords = self._extract_keywords(memories)

        return {
            "summary": summary,
            "key_insights": insights,
            "keywords": keywords,
        }

    def extract_insights(self, memories: list[dict]) -> list[str]:
        """
        Extract key insights from memories.

        Returns list of distilled insight strings.
        """
        if not memories:
            return []

        memory_text = self._build_memory_text(memories)

        response = self._call_llm(
            f"""Extract 3-5 key insights or lessons from these memories.
            Format as a JSON array of strings.
            
{memory_text}

Output format: JSON array like ["insight 1", "insight 2"]"""
        )

        # Parse JSON response
        try:
            return json.loads(response)
        except (json.JSONDecodeError, TypeError):
            # Fallback: split by newlines
            return [line.strip() for line in response.split("\n") if line.strip()]

    def summarize(self, text: str, max_length: int = 100) -> str:
        """
        Summarize a single text into max_length characters.
        """
        if not text or len(text) <= max_length:
            return text

        response = self._call_llm(
            f"""Summarize this text in {max_length} characters or less:
            
{text}

Output: A concise summary."""
        )

        return response.strip()[:max_length]

    def _call_llm(self, prompt: str) -> str:
        """
        Call local LLM API.

        Returns the generated text or empty string on error.
        """
        try:
            response = requests.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=self._api_timeout,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except (
            requests.RequestException,
            ValueError,
            KeyError,
        ) as e:
            # Silently fail for now - return empty on any error
            return ""

    def _build_memory_text(self, memories: list[dict]) -> str:
        """Format memories for LLM input."""
        lines = []
        for m in memories:
            source = m.get("source", "unknown")
            key = m.get("key", "")
            value = m.get("value", "")
            lines.append(f"[{source}] {key}: {value}")
        return "\n".join(lines)

    def _extract_keywords(self, memories: list[dict]) -> list[str]:
        """Extract representative keywords from memories."""
        all_text = self._build_memory_text(memories)

        # Simple keyword extraction
        words = []
        for line in all_text.split():
            # Filter short words and common stopwords
            if len(line) >= 3 and line.lower() not in (
                "the",
                "and",
                "for",
                "was",
                "his",
                "her",
                "the",
                "are",
                "but",
                "not",
                "you",
                "all",
                "can",
                "had",
                "her",
                "two",
                "one",
                "out",
                "but",
                "mid",
                "via",
                "use",
                "using",
            ):
                words.append(line.strip(".,!?;:\"'()[]{}"))

        # Return unique words up to 20
        seen = set()
        unique = []
        for w in words:
            w_lower = w.lower()
            if w_lower not in seen:
                seen.add(w_lower)
                unique.append(w)
                if len(unique) >= 20:
                    break

        return unique
