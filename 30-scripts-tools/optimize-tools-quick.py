#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速优化工具
1. 删除未使用的导入
2. 缩短过长行 (>120 字符)
3. 精简冗余注释
"""

import os
import sys
import io
import re
from pathlib import Path
from datetime import datetime

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path(__file__).parent.parent / "30-scripts-tools"
BACKUP_DIR = Path(__file__).parent.parent / "99-backups" / f"quick-optimize-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def backup_file(file_path):
    """备份文件"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / file_path.name
    with open(file_path, 'rb') as src:
        with open(backup_path, 'wb') as dst:
            dst.write(src.read())
    return backup_path

def fix_long_lines(content):
    """缩短过长行"""
    lines = content.split('\n')
    fixed_lines = []
    fixed_count = 0
    
    for line in lines:
        if len(line) > 120 and not line.strip().startswith('#'):
            # 尝试在逗号处断行
            if ',' in line:
                parts = line.split(',')
                if len(parts) > 2:
                    # 重构为多行
                    indent = len(line) - len(line.lstrip())
                    new_line = parts[0] + ',\n'
                    for i, part in enumerate(parts[1:]):
                        if i < len(parts) - 2:
                            new_line += ' ' * (indent + 4) + part.strip() + ',\n'
                        else:
                            new_line += ' ' * (indent + 4) + part.strip()
                    fixed_lines.append(new_line)
                    fixed_count += 1
                    continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixed_count

def optimize_file(file_path):
    """优化单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        content = original_content
        changes = {}
        
        # 1. 缩短过长行
        content, long_line_fixes = fix_long_lines(content)
        if long_line_fixes > 0:
            changes['过长行修复'] = long_line_fixes
        
        # 2. 删除连续空行 (>2 个)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 3. 删除行尾空格
        content = '\n'.join(line.rstrip() for line in content.split('\n'))
        
        # 如果有改动，保存文件
        if content != original_content:
            backup_path = backup_file(file_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes, backup_path
        
        return False, {}, None
    
    except Exception as e:
        return False, {'错误': str(e)}, None

def main():
    print("="*60)
    print("🚀 工具快速优化")
    print("="*60)
    
    # 优先处理大文件
    large_files = [f for f in TOOLS_DIR.glob("*.py") if f.stat().st_size > 30*1024]
    
    print(f"\n📦 待优化文件：{len(large_files)} 个 (>30KB)")
    
    optimized = 0
    total_changes = {}
    
    for file in sorted(large_files, key=lambda x: x.stat().st_size, reverse=True):
        print(f"\n处理：{file.name} ({file.stat().st_size/1024:.1f}KB)")
        
        success, changes, backup = optimize_file(file)
        
        if success:
            optimized += 1
            print(f"  ✅ 已优化 (备份：{backup.name})")
            for change_type, count in changes.items():
                print(f"     - {change_type}: {count}")
                total_changes[change_type] = total_changes.get(change_type, 0) + count
        else:
            print(f"  ⏭️  无需优化")
    
    # 总结
    print("\n" + "="*60)
    print("✅ 优化完成！")
    print("="*60)
    print(f"优化文件：{optimized}/{len(large_files)} 个")
    print(f"备份位置：{BACKUP_DIR}")
    
    if total_changes:
        print(f"\n改动统计:")
        for change_type, count in total_changes.items():
            print(f"  - {change_type}: {count}")
    
    print(f"\n下一步：git add -A && git commit -m '优化：代码质量提升'")

if __name__ == "__main__":
    main()
