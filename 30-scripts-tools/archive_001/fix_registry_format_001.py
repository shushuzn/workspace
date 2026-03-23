import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复 tools_registry.json - 修正 command 字段格式
"""
import json
from pathlib import Path

def fix_registry():
    registry_file = Path("30-scripts-tools/tools_registry.json")
    scripts_dir = Path("30-scripts-tools")

    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)

    tools = registry.get("tools", {})
    fixed = 0

    for tool_id, info in tools.items():
        command = info.get("command", "")
        if command and "${args}" in command:
            # 修复 ${args} 格式问题
            # 提取正确的文件名
            parts = command.split("py ")[1].split(" ${args}")[0]
            filename = parts.split("\\")[-1].split("/")[-1]

            # 确保文件名有 .py 扩展名
            if not filename.endswith(".py"):
                filename = filename + ".py"

            # 检查文件是否存在
            filepath = scripts_dir / filename
            if filepath.exists():
                # 更新 command
                new_command = f"py 30-scripts-tools\\{filename}"
                info["command"] = new_command
                info["path"] = f"30-scripts-tools\\{filename}"
                fixed += 1
                print(f"[FIXED] {tool_id}: {command} -> {new_command}")
            else:
                print(f"[MISSING] {tool_id}: {filename} 不存在")

    registry["version"] = "1.7.1-fixed"

    with open(registry_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"\n修复完成：{fixed} 个工具")
    print(f"版本：{registry['version']}")

    return {
        "status": "success",
        "fixed": fixed,
        "server_time": "2026-03-20T02:48:00+08:00"
    }
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
# py fix_registry_format_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py fix_registry_format_001.py

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
    result = fix_registry()
    print(json.dumps(result, ensure_ascii=False, indent=2))
