#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Utils - Consolidated memory utility functions

整合了以下工具的功能:
- memory_util_audit.py
- memory_util_health.py
- memory_util_indexer.py

功能:
1. 记忆文件审计 (audit)
2. 记忆系统健康检查 (health)
3. 记忆文件索引 (indexer)
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'


def audit_memory(memory_dir: Path = None) -> Dict:
    """Audit memory files for quality and consistency"""
    if memory_dir is None:
        memory_dir = MEMORY_DIR
    
    results = {
        'total_files': 0,
        'total_size': 0,
        'encoding_issues': 0,
        'empty_files': 0,
        'large_files': [],
        'daily_notes': 0,
        'special_files': [],
        'issues': []
    }
    
    if not memory_dir.exists():
        return {'error': f'目录不存在：{memory_dir}'}
    
    md_files = list(memory_dir.glob('*.md'))
    results['total_files'] = len(md_files)
    
    for file_path in md_files:
        try:
            size = file_path.stat().st_size
            results['total_size'] += size
            
            # Check empty files
            if size == 0:
                results['empty_files'] += 1
                results['issues'].append(f"空文件：{file_path.name}")
            
            # Check large files (>1MB)
            if size > 1024 * 1024:
                results['large_files'].append({
                    'name': file_path.name,
                    'size': size
                })
            
            # Check encoding
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check content
                if file_path.name.startswith('2026-'):
                    results['daily_notes'] += 1
                elif file_path.name in ['MEMORY.md', 'HEARTBEAT.md', 'USER.md']:
                    results['special_files'].append(file_path.name)
                    
            except UnicodeDecodeError:
                results['encoding_issues'] += 1
                results['issues'].append(f"编码问题：{file_path.name}")
                
        except Exception as e:
            results['issues'].append(f"读取失败 {file_path.name}: {str(e)}")
    
    return results


def health_check(memory_dir: Path = None) -> Dict:
    """Check memory system health"""
    if memory_dir is None:
        memory_dir = MEMORY_DIR
    
    health = {
        'status': 'healthy',
        'score': 100,
        'checks': {},
        'recommendations': []
    }
    
    if not memory_dir.exists():
        health['status'] = 'critical'
        health['score'] = 0
        health['checks']['directory_exists'] = False
        return health
    
    health['checks']['directory_exists'] = True
    
    # Check 1: MEMORY.md exists
    memory_md = memory_dir / 'MEMORY.md'
    if memory_md.exists():
        health['checks']['memory_md_exists'] = True
    else:
        health['checks']['memory_md_exists'] = False
        health['score'] -= 20
        health['recommendations'].append("创建 MEMORY.md 文件")
    
    # Check 2: Recent daily notes
    today = datetime.now().strftime('%Y-%m-%d')
    today_file = memory_dir / f"{today}.md"
    if today_file.exists():
        health['checks']['today_note_exists'] = True
    else:
        health['checks']['today_note_exists'] = False
        health['score'] -= 10
        health['recommendations'].append(f"创建今日笔记：{today}.md")
    
    # Check 3: Count files
    md_files = list(memory_dir.glob('*.md'))
    file_count = len(md_files)
    health['checks']['file_count'] = file_count
    
    if file_count < 10:
        health['score'] -= 10
        health['recommendations'].append("记忆文件较少，建议增加日常笔记")
    
    # Check 4: Check for encoding issues
    encoding_issues = 0
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError:
            encoding_issues += 1
    
    health['checks']['encoding_issues'] = encoding_issues
    if encoding_issues > 0:
        health['score'] -= (encoding_issues * 5)
        health['recommendations'].append(f"修复 {encoding_issues} 个编码问题文件")
    
    # Determine status
    if health['score'] >= 90:
        health['status'] = 'healthy'
    elif health['score'] >= 70:
        health['status'] = 'warning'
    else:
        health['status'] = 'critical'
    
    return health


def build_index(memory_dir: Path = None, output_file: str = None) -> Dict:
    """Build index of all memory files"""
    if memory_dir is None:
        memory_dir = MEMORY_DIR
    
    index = {
        'generated': datetime.now().isoformat(),
        'total_files': 0,
        'categories': defaultdict(list),
        'files': []
    }
    
    if not memory_dir.exists():
        return {'error': f'目录不存在：{memory_dir}'}
    
    md_files = sorted(memory_dir.glob('*.md'))
    index['total_files'] = len(md_files)
    
    for file_path in md_files:
        try:
            stat = file_path.stat()
            file_info = {
                'name': file_path.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'hash': hashlib.md5(file_path.read_bytes()).hexdigest()
            }
            
            # Categorize
            if file_path.name.startswith('2026-'):
                category = 'daily_notes'
            elif file_path.name.startswith('2025-'):
                category = 'daily_notes'
            elif 'MEMORY' in file_path.name.upper():
                category = 'core_memory'
            elif 'USER' in file_path.name.upper():
                category = 'user_docs'
            elif 'HEARTBEAT' in file_path.name.upper():
                category = 'heartbeat'
            else:
                category = 'other'
            
            index['categories'][category].append(file_path.name)
            index['files'].append(file_info)
            
        except Exception as e:
            index['files'].append({
                'name': file_path.name,
                'error': str(e)
            })
    
    # Convert defaultdict to dict for JSON serialization
    index['categories'] = dict(index['categories'])
    
    # Save to file if specified
    if output_file:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = WORKSPACE / '20-data-reports' / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        print(f"✅ 索引已保存到：{output_path}")
    
    return index


def print_report(data: Dict, title: str):
    """Pretty print report"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()
    
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        elif isinstance(value, list):
            print(f"{key}: {len(value)} 项")
            for item in value[:5]:  # Show first 5
                print(f"  - {item}")
            if len(value) > 5:
                print(f"  ... 还有 {len(value)-5} 项")
        else:
            print(f"{key}: {value}")
    
    print()
    print("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Utils')
    parser.add_argument('--audit', action='store_true', help='Audit memory files')
    parser.add_argument('--health', action='store_true', help='Check memory health')
    parser.add_argument('--index', action='store_true', help='Build memory index')
    parser.add_argument('--output', type=str, help='Output file for index')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Memory Utils - 记忆工具集")
    print("=" * 60)
    
    if args.audit:
        results = audit_memory()
        print_report(results, "记忆审计报告")
        return 0
    
    elif args.health:
        health = health_check()
        print_report(health, "记忆健康检查")
        
        # Visual status
        status_icons = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌'
        }
        print(f"\n状态：{status_icons.get(health['status'], '?')} {health['status'].upper()}")
        print(f"评分：{health['score']}/100")
        return 0 if health['score'] >= 70 else 1
    
    elif args.index:
        output = args.output or 'memory-index.json'
        index = build_index(output_file=output)
        print_report(index, "记忆文件索引")
        print(f"\n总文件数：{index.get('total_files', 0)}")
        print(f"分类数：{len(index.get('categories', {}))}")
        return 0
    
    else:
        parser.print_help()
        print("\n示例:")
        print("  py memory_utils.py --audit")
        print("  py memory_utils.py --health")
        print("  py memory_utils.py --index --output memory-index.json")
        return 0


if __name__ == '__main__':
    sys.exit(main())
