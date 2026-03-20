#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试工具包装器集成效果
"""

import sys
from pathlib import Path
import shutil

print("=" * 70)
print("测试工具包装器集成")
print("=" * 70)

# 临时移除所有 state 文件
state_files = list(Path("flow-archive").glob("*/execution-state.json"))
print(f"\n[1] 临时移除 {len(state_files)} 个 state 文件")
for f in state_files:
    shutil.move(str(f), str(f) + ".backup")

print("\n[2] 测试 safe_shell_executor (无 session)")
print("-" * 70)

# 测试 safe_shell_executor
sys.path.insert(0, '30-scripts-tools')
from safe_shell_executor import SafeShellExecutor

executor = SafeShellExecutor()
result = executor.execute('echo "test"')

print(f"\n结果：{result.get('status')}")
if result.get('status') == 'blocked':
    print("[PASS] 防护生效：无 session 时拒绝执行")
else:
    print("[FAIL] 防护失效：无 session 时仍然执行")

print("\n" + "=" * 70)

# 恢复 state 文件
print("\n[3] 恢复 state 文件")
for f in Path("flow-archive").glob("*/execution-state.json.backup"):
    shutil.move(str(f), str(f).replace('.backup', ''))
    print(f"  恢复：{f.name}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
