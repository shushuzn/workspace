#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查找孤立文件 - 被 0 个其他工具调用"""

from pathlib import Path
import re

# 获取所有工具
tools = [f for f in Path('.').glob('*.py') if f.stem not in ['find_orphans', 'analyze_duplicates', 'scan_review_files']]
tool_names = set(f.stem for f in tools)

print(f'Total tools: {len(tools)}')
print('='*70)

# 统计每个工具被其他工具调用的次数
call_count = {}

for tool in tools:
    name = tool.stem
    call_count[name] = 0
    
    for other in tools:
        if other == tool:
            continue
        try:
            content = other.read_text(encoding='utf-8', errors='ignore')
            # 检查是否导入或调用
            if name in content:
                call_count[name] += 1
        except:
            pass

# 找出孤立文件 (被调用次数 = 0)
orphans = [(name, count) for name, count in call_count.items() if count == 0]

print(f'Orphan files (0 dependencies): {len(orphans)}')
print('='*70)

for name, count in sorted(orphans):
    print(f'  {name}')

# 按类别分组
print('\n' + '='*70)
print('BY CATEGORY')
print('='*70)

categories = {
    'test_': [],
    'bad_': [],
    'reg_': [],
    'add_': [],
    'auto_': [],
    'fix_': [],
    'base_': [],
    'mark_': [],
    'sync_': [],
    'update_': [],
    'other': []
}

for name, count in orphans:
    if count == 0:
        if 'test' in name.lower():
            categories['test_'].append(name)
        elif 'bad_' in name:
            categories['bad_'].append(name)
        elif name.startswith('reg_'):
            categories['reg_'].append(name)
        elif name.startswith('add_'):
            categories['add_'].append(name)
        elif name.startswith('auto_'):
            categories['auto_'].append(name)
        elif 'fix' in name.lower():
            categories['fix_'].append(name)
        elif 'base' in name.lower():
            categories['base_'].append(name)
        elif 'mark' in name.lower():
            categories['mark_'].append(name)
        elif 'sync' in name.lower():
            categories['sync_'].append(name)
        elif 'update' in name.lower():
            categories['update_'].append(name)
        else:
            categories['other'].append(name)

for cat, items in sorted(categories.items(), key=lambda x: -len(x[1])):
    if items:
        print(f'\n[{cat.upper()}] ({len(items)}):')
        for item in sorted(items)[:10]:
            print(f'  {item}')
        if len(items) > 10:
            print(f'  ... and {len(items)-10} more')
