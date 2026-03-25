#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git Pre-Commit 检查增强版 v2.0 - 强制检查工作流合规性
集成 workflow_guardian_v2.py 进行深度验证
完成率<100% 或类型不匹配 阻止提交
"""

import json
from pathlib import Path
import sys
from datetime import datetime
import subprocess

def run_workflow_guardian() -> bool:
    """运行 workflow_guardian_v2.py 进行深度验证"""
    try:
        result = subprocess.run(
            [sys.executable, '30-scripts-tools/workflow_guardian_v2.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )

        # 打印 guardian 输出
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] workflow_guardian 执行失败：{e}")
        return False

def check_workflow_completion() -> bool:
    """检查工作流完成率 - 增强版 v2.0"""

    print("\n" + "=" * 80)
    print(" " * 20 + "Git Pre-Commit 工作流检查 v2.0")
    print("=" * 80)
    print(f"检查时间：{datetime.now().isoformat()}")

    # 第 0 步：运行 workflow_guardian 深度验证
    print("\n[阶段 1] 运行 Workflow Guardian 深度验证...")
    guardian_passed = run_workflow_guardian()

    if not guardian_passed:
        print("\n[FAIL] Workflow Guardian 验证失败！")
        print("[BLOCK] Git 提交被阻止！")
        print("\n[ACTION] 请先修复 workflow_guardian 报告的问题")
        print("=" * 80)
        return False

    print("\n[阶段 1] Workflow Guardian 验证通过")

    # 第 1 步：传统检查
    print("\n[阶段 2] 传统完成率检查...")

    state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
    workflow_file = Path("flow-archive/20260318-universal-workflow-001/workflow.json")

    # 检查 1: 状态文件是否存在
    if not state_file.exists():
        print("\n[WARN] 执行状态文件不存在")
        print("[ACTION] 请先运行 workflow_autoloader.py 初始化任务")
        return False

    # 检查 2: 加载状态
    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    # 检查 3: 加载工作流
    if not workflow_file.exists():
        print("\n[FAIL] 工作流配置文件不存在！")
        return False

    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    steps = workflow.get('steps', [])
    required_steps = [s.get('step_id') for s in steps if s.get('required', True)]
    completed = state.get('completed_steps', [])

    # 计算完成率
    completed_required = [s for s in completed if s in required_steps]
    completion_rate = len(completed_required) / len(required_steps) * 100 if required_steps else 0

    # 显示状态
    print(f"\n任务：{state.get('task', 'N/A')}")
    print(f"Flow ID: {state.get('flow_id', 'N/A')}")
    print(f"状态：{state.get('status', 'unknown')}")
    print(f"\n必需步骤：{len(required_steps)} 步")
    print(f"已完成：{len(completed_required)} 步")
    print(f"完成率：{completion_rate:.1f}%")

    # 检查 4: 完成率是否 100%
    if completion_rate < 100:
        missing = [s for s in required_steps if s not in completed]

        print(f"\n[FAIL] 完成率不足 100%！")
        print(f"[BLOCK] Git 提交被阻止！")
        print(f"\n缺失步骤：{len(missing)}")
        for step_id in missing[:10]:
            print(f"  - {step_id}")

        if len(missing) > 10:
            print(f"  ... 还有 {len(missing) -10} 个")

        print("\n[ACTION] 请完成所有必需步骤后再提交")
        print("=" * 80)
        return False

    # 检查 5: 当日笔记大小
    daily_note = Path("13-memory/2026-03-19.md")
    if daily_note.exists():
        size = daily_note.stat().st_size
        if size > 5120:  # 5KB
            print(f"\n[FAIL] 当日笔记过大：{size} bytes (>5KB)")
            print("[BLOCK] 请先压缩会话笔记！")
            print("=" * 80)
            return False
        else:
            print(f"\n[OK] 当日笔记大小：{size /1024:.1f}KB (<5KB)")

    # 检查 6: 状态是否为 completed
    if state.get('status') != 'completed':
        print(f"\n[WARN] 任务状态不是 'completed'")
        print(f"[INFO] 当前状态：{state.get('status')}")
        # 警告但不阻止

    print(f"\n[OK] 完成率：{completion_rate:.1f}%")
    print("[OK] 所有必需步骤已完成")
    print("[OK] 允许 Git 提交")
    print("=" * 80)
    return True

def main():
    """测试入口"""
    success = check_workflow_completion()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
