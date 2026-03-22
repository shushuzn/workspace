#!/usr/bin/env python3
# -*- coding: utf-8 -*-
REQUIRES_MANUAL_REVIEW = [
    'reg_agent_monitor_001.py',
    'reg_antibypass_001.py',
    'reg_auto_backup_001.py',
    'reg_auto_critic_v_001.py',
    'reg_auto_protection_001.py',
    'reg_confirmation_gate_001.py',
    'reg_context_verify_001.py',
    'reg_dashboard_fix_001.py',
    'reg_diagnose_001.py',
    'reg_fix_state_v_001.py',
    'reg_forced_protection_001.py',
    'reg_mark_all_001.py',
    'reg_phase_001.py',
    'reg_protection_phase_001.py',
    'reg_reward_stop_001.py',
    'reg_risk_assessor_001.py',
    'reg_rules_verifier_001.py',
    'reg_safe_shell_001.py',
    'reg_task_001.py',
    'reg_tool_executor_001.py',
    'reg_tool_selector_001.py',
    'reg_update_step_001.py',
    'reg_v_001.py',
    'reg_workflow_scheduler_001.py',
    'smart_compress_001.py',
    'smart_compress_002.py',
    'sa_backtest_001.py',
    'sa_backtest_optimizer_001.py',
    'sa_backtesting_001.py',
    'workflow_optimizer.py',
    'workflow_optimizer_001.py',
]

if __name__ == "__main__":
    from pathlib import Path
    tools_dir = Path("D:/OpenClaw/workspace/30-scripts-tools")
    print("REQUIRES MANUAL REVIEW (31 tools):")
    print("=" * 60)
    for i, t in enumerate(REQUIRES_MANUAL_REVIEW, 1):
        path = tools_dir / t
        if path.exists():
            size = path.stat().st_size
            print(f"{i:2}. {t:40} {size:>8} bytes")
        else:
            print(f"{i:2}. {t:40} [NOT FOUND]")
