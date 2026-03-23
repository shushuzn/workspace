#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度扫描 reg_ 文件"""

from pathlib import Path

reg_files = [f for f in Path('.').glob('reg_*.py')]
print(f'Found {len(reg_files)} reg_ files')
print('=' *70)

# 读取每个文件的关键信息
for f in sorted(reg_files):
    content = f.read_text(encoding='utf-8', errors='ignore')

    # 提取描述
    desc = ''
    for line in content.split('\n')[:20]:
        if '"""' in line or "'''" in line:
            desc = line.strip().replace('"""', '').replace("'''", '')
            break

    # 检查是否被其他文件调用
    called_by = []
    for other in Path('.').glob('*.py'):
        if other.name == f.name:
            continue
        try:
            other_content = other.read_text(encoding='utf-8', errors='ignore')
            if f.stem in other_content:
                called_by.append(other.name)
        except Exception:
            pass

    call_count = len(called_by)

    print(f'{f.name}')
    print(f'  Desc: {desc[:60]}')
    print(f'  Called by: {call_count} files')
    if called_by[:3]:
        print(f'  Examples: {", ".join(called_by[:3])}')
    print()
