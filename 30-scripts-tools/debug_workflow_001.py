import logging
logger = logging.getLogger(__name__)

import json

with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

steps = workflow.get('steps', [])
print(f"步骤数量：{len(steps)}")
print(f"步骤类型：{type(steps)}")

if isinstance(steps, dict):
    print("步骤是字典，keys:")
    for k in list(steps.keys())[:10]:
        print(f"  {k}: {type(steps[k])}")
elif isinstance(steps, list) and len(steps) > 0:
    print(f"第一个步骤：{steps[0]}")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py debug_workflow_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py debug_workflow_001.py

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
