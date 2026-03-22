#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""比较 reg_ 文件的功能"""

from pathlib import Path
import re

reg_files = sorted(Path('.').glob('reg_*.py'))

# 提取每个文件的功能
func_map = {}
for f in reg_files:
    content = f.read_text(encoding='utf-8', errors='ignore')
    funcs = re.findall(r'def (\w+)\(', content)
    func_map[f.name] = funcs

# 找出相似的功能
from collections import defaultdict
func_groups = defaultdict(list)

for fname, funcs in func_map.items():
    for func in funcs:
        func_groups[func].append(fname)

# 显示重复功能
print("=" * 70)
print("DUPLICATE FUNCTIONS ACROSS reg_ FILES")
print("=" * 70)

dup_funcs = [(f, files) for f, files in func_groups.items() if len(files) > 1]
dup_funcs.sort(key=lambda x: -len(x[1]))

for func, files in dup_funcs[:15]:
    print(f"\n{func}:")
    for f in files:
        print(f"  - {f}")

print("\n" + "=" * 70)
print(f"TOTAL: {len(dup_funcs)} functions appear in multiple files")
print("=" * 70)

# 建议删除的文件
print("\n[SUGGESTED DELETIONS]:")
for func, files in dup_funcs:
    if len(files) > 1:
        # 保留第一个，删除其他的
        to_delete = files[1:]
        for f in to_delete:
            print(f"  {f}")
