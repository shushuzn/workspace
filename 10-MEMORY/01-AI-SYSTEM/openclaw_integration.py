"""
OpenClaw Integration - Makes AI Memory System compatible with OpenClaw workspace.

Usage:
    from ai_memory_system.openclaw_integration import OpenClawMemoryTool
    tool = OpenClawMemoryTool()
    tool.add_memory("user_name", "Alice")
    results = tool.search_memory("alice")
"""

from typing import Any

from .memory_system import MemorySystem


class OpenClawMemoryTool:
    """OpenClaw-compatible wrapper for the AI Memory System."""

    def __init__(self):
        self._ms = MemorySystem()

    def add_memory(self, key: str, value: Any, memory_type: str = "short") -> dict:
        self._ms.add(key, value, memory_type)
        return {"success": True, "key": key, "type": memory_type}

    def get_memory(self, key: str) -> dict:
        value = self._ms.get(key)
        return {"success": value is not None, "key": key, "value": value}

    def search_memory(
        self, query: str, memory_type: str = "all", top_k: int = 5
    ) -> dict:
        results = self._ms.search(query, memory_type)[:top_k]
        return {"success": True, "query": query, "results": results}

    def get_context(self, query: str, max_items: int = 5) -> dict:
        context = self._ms.get_context(query, max_items)
        return {"success": True, "context": context}

    def distill_memories(self) -> dict:
        distilled = self._ms.distill()
        return {"success": True, "distilled": distilled}

    def save_memories(self) -> dict:
        self._ms.save()
        return {"success": True}

    def clear_memories(self, memory_type: str = "all") -> dict:
        self._ms.clear(memory_type)
        return {"success": True, "type": memory_type}

    def get_stats(self) -> dict:
        return {"success": True, "stats": self._ms.stats()}

    def run(self, action: str, **kwargs) -> dict:
        actions = {
            "add": self.add_memory,
            "get": self.get_memory,
            "search": self.search_memory,
            "context": self.get_context,
            "distill": self.distill_memories,
            "save": self.save_memories,
            "clear": self.clear_memories,
            "stats": self.get_stats,
        }
        if action not in actions:
            return {"success": False, "error": f"Unknown action: {action}"}
        return actions[action](**kwargs)
