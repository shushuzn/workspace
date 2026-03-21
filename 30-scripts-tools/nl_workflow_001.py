import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NL-WORKFLOW-001 Natural Language Workflow Generator
[Natural Language Workflow]

功能:
  - 输入描述自动生成工作流
  - 意图识别
  - 工具推荐
  - 步骤规划

使用:
  py nl_workflow_001.py --parse "<description>"
  py nl_workflow_001.py --generate "<description>"
  py nl_workflow_001.py --intent "<description>"
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


INTENT_PATTERNS = {
    "optimize": ["优化", "提升", "改进", "效率", "optimize", "improve"],
    "analyze": ["分析", "研究", "调研", "analyze", "research"],
    "discover": ["发现", "探索", "扫描", "搜索", "discover", "scan", "find"],
    "automate": ["自动", "批量", "批量处理", "automate", "batch"],
    "report": ["报告", "总结", "导出", "report", "summary", "export"],
    "brainstorm": ["头脑风暴", "创意", "想法", "brainstorm", "idea"],
    "test": ["验证", "检查", "test", "verify"],
    "manage": ["管理", "整理", "归档", "manage", "organize"]
}

TOOL_RECOMMENDATIONS = {
    "optimize": ["smart_cache_001", "batch_tools_001", "optimize_master_001"],
    "analyze": ["report_001_summary", "tool_monitor", "auto_discover_001"],
    "discover": ["auto_discover_001", "brainstorm_matcher_001"],
    "automate": ["chain_runner_001", "event_bus_001", "retry_handler_001"],
    "report": ["report_001_summary", "export_format_001", "version_ctrl_001"],
    "brainstorm": ["brainstorm_workflow", "brainstorm_scamper", "brainstorm_sixhats"],
    "test": ["batch_tools_001", "tool_monitor", "auto_discover_001"],
    "manage": ["workflow_market_001", "version_ctrl_001", "undo_redo_001"]
}


class NLWorkflowGenerator:
    """Natural Language Workflow Generator"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.tools_dir = self.workspace / "30-scripts-tools"
    
    def detect_intent(self, description: str) -> Dict:
        """检测意图 - 优先精确匹配"""
        desc_lower = description.lower()
        matched_intents = []
        
        # 精确匹配 (优先)
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if len(pattern) >= 2 and pattern.lower() in desc_lower:
                    matched_intents.append(intent)
                    break
        
        primary = matched_intents[0] if matched_intents else "general"
        return {
            "primary": primary,
            "all": list(set(matched_intents)),
            "confidence": len(matched_intents) / len(INTENT_PATTERNS) if matched_intents else 0
        }
    
    def recommend_tools(self, intents: List[str]) -> List[Dict]:
        """推荐工具"""
        tools = []
        seen = set()
        
        for intent in intents:
            if intent in TOOL_RECOMMENDATIONS:
                for tool in TOOL_RECOMMENDATIONS[intent]:
                    if tool not in seen:
                        tools.append({"tool": tool, "reason": intent})
                        seen.add(tool)
        
        return tools
    
    def generate_workflow(self, description: str) -> Dict:
        """生成工作流"""
        intent_result = self.detect_intent(description)
        intents = intent_result["all"] if intent_result["all"] else [intent_result["primary"]]
        tools = self.recommend_tools(intents)
        
        # 构建步骤
        steps = []
        for t in tools[:5]:  # 最多5步
            steps.append({
                "tool": t["tool"],
                "args": [],
                "reason": t["reason"]
            })
        
        return {
            "description": description,
            "intent": intent_result,
            "workflow": {
                "steps": steps,
                "total_steps": len(steps)
            }
        }
    
    def parse(self, description: str) -> Dict:
        """解析描述"""
        return {
            "input": description,
            "intent": self.detect_intent(description),
            "tools": self.recommend_tools(self.detect_intent(description)["all"] or [self.detect_intent(description)["primary"]])
        }


logging.basicConfig(level=logging.INFO)
def main():
    generator = NLWorkflowGenerator()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        
        if cmd == "--parse" and text:
            result = generator.parse(text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--generate" and text:
            result = generator.generate_workflow(text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--intent" and text:
            result = generator.detect_intent(text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("NL-WORKFLOW-001 Natural Language Workflow Generator")
    print("Usage:")
    print("  py nl_workflow_001.py --parse <description>    # Parse intent")
    print("  py nl_workflow_001.py --generate <description> # Generate workflow")
    print("  py nl_workflow_001.py --intent <description>   # Detect intent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
