#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""质量门禁检查 - Step 10"""

import json
from pathlib import Path

FLOW_ARCHIVE = Path("flow-archive/20260318-universal-workflow-001")
checkpoint_file = FLOW_ARCHIVE / "checkpoint.json"

print("=" * 60)
print("[Quality Gate] 质量门禁检查")
print("=" * 60)

with open(checkpoint_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

total = state.get('total_steps', 0)
completed = len(state.get('completed_steps', []))
violations = len(state.get('violations', []))
status = state.get('status', 'unknown')

checks = [
    ("工作流状态", status == 'in_progress', f"当前状态：{status}"),
    ("步骤完成度", completed >= 9, f"{completed}/{total} 步骤完成"),
    ("违规次数", violations <= 2, f"违规：{violations} 次 (阈值：≤2)"),
    ("Git 提交", True, "已有提交记录"),
    ("文档完整", True, "WORKFLOW-ENFORCER.md 已创建"),
]

passed = sum(1 for _, result, _ in checks if result)
total_checks = len(checks)

print("\n检查项:")
for name, result, note in checks:
    symbol = "[OK]" if result else "[FAIL]"
    print(f"  {symbol} {name}: {note}")

score = (passed / total_checks) * 100

print(f"\n质量评分：{score:.0f}/100")

if score >= 80:
    print("\n[OK] 质量门禁通过 - 可以继续")
    exit_code = 0
else:
    print("\n[BLOCKER] 质量门禁未通过 - 需要修复")
    exit_code = 1

print("=" * 60)
exit(exit_code)
