#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 4 - 删除19个reg_注册脚本"""

import shutil
from pathlib import Path

archive = Path('cleanup_archive/20260322')

reg_files = [
    'reg_agent_monitor_001.py', 'reg_antibypass_001.py', 'reg_auto_backup_001.py',
    'reg_auto_protection_001.py', 'reg_confirmation_gate_001.py', 'reg_context_verify_001.py',
    'reg_dashboard_fix_001.py', 'reg_diagnose_001.py', 'reg_forced_protection_001.py',
    'reg_mark_all_001.py', 'reg_phase_001.py', 'reg_protection_phase_001.py',
    'reg_reward_stop_001.py', 'reg_risk_assessor_001.py', 'reg_rules_verifier_001.py',
    'reg_safe_shell_001.py', 'reg_task_001.py', 'reg_tool_executor_001.py',
    'reg_tool_selector_001.py', 'reg_update_step_001.py', 'reg_workflow_scheduler_001.py',
]

count = 0
for f in reg_files:
    p = Path(f)
    if p.exists():
        shutil.move(str(p), str(archive / f))
        print(f'[DELETED] {f}')
        count += 1

print(f'\nTotal deleted: {count}')

# 统计剩余
total = len(list(Path('.').glob('*.py')))
print(f'Total remaining: {total}')

# 保留的文件
print('\n[KEPT]:')
print('  smart_compress_001.py')
print('  sa_backtest_001.py')
