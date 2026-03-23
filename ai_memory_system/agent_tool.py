"""
OpenClaw Agent Memory Tool - Wrapper for MemorySystem.

Provides a simple string-based interface for AI agents to interact with memory.
"""

from .memory_system import MemorySystem

try:
    from .ai_research_tool import ResearchTool, get_research_tool

    RESEARCH_TOOL_AVAILABLE = True
except ImportError:
    RESEARCH_TOOL_AVAILABLE = False
    ResearchTool = None
    get_research_tool = None


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

    def delete(self, key: str) -> str:
        """删除记忆。"""
        short_removed = self._ms._short_term.remove(key)
        long_removed = self._ms._long_term.remove(key)
        if short_removed or long_removed:
            self._ms.save()
            return f"🗑️ 已删除记忆: {key}"
        return f"❌ 未找到记忆: {key}"

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

    def semantic_search(self, query: str, top_k: int = 3) -> str:
        """语义搜索 - 使用 embeddings 检索记忆。"""
        results = self._ms.semantic_search(query, top_k)
        if not results:
            return f"🔍 无语义搜索结果: {query}"
        lines = [f"🔍 语义搜索 '{query}' (共 {len(results)} 条):"]
        for i, r in enumerate(results[:top_k], 1):
            lines.append(
                f"  {i}. [{r['source']}] {r['key']} = {r['value']} (score: {r['score']:.3f})"
            )
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

    def research(self, task: str) -> str:
        """
        AI 研究任务 - 使用 FLARE/MEMORA/AutoTool 进行研究。

        Args:
            task: 研究任务描述

        Returns:
            研究结果
        """
        if not RESEARCH_TOOL_AVAILABLE:
            return "❌ 研究工具未安装 (需要 ai_research_tool)"

        _get_tool = get_research_tool
        assert _get_tool is not None
        tool = _get_tool()
        result = tool.research(task)

        lines = [
            f"🔬 研究任务: {task}",
            f"✅ 成功: {result['success']}",
            f"📋 计划动作: {len(result['plan']['actions'])} 个",
        ]

        for action in result["plan"]["actions"]:
            lines.append(f"  - [{action['action_type']}] {action['description']}")

        if result.get("tool_sequence"):
            lines.append(f"\n🔧 工具序列 (AutoTool 惯性):")
            for t in result["tool_sequence"]:
                lines.append(f"  - {t['tool']} (via {t['method']})")

        stats = result.get("tool_registry_stats", {})
        if stats:
            lines.append(f"\n📊 工具效率: {stats.get('efficiency_score', 0):.1%}")

        return "\n".join(lines)

    def add_research_memory(self, content: str, entities: str = "") -> str:
        """
        添加研究记忆 - 使用 MEMORA 双层记忆。

        Args:
            content: 记忆内容
            entities: 实体列表 (逗号分隔)

        Returns:
            确认信息
        """
        if not RESEARCH_TOOL_AVAILABLE:
            return "❌ 研究工具未安装"

        _get_tool = get_research_tool
        assert _get_tool is not None
        tool = _get_tool()
        entity_list = [e.strip() for e in entities.split(",")] if entities else None
        result = tool.add_research_memory(content, entity_list)

        if result["success"]:
            return f"✅ 已添加研究记忆 [{result['memory_id'][:8]}]: {content[:50]}..."
        return f"❌ 添加失败"

    def search_research_memory(self, query: str, limit: int = 3) -> str:
        """
        搜索研究记忆 - 使用谐波检索。

        Args:
            query: 搜索查询
            limit: 返回数量

        Returns:
            搜索结果
        """
        if not RESEARCH_TOOL_AVAILABLE:
            return "❌ 研究工具未安装"

        _get_tool = get_research_tool
        assert _get_tool is not None
        tool = _get_tool()
        result = tool.search_research_memory(query, limit=limit)

        if not result["results"]:
            return f"🔍 无研究记忆结果: {query}"

        lines = [f"🔍 研究记忆搜索 '{query}' ({result['count']} 条):"]
        for r in result["results"]:
            lines.append(f"  • {r['abstraction'][:60]}...")
            if r.get("cue_anchors"):
                lines.append(f"    锚点: {', '.join(r['cue_anchors'][:3])}")

        return "\n".join(lines)

    def get_next_tool(self, current_tool: str) -> str:
        """
        获取下一个工具 - 基于 AutoTool 惯性。

        Args:
            current_tool: 当前工具

        Returns:
            下一个工具建议
        """
        if not RESEARCH_TOOL_AVAILABLE:
            return "❌ 研究工具未安装"

        _get_tool = get_research_tool
        assert _get_tool is not None
        tool = _get_tool()
        result = tool.get_next_tool(current_tool)

        if result["next"]:
            return f"🔧 {current_tool} → {result['next']} (via {result['method']}, 效率 {result['efficiency']:.1%})"
        return f"🔧 {current_tool} → 无惯性建议 (使用 LLM)"

    def help(self) -> str:
        """显示帮助信息。"""
        return """🧠 AI Memory System 帮助

可用命令:
  memorize      添加记忆      memorize '{"key": "name", "value": "Alice", "memory_type": "short"}'
  batch_memorize 批量添加    batch_memorize '{"memories": [{"key": "k1", "value": "v1"}], "memory_type": "short"}'
  recall       召回记忆    recall '{"key": "name"}'
  search   搜索记忆    search '{"query": "关键词", "top_k": 5}'
  semantic_search 语义搜索 semantic_search '{"query": "自然语言", "top_k": 5}'
  context  RAG上下文   context '{"query": "query", "max_items": 5}'
  distill  蒸馏压缩    distill
  clear    清理短期    clear
  status   查看状态    status
  help     显示帮助    help

AI研究命令 (FLARE+MEMORA+AutoTool):
  research     AI研究任务   research '{"task": "研究AI Agent规划"}'
  add_research_memory 添加研究记忆 add_research_memory '{"content": "内容", "entities": "e1,e2"}'
  search_research_memory 搜索研究记忆 search_research_memory '{"query": "查询", "limit": 3}'
  get_next_tool 下一工具    get_next_tool '{"current_tool": "research_scan"}'

示例:
  py active_skills/memory-assistant/run_memory.py status
  py active_skills/memory-assistant/run_memory.py memorize '{"key": "user", "value": "Alice", "memory_type": "long"}'
  py active_skills/memory-assistant/run_memory.py search '{"query": "alice"}'
  py active_skills/memory-assistant/run_memory.py research '{"task": "研究自治Agent"}'"""

    def run(self, action: str, **kwargs) -> str:
        actions = {
            "memorize": self.memorize,
            "batch_memorize": self.batch_memorize,
            "delete": self.delete,
            "recall": self.recall,
            "recall_all": self.recall_all,
            "search": self.search_memories,
            "semantic_search": self.semantic_search,
            "context": self.get_context,
            "distill": self.distill_memories,
            "clear": self.clear_short_term,
            "status": self.get_status,
            "help": self.help,
            # AI Research Tool integration
            "research": self.research,
            "add_research_memory": self.add_research_memory,
            "search_research_memory": self.search_research_memory,
            "get_next_tool": self.get_next_tool,
        }
        if action not in actions:
            return f"❌ 未知动作: {action}"
        return actions[action](**kwargs)
