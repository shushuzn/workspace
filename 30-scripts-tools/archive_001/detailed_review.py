#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""详细审查23个待定文件"""

from pathlib import Path
import re

files = [
    'reg_agent_monitor_001.py', 'reg_antibypass_001.py', 'reg_auto_backup_001.py',
    'reg_auto_protection_001.py', 'reg_confirmation_gate_001.py', 'reg_context_verify_001.py',
    'reg_dashboard_fix_001.py', 'reg_diagnose_001.py', 'reg_forced_protection_001.py',
    'reg_mark_all_001.py', 'reg_phase_001.py', 'reg_protection_phase_001.py',
    'reg_reward_stop_001.py', 'reg_risk_assessor_001.py', 'reg_rules_verifier_001.py',
    'reg_safe_shell_001.py', 'reg_task_001.py', 'reg_tool_executor_001.py',
    'reg_tool_selector_001.py', 'reg_update_step_001.py', 'reg_workflow_scheduler_001.py',
    'smart_compress_001.py', 'sa_backtest_001.py',
]

# 读取并分析每个文件
print("=" * 80)
print("DETAILED REVIEW OF 23 FILES")
print("=" * 80)

keep = []
delete = []
unclear = []

for f in files:
    p = Path(f)
    if not p.exists():
        print(f"[DELETED] {f}")
        continue

    content = p.read_text(encoding='utf-8', errors='ignore')

    # 提取描述
    desc = ""
    doc_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
    if doc_match:
        desc = doc_match.group(1).strip().split('\n')[0][:60]

    # 提取主要函数
    funcs = re.findall(r'def (\w+)\(', content)

    # 检查是否有实际逻辑
    lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
    logic_lines = len(lines)

    # 判断
    if 'register_tools' in content and len(funcs) <= 3 and logic_lines < 50:
        # 简单的注册器文件
        delete.append((f, desc, funcs))
        status = "[DELETE]"
    elif 'main' in content or 'if __name__' in content:
        # 有主逻辑
        keep.append((f, desc, funcs))
        status = "[KEEP]"
    else:
        unclear.append((f, desc, funcs))
        status = "[UNSURE]"

    print(f"\n{status} {f}")
    print(f"  Desc: {desc}")
    print(f"  Funcs: {funcs}")
    print(f"  Lines: {logic_lines}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"KEEP:    {len(keep)}")
print(f"DELETE:  {len(delete)}")
print(f"UNSURE:  {len(unclear)}")

print("\n[DELETE LIST]:")
for f, d, fn in delete:
    print(f"  {f}")

print("\n[KEEP LIST]:")
for f, d, fn in keep:
    print(f"  {f}")

print("\n[UNSURE - NEED MANUAL CHECK]:")
for f, d, fn in unclear:
    print(f"  {f}")
