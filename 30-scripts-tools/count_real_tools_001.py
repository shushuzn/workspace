#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统计实际工具文件数量
"""
from pathlib import Path

scripts_dir = Path("30-scripts-tools")

# 排除辅助脚本
exclude_prefixes = ["check_", "debug_", "fix_", "sync_", "reg_", "count_", "list_", "find_", "test_", "diagnose_"]

all_py = list(scripts_dir.glob("*.py"))
valid_py = [f for f in all_py if not any(f.name.startswith(p) for p in exclude_prefixes)]

print("=" * 70)
print("30-scripts-tools 文件统计")
print("=" * 70)
print(f"\n所有 .py 文件：{len(all_py)}")
print(f"有效工具文件：{len(valid_py)} (排除辅助脚本)")

print("\n有效工具列表:")
for i, f in enumerate(sorted(valid_py), 1):
    print(f"  {i}. {f.name}")

print(f"\n{'=' * 70}")
print(f"结论：应该注册 {len(valid_py)} 个工具")
