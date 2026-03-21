import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path

state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

print("当前 execution-state.json 状态:")
print(f"  Session: {state.get('session_id')}")
print(f"  当前步骤：{state.get('current_step')}")
print(f"  完成率：{state.get('completion_percentage')}%")
print(f"  已完成步骤数：{len(state.get('completed_steps', []))}")
print(f"\n最近 5 个 step_status:")

step_status = state.get('step_status', {})
for i, (step_id, step_data) in enumerate(list(step_status.items())[-5:]):
    print(f"  Step {step_id}: {step_data.get('name', 'N/A')} - {step_data.get('status', 'N/A')}")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py check_current_state_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_current_state_001.py

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
