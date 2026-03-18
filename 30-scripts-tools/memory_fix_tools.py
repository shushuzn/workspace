#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Fix Tools - Consolidated memory repair utilities

整合了以下工具的功能:
- fix_memory_complete.py
- memory_fix_auto.py
- memory_fix_ultimate.py
- fix_memory_encoding_deep.py

功能:
1. 自动修复记忆文件编码问题
2. 修复损坏的记忆文件
3. 批量修复多个文件
4. 深度扫描和修复
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
BACKUP_DIR = WORKSPACE / '99-backups' / 'memory-fixes'


def create_backup(file_path: Path) -> Path:
    """Create backup before fixing"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = BACKUP_DIR / backup_name
    shutil.copy2(file_path, backup_path)
    return backup_path


def fix_encoding(file_path: Path) -> Tuple[bool, str]:
    """Fix file encoding to UTF-8"""
    try:
        # Try to read with different encodings
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        content = None
        used_encoding = None
        
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                used_encoding = enc
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if content is None:
            return False, "无法读取文件"
        
        # If already UTF-8, no need to fix
        if used_encoding == 'utf-8':
            return True, "已经是 UTF-8 编码"
        
        # Create backup
        create_backup(file_path)
        
        # Rewrite as UTF-8
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"从 {used_encoding} 修复为 UTF-8"
        
    except Exception as e:
        return False, f"修复失败：{str(e)}"


def fix_corrupted_file(file_path: Path) -> Tuple[bool, str]:
    """Fix corrupted memory file"""
    try:
        # Check if file exists
        if not file_path.exists():
            return False, "文件不存在"
        
        # Check file size
        if file_path.stat().st_size == 0:
            return False, "文件为空"
        
        # Try to read and validate
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common corruption patterns
            if '\x00' in content:
                # Remove null bytes
                content = content.replace('\x00', '')
                create_backup(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, "移除空字节修复"
            
            # Check for broken line endings
            if '\r\r' in content:
                content = content.replace('\r\r', '\r\n')
                create_backup(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, "修复换行符"
            
            return True, "文件正常，无需修复"
            
        except UnicodeDecodeError:
            # Encoding issue, delegate to fix_encoding
            return fix_encoding(file_path)
            
    except Exception as e:
        return False, f"修复失败：{str(e)}"


def scan_and_fix(memory_dir: Path = None, dry_run: bool = False) -> Dict:
    """Scan memory directory and fix all issues"""
    if memory_dir is None:
        memory_dir = MEMORY_DIR
    
    results = {
        'scanned': 0,
        'fixed': 0,
        'failed': 0,
        'backups': [],
        'details': []
    }
    
    if not memory_dir.exists():
        return {'error': f'目录不存在：{memory_dir}'}
    
    # Scan all .md files
    md_files = list(memory_dir.glob('*.md'))
    
    print(f"🔍 扫描记忆文件：{len(md_files)} 个")
    print(f"📁 目录：{memory_dir}")
    print()
    
    for file_path in md_files:
        results['scanned'] += 1
        
        # Check encoding
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
            # UTF-8 OK, check corruption
            success, msg = fix_corrupted_file(file_path)
        except UnicodeDecodeError:
            # Encoding issue
            if dry_run:
                msg = "需要修复编码"
                success = False
            else:
                success, msg = fix_encoding(file_path)
        
        if success:
            results['fixed'] += 1
        else:
            results['failed'] += 1
        
        results['details'].append({
            'file': file_path.name,
            'success': success,
            'message': msg
        })
        
        # Print progress
        status = '✅' if success else '❌'
        print(f"{status} {file_path.name}: {msg}")
    
    print()
    print("=" * 60)
    print("修复总结:")
    print(f"  扫描：{results['scanned']} 个文件")
    print(f"  成功：{results['fixed']} 个")
    print(f"  失败：{results['failed']} 个")
    print(f"  备份：{len(results['backups'])} 个")
    print("=" * 60)
    
    return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Fix Tools')
    parser.add_argument('--scan', action='store_true', help='Scan and fix all memory files')
    parser.add_argument('--file', type=str, help='Fix specific file')
    parser.add_argument('--encoding', type=str, help='Fix encoding of specific file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Memory Fix Tools - 记忆修复工具")
    print("=" * 60)
    print()
    
    if args.scan:
        results = scan_and_fix(dry_run=args.dry_run)
        return 0 if results.get('failed', 0) == 0 else 1
    
    elif args.file:
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = MEMORY_DIR / file_path
        
        print(f"🔧 修复文件：{file_path.name}")
        success, msg = fix_corrupted_file(file_path)
        print(f"{'✅' if success else '❌'} {msg}")
        return 0 if success else 1
    
    elif args.encoding:
        file_path = Path(args.encoding)
        if not file_path.is_absolute():
            file_path = MEMORY_DIR / file_path
        
        print(f"🔧 修复编码：{file_path.name}")
        success, msg = fix_encoding(file_path)
        print(f"{'✅' if success else '❌'} {msg}")
        return 0 if success else 1
    
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
