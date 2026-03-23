"""
Tests for agent_tool module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_memory_system.agent_tool import MemoryAgentTool


class TestMemoryAgentTool:
    def setup_method(self):
        self.tool = MemoryAgentTool()

    def test_memorize(self):
        result = self.tool.memorize("key1", "value1", "short")
        assert "key1" in result
        assert "short" in result

    def test_recall(self):
        self.tool.memorize("key1", "value1", "short")
        result = self.tool.recall("key1")
        assert "value1" in result

    def test_recall_not_found(self):
        result = self.tool.recall("nonexistent")
        assert "not found" in result.lower() or "nonexistent" in result.lower()

    def test_search_memories(self):
        self.tool.memorize("user", "Alice", "short")
        result = self.tool.search_memories("Alice")
        assert "Alice" in result

    def test_get_status(self):
        self.tool.memorize("k1", "v1", "short")
        result = self.tool.get_status()
        assert "短期" in result or "short" in result.lower()

    def test_clear_short_term(self):
        self.tool.memorize("k1", "v1", "short")
        result = self.tool.clear_short_term()
        assert "已清理" in result or "clear" in result.lower()

    def test_run_unknown_action(self):
        result = self.tool.run("unknown_action")
        assert "未知动作" in result
