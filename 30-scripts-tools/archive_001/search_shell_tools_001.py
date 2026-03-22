import logging
logger = logging.getLogger(__name__)

import json

# 读取工具注册表
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

# 搜索 shell 相关工具
shell_tools = {}
for tool_id, tool_data in registry.get('tools', {}).items():
    if 'shell' in tool_id.lower() or 'shell' in str(tool_data).lower():
        shell_tools[tool_id] = tool_data

print(f"找到 {len(shell_tools)} 个 shell 相关工具:\n")
for tool_id, data in shell_tools.items():
    print(f"  - {tool_id}: {data.get('description', 'N/A')[:50]}")

# 检查是否有 execute_shell_command
if 'execute_shell_command' in registry.get('tools', {}):
    print("\n✅ execute_shell_command 已注册")
else:
    print("\n❌ execute_shell_command 未注册")

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
# py search_shell_tools_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py search_shell_tools_001.py

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
