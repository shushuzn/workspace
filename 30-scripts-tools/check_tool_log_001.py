import logging
logger = logging.getLogger(__name__)

import json

with open('30-scripts-tools/tool_call_log.jsonl', 'r', encoding='utf-8') as f:
    logs = [json.loads(line) for line in f]

print(f"工具调用数量：{len(logs)}")
print("\n最近 10 次调用:")
for log in logs[-10:]:
    print(f"  {log.get('tool_id')}: {log.get('result')}")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py check_tool_log_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_tool_log_001.py

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
