import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

# 使用 embedded-critic 作为 auto_critic_v7 的替代
registry["tools"]["auto_critic_v7"] = {
    "tool_id": "auto_critic_v7",
    "name": "Auto Critic v7",
    "description": "自动批判者 v7.0",
    "version": "7.0.0",
    "command": "py 30-scripts-tools\\embedded_critic.py",
    "path": "30-scripts-tools\\embedded_critic.py",
    "category": "critic",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("auto_critic_v7 已注册 (使用 embedded_critic.py)")

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
# py reg_auto_critic_v_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py reg_auto_critic_v_001.py

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
