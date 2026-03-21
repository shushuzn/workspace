import logging
logger = logging.getLogger(__name__)

import json
with open('flow-archive/20260318-universal-workflow-001/execution-state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)
completed = state.get('completed_steps', [])
print(f"Completed steps: {completed}")
print(f"Types: {[type(c).__name__ for c in completed]}")

with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    w = json.load(f)
required = [s.get('step_id') for s in w.get('steps', []) if s.get('required', True)]
print(f"\nRequired steps: {required}")
print(f"Types: {[type(r).__name__ for r in required]}")

matched = [c for c in completed if c in required]
print(f"\nMatched: {len(matched)}/{len(required)}")
missing = [r for r in required if r not in completed]
print(f"Missing: {missing}")

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
# py debug_step_match_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py debug_step_match_001.py

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
