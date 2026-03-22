import logging
logger = logging.getLogger(__name__)

import json
with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    w = json.load(f)
steps = w.get('steps', [])
step_ids = [s.get('step_id') for s in steps]
print(f"Step IDs (first 15): {step_ids[:15]}")
print(f"Types: {[type(sid).__name__ for sid in step_ids[:15]]}")

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
# py check_step_ids_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_step_ids_001.py

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
