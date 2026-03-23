#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Research Tool - OpenClaw Skill Runner

Integrates FLARE planner, MEMORA memory, and AutoTool selection.
"""

import sys
from pathlib import Path
import json

sys.stdout.reconfigure(encoding="utf-8")

# Use ai_memory_system
ai_memory = Path("D:/ai_memory_system")
sys.path.insert(0, str(ai_memory))

from ai_memory_system.ai_research_tool import ResearchTool, get_research_tool


def format_research_result(result):
    """Format research result for display"""
    lines = [
        f"🔬 研究任务: {result['task']}",
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


def format_add_result(result):
    """Format add memory result"""
    if result["success"]:
        return f"✅ 已添加研究记忆 [{result['memory_id'][:8]}]: 长度 {result.get('stats', {}).get('total_memories', '?')} 条记忆"
    return "❌ 添加失败"


def format_search_result(result):
    """Format search result"""
    if not result["results"]:
        return f"🔍 无研究记忆结果: {result['query']}"

    lines = [f"🔍 研究记忆搜索 '{result['query']}' ({result['count']} 条):"]
    for r in result["results"]:
        lines.append(f"  • {r['abstraction'][:60]}...")
        if r.get("cue_anchors"):
            lines.append(f"    锚点: {', '.join(r['cue_anchors'][:3])}")
    return "\n".join(lines)


def format_next_result(result):
    """Format next tool result"""
    if result["next"]:
        return f"🔧 {result['current']} → {result['next']} (via {result['method']}, 效率 {result['efficiency']:.1%})"
    return f"🔧 {result['current']} → 无惯性建议 (使用 LLM)"


def main():
    """CLI entry point"""
    action = sys.argv[1] if len(sys.argv) > 1 else "stats"
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    tool = get_research_tool()

    if action == "research":
        result = tool.research(**params)
        print(format_research_result(result))

    elif action == "add":
        result = tool.add_research_memory(**params)
        print(format_add_result(result))

    elif action == "search":
        result = tool.search_research_memory(**params)
        print(format_search_result(result))

    elif action == "next":
        result = tool.get_next_tool(**params)
        print(format_next_result(result))

    elif action == "stats":
        stats = tool.memory.stats()
        print("📊 AI Research 系统状态:")
        print(f"  总记忆数: {stats.get('total_memories', 0)}")
        print(f"  平均token节省: {stats.get('avg_token_savings', 0):.1%}")
        print(f"  检索模式: harmonic")

    else:
        print(f"❌ 未知动作: {action}")
        print("可用: research, add, search, next, stats")


if __name__ == "__main__":
    main()
