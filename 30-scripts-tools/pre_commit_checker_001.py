import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git 提交前强制检查 - 阻止不合规的提交
集成到 Git pre-commit hook
"""

import json
from pathlib import Path
import sys
from datetime import datetime

def check_workflow_compliance():
    """检查工作流合规性"""
    
    print("\n" + "=" * 60)
    print("Git Pre-Commit Workflow Compliance Check")
    print("=" * 60)
    
    workflow_file = Path("flow-archive/20260318-universal-workflow-001/workflow.json")
    daily_note = Path("13-memory/2026-03-20.md")
    
    issues = []
    warnings = []
    
    # 检查 1: 主工作流是否存在
    if not workflow_file.exists():
        issues.append("主工作流配置文件不存在！")
    else:
        print("[OK] 主工作流配置文件存在")
    
    # 检查 2: 当日笔记是否存在
    if not daily_note.exists():
        warnings.append("当日笔记不存在，建议创建")
    else:
        size = daily_note.stat().st_size
        if size > 5120:  # 5KB
            issues.append(f"当日笔记过大：{size} bytes (>5KB)，请压缩")
        else:
            print(f"[OK] 当日笔记已压缩：{size/1024:.1f}KB")
    
    # 检查 3: 检查最近提交消息是否包含工作流步骤
    try:
        import subprocess
        result = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd="D:\\OpenClaw\\workspace"
        , timeout=60)
        
        if result.returncode == 0:
            last_commit_msg = result.stdout.strip()
            print(f"[OK] 上次提交：{last_commit_msg[:50]}...")
    except (Exception,):
        warnings.append("无法检查 Git 历史")
    
    # 检查 4: 检查是否有未提交的工具文件
    try:
        import subprocess
        result = subprocess.run(
            ["git", "status", "--short", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd="D:\\OpenClaw\\workspace"
        , timeout=60)
        
        if result.returncode == 0:
            untracked = [line for line in result.stdout.split('\n') if line.startswith('??') and '30-scripts-tools/' in line and '.py' in line]
            if untracked:
                warnings.append(f"发现未跟踪的工具文件：{len(untracked)} 个")
                for f in untracked[:3]:
                    print(f"  - {f}")
    except (Exception,):
        pass
    
    # 输出结果
    print("\n" + "-" * 60)
    
    if issues:
        print(f"\n[FAIL] 发现 {len(issues)} 个严重问题:")
        for issue in issues:
            print(f"  ❌ {issue}")
        
        print("\n[BLOCK] Git 提交被阻止！")
        print("[ACTION] 请解决以上问题后再提交")
        print("=" * 60)
        return False
    
    if warnings:
        print(f"\n[WARN] 发现 {len(warnings)} 个警告:")
        for warning in warnings:
            print(f"  ⚠️ {warning}")
        print("\n[OK] 警告不会阻止提交，但建议处理")
    
    print("\n[OK] 工作流合规性检查通过")
    print("[OK] 允许 Git 提交")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = check_workflow_compliance()
    sys.exit(0 if success else 1)
