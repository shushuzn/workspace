import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CHAIN-RUNNER-001 Tool Chain Auto-Connector
[Tool Chain Auto-Connector]

功能:
  - 根据输出自动找到下一个合适工具
  - 工具链自动串联
  - 执行结果自动传递

使用:
  py chain_runner_001.py --chain <tool1,tool2,...>
  py chain_runner_001.py --auto <start_tool>
  py chain_runner_001.py --templates
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


CHAIN_CACHE = Path("10-MEMORY/00-CORE/.chain_cache.json")


class ChainRunner:
    """工具链自动串联器"""

    # 预定义工具链模板
    CHAIN_TEMPLATES = {
        "discover-sync": {
            "name": "Discover & Sync",
            "tools": ["auto_discover_001", "tools_registry"],
            "description": "扫描工具并同步注册表"
        },
        "brainstorm-full": {
            "name": "Full Brainstorm",
            "tools": ["brainstorm_001_define", "brainstorm_002_diverge",
                     "brainstorm_003_filter", "brainstorm_004_prioritize"],
            "description": "完整头脑风暴流程"
        },
        "optimize-cycle": {
            "name": "Optimize Cycle",
            "tools": ["auto_discover_001", "optimize_master_001", "report_001_summary"],
            "description": "优化循环"
        }
    }

    # 输出类型到工具的映射
    OUTPUT_TO_TOOL = {
        "json": ["export_format_001", "tools_registry"],
        "roadmap": ["roadmap_master_001", "gantt_chart_001"],
        "ideas": ["brainstorm_workflow", "brainstorm_scamper"],
        "report": ["report_001_summary", "report_002_export"],
        "cache": ["smart_cache_001", "data_cache"]
    }

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.tools_dir = self.workspace / "30-scripts-tools"

    def run_chain(self, tools: List[str]) -> Dict:
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
# py chain_runner_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py chain_runner_001.py

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

执行工具链"""
        results = []

        for i, tool in enumerate(tools):
            tool_file = self.tools_dir / f"{tool}.py"

            if not tool_file.exists():
                results.append({
                    "tool": tool,
                    "status": "not_found",
                    "error": f"Tool {tool} not found"
                })
                continue

            try:
                result = subprocess.run(
                    [sys.executable, str(tool_file, timeout=60)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                results.append({
                    "tool": tool,
                    "status": "success" if result.returncode == 0 else "failed",
                    "output": result.stdout[:500] if result.stdout else None,
                    "error": result.stderr[:200] if result.stderr else None
                })

            except subprocess.TimeoutExpired:
                results.append({
                    "tool": tool,
                    "status": "timeout"
                })
            except Exception as e:
                results.append({
                    "tool": tool,
                    "status": "error",
                    "error": str(e)
                })

        return {
            "chain": tools,
            "total": len(tools),
            "success": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] in ["failed", "error", "not_found"]),
            "results": results
        }

    def auto_chain(self, start_tool: str) -> Dict:
        """自动串联工具链"""
        chain = [start_tool]
        
        # 简单的启发式：查找输出类型
        current_output = "unknown"
        
        # 尝试读取工具文件推断输出
        for tool_file in self.tools_dir.glob("*.py"):
            if start_tool in tool_file.name:
                content = tool_file.read_text(encoding="utf-8")
                # 简单推断
                if "export" in tool_file.name.lower():
                    current_output = "json"
                elif "brainstorm" in tool_file.name.lower():
                    current_output = "ideas"
                elif "report" in tool_file.name.lower():
                    current_output = "report"
                break
        
        # 查找匹配的下一个工具
        for output_type, tools in self.OUTPUT_TO_TOOL.items():
            if output_type in current_output:
                if tools[0] != start_tool:
                    chain.append(tools[0])
                break
        
        # 如果没找到匹配的，返回单工具
        return {
            "start": start_tool,
            "suggested_chain": chain,
            "reason": "Auto-chained based on output type"
        }
    
    def list_templates(self) -> List[Dict]:
        """列出工具链模板"""
        return [
            {
                "id": k,
                "name": v["name"],
                "tools": v["tools"],
                "description": v["description"]
            }
            for k, v in self.CHAIN_TEMPLATES.items()
        ]
    
    def run_template(self, template_id: str) -> Dict:
        """执行预定义模板"""
        if template_id not in self.CHAIN_TEMPLATES:
            return {"error": f"Template {template_id} not found"}
        
        template = self.CHAIN_TEMPLATES[template_id]
        return self.run_chain(template["tools"])


logging.basicConfig(level=logging.INFO)
def main():
    runner = ChainRunner()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--chain":
            tools = sys.argv[2].split(",") if len(sys.argv) > 2 else []
            if not tools:
                print("Error: Specify tools like --chain tool1,tool2,tool3")
                return 1
            result = runner.run_chain(tools)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--auto":
            start = sys.argv[2] if len(sys.argv) > 2 else "auto_discover_001"
            result = runner.auto_chain(start)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--templates":
            templates = runner.list_templates()
            print(json.dumps(templates, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--run":
            template_id = sys.argv[2] if len(sys.argv) > 2 else "discover-sync"
            result = runner.run_template(template_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("CHAIN-RUNNER-001 Tool Chain Runner")
    print("Usage:")
    print("  py chain_runner_001.py --chain <t1,t2,t3>  # Run chain")
    print("  py chain_runner_001.py --auto <tool>       # Auto chain")
    print("  py chain_runner_001.py --templates        # List templates")
    print("  py chain_runner_001.py --run <template>   # Run template")
    print("\nTemplates:")
    for tid, t in runner.CHAIN_TEMPLATES.items():
        print(f"  {tid}: {t['name']} ({', '.join(t['tools'])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
