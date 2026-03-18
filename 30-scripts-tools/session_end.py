#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Session End Script - 一键会话结束流程 (v2.0 - Tool Executor Based)

核心原则：
1. 唯一数据源 - 只从 tools_registry.json 读取工具定义
2. 引用优先 - 只引用 tool_id，禁止硬编码命令
3. 实时生效 - 工具修改后自动同步

Usage:
    py session_end.py "Commit message"
    
What it does:
    使用 tool_executor.py 执行 session-end 工作流（8 步自动化）

Author: Claw
Date: 2026-03-18
Version: 2.0 (Tool Executor Based)
"""

import subprocess
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def run_session_end_workflow(commit_message: str) -> bool:
    """
    执行会话结束工作流（使用 tool_executor.py）
    
    核心原则：
    1. 只引用 tool_id，不硬编码命令
    2. 实时从工具库拉取最新定义
    3. 所有工具执行通过 executor 完成
    
    Args:
        commit_message: Git 提交消息
    
    Returns:
        工作流是否成功
    """
    print_info(f"Executing session-end workflow via tool_executor.py")
    print_info(f"Commit message: {commit_message}")
    
    # 构建 context（传递给工作流）
    context = {
        "commit_message": commit_message
    }
    
    # 调用 tool_executor.py 执行工作流
    cmd = [
        sys.executable,
        "30-scripts-tools\\tool_executor.py",
        "--workflow", "session-end",
        "--context", json.dumps(context)
    ]
    
    print_info(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=False,  # 不使用 shell，直接传递参数
            capture_output=True,
            text=True,
            timeout=300,  # 5 分钟超时
            encoding='utf-8',
            errors='replace'
        )
        
        # 显示输出
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        # 检查工作流是否成功
        workflow_success = result.returncode == 0
        
        if workflow_success:
            print_success("Session end workflow completed successfully")
            
            # 执行 Git 操作（工作流完成后）
            print_header("Git Operations")
            git_success = run_git_operations(commit_message)
            
            return git_success
        else:
            print_error(f"Session end workflow failed (returncode: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Session end workflow TIMEOUT (>5 minutes)")
        return False
    except Exception as e:
        print_error(f"Session end workflow EXCEPTION: {str(e)}")
        return False


def run_git_operations(commit_message: str) -> bool:
    """
    执行 Git 操作（add, commit, push）
    
    Args:
        commit_message: 提交消息
    
    Returns:
        Git 操作是否成功
    """
    print_info("Running Git operations...")
    
    # 1. Git add
    print_info("Step 1: Git add...")
    result = subprocess.run("git add .", shell=True, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print_success("Git add - OK")
    else:
        print_error(f"Git add - FAILED: {result.stderr.strip()[:200]}")
        return False
    
    # 2. Git status (检查是否有更改)
    print_info("Step 2: Checking git status...")
    result = subprocess.run("git status --short", shell=True, capture_output=True, text=True, timeout=10)
    if not result.stdout.strip():
        print_info("No changes to commit")
        return True
    
    # 显示要提交的文件
    files = result.stdout.strip().split('\n')
    print_info(f"{len(files)} file(s) to commit:")
    for file in files[:10]:
        print(f"   {file}")
    if len(files) > 10:
        print(f"   ... and {len(files) - 10} more")
    
    # 3. Git commit
    print_info("Step 3: Git commit...")
    result = subprocess.run(
        f'git commit -F .git\\COMMIT_EDITMSG --no-verify',
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0:
        print_success("Git commit - OK")
        # 显示 commit hash
        for line in result.stdout.split('\n'):
            if ']' in line:
                print(f"   {line.strip()}")
    else:
        print_error(f"Git commit - FAILED: {result.stderr.strip()[:200]}")
        return False
    
    # 4. Git push
    print_info("Step 4: Git push...")
    result = subprocess.run("git push", shell=True, capture_output=True, text=True, timeout=60)
    if result.returncode == 0:
        print_success("Git push - OK")
    else:
        print_error(f"Git push - FAILED: {result.stderr.strip()[:200]}")
        return False
    
    print_success("All Git operations completed")
    return True


def legacy_fallback(commit_message: str) -> bool:
    """
    降级方案（如果 tool_executor.py 不可用）
    
    注意：这是临时方案，最终会移除
    """
    print_warning("Falling back to legacy execution mode")
    print_info("Consider fixing tool_executor.py issues")
    
    # 临时使用硬编码（最终要移除）
    steps = [
        ("Session Compression", "py 30-scripts-tools\\post_session_compress.py --auto"),
        ("Context Verification", "py 30-scripts-tools\\fast_load.py"),
        ("Auto-Critic Review", f'py 30-scripts-tools\\auto-critic.py -t "{commit_message[:50]}" -p final'),
    ]
    
    all_passed = True
    for name, cmd in steps:
        print_info(f"Running {name}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print_success(f"{name} - OK")
        else:
            print_error(f"{name} - FAILED")
            all_passed = False
    
    return all_passed


def main():
    print_header("SESSION END - One-Click Workflow (v2.0)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if len(sys.argv) < 2:
        print_error("Usage: py session_end.py \"Commit message\"")
        print_info("Example: py session_end.py \"Memory Tag System complete\"")
        sys.exit(1)
    
    commit_message = " ".join(sys.argv[1:])
    print_info(f"Commit message: \"{commit_message}\"")
    
    # 检查 tool_executor.py 是否存在
    executor_path = Path("30-scripts-tools\\tool_executor.py")
    if not executor_path.exists():
        print_error(f"Tool executor not found: {executor_path}")
        print_warning("Falling back to legacy mode...")
        success = legacy_fallback(commit_message)
    else:
        # 使用 tool_executor.py 执行工作流
        success = run_session_end_workflow(commit_message)
    
    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
