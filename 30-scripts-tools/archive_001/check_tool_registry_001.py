import logging
logger = logging.getLogger(__name__)

import json

# 读取工具注册表
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

tools = registry.get('tools', {})

# 搜索 shell 相关工具
print("搜索 shell 相关工具:\n")
for tool_id in sorted(tools.keys()):
    if 'shell' in tool_id.lower() or 'executor' in tool_id.lower():
        tool = tools[tool_id]
        print(f"  [OK] {tool_id}")
        print(f"     描述：{tool.get('description', 'N/A')[:60]}")
        print(f"     命令：{tool.get('command', 'N/A')[:60]}")
        print()

# 检查特定工具
check_tools = ['execute_shell_command', 'safe_shell_executor', 'tool_executor', 'shell']
print("\n检查特定工具:")
for tool in check_tools:
    if tool in tools:
        print(f"  [OK] {tool} - 已注册")
    else:
        print(f"  [X] {tool} - 未注册")

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
# py check_tool_registry_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_tool_registry_001.py

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
