"""
Short-term memory module - in-memory cache for recent context.
"""

import time
from collections import OrderedDict
from typing import Any, Optional

from .config import SHORT_TERM_MAX_ITEMS, SHORT_TERM_TTL_SECONDS


class ShortTermMemory:
    """
    In-memory cache for short-term context.
    Uses LRU eviction when max_items is reached.
    """

    def __init__(
        self,
        max_items: int = SHORT_TERM_MAX_ITEMS,
        ttl_seconds: int = SHORT_TERM_TTL_SECONDS,
    ):
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._max_items = max_items
        self._ttl = ttl_seconds

    def add(self, key: str, value: Any) -> None:
        """Add or update a memory entry."""
        # Evict expired items first
        self._evict_expired()

        # Remove if exists (to move to end)
        if key in self._store:
            del self._store[key]

        # Add new entry
        self._store[key] = (value, time.time())

        # Evict oldest if over capacity
        while len(self._store) > self._max_items:
            self._store.popitem(last=False)

    def get(self, key: str) -> Optional[Any]:
        """Get a memory entry, returns None if not found or expired."""
        if key not in self._store:
            return None

        value, timestamp = self._store[key]

        # Check if expired
        if time.time() - timestamp > self._ttl:
            del self._store[key]
            return None

        # Move to end (most recently used)
        self._store.move_to_end(key)
        return value

    def get_recent(self, n: int = 10) -> list[tuple[str, Any]]:
        """Get the n most recent entries."""
        self._evict_expired()
        items = list(self._store.items())[-n:]
        return [(k, v[0]) for k, v in items]

    def contains(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None

    def remove(self, key: str) -> bool:
        """Remove a specific key. Returns True if found."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all short-term memory."""
        self._store.clear()

    def _evict_expired(self) -> None:
        """Remove expired entries."""
        now = time.time()
        expired_keys = [k for k, (_, ts) in self._store.items() if now - ts > self._ttl]
        for key in expired_keys:
            del self._store[key]

    def size(self) -> int:
        """Return current number of items."""
        self._evict_expired()
        return len(self._store)

    def keys(self) -> list[str]:
        """Return all keys."""
        self._evict_expired()
        return list(self._store.keys())

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary."""
        self._evict_expired()
        return {k: v[0] for k, v in self._store.items()}

    def __repr__(self) -> str:
        self._evict_expired()
        return f"ShortTermMemory(size={len(self._store)}, max={self._max_items})"
