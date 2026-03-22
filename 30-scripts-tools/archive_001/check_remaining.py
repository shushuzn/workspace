#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查剩余待审查文件"""

from pathlib import Path

review_list = [
    'reg_agent_monitor_001.py', 'reg_antibypass_001.py', 'reg_auto_backup_001.py',
    'reg_auto_protection_001.py', 'reg_confirmation_gate_001.py', 'reg_context_verify_001.py',
    'reg_dashboard_fix_001.py', 'reg_diagnose_001.py', 'reg_forced_protection_001.py',
    'reg_mark_all_001.py', 'reg_phase_001.py', 'reg_protection_phase_001.py',
    'reg_reward_stop_001.py', 'reg_risk_assessor_001.py', 'reg_rules_verifier_001.py',
    'reg_safe_shell_001.py', 'reg_task_001.py', 'reg_tool_executor_001.py',
    'reg_tool_selector_001.py', 'reg_update_step_001.py', 'reg_workflow_scheduler_001.py',
    'smart_compress_001.py',
    'sa_backtest_001.py',
]

print('REMAINING REVIEW LIST:')
print('='*60)
count = 0
for f in review_list:
    p = Path(f)
    if p.exists():
        size = p.stat().st_size
        print(f'  {f:40} {size:>6} bytes')
        count += 1
    else:
        print(f'  {f:40} [DELETED]')

print(f'\nTotal remaining: {count}')

# 统计
total = len(list(Path('.').glob('*.py')))
print(f'Total tools in directory: {total}')
