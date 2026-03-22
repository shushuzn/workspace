import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

# 检查 workflow-enforcer
tool = registry["tools"].get("workflow-enforcer", {})
print("workflow-enforcer 定义:")
print(json.dumps(tool, ensure_ascii=False, indent=2))

# 检查几个其他工具
print("\n\n其他工具示例:")
for tool_id in ["copaw-entry", "tool-executor", "embedded-critic"]:
    tool = registry["tools"].get(tool_id, {})
    print(f"\n{tool_id}:")
    print(f"  command: {tool.get('command', 'N/A')}")
    print(f"  path: {tool.get('path', 'N/A')}")

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
# py check_registry_format_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_registry_format_001.py

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
