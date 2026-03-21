import logging
logger = logging.getLogger(__name__)

import json

# 读取 workflow.json
with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 读取 execution-state.json
with open('flow-archive/20260318-universal-workflow-001/execution-state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

# 获取 workflow 中的 step_id 列表（数字类型）
workflow_step_ids = [s['step_id'] for s in workflow['steps']]
print(f"Workflow step IDs (numeric): {workflow_step_ids[:10]}...")

# 获取 state 中的 step_status 键（字符串类型）
state_step_keys = list(state['step_status'].keys())
print(f"State step keys (string): {state_step_keys[:10]}...")

# 修复：将 step_status 的键从字符串转换为数字格式
new_step_status = {}
for key, value in state['step_status'].items():
    # 尝试转换为数字
    try:
        if '.' in key:
            new_key = float(key)
        else:
            new_key = int(key)
    except ValueError:
        new_key = key
    new_step_status[new_key] = value

# 修复 completed_steps 列表
new_completed_steps = []
for key in state['completed_steps']:
    try:
        if '.' in key:
            new_key = float(key)
        else:
            new_key = int(key)
    except ValueError:
        new_key = key
    new_completed_steps.append(new_key)

# 更新 state
state['step_status'] = new_step_status
state['completed_steps'] = new_completed_steps

# 保存修复后的文件
with open('flow-archive/20260318-universal-workflow-001/execution-state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print(f"\n修复完成:")
print(f"  step_status 键数：{len(state['step_status'])}")
print(f"  completed_steps 数：{len(state['completed_steps'])}")
print(f"  新 step_status 键：{list(state['step_status'].keys())[:10]}...")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py fix_step_id_type_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py fix_step_id_type_001.py

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
