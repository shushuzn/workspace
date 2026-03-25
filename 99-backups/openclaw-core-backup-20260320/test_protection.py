#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试防护系统 - 验证所有绕过方式都被阻断
"""

import subprocess
import sys
from pathlib import Path

def test(description, command, should_block=True):
    """测试命令"""
    print(f"\n测试：{description}")
    print(f"  命令：{command}")

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    blocked = result.returncode != 0 or '[BLOCK]' in result.stdout or '[BLOCK]' in result.stderr

    if should_block and blocked:
        print("  [PASS] 已阻断")
        return True
    elif not should_block and not blocked:
        print("  [PASS] 已允许")
        return True
    else:
        print(f"  [FAIL] 预期{'阻断' if should_block else '允许'}但{'未阻断' if should_block else '被阻断'}")
        return False

def main():
    print("=" * 70)
    print("防护系统测试")
    print("=" * 70)

    # 备份 state 文件
    state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
    if state_file.exists():
        Path("flow-archive/20260318-universal-workflow-001/execution-state.json.backup").write_text(
            state_file.read_text(encoding='utf-8'), encoding='utf-8'
        )
        state_file.unlink()

    results = []

    # 测试 1: safe_shell_executor 无 session
    results.append(test(
        "safe_shell_executor 无 session",
        "py 30-scripts-tools/safe_shell_executor.py echo test",
        should_block=True
    ))

    # 测试 2: tool_executor 无 session
    results.append(test(
        "tool_executor 无 session",
        "py 30-scripts-tools/tool_executor.py safe-shell-executor echo test",
        should_block=True
    ))

    # 测试 3: git_commit_helper --no-verify
    results.append(test(
        "git_commit_helper --no-verify",
        "py 30-scripts-tools/git_commit_helper.py test --no-verify",
        should_block=True
    ))

    # 测试 4: safe_git_executor --no-verify
    results.append(test(
        "safe_git_executor --no-verify",
        "py 30-scripts-tools/safe_git_executor.py commit --no-verify",
        should_block=True
    ))

    # 恢复 state 文件
    backup_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json.backup")
    if backup_file.exists():
        state_file.write_text(backup_file.read_text(encoding='utf-8'), encoding='utf-8')
        backup_file.unlink()

    # 总结
    print("\n" + "=" * 70)
    print(f"测试结果：{sum(results)}/{len(results)} 通过")
    print("=" * 70)

    if all(results):
        print("[OK] 所有防护措施生效")
        sys.exit(0)
    else:
        print("[FAIL] 有防护措施未生效")
        sys.exit(1)

if __name__ == '__main__':
    main()
