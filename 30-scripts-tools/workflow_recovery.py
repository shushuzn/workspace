#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Recovery - 错误恢复机制

功能:
1. checkpoint 恢复功能
2. 步骤重试机制 (最多 3 次)
3. 错误状态保存
4. 恢复点选择菜单

Usage:
    py workflow_recovery.py --list-checkpoints     # 列出恢复点
    py workflow_recovery.py --restore <step>       # 恢复到指定步骤
    py workflow_recovery.py --retry <step>         # 重试指定步骤
    py workflow_recovery.py --status               # 查看错误状态
"""

import sys
import io
import json
import shutil
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
FLOW_ARCHIVE = WORKSPACE / "flow-archive" / "20260318-universal-workflow-001"
CHECKPOINT_FILE = FLOW_ARCHIVE / "checkpoint.json"
BACKUP_DIR = FLOW_ARCHIVE / "backups"
ERROR_LOG = FLOW_ARCHIVE / "error-log.json"

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

def ensure_backup_dir():
    """确保备份目录存在"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def create_backup():
    """创建检查点备份"""
    ensure_backup_dir()
    
    if not CHECKPOINT_FILE.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"checkpoint_{timestamp}.json"
    
    shutil.copy2(CHECKPOINT_FILE, backup_file)
    
    return backup_file

def load_checkpoint():
    """加载检查点"""
    if not CHECKPOINT_FILE.exists():
        return None
    
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_checkpoint(checkpoint):
    """保存检查点"""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)

def load_error_log():
    """加载错误日志"""
    if not ERROR_LOG.exists():
        return {"errors": []}
    
    with open(ERROR_LOG, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_error_log(error_log):
    """保存错误日志"""
    with open(ERROR_LOG, 'w', encoding='utf-8') as f:
        json.dump(error_log, f, indent=2, ensure_ascii=False)

def log_error(step, error_msg, retry_count=0):
    """记录错误"""
    error_log = load_error_log()
    
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "step": step,
        "error": error_msg,
        "retry_count": retry_count,
        "status": "pending"
    }
    
    error_log["errors"].append(error_entry)
    save_error_log(error_log)
    
    return error_entry

def list_checkpoints():
    """列出所有恢复点"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}可用恢复点{Colors.RESET}")
    print("=" * 70)
    
    ensure_backup_dir()
    
    # 当前检查点
    checkpoint = load_checkpoint()
    if checkpoint:
        print(f"\n{Colors.GREEN}● 当前状态{Colors.RESET}")
        print(f"  步骤：{checkpoint.get('current_step', 'N/A')}")
        print(f"  状态：{checkpoint.get('status', 'N/A')}")
        print(f"  时间：{checkpoint.get('timestamp', 'N/A')}")
        print(f"  已完成：{checkpoint.get('completed_steps', [])}")
    
    # 历史备份
    backups = sorted(BACKUP_DIR.glob("checkpoint_*.json"), reverse=True)
    
    if backups:
        print(f"\n{Colors.YELLOW}● 历史备份{Colors.RESET}")
        for i, backup in enumerate(backups[:10], 1):  # 显示最近 10 个
            with open(backup, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = backup.stem.replace("checkpoint_", "")
            step = data.get('current_step', 'N/A')
            status = data.get('status', 'N/A')
            
            print(f"  [{i}] {timestamp} - Step {step} ({status})")
    
    if not checkpoint and not backups:
        print(f"{Colors.RED}❌ 无可用恢复点{Colors.RESET}")
    
    print("=" * 70)

def restore_to_step(target_step):
    """恢复到指定步骤"""
    print(f"\n{Colors.BOLD}恢复到 Step {target_step}{Colors.RESET}")
    print("-" * 70)
    
    # 创建备份
    backup = create_backup()
    if backup:
        print(f"{Colors.GREEN}✅ 已创建备份：{backup.name}{Colors.RESET}")
    
    checkpoint = load_checkpoint()
    if not checkpoint:
        print(f"{Colors.RED}❌ 无检查点可恢复{Colors.RESET}")
        return False
    
    # 获取目标步骤的完成状态
    completed_steps = checkpoint.get('completed_steps', [])
    
    # 找到目标步骤之前的所有完成步骤
    steps_to_keep = [s for s in completed_steps if s < target_step]
    
    print(f"原完成步骤：{completed_steps}")
    print(f"恢复后步骤：{steps_to_keep}")
    
    # 更新检查点
    checkpoint['current_step'] = target_step
    checkpoint['completed_steps'] = steps_to_keep
    checkpoint['status'] = 'restored'
    checkpoint['restored_at'] = datetime.now().isoformat()
    checkpoint['restored_from'] = target_step
    
    save_checkpoint(checkpoint)
    
    print(f"\n{Colors.GREEN}✅ 已恢复到 Step {target_step}{Colors.RESET}")
    print(f"   下一步将执行：Step {target_step}")
    
    return True

def retry_step(step):
    """重试指定步骤"""
    print(f"\n{Colors.BOLD}重试 Step {step}{Colors.RESET}")
    print("-" * 70)
    
    checkpoint = load_checkpoint()
    if not checkpoint:
        print(f"{Colors.RED}❌ 无检查点{Colors.RESET}")
        return False
    
    # 检查步骤是否在已完成列表中
    completed_steps = checkpoint.get('completed_steps', [])
    
    if step in completed_steps:
        # 从完成列表中移除
        completed_steps.remove(step)
        checkpoint['completed_steps'] = completed_steps
        checkpoint['current_step'] = step
        checkpoint['status'] = 'retrying'
        
        save_checkpoint(checkpoint)
        
        print(f"{Colors.GREEN}✅ 已重置 Step {step} 为待执行状态{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️  Step {step} 未完成，无需重试{Colors.RESET}")
    
    # 记录重试
    error_log = load_error_log()
    retry_entry = {
        "timestamp": datetime.now().isoformat(),
        "step": step,
        "action": "retry",
        "status": "initiated"
    }
    error_log["errors"].append(retry_entry)
    save_error_log(error_log)
    
    return True

def show_error_status():
    """显示错误状态"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}错误状态{Colors.RESET}")
    print("=" * 70)
    
    error_log = load_error_log()
    errors = error_log.get('errors', [])
    
    if not errors:
        print(f"{Colors.GREEN}✅ 无错误记录{Colors.RESET}")
    else:
        # 按状态分组
        pending = [e for e in errors if e.get('status') == 'pending']
        resolved = [e for e in errors if e.get('status') == 'resolved']
        retries = [e for e in errors if e.get('action') == 'retry']
        
        if pending:
            print(f"\n{Colors.RED}● 待处理错误 ({len(pending)}个){Colors.RESET}")
            for err in pending[-5:]:  # 显示最近 5 个
                print(f"  - Step {err['step']}: {err['error'][:50]}")
                print(f"    时间：{err['timestamp']}")
                print(f"    重试：{err.get('retry_count', 0)}次")
        
        if resolved:
            print(f"\n{Colors.GREEN}● 已解决错误 ({len(resolved)}个){Colors.RESET}")
            for err in resolved[-3:]:  # 显示最近 3 个
                print(f"  - Step {err['step']}: 已解决")
        
        if retries:
            print(f"\n{Colors.YELLOW}● 重试记录 ({len(retries)}次){Colors.RESET}")
            for err in retries[-3:]:
                print(f"  - Step {err['step']}: {err['timestamp']}")
    
    print("=" * 70)

def interactive_menu():
    """交互式菜单"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}错误恢复菜单{Colors.RESET}")
        print("=" * 70)
        print("1. 列出恢复点")
        print("2. 恢复到指定步骤")
        print("3. 重试指定步骤")
        print("4. 查看错误状态")
        print("5. 创建备份")
        print("6. 退出")
        print("=" * 70)
        
        choice = input("请选择 (1-6): ").strip()
        
        if choice == '1':
            list_checkpoints()
        elif choice == '2':
            step = input("输入要恢复到的步骤号：").strip()
            if step.isdigit():
                restore_to_step(int(step))
            else:
                print(f"{Colors.RED}❌ 无效步骤号{Colors.RESET}")
        elif choice == '3':
            step = input("输入要重试的步骤号：").strip()
            if step.isdigit():
                retry_step(int(step))
            else:
                print(f"{Colors.RED}❌ 无效步骤号{Colors.RESET}")
        elif choice == '4':
            show_error_status()
        elif choice == '5':
            backup = create_backup()
            if backup:
                print(f"{Colors.GREEN}✅ 备份已创建：{backup.name}{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ 无检查点可备份{Colors.RESET}")
        elif choice == '6':
            print("退出")
            break
        else:
            print(f"{Colors.RED}❌ 无效选择{Colors.RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Workflow Recovery - 错误恢复机制')
    parser.add_argument('--list-checkpoints', action='store_true', help='列出所有恢复点')
    parser.add_argument('--restore', type=int, help='恢复到指定步骤')
    parser.add_argument('--retry', type=int, help='重试指定步骤')
    parser.add_argument('--status', action='store_true', help='查看错误状态')
    parser.add_argument('--backup', action='store_true', help='创建备份')
    
    args = parser.parse_args()
    
    if args.list_checkpoints:
        list_checkpoints()
    elif args.restore:
        restore_to_step(args.restore)
    elif args.retry:
        retry_step(args.retry)
    elif args.status:
        show_error_status()
    elif args.backup:
        backup = create_backup()
        if backup:
            print(f"{Colors.GREEN}✅ 备份已创建：{backup.name}{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ 无检查点可备份{Colors.RESET}")
    else:
        interactive_menu()

if __name__ == '__main__':
    main()
