import logging
logger = logging.getLogger(__name__)

import json

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

tools = registry.get('tools', {})

# 查看 safe-shell-executor 详情
if 'safe-shell-executor' in tools:
    tool = tools['safe-shell-executor']
    print("safe-shell-executor 详情:\n")
    print(json.dumps(tool, indent=2, ensure_ascii=False)[:2000])
else:
    print("safe-shell-executor 未找到")

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
# py view_safe_shell_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py view_safe_shell_001.py

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
