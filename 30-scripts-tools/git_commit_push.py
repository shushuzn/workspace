#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git Commit Push - Git 提交和推送

功能:
- 自动 git add/commit/push
- 支持自定义 commit message
- 支持 UTF-8 编码
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_command(cmd, cwd=None):
    """运行命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def git_commit_push(message, cwd="D:\\OpenClaw\\workspace"):
    """Git 提交和推送"""
    
    print("=" * 70)
    print("🔧 Git Commit Push")
    print("=" * 70)
    
    print(f"\n📝 Commit message: {message}")
    print(f"📂 工作目录：{cwd}")
    
    # Step 1: git add
    print("\n[1/3] git add -A...")
    success, stdout, stderr = run_command("git add -A", cwd)
    if not success:
        print(f"❌ git add 失败：{stderr}")
        return False
    print("✅ git add 完成")
    
    # Step 2: git commit
    print(f"\n[2/3] git commit -m '{message}'...")
    success, stdout, stderr = run_command(f"git commit -m '{message}'", cwd)
    if not success:
        if "nothing to commit" in stderr or "nothing to commit" in stdout:
            print("⚠️  没有需要提交的文件")
        else:
            print(f"❌ git commit 失败：{stderr}")
            return False
    else:
        print("✅ git commit 完成")
    
    # Step 3: git push
    print("\n[3/3] git push origin master...")
    success, stdout, stderr = run_command("git push origin master", cwd)
    if not success:
        print(f"❌ git push 失败：{stderr}")
        return False
    print("✅ git push 完成")
    
    print("\n" + "=" * 70)
    print("✅ Git Commit Push 完成!")
    print("=" * 70)
    
    return True

def main():
    """主函数"""
    message = f"chore: update {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    
    success = git_commit_push(message)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
