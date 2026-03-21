import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安全 Git 执行器 - 唯一允许执行 git 命令的入口

防止绕过：
- 禁止 --no-verify 参数
- 禁止 --no-hooks 参数
- 强制 pre-commit hook 执行

使用方法：
  py safe_git_executor.py commit -m "message"
  py safe_git_executor.py push
  py safe_git_executor.py status
"""

import subprocess
import sys
from pathlib import Path

# 禁止的参数
FORBIDDEN_ARGS = [
    '--no-verify',
    '--no-hooks',
    '-n',  # --no-verify 的简写
]

def check_session():
    """检查 session 存在"""
    state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
    
    if not state_file.exists():
        print("=" * 70, file=sys.stderr)
        print("[BLOCK] Git 命令被拒绝", file=sys.stderr)
        print("[BLOCK] 原因：execution-state.json 不存在", file=sys.stderr)
        print("[BLOCK] 请先运行：py 30-scripts-tools/copaw_entry.py <task>", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)
    
    try:
        import json
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        assert state.get('session_id'), "session_id missing"
        assert state.get('mandatory_execution'), "mandatory_execution not enabled"
    except Exception as e:
        print("=" * 70, file=sys.stderr)
        print("[BLOCK] Git 命令被拒绝", file=sys.stderr)
        print(f"[BLOCK] 原因：session 无效 - {e}", file=sys.stderr)
        print("[BLOCK] 请先运行：py 30-scripts-tools/copaw_entry.py <task>", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

logging.basicConfig(level=logging.INFO)
def main():
    # 检查 session
    check_session()
    
    # 检查禁止的参数
    for arg in sys.argv[1:]:
        if arg in FORBIDDEN_ARGS:
            print("=" * 70, file=sys.stderr)
            print("[BLOCK] Git 命令被拒绝", file=sys.stderr)
            print(f"[BLOCK] 禁止的参数：{arg}", file=sys.stderr)
            print("[BLOCK] 不允许绕过 pre-commit hook", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            sys.exit(1)
    
    # 构建 git 命令
    git_cmd = ['git'] + sys.argv[1:]
    
    # 执行
    try:
        result = subprocess.run(
            git_cmd,
            capture_output=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        , timeout=60)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"[ERROR] Git 命令执行失败：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <args>")
        sys.exit(1)
