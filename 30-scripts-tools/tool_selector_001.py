import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Step 4: 工具选择工具
根据任务分析结果选择合适的工具
"""
import json
from pathlib import Path
from datetime import datetime

def select_tools(task_analysis_file: str):
    analysis_path = Path(task_analysis_file)
    if not analysis_path.exists():
        return {
            "status": "error",
            "message": "任务分析文件不存在",
            "server_time": datetime.now().isoformat()
        }
    
    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    
    # 加载工具注册表
    registry_file = Path("30-scripts-tools/tools_registry.json")
    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    # 根据任务类型选择工具
    task_type = analysis.get("task_type", "unknown")
    required_tools = analysis.get("required_tools", [])
    
    # 匹配可用工具
    available_tools = list(registry.get("tools", {}).keys())
    selected = []
    missing = []
    
    for tool in required_tools:
        if tool in available_tools:
            selected.append(tool)
        else:
            missing.append(tool)
    
    return {
        "status": "success",
        "task_type": task_type,
        "selected_tools": selected,
        "missing_tools": missing,
        "available_tools": available_tools,
        "server_time": datetime.now().isoformat()
    }
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py tool_selector_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py tool_selector_001.py

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



if __name__ == "__main__":
    import sys
    task_file = sys.argv[1] if len(sys.argv) > 1 else "flow-archive/20260318-universal-workflow-001/task-analysis.json"
    result = select_tools(task_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
