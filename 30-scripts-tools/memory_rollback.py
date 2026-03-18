#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
记忆回滚工具
功能：撤销最近一次蒸馏操作
"""

import os
import sys
import re
import shutil
from datetime import datetime

def create_backup(file_path):
    """创建文件备份"""
    if not os.path.exists(file_path):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"[ERROR] 创建备份失败：{str(e)}")
        return None

def find_last_distill_entry(memory_file):
    """查找最后一次蒸馏添加的记忆条目"""
    
    if not os.path.exists(memory_file):
        return None
    
    with open(memory_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找实时蒸馏添加的条目
    pattern = r'<!-- 实时蒸馏 v3\.0 自动添加 -->\s*\n(.*?)(?=\n<!-- 实时蒸馏 v3\.0 自动添加 -->|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if not matches:
        return None
    
    # 返回最后一个
    return matches[-1]

def remove_last_distill_entry(memory_file):
    """移除最后一次蒸馏添加的记忆条目"""
    
    if not os.path.exists(memory_file):
        print(f"[ERROR] 文件不存在：{memory_file}")
        return False
    
    with open(memory_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并移除最后一个蒸馏条目
    pattern = r'\n<!-- 实时蒸馏 v3\.0 自动添加 -->\s*\n(.*?)(?=\n<!-- 实时蒸馏 v3\.0 自动添加 -->|\Z)'
    
    # 查找所有匹配
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    if not matches:
        print("[INFO] 未找到可移除的蒸馏条目")
        return False
    
    # 移除最后一个匹配
    last_match = matches[-1]
    new_content = content[:last_match.start()] + content[last_match.end():]
    
    # 写回文件
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"[OK] 已移除最后 {len(last_match.group(1).split('###')) - 1} 条记忆条目")
    return True

def rollback(memory_file=None, dry_run=False):
    """回滚最后一次蒸馏操作"""
    
    # 自动检测文件
    if not memory_file:
        possible_memory = [
            'MEMORY.md',
            os.path.join('memory', 'MEMORY.md'),
            os.path.join('13-memory', 'MEMORY.md'),
            r'C:\Users\华为\.copaw\workspaces\default\memory\MEMORY.md',
        ]
        
        for pm in possible_memory:
            if os.path.exists(pm):
                memory_file = pm
                break
        
        if not memory_file:
            print("[ERROR] 未找到 MEMORY.md")
            return False
    
    print(f"[INFO] 回滚目标：{memory_file}")
    
    # 创建备份
    backup_path = create_backup(memory_file)
    if not backup_path:
        print("[ERROR] 无法创建备份，中止回滚")
        return False
    
    print(f"[OK] 已创建备份：{backup_path}")
    
    if dry_run:
        # 预览模式
        entry = find_last_distill_entry(memory_file)
        if not entry:
            print("[INFO] 未找到可回滚的条目")
            return True
        
        print("\n[预览] 将要移除的内容:")
        print("-" * 60)
        print(entry[:500])  # 只显示前 500 字符
        if len(entry) > 500:
            print("...")
        print("-" * 60)
        return True
    
    # 执行回滚
    success = remove_last_distill_entry(memory_file)
    
    if not success:
        # 回滚失败，恢复备份
        print("[ERROR] 回滚失败，尝试恢复备份...")
        try:
            shutil.copy2(backup_path, memory_file)
            print(f"[OK] 已恢复备份")
        except Exception as e:
            print(f"[ERROR] 恢复备份失败：{str(e)}")
        return False
    
    print(f"[OK] 回滚完成")
    print(f"[INFO] 备份文件：{backup_path}")
    print(f"[INFO] 如需恢复，手动复制备份到原位置即可")
    
    return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='记忆回滚工具')
    parser.add_argument('--file', '-f', help='MEMORY.md 文件路径')
    parser.add_argument('--dry-run', '-n', action='store_true', help='预览模式，不实际修改')
    
    args = parser.parse_args()
    
    success = rollback(
        memory_file=args.file,
        dry_run=args.dry_run
    )
    
    sys.exit(0 if success else 1)
