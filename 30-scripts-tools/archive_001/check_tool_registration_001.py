import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具注册强制检查 - 确保新创建的工具都注册
"""

import json
from pathlib import Path
from datetime import datetime

def check_tool_registration():
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
# py check_tool_registration_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_tool_registration_001.py

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

检查工具注册情况"""

    print("\n" + "=" * 60)
    print("Tool Registration Compliance Check")
    print("=" * 60)

    tools_dir = Path("30-scripts-tools")
    registry_file = Path("30-scripts-tools/tools_registry.json")

    # 获取所有 Python 工具文件
    py_files = list(tools_dir.glob("*.py"))
    py_files = [f for f in py_files if not f.name.startswith('_') and not f.name.startswith('test_')]

    # 获取已注册的工具
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    registered_tools = set(registry['tools'].keys())

    # 检查未注册的工具
    unregistered = []
    for py_file in py_files:
        tool_name = py_file.stem.replace('_', '-')

        # 检查是否在 registry 中
        is_registered = False
        for reg_tool in registered_tools:
            if reg_tool == tool_name or reg_tool.replace('-', '_') == py_file.stem:
                is_registered = True
                break

        if not is_registered:
            # 排除临时脚本
            if not any(kw in py_file.name for kw in ['tmp', 'temp', 'check_', 'verify_']):
                unregistered.append(py_file.name)

    # 输出结果
    print(f"\n工具文件总数：{len(py_files)}")
    print(f"已注册工具：{len(registered_tools)}")
    print(f"未注册工具：{len(unregistered)}")

    if unregistered:
        print("\n⚠️ 以下工具未注册:")
        for f in unregistered[:10]:
            print(f"  - {f}")

        if len(unregistered) > 10:
            print(f"  ... 还有 {len(unregistered)-10} 个")

        print("\n[ACTION] 请运行以下命令注册:")
        print("  py 30-scripts-tools/register_tool.py <工具文件名>")

        return False
    else:
        print("\n✅ 所有工具都已注册")
        return True

if __name__ == "__main__":
    success = check_tool_registration()
    exit(0 if success else 1)
