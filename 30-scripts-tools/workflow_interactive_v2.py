#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Interactive v2.0 - 可视化进度条增强版

功能:
1. 实时进度条显示
2. 剩余时间估算
3. 步骤状态可视化
4. 颜色编码状态
5. 交互式菜单

Usage:
    py workflow_interactive.py                    # 交互模式
    py workflow_interactive.py --show-progress    # 显示进度
    py workflow_interactive.py --estimate-time    # 估算时间
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
FLOW_ARCHIVE = WORKSPACE / "flow-archive"
CHECKPOINT_FILE = FLOW_ARCHIVE / "20260318-universal-workflow-001" / "checkpoint.json"
WORKFLOW_FILE = FLOW_ARCHIVE / "20260318-universal-workflow-001" / "workflow.json"

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

def load_checkpoint():
    """加载检查点"""
    if not CHECKPOINT_FILE.exists():
        return None
    
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_workflow():
    """加载工作流配置"""
    if not WORKFLOW_FILE.exists():
        return None
    
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_progress_bar(current, total, width=40):
    """打印进度条"""
    percentage = current / total
    filled = int(width * percentage)
    bar = "█" * filled + "░" * (width - filled)
    
    # 颜色根据进度变化
    if percentage < 0.3:
        color = Colors.RED
    elif percentage < 0.7:
        color = Colors.YELLOW
    else:
        color = Colors.GREEN
    
    print(f"{color}[{bar}] {percentage*100:.1f}%{Colors.RESET}")

def print_step_status(steps, completed_steps, current_step):
    """打印步骤状态"""
    print(f"\n{Colors.BOLD}步骤状态:{Colors.RESET}")
    print("=" * 60)
    
    for i, step in enumerate(steps, 1):
        step_num = i
        
        # 确定状态
        if step_num in completed_steps:
            status = f"{Colors.GREEN}✅ 完成{Colors.RESET}"
        elif step_num == current_step:
            status = f"{Colors.BLUE}▶️ 进行中{Colors.RESET}"
        elif step_num < current_step:
            status = f"{Colors.RED}❌ 跳过{Colors.RESET}"
        else:
            status = f"{Colors.GRAY}⏳ 等待{Colors.RESET}"
        
        # 阻塞标记
        blocker = step.get('blocker', False)
        blocker_mark = f" {Colors.RED}[阻塞]{Colors.RESET}" if blocker else ""
        
        print(f"Step {step_num:2d}: {step['name']:<30s} {status}{blocker_mark}")
    
    print("=" * 60)

def estimate_remaining_time(completed_steps, total_steps, elapsed_time):
    """估算剩余时间"""
    if len(completed_steps) == 0:
        return None
    
    # 平均每步时间
    avg_time_per_step = elapsed_time / len(completed_steps)
    
    # 剩余步骤
    remaining_steps = total_steps - len(completed_steps)
    
    # 估算剩余时间
    remaining_time = avg_time_per_step * remaining_steps
    
    return remaining_time

def format_time(seconds):
    """格式化时间显示"""
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}分{secs}秒"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}小时{minutes}分钟"

def show_progress():
    """显示完整进度"""
    checkpoint = load_checkpoint()
    workflow = load_workflow()
    
    if not checkpoint:
        print(f"{Colors.RED}❌ 检查点文件不存在{Colors.RESET}")
        print("请先启动工作流：py workflow_enforcer.py --start")
        return
    
    if not workflow:
        print(f"{Colors.RED}❌ 工作流配置文件不存在{Colors.RESET}")
        return
    
    # 基本信息
    print(f"\n{Colors.BOLD}{Colors.CYAN}工作流进度{Colors.RESET}")
    print("=" * 60)
    print(f"Flow ID: {checkpoint.get('flow_id', 'N/A')}")
    print(f"状态：{checkpoint.get('status', 'N/A')}")
    print(f"任务：{checkpoint.get('task', 'N/A')}")
    print(f"当前步骤：{checkpoint.get('current_step', 0)}/{workflow['total_steps']}")
    print(f"已完成：{len(checkpoint.get('completed_steps', []))}/{workflow['total_steps']}")
    
    # 进度条
    print(f"\n{Colors.BOLD}进度:{Colors.RESET}")
    current = checkpoint.get('current_step', 0)
    total = workflow['total_steps']
    print_progress_bar(current, total)
    
    # 步骤状态
    steps = workflow['steps']
    completed = checkpoint.get('completed_steps', [])
    print_step_status(steps, completed, current)
    
    # 时间估算
    timestamp = checkpoint.get('timestamp')
    if timestamp:
        start_time = datetime.fromisoformat(timestamp)
        elapsed = (datetime.now() - start_time).total_seconds()
        remaining = estimate_remaining_time(completed, total, elapsed)
        
        print(f"\n{Colors.BOLD}时间统计:{Colors.RESET}")
        print(f"已用时间：{format_time(elapsed)}")
        if remaining:
            print(f"预计剩余：{format_time(remaining)}")
            print(f"预计完成：{format_time(elapsed + remaining)}")
    
    # 交付物
    deliverables = checkpoint.get('deliverables', [])
    if deliverables:
        print(f"\n{Colors.BOLD}交付物:{Colors.RESET}")
        for item in deliverables:
            print(f"  - {item}")
    
    print()

def interactive_menu():
    """交互式菜单"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}工作流交互式菜单 v2.0{Colors.RESET}")
        print("=" * 60)
        print("1. 显示进度")
        print("2. 步骤详情")
        print("3. 时间估算")
        print("4. 刷新状态")
        print("5. 退出")
        print("=" * 60)
        
        choice = input("请选择 (1-5): ").strip()
        
        if choice == '1':
            show_progress()
        elif choice == '2':
            checkpoint = load_checkpoint()
            workflow = load_workflow()
            if checkpoint and workflow:
                steps = workflow['steps']
                completed = checkpoint.get('completed_steps', [])
                current = checkpoint.get('current_step', 0)
                print_step_status(steps, completed, current)
        elif choice == '3':
            checkpoint = load_checkpoint()
            if checkpoint:
                timestamp = checkpoint.get('timestamp')
                if timestamp:
                    start_time = datetime.fromisoformat(timestamp)
                    elapsed = (datetime.now() - start_time).total_seconds()
                    completed = checkpoint.get('completed_steps', [])
                    workflow = load_workflow()
                    if workflow:
                        remaining = estimate_remaining_time(
                            completed, 
                            workflow['total_steps'], 
                            elapsed
                        )
                        if remaining:
                            print(f"\n预计剩余时间：{format_time(remaining)}")
                        else:
                            print("\n无法估算剩余时间")
        elif choice == '4':
            print("刷新中...")
            time.sleep(0.5)
            show_progress()
        elif choice == '5':
            print("退出")
            break
        else:
            print("无效选择，请重试")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Workflow Interactive v2.0')
    parser.add_argument('--show-progress', action='store_true', help='显示进度')
    parser.add_argument('--estimate-time', action='store_true', help='估算时间')
    parser.add_argument('--step-status', action='store_true', help='步骤状态')
    
    args = parser.parse_args()
    
    if args.show_progress:
        show_progress()
    elif args.estimate_time:
        checkpoint = load_checkpoint()
        if checkpoint:
            timestamp = checkpoint.get('timestamp')
            if timestamp:
                start_time = datetime.fromisoformat(timestamp)
                elapsed = (datetime.now() - start_time).total_seconds()
                completed = checkpoint.get('completed_steps', [])
                workflow = load_workflow()
                if workflow:
                    remaining = estimate_remaining_time(
                        completed, 
                        workflow['total_steps'], 
                        elapsed
                    )
                    if remaining:
                        print(f"预计剩余时间：{format_time(remaining)}")
    elif args.step_status:
        checkpoint = load_checkpoint()
        workflow = load_workflow()
        if checkpoint and workflow:
            steps = workflow['steps']
            completed = checkpoint.get('completed_steps', [])
            current = checkpoint.get('current_step', 0)
            print_step_status(steps, completed, current)
    else:
        interactive_menu()

if __name__ == '__main__':
    main()
