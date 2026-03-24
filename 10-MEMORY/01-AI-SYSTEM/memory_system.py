"""
Core memory system - unified interface for short and long-term memory.
"""

from typing import Any, Optional

from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .retrieval import MemoryRetriever
from .distiller import MemoryDistiller


class MemorySystem:
    """
    Unified memory system combining short-term and long-term storage.

    Usage:
        ms = MemorySystem()
        ms.add("user_name", "Alice")
        ms.add("last_login", "2026-03-23")

        # Search memories
        results = ms.search("alice login")

        # Get with context
        context = ms.get_context("user preferences")

        # Distill memories
        distilled = ms.distill()

        # Persist
        ms.save()
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize memory system with optional config overrides."""
        # Short-term: recent context in memory
        self._short_term = ShortTermMemory(
            max_items=config.get("short_term_max_items", 100) if config else 100
        )

        # Long-term: persistent storage
        self._long_term = LongTermMemory()

        # Retrieval: unified search
        self._retriever = MemoryRetriever(
            short_term=self._short_term,
            long_term=self._long_term,
        )

        # Distiller: memory compression
        self._distiller = MemoryDistiller()

    def add(self, key: str, value: Any, memory_type: str = "short") -> None:
        """
        Add a memory entry.

        Args:
            key: Unique identifier for this memory
            value: The content to store
            memory_type: "short" for short-term, "long" for long-term
        """
        if memory_type == "short":
            self._short_term.add(key, value)
        else:
            self._long_term.add(key, value)

    def get(self, key: str) -> Optional[Any]:
        """
        Get a memory by key.
        Checks short-term first, then long-term.
        """
        return self._retriever.recall(key)

    def search(self, query: str, memory_type: str = "all") -> list[dict]:
        """
        Search memories by query string.

        Args:
            query: Search query
            memory_type: "short", "long", or "all"

        Returns:
            List of {source, key, value, score} dicts
        """
        return self._retriever.search(query, memory_type)

    def semantic_search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Semantic search using embeddings.
        Only searches long-term memory.
        Requires sentence-transformers package.
        """
        return self._retriever.semantic_search(query, top_k)

    def get_context(self, query: str, max_items: int = 5) -> str:
        """
        Get formatted context string for LLM prompts.

        Useful for RAG-style augmentation.
        """
        return self._retriever.get_context(query, max_items)

    def distill(self) -> dict:
        """
        Distill memories into compressed form.

        Combines recent short-term memories, compresses them,
        and returns summary + insights.
        """
        # Get recent short-term memories
        recent = self._short_term.get_recent(n=20)

        if not recent:
            return {
                "summary": "",
                "key_insights": [],
                "compressed_memories": [],
            }

        # Format for distillation
        memories = [{"key": k, "value": v, "source": "short"} for k, v in recent]

        # Also get some long-term for context
        long_memories = []
        for key in self._long_term.keys()[-10:]:
            value = self._long_term.get(key)
            if value:
                long_memories.append(
                    {
                        "key": key,
                        "value": value,
                        "source": "long",
                    }
                )

        # Combine and distill
        all_memories = memories + long_memories
        distilled = self._distiller.compress(all_memories)

        return {
            "summary": distilled["summary"],
            "key_insights": distilled["key_insights"],
            "keywords": distilled["keywords"],
            "compressed_memories": [
                {"key": m["key"], "value": m["value"]} for m in memories[:10]
            ],
        }

    def save(self) -> None:
        """Persist long-term memory to disk."""
        self._long_term.save()

    def load(self) -> None:
        """Load long-term memory from disk."""
        # LongTermMemory loads automatically in __init__
        pass

    def clear(self, memory_type: str = "all") -> None:
        """
        Clear memory.

        Args:
            memory_type: "short", "long", or "all"
        """
        if memory_type in ("short", "all"):
            self._short_term.clear()
        if memory_type in ("long", "all"):
            self._long_term.clear()

    def stats(self) -> dict:
        """Get memory system statistics."""
        return {
            "short_term_size": self._short_term.size(),
            "long_term_size": self._long_term.size(),
            "short_term_keys": self._short_term.keys(),
            "long_term_keys": self._long_term.keys(),
        }

    def __repr__(self) -> str:
        return (
            f"MemorySystem(short={self._short_term.size()}, "
            f"long={self._long_term.size()})"
        )
