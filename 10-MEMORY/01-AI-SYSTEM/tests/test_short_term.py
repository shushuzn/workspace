"""
Tests for short_term module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_memory_system.short_term import ShortTermMemory


class TestShortTermMemory:
    def test_add_and_get(self):
        stm = ShortTermMemory(max_items=10)
        stm.add("key1", "value1")
        assert stm.get("key1") == "value1"

    def test_get_nonexistent(self):
        stm = ShortTermMemory()
        assert stm.get("nonexistent") is None

    def test_update_existing(self):
        stm = ShortTermMemory()
        stm.add("key1", "value1")
        stm.add("key1", "value2")
        assert stm.get("key1") == "value2"

    def test_lru_eviction(self):
        stm = ShortTermMemory(max_items=3)
        stm.add("k1", "v1")
        stm.add("k2", "v2")
        stm.add("k3", "v3")
        stm.add("k4", "v4")
        assert stm.get("k1") is None
        assert stm.get("k4") == "v4"

    def test_get_recent(self):
        stm = ShortTermMemory()
        for i in range(5):
            stm.add(f"key{i}", f"value{i}")
        recent = stm.get_recent(3)
        assert len(recent) == 3
        assert recent[-1][0] == "key4"

    def test_clear(self):
        stm = ShortTermMemory()
        stm.add("k1", "v1")
        stm.add("k2", "v2")
        stm.clear()
        assert stm.size() == 0

    def test_size(self):
        stm = ShortTermMemory(max_items=10)
        stm.add("k1", "v1")
        stm.add("k2", "v2")
        assert stm.size() == 2

    def test_contains(self):
        stm = ShortTermMemory()
        stm.add("key1", "value1")
        assert stm.contains("key1") is True
        assert stm.contains("nonexistent") is False

    def test_remove(self):
        stm = ShortTermMemory()
        stm.add("key1", "value1")
        assert stm.remove("key1") is True
        assert stm.remove("nonexistent") is False

    def test_keys(self):
        stm = ShortTermMemory()
        stm.add("k1", "v1")
        stm.add("k2", "v2")
        keys = stm.keys()
        assert set(keys) == {"k1", "k2"}

    def test_to_dict(self):
        stm = ShortTermMemory()
        stm.add("k1", "v1")
        stm.add("k2", "v2")
        d = stm.to_dict()
        assert d == {"k1": "v1", "k2": "v2"}
