"""
Tests for memory_system module.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_memory_system.memory_system import MemorySystem


class TestMemorySystem:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ms = MemorySystem()

    def test_add_and_get_short(self):
        self.ms.add("key1", "value1", "short")
        assert self.ms.get("key1") == "value1"

    def test_add_and_get_long(self):
        self.ms.add("key1", "value1", "long")
        assert self.ms.get("key1") == "value1"

    def test_get_nonexistent(self):
        assert self.ms.get("nonexistent") is None

    def test_search(self):
        self.ms.add("user", "Alice", "short")
        self.ms.add("project", "AI Memory System", "long")
        results = self.ms.search("Alice")
        assert len(results) >= 1
        assert any(r["key"] == "user" for r in results)

    def test_stats(self):
        self.ms.add("k1", "v1", "short")
        self.ms.add("k2", "v2", "long")
        stats = self.ms.stats()
        assert stats["short_term_size"] == 1
        assert stats["long_term_size"] == 1

    def test_clear_short(self):
        self.ms.add("k1", "v1", "short")
        self.ms.add("k2", "v2", "long")
        self.ms.clear("short")
        stats = self.ms.stats()
        assert stats["short_term_size"] == 0
        assert stats["long_term_size"] == 1

    def test_clear_all(self):
        self.ms.add("k1", "v1", "short")
        self.ms.add("k2", "v2", "long")
        self.ms.clear("all")
        stats = self.ms.stats()
        assert stats["short_term_size"] == 0
        assert stats["long_term_size"] == 0

    def test_get_context(self):
        self.ms.add("user_name", "Alice", "short")
        self.ms.add("project", "AI Memory", "long")
        context = self.ms.get_context("Alice")
        assert isinstance(context, str)

    def test_distill(self):
        self.ms.add("k1", "v1", "short")
        self.ms.add("k2", "v2", "long")
        distilled = self.ms.distill()
        assert "summary" in distilled
        assert "key_insights" in distilled
