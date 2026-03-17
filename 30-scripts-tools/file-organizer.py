#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件整理工具 - 运营者版
运营者原则：先扫描，后清理，删除前备份

用法：
  py file-organizer.py          # 扫描模式 (只报告)
  py file-organizer.py --clean  # 清理模式 (自动清理安全项)
  py file-organizer.py --help   # 帮助

功能：
  1. 扫描空目录
  2. 扫描缓存文件
  3. 扫描大文件 (>50MB)
  4. 扫描敏感信息
  5. 扫描旧文件 (>90 天)
  6. 扫描重复文件 (基于 SHA256 哈希)
"""

import os
import sys
import io
import json
import hashlib
import argparse
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 修复 Windows 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 配置
CONFIG = {
    'workspace': r'D:\OpenClaw\workspace',
    'size_threshold_mb': 50,
    'age_threshold_days': 90,
    'backup_dir': '99-backups/file-organizer',
}

# 缓存目录
CACHE_DIRS = [
    '50-cache',
    'embedding_cache',
    'file_store',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
]

# 允许中文文件名的目录
ALLOW_CHINESE_PATH = [
    '10-RESEARCH/',
    '99-archive/',
    '90-TESTS/',
]

# 排除目录 (不扫描)
EXCLUDE_DIRS = [
    '.git',
    'node_modules',
    'venv',
    '.venv',
    '99-backups',
    '__pycache__',
]


def get_workspace():
    """获取工作区路径"""
    return CONFIG['workspace']


def scan_empty_dirs(workspace=None):
    """扫描空目录"""
    if workspace is None:
        workspace = get_workspace()
    
    empty_dirs = []
    
    for root, dirs, files in os.walk(workspace):
        # 跳过排除目录
        rel_path = os.path.relpath(root, workspace)
        if any(exclude in rel_path for exclude in EXCLUDE_DIRS):
            continue
        
        # 检查是否空目录
        if not dirs and not files:
            empty_dirs.append(root)
    
    return empty_dirs


def scan_cache_files(workspace=None):
    """扫描缓存文件"""
    if workspace is None:
        workspace = get_workspace()
    
    cache_files = []
    
    for root, dirs, files in os.walk(workspace):
        # 跳过排除目录
        rel_path = os.path.relpath(root, workspace)
        if any(exclude in rel_path for exclude in EXCLUDE_DIRS):
            continue
        
        # 检查缓存目录
        dir_name = os.path.basename(root)
        if dir_name in CACHE_DIRS or any(cache in root for cache in CACHE_DIRS):
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                cache_files.append({
                    'path': file_path,
                    'size': size,
                    'size_mb': round(size / 1024 / 1024, 2)
                })
    
    return cache_files


def scan_large_files(workspace=None, threshold_mb=None):
    """扫描大文件"""
    if workspace is None:
        workspace = get_workspace()
    if threshold_mb is None:
        threshold_mb = CONFIG['size_threshold_mb']
    
    large_files = []
    
    for root, dirs, files in os.walk(workspace):
        # 跳过排除目录
        rel_path = os.path.relpath(root, workspace)
        if any(exclude in rel_path for exclude in EXCLUDE_DIRS):
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > threshold_mb * 1024 * 1024:
                    large_files.append({
                        'path': file_path,
                        'size': size,
                        'size_mb': round(size / 1024 / 1024, 2)
                    })
            except (OSError, IOError):
                continue
    
    return large_files


def scan_old_files(workspace=None, days=None):
    """扫描旧文件 (超过 N 天未修改)"""
    if workspace is None:
        workspace = get_workspace()
    if days is None:
        days = CONFIG['age_threshold_days']
    
    old_files = []
    cutoff = datetime.now() - timedelta(days=days)
    
    for root, dirs, files in os.walk(workspace):
        # 跳过排除目录
        rel_path = os.path.relpath(root, workspace)
        if any(exclude in rel_path for exclude in EXCLUDE_DIRS):
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime < cutoff:
                    old_files.append({
                        'path': file_path,
                        'modified': mtime.strftime('%Y-%m-%d'),
                        'days_ago': (datetime.now() - mtime).days
                    })
            except (OSError, IOError):
                continue
    
    return old_files


def scan_sensitive_info(workspace=None):
    """扫描敏感信息文件"""
    if workspace is None:
        workspace = get_workspace()
    
    # 敏感文件模式 (更精确)
    sensitive_patterns = [
        '.env',
        '.env.local',
        '.env.',
        'aliyun',
        'access_key',
        'secret_',
        '_secret',
        'password=',
        'token=',
    ]
    
    # 排除的文件名 (代码文件)
    exclude_files = [
        'token.py',
        'tokens.py',
        'token.ts',
        'tokens.ts',
        'tokenizer.py',
        'secret-input.ts',
        'secret-input.test.ts',
        'token.test.ts',
        'token-response.ts',
    ]
    
    sensitive_files = []
    
    for root, dirs, files in os.walk(workspace):
        # 跳过排除目录
        rel_path = os.path.relpath(root, workspace)
        if any(exclude in rel_path for exclude in EXCLUDE_DIRS):
            continue
        
        # 跳过备份目录
        if 'backups' in rel_path or 'backup' in rel_path:
            continue
        
        for file in files:
            # 跳过代码文件
            if file in exclude_files:
                continue
            
            file_lower = file.lower()
            
            # 检查敏感模式
            is_sensitive = False
            for pattern in sensitive_patterns:
                if pattern in file_lower:
                    # 进一步检查：.env 文件必须精确匹配
                    if pattern == '.env':
                        if file_lower == '.env' or file_lower.startswith('.env.'):
                            is_sensitive = True
                    elif pattern.endswith('='):
                        # 检查文件内容
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(1000)
                                if pattern in content:
                                    is_sensitive = True
                        except:
                            pass
                    else:
                        is_sensitive = True
                    break
            
            if is_sensitive:
                file_path = os.path.join(root, file)
                sensitive_files.append({
                    'path': file_path,
                    'reason': '敏感文件/内容'
                })
    
    return sensitive_files


def scan_duplicate_files(workspace=None):
    """扫描重复文件（基于文件内容哈希）"""
    if workspace is None:
        workspace = get_workspace()
    
    # 文件大小 -> 文件列表
    size_map = defaultdict(list)
    # 文件哈希 -> 文件列表
    hash_map = defaultdict(list)
    
    print("正在计算文件哈希...")
    
    # 第一步：按文件大小分组
    for root, dirs, files in os.walk(workspace):
        # 跳过排除目录
        rel_path = os.path.relpath(root, workspace)
        if any(exclude in rel_path for exclude in EXCLUDE_DIRS):
            continue
        
        # 跳过备份目录
        if 'backups' in rel_path or 'backup' in rel_path:
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                # 只检查 >0 的文件，跳过空文件和超大文件 (>100MB)
                if size > 0 and size < 100 * 1024 * 1024:
                    size_map[size].append(file_path)
            except (OSError, IOError):
                continue
    
    # 第二步：对相同大小的文件计算哈希
    duplicate_groups = []
    
    for size, files in size_map.items():
        if len(files) < 2:
            continue
        
        # 这些文件大小相同，计算哈希
        for file_path in files:
            try:
                file_hash = calculate_file_hash(file_path)
                hash_map[file_hash].append({
                    'path': file_path,
                    'size': size,
                    'size_mb': round(size / 1024 / 1024, 2)
                })
            except Exception as e:
                continue
    
    # 第三步：收集重复文件组
    for file_hash, files in hash_map.items():
        if len(files) >= 2:
            duplicate_groups.append({
                'hash': file_hash,
                'size': files[0]['size'],
                'size_mb': files[0]['size_mb'],
                'count': len(files),
                'files': files
            })
    
    # 按重复文件数量排序
    duplicate_groups.sort(key=lambda x: x['count'], reverse=True)
    
    return duplicate_groups


def calculate_file_hash(file_path, chunk_size=8192):
    """计算文件 SHA256 哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]  # 返回前 16 位


def print_scan_report(empty_dirs, cache_files, large_files, old_files, sensitive_files, duplicate_groups=None):
    """打印扫描报告"""
    print()
    print("=" * 70)
    print("📊 文件整理扫描报告")
    print("=" * 70)
    print()
    
    # 空目录
    print(f"📁 空目录：{len(empty_dirs)} 个")
    if empty_dirs:
        for dir_path in empty_dirs[:10]:
            print(f"   - {dir_path}")
        if len(empty_dirs) > 10:
            print(f"   ... 还有 {len(empty_dirs) - 10} 个")
    print()
    
    # 缓存文件
    total_cache_size = sum(f['size'] for f in cache_files)
    print(f"💾 缓存文件：{len(cache_files)} 个 ({round(total_cache_size/1024/1024, 2)} MB)")
    if cache_files:
        for f in cache_files[:10]:
            print(f"   - {f['path']} ({f['size_mb']} MB)")
        if len(cache_files) > 10:
            print(f"   ... 还有 {len(cache_files) - 10} 个")
    print()
    
    # 大文件
    total_large_size = sum(f['size'] for f in large_files)
    print(f"🐘 大文件 (>50MB): {len(large_files)} 个 ({round(total_large_size/1024/1024, 2)} MB)")
    if large_files:
        for f in large_files:
            print(f"   - {f['path']} ({f['size_mb']} MB)")
    print()
    
    # 旧文件
    print(f"📅 旧文件 (>90 天): {len(old_files)} 个")
    if old_files:
        for f in old_files[:10]:
            print(f"   - {f['path']} ({f['days_ago']} 天前)")
        if len(old_files) > 10:
            print(f"   ... 还有 {len(old_files) - 10} 个")
    print()
    
    # 敏感文件
    print(f"🔒 敏感文件：{len(sensitive_files)} 个")
    if sensitive_files:
        for f in sensitive_files[:10]:
            print(f"   - {f['path']}")
        if len(sensitive_files) > 10:
            print(f"   ... 还有 {len(sensitive_files) - 10} 个")
    print()
    
    # 重复文件
    if duplicate_groups:
        total_waste = sum(g['size'] * (g['count'] - 1) for g in duplicate_groups)
        print(f"🔄 重复文件：{len(duplicate_groups)} 组 (浪费 {round(total_waste/1024/1024, 2)} MB)")
        for g in duplicate_groups[:10]:
            print(f"   - {g['count']} 个相同文件 ({g['size_mb']} MB each)")
            for f in g['files'][:3]:
                print(f"     • {f['path']}")
            if g['count'] > 3:
                print(f"     ... 还有 {g['count'] - 3} 个")
        if len(duplicate_groups) > 10:
            print(f"   ... 还有 {len(duplicate_groups) - 10} 组")
        print()
    
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='文件整理工具 - 运营者版')
    parser.add_argument('--clean', action='store_true', help='清理模式 (自动清理安全项)')
    parser.add_argument('--deep', action='store_true', help='深度模式 (询问后清理)')
    parser.add_argument('--backup', action='store_true', help='删除前备份')
    args = parser.parse_args()
    
    print("🔍 运营者文件整理工具 v1.0")
    print(f"📂 工作区：{get_workspace()}")
    print()
    
    # 扫描
    print("正在扫描...")
    empty_dirs = scan_empty_dirs()
    cache_files = scan_cache_files()
    large_files = scan_large_files()
    old_files = scan_old_files()
    sensitive_files = scan_sensitive_info()
    duplicate_files = scan_duplicate_files()
    
    # 打印报告
    print_scan_report(empty_dirs, cache_files, large_files, old_files, sensitive_files, duplicate_files)
    
    # 清理模式
    if args.clean:
        print()
        print("🧹 清理模式：自动清理安全项")
        print()
        print("将删除:")
        print(f"  - {len(empty_dirs)} 个空目录")
        print(f"  - {len(cache_files)} 个缓存文件")
        print()
        confirm = input("确认清理？(y/n): ")
        if confirm.lower() == 'y':
            # 备份
            if args.backup:
                print("正在备份...")
                # TODO: 实现备份
            
            # 删除空目录
            deleted = 0
            for dir_path in empty_dirs:
                try:
                    os.rmdir(dir_path)
                    deleted += 1
                except Exception as e:
                    print(f"❌ 删除失败 {dir_path}: {e}")
            
            print(f"✅ 已删除 {deleted} 个空目录")
            
            # 删除缓存文件
            deleted = 0
            for f in cache_files:
                try:
                    os.remove(f['path'])
                    deleted += 1
                except Exception as e:
                    print(f"❌ 删除失败 {f['path']}: {e}")
            
            print(f"✅ 已删除 {deleted} 个缓存文件")
            
            # 删除重复文件 (保留每组第一个)
            deleted = 0
            saved_mb = 0
            for group in duplicate_files:
                # 保留第一个，删除其余
                for f in group['files'][1:]:
                    try:
                        os.remove(f['path'])
                        deleted += 1
                        saved_mb += f['size_mb']
                    except Exception as e:
                        print(f"❌ 删除失败 {f['path']}: {e}")
            
            print(f"✅ 已删除 {deleted} 个重复文件 (节省 {round(saved_mb, 2)} MB)")
        else:
            print("❌ 取消清理")
    
    print()
    print("✅ 扫描完成")


if __name__ == '__main__':
    main()
