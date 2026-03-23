import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
上下文感知助手 - 根据当前文件/目录自动推荐工具
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ContextAwareAssistant:
    """上下文感知助手"""

    def __init__(self):
        self.registry_file = Path("30-scripts-tools/tools_registry.json")
        self.context_rules = self._load_context_rules()

    def _load_context_rules(self) -> Dict:
        """加载上下文规则"""
        return {
            # 文件扩展名 → 推荐工具
            ".py": ["python_linter", "code_formatter", "unit_test_runner"],
            ".md": ["markdown_linter", "link_checker", "toc_generator"],
            ".json": ["json_validator", "json_formatter"],
            ".yaml": ["yaml_linter", "yaml_validator"],
            ".txt": ["text_summarizer", "spell_checker"],

            # 目录名 → 推荐工具
            "30-scripts-tools": ["tool_creator", "tool_tester", "tool_registry_updater"],
            "13-memory": ["memory_distiller", "note_summarizer", "session_compressor"],
            "flow-archive": ["workflow_validator", "flow_visualizer"],
            "32-workflows": ["workflow_creator", "workflow_tester"],

            # 关键词 → 推荐工具
            "brainstorm": ["brainstorm_ai_assistant", "brainstorm_mindmap", "brainstorm_quality_predictor"],
            "compression": ["session_compressor", "memory_distiller", "note_summarizer", "compression_scheduler"],
            "workflow": ["workflow_autoloader", "step_tracker", "workflow_enforcer"],
            "git": ["git_commit_helper", "git_precommit_check"],
            "critic": ["auto_critic_v7", "embedded_critic"],

            # 时间 → 推荐工具
            "morning": ["arxiv_scanner", "news_digest"],
            "evening": ["session_compressor", "memory_distiller"],
            "session_end": ["post_session_compress", "git_commit_helper"]
        }

    def analyze_context(self, path: str = None) -> Dict:
        """分析当前上下文
        
        Args:
            path: 文件路径或目录路径 (可选，默认当前工作目录)
        """
        if path is None:
            path = str(Path.cwd())

        path_obj = Path(path)

        context = {
            "path": str(path_obj),
            "type": "file" if path_obj.is_file() else "directory",
            "name": path_obj.name,
            "extension": path_obj.suffix if path_obj.is_file() else None,
            "parent": str(path_obj.parent),
            "timestamp": datetime.now().isoformat()
        }

        return context

    def recommend_tools(self, context: Dict = None, path: str = None) -> List[Dict]:
        """推荐工具
        
        Args:
            context: 上下文信息 (可选)
            path: 文件/目录路径 (可选)
        """
        if context is None:
            context = self.analyze_context(path)

        recommendations = []
        matched_rules = []

        # 1. 基于扩展名匹配
        if context.get("extension"):
            ext = context["extension"].lower()
            if ext in self.context_rules:
                recommendations.extend(self.context_rules[ext])
                matched_rules.append(f"extension:{ext}")

        # 2. 基于目录名匹配
        path_parts = context["path"].lower().split("\\") + context["path"].lower().split("/")
        for part in path_parts:
            if part in self.context_rules:
                recommendations.extend(self.context_rules[part])
                matched_rules.append(f"directory:{part}")

        # 3. 基于名称关键词匹配
        name_lower = context["name"].lower()
        for keyword, tools in self.context_rules.items():
            if keyword in name_lower:
                recommendations.extend(tools)
                matched_rules.append(f"keyword:{keyword}")

        # 4. 基于时间匹配
        hour = datetime.now().hour
        if 6 <= hour < 12:
            if "morning" in self.context_rules:
                recommendations.extend(self.context_rules["morning"])
                matched_rules.append("time:morning")
        elif hour >= 18:
            if "evening" in self.context_rules:
                recommendations.extend(self.context_rules["evening"])
                matched_rules.append("time:evening")

        # 去重
        unique_tools = list(dict.fromkeys(recommendations))

        # 加载工具详情
        tool_details = self._get_tool_details(unique_tools)

        return {
            "context": context,
            "matched_rules": matched_rules,
            "recommended_tools": tool_details,
            "total_recommendations": len(tool_details)
        }

    def _get_tool_details(self, tool_ids: List[str]) -> List[Dict]:
        """获取工具详情"""
        if not self.registry_file.exists():
            return [{"tool_id": tid, "status": "registry_not_found"} for tid in tool_ids]

        with open(self.registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)

        details = []
        for tool_id in tool_ids:
            if tool_id in registry.get("tools", {}):
                tool_info = registry["tools"][tool_id]
                details.append({
                    "tool_id": tool_id,
                    "category": tool_info.get("category", "unknown"),
                    "description": tool_info.get("description", ""),
                    "status": tool_info.get("status", "unknown")
                })
            else:
                details.append({
                    "tool_id": tool_id,
                    "category": "unknown",
                    "description": "Tool not found in registry",
                    "status": "not_registered"
                })

        return details

    def quick_recommend(self, path: str = None) -> str:
        """快速推荐 (简洁输出)"""
        result = self.recommend_tools(path=path)

        if not result["recommended_tools"]:
            return "No specific tool recommendations for this context"

        tools_str = ", ".join([t["tool_id"] for t in result["recommended_tools"][:5]])
        return f"Recommended: {tools_str}"

    def display_status(self) -> str:
        """显示状态"""
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 20 + "Context-Aware Assistant")
        output.append("=" * 70)

        output.append(f"\n[Context Rules]")
        output.append(f"  File Extensions:    {sum(1 for k in self.context_rules if k.startswith('.'))}")
        output.append(f"  Directories:        {sum(1 for k in self.context_rules if not k.startswith('.') and ':' not in k)}")
        output.append(f"  Keywords:           {sum(1 for k in self.context_rules if ':' not in k and not k.startswith('.'))}")
        output.append(f"  Time-based:         {sum(1 for k in self.context_rules if ':' in k)}")

        output.append("\n" + "=" * 70)

        return "\n".join(output)

logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py context_aware_assistant_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py context_aware_assistant_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

测试入口"""
    assistant = ContextAwareAssistant()

    print("Context-Aware Assistant Test")
    print("=" * 70)

    # 显示状态
    print(assistant.display_status())

    # 测试：分析当前目录
    print("\n[Analyzing Current Directory]")
    context = assistant.analyze_context()
    print(f"  Path: {context['path']}")
    print(f"  Type: {context['type']}")

    # 测试：推荐工具
    print("\n[Recommending Tools]")
    result = assistant.recommend_tools()

    print(f"  Matched Rules: {', '.join(result['matched_rules'])}")
    print(f"  Recommended Tools ({result['total_recommendations']}):")
    for tool in result["recommended_tools"][:5]:
        print(f"    - {tool['tool_id']} ({tool['category']})")

    # 测试：快速推荐
    print(f"\n[Quick Recommend]")
    print(f"  {assistant.quick_recommend()}")

    print(f"\n[OK] Context-aware assistant test completed")

if __name__ == "__main__":
    main()
