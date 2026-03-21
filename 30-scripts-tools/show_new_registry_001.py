import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

print(f"Registry 版本：{registry.get('version', 'N/A')}")
print(f"工具总数：{len(registry.get('tools', {}))}\n")

print("可用工具列表 (前 30 个):")
for i, (tool_id, info) in enumerate(list(registry["tools"].items())[:30], 1):
    cmd = info.get("command", "N/A")
    print(f"  {i}. {tool_id}")
    print(f"     {cmd}")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py show_new_registry_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py show_new_registry_001.py

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
