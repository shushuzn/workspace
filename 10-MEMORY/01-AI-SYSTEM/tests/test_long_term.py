"""
Tests for long_term module.
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_memory_system.long_term import LongTermMemory


class TestLongTermMemory:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_path = Path(self.temp_file.name)
        self.temp_file.close()
        self.ltm = LongTermMemory(storage_path=self.temp_path)

    def teardown_method(self):
        if self.temp_path.exists():
            self.temp_path.unlink()

    def test_add_and_get(self):
        self.ltm.add("key1", "value1")
        assert self.ltm.get("key1") == "value1"

    def test_get_nonexistent(self):
        assert self.ltm.get("nonexistent") is None

    def test_search(self):
        self.ltm.add("project", "AI Memory System")
        self.ltm.add("user", "Alice")
        results = self.ltm.search("AI")
        assert len(results) >= 1
        assert any("AI Memory System" in str(r["value"]) for r in results)

    def test_remove(self):
        self.ltm.add("key1", "value1")
        assert self.ltm.remove("key1") is True
        assert self.ltm.get("key1") is None

    def test_clear(self):
        self.ltm.add("k1", "v1")
        self.ltm.add("k2", "v2")
        self.ltm.clear()
        assert self.ltm.size() == 0

    def test_save_and_load(self):
        self.ltm.add("key1", "value1")
        self.ltm.add("key2", "value2")
        self.ltm.save()

        new_ltm = LongTermMemory(storage_path=self.temp_path)
        assert new_ltm.get("key1") == "value1"
        assert new_ltm.get("key2") == "value2"

    def test_size(self):
        self.ltm.add("k1", "v1")
        self.ltm.add("k2", "v2")
        assert self.ltm.size() == 2

    def test_keywords_extraction(self):
        self.ltm.add("test", "Python programming language")
        results = self.ltm.search("Python")
        assert len(results) >= 1
