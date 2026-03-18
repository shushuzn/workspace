#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify CLI command aliases - check if all referenced tools exist
"""

import re
import sys
from pathlib import Path

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

TOOLS_DIR = Path(__file__).parent

# Read CLI file
cli_file = TOOLS_DIR / 'unified_cli_v3.py'
content = cli_file.read_text(encoding='utf-8')

# Extract all tool filenames
tools = set()
for line in content.split('\n'):
    if "'" in line and ':' in line:
        match = re.search(r"'([^']+\.py)'", line)
        if match:
            tools.add(match.group(1))

# Check which tools exist
missing = []
exists = []
for tool in sorted(tools):
    if (TOOLS_DIR / tool).exists():
        exists.append(tool)
    else:
        missing.append(tool)

# Print results
print("=" * 60)
print("CLI Command Alias Verification")
print("=" * 60)
print(f"\n总工具数：{len(tools)}")
print(f"✅ 存在：{len(exists)}")
print(f"❌ 缺失：{len(missing)}")

if missing:
    print("\n" + "=" * 60)
    print("❌ 缺失的工具 (需要修复):")
    print("=" * 60)
    for t in missing:
        print(f"  - {t}")

if exists:
    print(f"\n✅ 存在的工具 ({len(exists)}个):")
    for t in sorted(exists)[:20]:
        print(f"  - {t}")
    if len(exists) > 20:
        print(f"  ... 还有 {len(exists)-20} 个")

print("\n" + "=" * 60)
print(f"验证完成：{len(exists)}/{len(tools)} 工具存在 ({len(exists)/len(tools)*100:.1f}%)")
print("=" * 60)
