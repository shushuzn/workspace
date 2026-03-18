#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Tools Analysis - Identify duplicates and consolidation opportunities
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

TOOLS_DIR = Path(__file__).parent

# Find all memory-related files
memory_files = list(TOOLS_DIR.glob('*memory*.py'))

print("=" * 60)
print("Memory Tools Analysis")
print("=" * 60)
print(f"\n总文件数：{len(memory_files)}\n")

# Group by base name (remove version numbers)
groups = defaultdict(list)
for f in memory_files:
    name = f.stem
    # Remove version suffixes (_v1, _v2, _v3, etc.)
    base_name = re.sub(r'_v\d+$', '', name)
    base_name = re.sub(r'_v\d+_\d+$', '', base_name)
    groups[base_name].append(name)

# Find groups with multiple versions
print("📊 版本分组 (可能重复):")
print("=" * 60)
duplicates = []
for base, versions in sorted(groups.items()):
    if len(versions) > 1:
        duplicates.append((base, versions))
        print(f"\n{base}:")
        for v in versions:
            file_path = TOOLS_DIR / f"{v}.py"
            size = file_path.stat().st_size if file_path.exists() else 0
            print(f"  - {v}.py ({size:,} bytes)")

print("\n" + "=" * 60)
print(f"发现 {len(duplicates)} 组重复/多版本文件")
print("=" * 60)

# Analyze specific patterns
print("\n🔍 特定模式分析:")
print("=" * 60)

# Fix files
fix_files = [f for f in memory_files if 'fix' in f.stem.lower()]
if fix_files:
    print(f"\n修复工具 ({len(fix_files)}个):")
    for f in fix_files:
        print(f"  - {f.name}")

# Search files
search_files = [f for f in memory_files if 'search' in f.stem.lower()]
if search_files:
    print(f"\n搜索工具 ({len(search_files)}个):")
    for f in search_files:
        print(f"  - {f.name}")

# Dashboard files
dashboard_files = [f for f in memory_files if 'dashboard' in f.stem.lower()]
if dashboard_files:
    print(f"\nDashboard 工具 ({len(dashboard_files)}个):")
    for f in dashboard_files:
        print(f"  - {f.name}")

# Distiller files
distiller_files = [f for f in memory_files if 'distill' in f.stem.lower()]
if distiller_files:
    print(f"\nDistiller 工具 ({len(distiller_files)}个):")
    for f in distiller_files:
        print(f"  - {f.name}")

# Quality files
quality_files = [f for f in memory_files if 'quality' in f.stem.lower()]
if quality_files:
    print(f"\nQuality 工具 ({len(quality_files)}个):")
    for f in quality_files:
        print(f"  - {f.name}")

# Util files
util_files = [f for f in memory_files if 'util' in f.stem.lower()]
if util_files:
    print(f"\nUtil 工具 ({len(util_files)}个):")
    for f in util_files:
        print(f"  - {f.name}")

print("\n" + "=" * 60)
print("精简建议:")
print("=" * 60)
print("""
1. 保留最新版本 (v3 > v2 > v1)
2. 合并 fix 工具为单一脚本
3. 合并 util 工具为单一模块
4. 删除测试文件 (如果不再需要)
5. 归档旧版本到 99-archive

预计精简：10-15 个文件
""")
