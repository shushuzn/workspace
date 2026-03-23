"""
Memory retrieval module - search and recall from memory stores.
"""

from typing import Any, Optional

from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .config import RETRIEVAL_TOP_K


class MemoryRetriever:
    """
    Unified retrieval interface across short and long-term memory.
    """

    def __init__(
        self,
        short_term: ShortTermMemory,
        long_term: LongTermMemory,
        top_k: int = RETRIEVAL_TOP_K,
    ):
        self._short_term = short_term
        self._long_term = long_term
        self._top_k = top_k

    def search(self, query: str, memory_type: str = "all") -> list[dict]:
        """
        Search memories.

        Args:
            query: Search query string
            memory_type: "short", "long", or "all"

        Returns:
            List of {source, key, value, score} dicts
        """
        results = []

        if memory_type in ("short", "all"):
            # Search short-term by recent items
            recent = self._short_term.get_recent(n=self._top_k * 2)
            for key, value in recent:
                # Simple keyword match scoring
                score = self._calc_score(query, str(value))
                if score > 0:
                    results.append(
                        {
                            "source": "short",
                            "key": key,
                            "value": value,
                            "score": score,
                        }
                    )

        if memory_type in ("long", "all"):
            # Search long-term
            long_results = self._long_term.search(query, top_k=self._top_k)
            for item in long_results:
                item["source"] = "long"
                results.append(item)

        # Dedupe by key (prefer long-term if duplicate)
        seen = {}
        for r in results:
            if r["key"] not in seen:
                seen[r["key"]] = r
            elif r["score"] > seen[r["key"]]["score"]:
                seen[r["key"]] = r

        # Sort and limit
        final = list(seen.values())
        final.sort(key=lambda x: x["score"], reverse=True)
        return final[: self._top_k]

    def recall(self, key: str) -> Optional[Any]:
        """
        Direct recall by key.
        Checks short-term first, then long-term.
        """
        # Try short-term first
        value = self._short_term.get(key)
        if value is not None:
            return value

        # Fall back to long-term
        return self._long_term.get(key)

    @staticmethod
    def _calc_score(query: str, text: str) -> float:
        """Simple keyword-based relevance score."""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())

        if not query_words:
            return 0.0

        intersection = query_words & text_words
        return len(intersection) / len(query_words)

    def get_context(self, query: str, max_items: int = 5) -> str:
        """
        Get formatted context string for LLM prompt.

        Combines relevant memories into a single context string.
        """
        results = self.search(query, memory_type="all")[:max_items]

        if not results:
            return ""

        lines = ["[Relevant Memories]"]
        for r in results:
            lines.append(f"- [{r['source']}] {r['key']}: {r['value']}")

        return "\n".join(lines)
