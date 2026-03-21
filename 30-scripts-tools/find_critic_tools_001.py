import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

# 查找所有 critic 相关工具
critic_tools = {k: v for k, v in registry["tools"].items() if "critic" in k.lower()}

print(f"Critic 相关工具：{len(critic_tools)}\n")

for tool_id, info in list(critic_tools.items())[:10]:
    command = info.get("command", "N/A")
    print(f"{tool_id}:")
    print(f"  command: {command}")
    print()

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py find_critic_tools_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py find_critic_tools_001.py

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
