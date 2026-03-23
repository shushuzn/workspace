#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Cleanup Script - 识别和归档重复工具
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# 高优先级清理 (明确重复)
PRIORITY_1_DELETE = [
    # Stock PRO 重复版本 - 保留 stock_pro_v4.py (完整版)
    "stock_pro_001.py",
    "stock_pro_003.py",
    "stock_pro_v4_legacy.py",  # 旧版单文件

    # Tool call interceptor 重复
    "tool_call_interceptor_001.py",  # 被 tool_call_interceptor.py 替代
    "tool_call_interceptor_v_001.py",  # 另一个版本

    # Test wrapper 重复
    "test_wrapper_001.py",
    "test_wrapper_no_session_001.py",
    "test_wrapper_strict_001.py",

    # Execution state fix 重复
    "fix_execution_state_001.py",
    "fix_execution_state_v_001.py",
    "fix_state_signature_001.py",
    "fix_state_with_substeps_001.py",
    "update_execution_state_001.py",
    "update_state_for_mandatory_001.py",

    # Registry fix 重复
    "fix_registry_format_001.py",
    "fix_registry_paths_001.py",
    "rebuild_registry_001.py",
    "sync_registry_001.py",
    "sync_registry_smart_001.py",

    # Workflow enforcer 重复
    "workflow_enforcer_v_001.py",  # 被 workflow_enforcer_001.py 替代

    # Penalty system 重复
    "penalty_system_v_001.py",  # 被 penalty_system_001.py 替代
]

# 中优先级 - 需要检查功能差异
PRIORITY_2_REVIEW = [
    # 多个 reg_xxx 工具 - 需要检查功能
    "reg_agent_monitor_001.py",
    "reg_antibypass_001.py",
    "reg_auto_backup_001.py",
    "reg_auto_critic_v_001.py",
    "reg_auto_protection_001.py",
    "reg_confirmation_gate_001.py",
    "reg_context_verify_001.py",
    "reg_dashboard_fix_001.py",
    "reg_diagnose_001.py",
    "reg_fix_state_v_001.py",
    "reg_forced_protection_001.py",
    "reg_mark_all_001.py",
    "reg_phase_001.py",
    "reg_protection_phase_001.py",
    "reg_reward_stop_001.py",
    "reg_risk_assessor_001.py",
    "reg_rules_verifier_001.py",
    "reg_safe_shell_001.py",
    "reg_task_001.py",
    "reg_tool_executor_001.py",
    "reg_tool_selector_001.py",
    "reg_update_step_001.py",
    "reg_v_001.py",
    "reg_workflow_scheduler_001.py",

    # Smart compress 重复
    "smart_compress_001.py",
    "smart_compress_002.py",

    # SA backtest 重复
    "sa_backtest_001.py",
    "sa_backtest_optimizer_001.py",
    "sa_backtesting_001.py",

    # Workflow 多个版本
    "workflow_optimizer.py",
    "workflow_optimizer_001.py",
    "workflow_enforcer_001.py",
    "workflow_enforcer_v_001.py",
]

def cleanup_tools(delete_list, review_list, dry_run=True):
    tools_dir = Path("D:/OpenClaw/workspace/30-scripts-tools")
    archive_dir = tools_dir / "cleanup_archive" / datetime.now().strftime("%Y%m%d")

    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)

    deleted = []
    for tool in delete_list:
        path = tools_dir / tool
        if path.exists():
            if dry_run:
                print(f"[DRY-RUN] Would delete: {tool}")
            else:
                # 移动到归档目录
                archive_path = archive_dir / tool
                shutil.move(str(path), str(archive_path))
                print(f"[DELETED] {tool} -> {archive_path}")
            deleted.append(tool)
        else:
            print(f"[SKIP] Not found: {tool}")

    print(f"\n{'=' *60}")
    print(f"SUMMARY (dry_run={dry_run})")
    print(f"{'=' *60}")
    print(f"Files to delete: {len(delete_list)}")
    print(f"Files found: {len(deleted)}")
    print(f"Archive location: {archive_dir}")

    return deleted

def main():
    import sys
    dry_run = "--dry-run" in sys.argv
    execute = "--execute" in sys.argv

    if dry_run:
        print("=" *60)
        print("DRY RUN - No files will be deleted")
        print("=" *60)
        cleanup_tools(PRIORITY_1_DELETE, PRIORITY_2_REVIEW, dry_run=True)

        print("\n" + "=" *60)
        print("PRIORITY 2 - NEEDS MANUAL REVIEW")
        print("=" *60)
        for tool in PRIORITY_2_REVIEW:
            print(f"  {tool}")

    elif execute:
        print("=" *60)
        print("EXECUTE MODE - Files will be moved to archive")
        print("=" *60)
        cleanup_tools(PRIORITY_1_DELETE, PRIORITY_2_REVIEW, dry_run=False)
    else:
        print("Usage:")
        print("  python cleanup_tools.py --dry-run   # Preview what would be deleted")
        print("  python cleanup_tools.py --execute   # Actually delete files")

if __name__ == "__main__":
    main()
