#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

# 读取工作流
with open('30-scripts-tools/workflows/session-end.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 插入 P1 修复步骤（在 Issue Scanner 之前）
p1_step = {
    "step_id": 15,
    "name": "P1 Issue Auto-Fix",
    "description": "自动修复 P1 优先级问题（os.system/eval/exec 替换）",
    "tool_id": "p1-issue-fixer",
    "stage": "pre-commit",
    "parameters": {
        "action": "fix"
    },
    "blocking": False,
    "timeout_seconds": 60,
    "note": "P1 优先级修复：自动替换危险调用为安全替代方案"
}

# 在 Step 14 后插入
workflow['steps'].insert(14, p1_step)

# 重新编号所有步骤
for i, step in enumerate(workflow['steps'], 1):
    step['step_id'] = i

# 更新 Issue Scanner 的 step_id
workflow['steps'][15]['step_id'] = 16

# 更新工作流版本
workflow['version'] = '3.1'
workflow['last_updated'] = '2026-03-18'
workflow['description'] = '会话结束工作流 - 16 步自动化流程（含 P1 修复）'

# 保存
with open('30-scripts-tools/workflows/session-end.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print("OK: Workflow updated to v3.1")
print(f"Total steps: {len(workflow['steps'])}")
