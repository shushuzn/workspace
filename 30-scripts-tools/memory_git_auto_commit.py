#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
记忆系统 Git 自动提交工具
功能：MEMORY.md 更新后自动提交并推送
"""

import os
import sys
import subprocess
from datetime import datetime

def run_git_command(cmd, cwd=None):
    """执行 Git 命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def auto_commit_memory(memory_file, message_prefix="记忆"):
    """自动提交记忆文件"""
    
    # 检测工作区根目录
    workspace_dirs = [
        r'D:\OpenClaw\workspace',
        r'C:\Users\华为\.copaw\workspaces\default',
    ]
    
    workspace = None
    for wd in workspace_dirs:
        if os.path.exists(os.path.join(wd, '.git')):
            workspace = wd
            break
    
    if not workspace:
        print("[ERROR] 未找到 Git 仓库")
        return False
    
    # 检查文件是否存在
    if not os.path.exists(memory_file):
        print(f"[ERROR] 文件不存在：{memory_file}")
        return False
    
    # 获取相对路径
    rel_path = os.path.relpath(memory_file, workspace)
    
    # 检查是否有变更
    success, stdout, stderr = run_git_command(
        f'git diff --name-only "{rel_path}"',
        cwd=workspace
    )
    
    if not stdout.strip():
        print("[OK] 记忆文件无变更，跳过提交")
        return True
    
    # 添加文件
    print(f"[ADD] 添加文件：{rel_path}")
    success, stdout, stderr = run_git_command(
        f'git add "{rel_path}"',
        cwd=workspace
    )
    
    if not success:
        print(f"[ERROR] Git add 失败：{stderr}")
        return False
    
    # 生成提交信息
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"{message_prefix}: 更新记忆文件 ({timestamp})"
    
    # 提交
    print(f"[COMMIT] {commit_msg}")
    success, stdout, stderr = run_git_command(
        f'git commit -m "{commit_msg}"',
        cwd=workspace
    )
    
    if not success:
        print(f"[WARN] Git commit 失败：{stderr}")
        # 可能是没有变更
        if "nothing to commit" in stderr:
            return True
        return False
    
    # 推送
    print("[PUSH] 推送到远程仓库...")
    success, stdout, stderr = run_git_command(
        'git push origin master',
        cwd=workspace
    )
    
    if not success:
        print(f"[WARN] Git push 失败：{stderr}")
        # 推送失败不影响本地提交
        return True
    
    print("[OK] 记忆文件已提交并推送")
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 默认检查多个可能位置
        memory_files = [
            r'MEMORY.md',
            r'memory\MEMORY.md',
            r'13-memory\MEMORY.md',
            r'20-MEMORY\MEMORY.md',
        ]
        
        for mf in memory_files:
            if os.path.exists(mf):
                auto_commit_memory(mf)
                return
        print("[ERROR] 未找到记忆文件")
        return
    
    # 指定文件
    memory_file = sys.argv[1]
    message = sys.argv[2] if len(sys.argv) > 2 else "记忆"
    
    auto_commit_memory(memory_file, message)

if __name__ == '__main__':
    main()
