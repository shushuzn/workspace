#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试工具包装器 v2 - 自动步骤跟踪
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, '30-scripts-tools')

print("=" * 70)
print("测试工具包装器 v2 - 自动步骤跟踪")
print("=" * 70)

# 读取执行前的 state
state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
with open(state_file, 'r', encoding='utf-8') as f:
    state_before = json.load(f)

print(f"\n[执行前]")
print(f"  当前步骤：{state_before.get('current_step')}")
print(f"  完成率：{state_before.get('completion_percentage')}%")
print(f"  已完成步骤数：{len(state_before.get('completed_steps', []))}")

# 模拟工具调用
from tool_wrapper import before_tool_call, after_tool_call

print(f"\n[模拟工具调用]")
if before_tool_call('safe_shell_executor', {'command': 'echo test'}):
    print(f"  before_tool_call: 允许")
    after_tool_call('safe_shell_executor', {'command': 'echo test'}, 'success')
    print(f"  after_tool_call: 已记录 + 步骤已更新")
else:
    print(f"  before_tool_call: 拒绝")

# 读取执行后的 state
with open(state_file, 'r', encoding='utf-8') as f:
    state_after = json.load(f)

print(f"\n[执行后]")
print(f"  当前步骤：{state_after.get('current_step')}")
print(f"  完成率：{state_after.get('completion_percentage')}%")
print(f"  已完成步骤数：{len(state_after.get('completed_steps', []))}")

# 对比
print(f"\n[对比]")
print(f"  步骤变化：{state_before.get('current_step')} -> {state_after.get('current_step')}")
print(f"  完成率变化：{state_before.get('completion_percentage')}% -> {state_after.get('completion_percentage')}%")
print(f"  新增步骤：{set(state_after.get('completed_steps', [])) - set(state_before.get('completed_steps', []))}")

if state_after.get('completion_percentage', 0) > state_before.get('completion_percentage', 0):
    print(f"\n[PASS] 自动步骤跟踪生效 ✓")
else:
    print(f"\n[FAIL] 自动步骤跟踪未生效")

print("=" * 70)
