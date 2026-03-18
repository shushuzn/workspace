#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理重复文件 - 安全版本
只清理：
1. 带 _from_ 后缀的副本文件
2. Obsidian 配置重复（保留 .obsidian/）
3. 空目录
"""

import os
import sys
import io
import hashlib
from pathlib import Path
from collections import defaultdict

# 修复 Windows 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = r"D:\OpenClaw\workspace"

def calculate_file_hash(file_path, chunk_size=8192):
    """计算文件 SHA256 哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]

def clean_from_copies():
    """清理带 _from_ 后缀的副本文件"""
    print("🔍 扫描 _from_ 副本文件...")
    deleted = 0
    saved_mb = 0
    
    for root, dirs, files in os.walk(WORKSPACE):
        # 跳过备份和 git 目录
        if 'backups' in root or '.git' in root:
            continue
        
        for file in files:
            if '_from_' in file:
                file_path = os.path.join(root, file)
                try:
                    size_mb = os.path.getsize(file_path) / 1024 / 1024
                    os.remove(file_path)
                    deleted += 1
                    saved_mb += size_mb
                    print(f"  ✓ 删除：{file_path}")
                except Exception as e:
                    print(f"  ❌ 失败：{file_path} - {e}")
    
    print(f"✅ 删除 {deleted} 个 _from_ 副本文件 (节省 {round(saved_mb, 2)} MB)\n")
    return deleted, saved_mb

def clean_obsidian_duplicates():
    """清理 Obsidian 配置重复（保留 .obsidian/）"""
    print("🔍 扫描 Obsidian 配置重复...")
    deleted = 0
    
    obsidian_files = ['app.json', 'appearance.json', 'core.json']
    
    for root, dirs, files in os.walk(WORKSPACE):
        # 只保留 .obsidian/ 目录
        if '.obsidian' not in root or root.endswith('.obsidian'):
            continue
        
        # 跳过备份和 git
        if 'backups' in root or '.git' in root:
            continue
        
        for file in obsidian_files:
            if file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted += 1
                    print(f"  ✓ 删除：{file_path}")
                except Exception as e:
                    print(f"  ❌ 失败：{file_path} - {e}")
    
    print(f"✅ 删除 {deleted} 个 Obsidian 配置重复\n")
    return deleted

def clean_empty_dirs():
    """清理空目录"""
    print("🔍 扫描空目录...")
    deleted = 0
    
    for root, dirs, files in os.walk(WORKSPACE, topdown=False):
        if not dirs and not files:
            # 跳过 .git 和重要目录
            if '.git' in root or 'workspace' == os.path.basename(root):
                continue
            try:
                os.rmdir(root)
                deleted += 1
                print(f"  ✓ 删除目录：{root}")
            except Exception as e:
                print(f"  ❌ 失败：{root} - {e}")
    
    print(f"✅ 删除 {deleted} 个空目录\n")
    return deleted

def main():
    print("=" * 70)
    print("🧹 清理重复文件 - 安全版本")
    print(f"📂 工作区：{WORKSPACE}")
    print("=" * 70)
    print()
    
    total_deleted = 0
    total_saved = 0
    
    # 1. 清理 _from_ 副本
    deleted, saved = clean_from_copies()
    total_deleted += deleted
    total_saved += saved
    
    # 2. 清理 Obsidian 重复
    deleted = clean_obsidian_duplicates()
    total_deleted += deleted
    
    # 3. 清理空目录
    deleted = clean_empty_dirs()
    total_deleted += deleted
    
    print("=" * 70)
    print(f"✅ 清理完成！")
    print(f"   删除文件：{total_deleted} 个")
    print(f"   节省空间：{round(total_saved, 2)} MB")
    print("=" * 70)

if __name__ == '__main__':
    main()
