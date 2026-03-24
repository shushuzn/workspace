"""
Long-term memory module - persistent storage with simple retrieval.
"""

import json
from pathlib import Path
from typing import Any, Optional

from .config import LONG_TERM_STORAGE_PATH, LONG_TERM_MAX_ITEMS
from .vector_store import VectorStore


class LongTermMemory:
    """
    Persistent storage for long-term memories.
    Uses JSON file storage with simple keyword-based retrieval.
    """

    def __init__(self, storage_path: Path = LONG_TERM_STORAGE_PATH):
        self._storage_path = Path(storage_path)
        self._store: dict[str, dict] = {}  # key -> {value, keywords, timestamp}
        self._vector_store = VectorStore(storage_path)
        self._load()

    def add(self, key: str, value: Any, keywords: Optional[list[str]] = None) -> None:
        """
        Add a long-term memory entry.

        Args:
            key: Unique identifier
            value: The memory content
            keywords: Optional keywords for retrieval
        """
        import time

        # Generate keywords from value if not provided
        if keywords is None:
            keywords = self._extract_keywords(str(value))

        self._store[key] = {
            "value": value,
            "keywords": keywords,
            "timestamp": time.time(),
        }

        self._vector_store.add(key, str(value))

        # Evict oldest if over capacity
        if len(self._store) > LONG_TERM_MAX_ITEMS:
            self._evict_oldest()

    def get(self, key: str) -> Optional[Any]:
        """Get a memory entry by key."""
        if key in self._store:
            return self._store[key]["value"]
        return None

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Search memories by keyword matching.

        Returns list of dicts with {key, value, score} sorted by relevance.
        """
        query_keywords = set(self._extract_keywords(query.lower()))
        if not query_keywords:
            return []

        results = []
        for key, data in self._store.items():
            mem_keywords = set(k.lower() for k in data["keywords"])
            # Simple Jaccard similarity
            intersection = query_keywords & mem_keywords
            if intersection:
                score = len(intersection) / len(query_keywords | mem_keywords)
                results.append(
                    {
                        "key": key,
                        "value": data["value"],
                        "keywords": data["keywords"],
                        "score": score,
                        "timestamp": data["timestamp"],
                    }
                )

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def semantic_search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Semantic search using embeddings.

        Returns list of dicts with {key, value, score} sorted by relevance.
        Requires sentence-transformers package.
        """
        texts = {k: str(v["value"]) for k, v in self._store.items()}
        results = self._vector_store.search(query, texts, top_k)

        # Enrich with full data
        for r in results:
            if r["key"] in self._store:
                r["keywords"] = self._store[r["key"]].get("keywords", [])
                r["timestamp"] = self._store[r["key"]].get("timestamp", 0)

        return results

    def remove(self, key: str) -> bool:
        """Remove a memory entry."""
        if key in self._store:
            del self._store[key]
            self._vector_store.remove(key)
            return True
        return False

    def clear(self) -> None:
        """Clear all long-term memory."""
        self._store.clear()
        self._vector_store.clear()

    def save(self) -> None:
        """Persist memory to disk."""
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._storage_path, "w", encoding="utf-8") as f:
            json.dump(self._store, f, ensure_ascii=False, indent=2)
        self._vector_store.save_vectors()

    def _load(self) -> None:
        """Load memory from disk."""
        if self._storage_path.exists():
            try:
                with open(self._storage_path, "r", encoding="utf-8") as f:
                    self._store = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._store = {}

    def _evict_oldest(self) -> None:
        """Remove the oldest memory entry."""
        if not self._store:
            return
        oldest_key = min(
            self._store.keys(), key=lambda k: self._store[k].get("timestamp", 0)
        )
        del self._store[oldest_key]

    @staticmethod
    def _extract_keywords(text: str) -> list[str]:
        """Extract simple keywords from text."""
        import re

        # Remove special chars, split by whitespace
        words = re.findall(r"\b[a-zA-Z\u4e00-\u9fff]+\b", text.lower())
        # Filter short words
        keywords = [w for w in words if len(w) >= 2]
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for w in keywords:
            if w not in seen:
                seen.add(w)
                unique.append(w)
        return unique[:50]  # Limit to 50 keywords

    def size(self) -> int:
        """Return number of memories stored."""
        return len(self._store)

    def keys(self) -> list[str]:
        """Return all memory keys."""
        return list(self._store.keys())

    def __repr__(self) -> str:
        return f"LongTermMemory(size={len(self._store)}, path={self._storage_path})"
