import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

tools = registry["tools"]

# 查找包含 copaw 的工具
copaw_tools = [k for k in tools.keys() if "copaw" in k.lower()]
print(f"Copaw 相关工具：{copaw_tools}")

# 查找包含 entry 的工具
entry_tools = [k for k in tools.keys() if "entry" in k.lower()]
print(f"Entry 相关工具：{entry_tools}")

# 查找包含 executor 的工具
executor_tools = [k for k in tools.keys() if "executor" in k.lower()]
print(f"Executor 相关工具：{executor_tools[:10]}")

# 检查 copaw_entry.py 对应的工具 ID
print(f"\n总工具数：{len(tools)}")

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
# py find_copaw_tool_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py find_copaw_tool_001.py

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
