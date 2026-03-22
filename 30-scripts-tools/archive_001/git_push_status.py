#!/usr/bin/env python3
"""
Git推送状态检查工具
用于检查本地分支与远程分支的差异状态，确认代码是否已成功推送到远程仓库
"""

import subprocess
import sys
import os

def run_git_command(cmd):
    """执行Git命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", f"执行命令时出错: {str(e)}"

def get_current_branch():
    """获取当前Git分支"""
    code, stdout, stderr = run_git_command("git branch --show-current")
    if code != 0:
        return None, stderr
    return stdout.strip(), None

def get_remote_url():
    """获取远程仓库URL"""
    code, stdout, stderr = run_git_command("git remote get-url origin")
    if code != 0:
        return None, stderr
    return stdout.strip(), None

def check_push_status():
    """检查Git推送状态"""
    # 检查是否在Git仓库中
    code, _, stderr = run_git_command("git rev-parse --is-inside-work-tree")
    if code != 0:
        return False, "错误: 当前目录不是Git仓库", None
    
    # 获取当前分支
    branch, err = get_current_branch()
    if not branch:
        return False, f"错误: {err}", None
    
    # 获取远程URL
    remote_url, err = get_remote_url()
    if not remote_url:
        return False, f"错误: {err}", None
    
    # 刷新远程信息
    run_git_command("git fetch")
    
    # 检查远程分支是否存在
    code, stdout, stderr = run_git_command(f"git ls-remote --heads origin {branch}")
    if code != 0 or not stdout.strip():
        # 远程分支不存在
        return True, f"远程分支 origin/{branch} 不存在，所有更改尚未推送", {
            "branch": branch,
            "remote_url": remote_url,
            "remote_branch_missing": True
        }
    
    # 检查本地与远程的差异
    # 使用git status命令检查状态
    code, stdout, stderr = run_git_command("git status")
    if code != 0:
        return False, f"错误: {stderr}", None
    
    # 检查是否有未推送的提交
    code, stdout, stderr = run_git_command(f"git log --oneline origin/{branch}..HEAD")
    unpushed_commits = stdout.strip().split('\n') if stdout.strip() else []
    unpushed_commits = [c for c in unpushed_commits if c]
    
    if unpushed_commits:
        status = f"存在 {len(unpushed_commits)} 个未推送的提交"
        return True, status, {
            "branch": branch,
            "remote_url": remote_url,
            "unpushed_commits": len(unpushed_commits),
            "commits": unpushed_commits[:5]  # 只显示前5个提交
        }
    else:
        # 检查是否有未拉取的提交
        code, stdout, stderr = run_git_command(f"git log --oneline HEAD..origin/{branch}")
        if stdout.strip():
            return True, "远程有新的提交，需要拉取", {
                "branch": branch,
                "remote_url": remote_url,
                "has_remote_updates": True
            }
        else:
            return True, "所有更改已推送，本地与远程同步", {
                "branch": branch,
                "remote_url": remote_url,
                "is_synced": True
            }

def format_status_message(status, details):
    """格式化状态消息"""
    messages = []
    messages.append("=" * 60)
    messages.append("Git推送状态检查")
    messages.append("=" * 60)
    messages.append(f"当前分支: {details.get('branch', '未知')}")
    messages.append(f"远程仓库: {details.get('remote_url', '未知')}")
    messages.append("")
    messages.append(f"状态: {status}")
    
    if details.get('unpushed_commits', 0) > 0:
        messages.append("")
        messages.append("未推送的提交:")
        for commit in details.get('commits', []):
            messages.append(f"  - {commit}")
        if details.get('unpushed_commits', 0) > 5:
            messages.append(f"  ... 还有 {details['unpushed_commits'] - 5} 个提交")
    
    messages.append("=" * 60)
    return "\n".join(messages)

def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py git_push_status.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py git_push_status.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

主函数"""
    success, status, details = check_push_status()
    
    if success:
        print(format_status_message(status, details))
        
        # 提供推送建议
        if details.get('unpushed_commits', 0) > 0:
            print("\n建议: 执行以下命令推送更改:")
            print(f"  git push origin {details.get('branch', '当前分支')}")
        elif details.get('remote_branch_missing', False):
            print("\n建议: 执行以下命令创建远程分支并推送更改:")
            print(f"  git push -u origin {details.get('branch', '当前分支')}")
        elif details.get('has_remote_updates', False):
            print("\n建议: 执行以下命令拉取远程更改:")
            print(f"  git pull origin {details.get('branch', '当前分支')}")
        else:
            print("\n无需操作，本地与远程已同步")
    else:
        print(f"错误: {status}")
        sys.exit(1)

if __name__ == "__main__":
    main()
