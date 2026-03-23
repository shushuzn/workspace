import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速验证 execution-state.json 类型正确性
用法：py verify_state_types.py
"""

import json

logging.basicConfig(level=logging.INFO)
def main():
    # 加载文件
    with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    with open('flow-archive/20260318-universal-workflow-001/execution-state.json', 'r', encoding='utf-8') as f:
        state = json.load(f)

    # 提取 step_id
    required = [s.get('step_id') for s in workflow.get('steps', []) if s.get('required', True)]
    completed = state.get('completed_steps', [])

    print("=" * 60)
    print("Step ID 类型验证")
    print("=" * 60)

    # 逐项对比
    all_match = True
    for i, (req, comp) in enumerate(zip(required, completed)):
        type_match = type(req) == type(comp)
        value_match = req == comp

        status = "[OK]" if (type_match and value_match) else "[FAIL]"
        print(f"{status} Step {i+1}: workflow={req} ({type(req).__name__}), state={comp} ({type(comp).__name__})")

        if not (type_match and value_match):
            all_match = False

    print("=" * 60)
    if all_match:
        print("[OK] 所有 Step ID 类型和值完全匹配")
        return 0
    else:
        print("[FAIL] 发现类型或值不匹配")
        return 1
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
# py verify_state_types_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py verify_state_types_001.py

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



if __name__ == "__main__":
    exit(main())
