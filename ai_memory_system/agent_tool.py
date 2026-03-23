"""
OpenClaw Agent Memory Tool - Wrapper for MemorySystem.

Provides a simple string-based interface for AI agents to interact with memory.
"""

from .memory_system import MemorySystem


class MemoryAgentTool:
    """
    OpenClaw Agent 记忆工具 - 提供记忆存取和检索能力。

    Wraps MemorySystem to provide string-based return values
    suitable for direct Agent output.
    """

    def __init__(self):
        """Initialize the memory tool with a new MemorySystem instance."""
        self._ms = MemorySystem()
        self._ms.load()

    def memorize(self, key: str, value: str, memory_type: str = "short") -> str:
        """
        记忆存储 - 添加记忆。

        Args:
            key: Unique identifier for this memory
            value: The content to store
            memory_type: "short" for short-term, "long" for long-term

        Returns:
            Confirmation string
        """
        self._ms.add(key, value, memory_type)
        self._ms.save()
        return f"✅ 已记忆 [{memory_type}]: {key} = {value}"

    def batch_memorize(self, memories: list, memory_type: str = "short") -> str:
        """批量记忆存储 - 一次添加多条记忆。"""
        if not memories:
            return "❌ 记忆列表为空"
        count = 0
        for m in memories:
            if isinstance(m, dict) and "key" in m and "value" in m:
                self._ms.add(m["key"], m["value"], memory_type)
                count += 1
            elif isinstance(m, (list, tuple)) and len(m) >= 2:
                self._ms.add(str(m[0]), str(m[1]), memory_type)
                count += 1
        self._ms.save()
        return f"✅ 已批量记忆 {count} 条 [{memory_type}]"

    def recall(self, key: str) -> str:
        """
        记忆召回 - 根据 key 获取记忆。

        Args:
            key: The memory key to retrieve

        Returns:
            The stored value or not found message
        """
        result = self._ms.get(key)
        if result is None:
            return f"❌ 未找到记忆: {key}"
        return f"📝 [{key}]: {result}"

    def recall_all(self) -> str:
        """查看所有记忆。"""
        stats = self._ms.stats()
        short_keys = stats["short_term_keys"]
        long_keys = stats["long_term_keys"]

        if not short_keys and not long_keys:
            return "📝 暂无记忆"

        lines = ["📝 所有记忆:"]

        if short_keys:
            lines.append("  短期记忆:")
            for k in short_keys:
                v = self._ms.get(k)
                lines.append(f"    {k}: {v}")

        if long_keys:
            lines.append("  长期记忆:")
            for k in long_keys:
                v = self._ms.get(k)
                lines.append(f"    {k}: {v}")

        return "\n".join(lines)

    def search_memories(self, query: str, top_k: int = 3) -> str:
        """
        记忆搜索 - 语义搜索相关记忆。

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            Formatted search results
        """
        results = self._ms.search(query)
        if not results:
            return f"🔍 无搜索结果: {query}"

        lines = [f"🔍 搜索 '{query}' (共 {len(results)} 条结果):"]
        for i, r in enumerate(results[:top_k], 1):
            lines.append(f"  {i}. [{r['source']}] {r['key']} = {r['value']}")
        return "\n".join(lines)

    def get_context(self, query: str) -> str:
        """
        获取上下文 - RAG 风格注入 LLM。

        Args:
            query: Query to get context for

        Returns:
            Formatted context string for LLM injection
        """
        context = self._ms.get_context(query)
        if not context.strip():
            return f"📭 无上下文: {query}"
        return f"📚 上下文:\n{context}"

    def distill_memories(self) -> str:
        """
        记忆蒸馏 - 压缩提炼。

        Returns:
            Distilled summary of memories
        """
        distilled = self._ms.distill()

        if not distilled["summary"] and not distilled["key_insights"]:
            return "📭 暂无记忆可蒸馏"

        lines = ["🧠 记忆蒸馏结果:"]

        if distilled["summary"]:
            lines.append(f"\n📝 摘要:\n{distilled['summary']}")

        if distilled["key_insights"]:
            lines.append(f"\n💡 关键洞察 ({len(distilled['key_insights'])}):")
            for insight in distilled["key_insights"]:
                lines.append(f"  • {insight}")

        if distilled.get("keywords"):
            lines.append(f"\n🔑 关键词: {', '.join(distilled['keywords'])}")

        return "\n".join(lines)

    def clear_short_term(self) -> str:
        """
        清理短期记忆。

        Returns:
            Confirmation message
        """
        stats = self._ms.stats()
        short_count = stats["short_term_size"]
        self._ms.clear(memory_type="short")
        return f"🗑️ 已清理短期记忆 ({short_count} 条)"

    def get_status(self) -> str:
        """
        状态查询。

        Returns:
            Current status of the memory system
        """
        stats = self._ms.stats()
        lines = [
            "📊 记忆系统状态:",
            f"  短期记忆: {stats['short_term_size']} 条",
            f"  长期记忆: {stats['long_term_size']} 条",
        ]
        if stats["short_term_keys"]:
            lines.append(f"  短期 Key: {', '.join(stats['short_term_keys'][:5])}")
        if stats["long_term_keys"]:
            lines.append(f"  长期 Key: {', '.join(stats['long_term_keys'][:5])}")
        return "\n".join(lines)

    def help(self) -> str:
        """显示帮助信息。"""
        return """🧠 AI Memory System 帮助

可用命令:
  memorize      添加记忆      memorize '{"key": "name", "value": "Alice", "memory_type": "short"}'
  batch_memorize 批量添加    batch_memorize '{"memories": [{"key": "k1", "value": "v1"}], "memory_type": "short"}'
  recall       召回记忆    recall '{"key": "name"}'
  search   搜索记忆    search '{"query": "关键词", "top_k": 5}'
  context  RAG上下文   context '{"query": "query", "max_items": 5}'
  distill  蒸馏压缩    distill
  clear    清理短期    clear
  status   查看状态    status
  help     显示帮助    help

示例:
  py active_skills/memory-assistant/run_memory.py status
  py active_skills/memory-assistant/run_memory.py memorize '{"key": "user", "value": "Alice", "memory_type": "long"}'
  py active_skills/memory-assistant/run_memory.py search '{"query": "alice"}'"""

    def run(self, action: str, **kwargs) -> str:
        actions = {
            "memorize": self.memorize,
            "batch_memorize": self.batch_memorize,
            "recall": self.recall,
            "recall_all": self.recall_all,
            "search": self.search_memories,
            "context": self.get_context,
            "distill": self.distill_memories,
            "clear": self.clear_short_term,
            "status": self.get_status,
            "help": self.help,
        }
        if action not in actions:
            return f"❌ 未知动作: {action}"
        return actions[action](**kwargs)
