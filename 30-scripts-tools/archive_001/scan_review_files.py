#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描待审查文件"""

from pathlib import Path

review = [
    'reg_agent_monitor_001.py', 'reg_antibypass_001.py', 'reg_auto_backup_001.py',
    'reg_auto_critic_v_001.py', 'reg_auto_protection_001.py', 'reg_confirmation_gate_001.py',
    'reg_context_verify_001.py', 'reg_dashboard_fix_001.py', 'reg_diagnose_001.py',
    'reg_fix_state_v_001.py', 'reg_forced_protection_001.py', 'reg_mark_all_001.py',
    'reg_phase_001.py', 'reg_protection_phase_001.py', 'reg_reward_stop_001.py',
    'reg_risk_assessor_001.py', 'reg_rules_verifier_001.py', 'reg_safe_shell_001.py',
    'reg_task_001.py', 'reg_tool_executor_001.py', 'reg_tool_selector_001.py',
    'reg_update_step_001.py', 'reg_v_001.py', 'reg_workflow_scheduler_001.py',
    'smart_compress_001.py', 'smart_compress_002.py',
    'sa_backtest_001.py', 'sa_backtest_optimizer_001.py', 'sa_backtesting_001.py',
    'workflow_optimizer.py', 'workflow_optimizer_001.py',
]

print('SCANNING 31 FILES...')
print('='*70)

safe_delete = []
needs_review = []

for f in review:
    p = Path(f)
    if not p.exists():
        print(f'{f:40} | [NOT FOUND]')
        continue

    try:
        content = p.read_text(encoding='utf-8', errors='ignore')[:300]
        # 提取函数名
        lines = content.split('\n')
        funcs = [line.strip().replace('def ', '') for line in lines
                 if line.strip().startswith('def ') and not line.strip().startswith('def _')]
        func_str = ', '.join([f.split('(')[0] for f in funcs[:3]]) if funcs else 'N/A'

        # 简单判断
        if 'reg_' in f and '_v_' in f:
            safe_delete.append(f)
            status = '[SAFE DELETE - v_ variant]'
        elif 'smart_compress_002' in f:
            safe_delete.append(f)
            status = '[SAFE DELETE - dup version]'
        elif 'sa_backtest_optimizer' in f or 'sa_backtesting' in f:
            safe_delete.append(f)
            status = '[SAFE DELETE - dup variant]'
        elif 'workflow_optimizer.py' in f and 'workflow_optimizer_001' in f:
            safe_delete.append(f)
            status = '[SAFE DELETE - no suffix]'
        else:
            needs_review.append(f)
            status = '[NEEDS REVIEW]'

        print(f'{f:40} | {func_str[:35]:35} | {status}')
    except Exception as e:
        print(f'{f:40} | ERROR: {e}')

print('\n' + '='*70)
print(f'SAFE TO DELETE: {len(safe_delete)}')
print(f'NEEDS REVIEW: {len(needs_review)}')
print('='*70)

if safe_delete:
    print('\nSAFE DELETE LIST:')
    for f in safe_delete:
        print(f'  {f}')
