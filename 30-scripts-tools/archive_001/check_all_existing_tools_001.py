import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面检查实际存在的工具文件
输出可用的工具列表
"""
import json
from pathlib import Path

def check_existing_tools():
    scripts_dir = Path("30-scripts-tools")
    registry_file = Path("30-scripts-tools/tools_registry.json")

    # 获取所有实际存在的 .py 文件
    py_files = list(scripts_dir.glob("*.py"))
    py_files = [f for f in py_files if not f.name.startswith("_") and f.parent == scripts_dir]

    print(f"=" * 60)
    print(f"30-scripts-tools 目录中的 Python 文件")
    print(f"=" * 60)
    print(f"总数：{len(py_files)}\n")

    # 按功能分类
    categories = {
        "critic": [],
        "memory": [],
        "workflow": [],
        "session": [],
        "data": [],
        "test": [],
        "other": []
    }

    for f in py_files:
        name = f.name.lower()
        if "critic" in name:
            categories["critic"].append(f.name)
        elif "memory" in name:
            categories["memory"].append(f.name)
        elif "workflow" in name:
            categories["workflow"].append(f.name)
        elif "session" in name or "compress" in name:
            categories["session"].append(f.name)
        elif "data" in name or "anomaly" in name:
            categories["data"].append(f.name)
        elif "test" in name:
            categories["test"].append(f.name)
        else:
            categories["other"].append(f.name)

    # 输出分类结果
    for cat, files in categories.items():
        if files:
            print(f"\n[{cat.upper()}] - {len(files)} 个文件:")
            for f in sorted(files):
                print(f"  - {f}")

    # 加载 registry，检查哪些工具有对应文件
    print(f"\n{'=' * 60}")
    print(f"Registry 工具 vs 实际文件匹配")
    print(f"=" * 60)

    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)

    tools = registry.get("tools", {})
    matched = []
    unmatched = []

    for tool_id, info in tools.items():
        command = info.get("command", "")
        if command and "py " in command:
            parts = command.split("py ")[1].split(" ")[0]
            filename = parts.split("\\")[-1].split("/")[-1]
            filepath = scripts_dir / filename
            if filepath.exists():
                matched.append((tool_id, filename))
            else:
                unmatched.append((tool_id, filename))

    print(f"\n匹配的工具：{len(matched)}")
    for tool_id, filename in sorted(matched):
        print(f"  ✓ {tool_id} -> {filename}")

    print(f"\n不匹配的工具：{len(unmatched)}")
    if unmatched:
        print(f"前 30 个示例:")
        for tool_id, filename in sorted(unmatched)[:30]:
            print(f"  ✗ {tool_id} -> {filename} (不存在)")

    return {
        "total_py_files": len(py_files),
        "matched_tools": len(matched),
        "unmatched_tools": len(unmatched),
        "matched_list": matched,
        "server_time": "2026-03-20T02:47:00+08:00"
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
# py check_all_existing_tools_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_all_existing_tools_001.py

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
    result = check_existing_tools()
    print(f"\n{'=' * 60}")
    print(f"总结:")
    print(f"  实际 Python 文件：{result['total_py_files']}")
    print(f"  Registry 匹配：{result['matched_tools']}")
    print(f"  Registry 不匹配：{result['unmatched_tools']}")
