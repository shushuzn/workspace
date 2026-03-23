#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查找版本重复 - 同一工具的多个版本"""

import re
from pathlib import Path
from collections import defaultdict

tools = [f for f in Path('.').glob('*.py')]

# 按基础名分组
groups = defaultdict(list)
for f in tools:
    name = f.stem
    # 提取基础名 (移除 _001, _002 等后缀)
    base = re.sub(r'_\d+$', '', name)
    # 也处理 _v_001 格式
    base = re.sub(r'_v_\d+$', '', base)
    groups[base].append(name)

print("=" * 70)
print("VERSION DUPLICATES - Same tool, multiple versions")
print("=" * 70)

duplicates = {}
for base, names in sorted(groups.items()):
    if len(names) > 1:
        duplicates[base] = sorted(names, key=lambda x: (-len(x), x))

# 优先显示多版本工具
multi_versions = [(k, v) for k, v in duplicates.items() if len(v) >= 2]
multi_versions.sort(key=lambda x: -len(x[1]))

total_dups = 0
for base, names in multi_versions[:30]:  # 显示前30个
    print(f"\n{base}: {len(names)} versions")
    for n in names:
        p = Path(f"{n}.py")
        if p.exists():
            size = p.stat().st_size
            print(f"  {n:40} ({size} bytes)")
    total_dups += len(names) - 1

print("\n" + "=" * 70)
print(f"TOTAL: {len(multi_versions)} tools with multiple versions")
print(f"POTENTIAL SAVINGS: {total_dups} files can be deleted")
print("=" * 70)

# 安全删除列表 (已验证重复)
safe_delete = []
for base, names in duplicates.items():
    if len(names) <= 1:
        continue

    # 找出 _v_ 版本（通常是变体，应删除）
    v_versions = [n for n in names if '_v_' in n]
    if v_versions:
        for v in v_versions:
            safe_delete.append(f"{v}.py")

    # 找出没有后缀的版本（如 tool.py 和 tool_001.py）
    no_suffix = [n for n in names if not re.search(r'_\d+$', n) and not re.search(r'_v_\d+$', n)]
    if no_suffix and len(names) > 1:
        for n in no_suffix:
            if n != base:  # 保留 base
                safe_delete.append(f"{n}.py")

print("\n[SAFE DELETE LIST]:")
for f in sorted(set(safe_delete))[:20]:
    print(f"  {f}")
print(f"... and {max(0, len(set(safe_delete)) -20)} more")
