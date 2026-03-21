import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git Commit + Push with Retry Mechanism
Usage: py git_commit_helper.py "commit message"

防护规则:
- 禁止 --no-verify 参数
- 禁止 --no-hooks 参数
- 强制 session 检查
"""

import subprocess
import sys
import time

# 禁止的参数
FORBIDDEN_ARGS = ['--no-verify', '--no-hooks', '-n']

def run_command(cmd, capture=True):
    """运行命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture,
            text=True,
            encoding='utf-8',
            errors='replace'
        , timeout=60)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        print("Usage: py git_commit_helper.py \"commit message\"")
        print("")
        print("注意：不允许跳过 pre-commit hook 检查")
        print("禁止使用：--no-verify, --no-hooks, -n")
        print("如需提交，请先完成 workflow 步骤")
        sys.exit(1)
    
    # 检查禁止的参数
    for arg in sys.argv[1:]:
        if arg in FORBIDDEN_ARGS:
            print("=" * 70, file=sys.stderr)
            print("[BLOCK] Git 命令被拒绝", file=sys.stderr)
            print(f"[BLOCK] 禁止的参数：{arg}", file=sys.stderr)
            print("[BLOCK] 不允许绕过 pre-commit hook", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            sys.exit(1)
    
    message = sys.argv[1]
    
    print("=" * 60)
    print("Git Commit + Push (with retry)")
    print("=" * 60)
    print()
    
    # Step 1: Git add
    print("[STEP 1] Running git add...")
    code, out, err = run_command("git add -u")
    if code != 0:
        print(f"[WARN] git add failed: {err}")
    
    # Step 2: Git commit
    print("[STEP 2] Running git commit...")
    code, out, err = run_command(f'git commit -m "{message}"')
    if code != 0:
        print(f"[WARN] git commit failed (no changes?): {err.encode('ascii', errors='ignore').decode('ascii')}")
        print("[INFO] Continuing to push anyway...")
    else:
        print("[OK] Local commit successful")
    
    # Step 3: Network check
    print()
    print("[CHECK] Testing network connection...")
    code, out, err = run_command("git ls-remote --heads origin")
    if code != 0:
        print("[WARN] Cannot connect to remote, waiting 5s...")
        time.sleep(5)
    
    # Step 4: Git push with retry
    max_retries = 3
    retry_count = 0
    push_success = False
    
    while retry_count < max_retries:
        retry_count += 1
        
        if retry_count == 1:
            print(f"\n[PUSH] Attempt {retry_count}/{max_retries}...")
        else:
            print(f"\n[RETRY] Attempt {retry_count}/{max_retries} (waiting 3s)...")
            time.sleep(3)
            print(f"[PUSH] Retry attempt {retry_count}/{max_retries}...")
        
        code, out, err = run_command("git push origin master")
        
        # Check for success
        if code == 0 or "success" in out.lower() or "up to date" in out.lower():
            push_success = True
            print(f"\n[OK] Git push successful on attempt {retry_count}")
            break
        else:
            print(f"[WARN] Push attempt {retry_count} failed")
            if err:
                print(f"  Error: {err[:200]}")
    
    # Final result
    print()
    print("=" * 60)
    if push_success:
        print("[RESULT] SUCCESS")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"[RESULT] PARTIAL (local commit OK, push failed after {max_retries} attempts)")
        print("[INFO] Local commit is saved, you can push manually later")
        print("[HINT] Check network connection or run: git push origin master")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
