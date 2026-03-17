#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告存储优化系统
=================
优化报告存储空间，包括压缩、去重、归档策略等

功能:
1. 重复检测 - 识别内容相似的报告
2. 空间分析 - 分析存储空间使用情况
3. 智能归档 - 根据策略自动归档旧报告
4. 压缩建议 - 识别可压缩的大文件
5. 清理建议 - 识别可删除的低价值报告

使用:
  python report_storage.py --analyze          # 分析存储使用
  python report_storage.py --duplicates       # 查找重复报告
  python report_storage.py --optimize         # 执行优化
  python report_storage.py --archive          # 归档旧报告
  python report_storage.py --stats            # 显示统计
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path('D:/OpenClaw/workspace')
REPORTS_DIR = WORKSPACE / '21-reports'
ARCHIVE_DIR = WORKSPACE / '21-reports' / 'archive'
STORAGE_CONFIG = WORKSPACE / 'data' / 'report_storage_config.json'
STORAGE_STATE = WORKSPACE / 'data' / 'report_storage_state.json'


class ReportStorageOptimizer:
    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
    
    def _load_config(self):
        default_config = {
            'enabled': True,
            'similarity_threshold': 0.9,  # 90% 相似度视为重复
            'archive_after_days': 90,
            'delete_after_days': 365,
            'min_file_size': 1024,  # 1KB
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'keep_versions': 3,  # 保留多少个版本
            'compression_enabled': False,
            'auto_archive': True,
            'auto_delete': False,
            'important_patterns': [
                'PRODUCTION', 'COMPLETE', 'FINAL', 'SECURITY',
                'SUMMARY', 'ANNUAL', 'QUARTERLY'
            ]
        }
        
        if STORAGE_CONFIG.exists():
            with open(STORAGE_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config
    
    def _load_state(self):
        if STORAGE_STATE.exists():
            with open(STORAGE_STATE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'last_analysis': None,
            'total_size': 0,
            'total_files': 0,
            'duplicates': [],
            'archived': [],
            'deleted': []
        }
    
    def _save_state(self):
        STORAGE_STATE.parent.mkdir(parents=True, exist_ok=True)
        with open(STORAGE_STATE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def _calculate_file_hash(self, filepath):
        """计算文件哈希值"""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    
    def _calculate_content_similarity(self, content1, content2):
        """计算内容相似度 (简单 Jaccard 相似度)"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def analyze_storage(self):
        """分析存储空间使用情况"""
        print('='*60)
        print('Storage Analysis')
        print('='*60)
        
        total_size = 0
        total_files = 0
        size_by_dir = defaultdict(int)
        size_by_age = defaultdict(int)
        large_files = []
        
        now = datetime.now()
        
        for root, dirs, files in os.walk(REPORTS_DIR):
            rel_path = Path(root).relative_to(REPORTS_DIR)
            dir_name = str(rel_path) if str(rel_path) != '.' else 'root'
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                
                try:
                    stat = filepath.stat()
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    age_days = (now - mtime).days
                    
                    total_size += size
                    total_files += 1
                    size_by_dir[dir_name] += size
                    
                    # Age categorization
                    if age_days < 7:
                        size_by_age['new (<7 days)'] += size
                    elif age_days < 30:
                        size_by_age['recent (7-30 days)'] += size
                    elif age_days < 90:
                        size_by_age['active (30-90 days)'] += size
                    elif age_days < 365:
                        size_by_age['old (90-365 days)'] += size
                    else:
                        size_by_age['ancient (>365 days)'] += size
                    
                    # Large files
                    if size > 100 * 1024:  # >100KB
                        large_files.append({
                            'file': str(filepath.relative_to(WORKSPACE)),
                            'size': size,
                            'age_days': age_days
                        })
                
                except Exception as e:
                    print(f'  Error analyzing {file}: {e}')
        
        # Update state
        self.state['last_analysis'] = now.isoformat()
        self.state['total_size'] = total_size
        self.state['total_files'] = total_files
        self._save_state()
        
        # Print results
        print(f'\nTotal storage: {total_size / 1024:.1f} KB ({total_size / 1024 / 1024:.2f} MB)')
        print(f'Total files: {total_files}')
        print(f'Average file size: {total_size / total_files / 1024:.1f} KB' if total_files > 0 else 'N/A')
        
        print('\nBy directory:')
        for dir_name, size in sorted(size_by_dir.items(), key=lambda x: -x[1]):
            pct = size / total_size * 100 if total_size > 0 else 0
            print(f'  {dir_name}: {size / 1024:.1f} KB ({pct:.1f}%)')
        
        print('\nBy age:')
        for age, size in size_by_age.items():
            pct = size / total_size * 100 if total_size > 0 else 0
            print(f'  {age}: {size / 1024:.1f} KB ({pct:.1f}%)')
        
        if large_files:
            print(f'\nLarge files (>100KB): {len(large_files)}')
            for f in large_files[:10]:
                print(f'  {f["file"]} ({f["size"] / 1024:.1f} KB, {f["age_days"]} days old)')
        
        return {
            'total_size': total_size,
            'total_files': total_files,
            'size_by_dir': dict(size_by_dir),
            'size_by_age': dict(size_by_age),
            'large_files': large_files
        }
    
    def find_duplicates(self):
        """查找重复报告"""
        print('='*60)
        print('Finding Duplicates')
        print('='*60)
        
        # Group by hash
        hash_groups = defaultdict(list)
        
        for root, dirs, files in os.walk(REPORTS_DIR):
            if 'archive' in root:
                continue
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                
                try:
                    file_hash = self._calculate_file_hash(filepath)
                    hash_groups[file_hash].append(str(filepath.relative_to(WORKSPACE)))
                except Exception as e:
                    print(f'  Error hashing {file}: {e}')
        
        # Find duplicates
        duplicates = []
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                duplicates.append({
                    'hash': file_hash,
                    'files': files,
                    'count': len(files)
                })
        
        # Also check for similar content (not exact duplicates)
        print('\nChecking for similar content...')
        similar_groups = []
        
        # Get all report contents
        reports = []
        for root, dirs, files in os.walk(REPORTS_DIR):
            if 'archive' in root:
                continue
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    reports.append({
                        'file': str(filepath.relative_to(WORKSPACE)),
                        'content': content,
                        'size': len(content)
                    })
                except Exception as e:
                    pass
        
        # Check pairwise similarity
        checked = set()
        for i, report1 in enumerate(reports):
            if report1['file'] in checked:
                continue
            
            similar = [report1['file']]
            
            for j, report2 in enumerate(reports):
                if i >= j or report2['file'] in checked:
                    continue
                
                # Skip if size difference is too large
                size_ratio = min(report1['size'], report2['size']) / max(report1['size'], report2['size'])
                if size_ratio < 0.7:
                    continue
                
                similarity = self._calculate_content_similarity(report1['content'], report2['content'])
                
                if similarity >= self.config['similarity_threshold']:
                    similar.append(report2['file'])
                    checked.add(report2['file'])
            
            if len(similar) > 1:
                similar_groups.append({
                    'files': similar,
                    'count': len(similar),
                    'reason': 'content_similarity'
                })
                checked.add(report1['file'])
        
        # Update state
        self.state['duplicates'] = duplicates + similar_groups
        self._save_state()
        
        # Print results
        print(f'\nExact duplicates: {len(duplicates)} groups')
        for dup in duplicates:
            print(f'  {dup["count"]} files with hash {dup["hash"][:8]}...')
            for f in dup['files']:
                print(f'    - {f}')
        
        print(f'\nSimilar content: {len(similar_groups)} groups')
        for sim in similar_groups:
            print(f'  {sim["count"]} similar files')
            for f in sim['files']:
                print(f'    - {f}')
        
        total_waste = sum(
            (len(dup['files']) - 1) for dup in duplicates
        )
        print(f'\nPotential space savings: {total_waste} files')
        
        return {
            'exact_duplicates': duplicates,
            'similar_content': similar_groups
        }
    
    def archive_old_reports(self, dry_run=True):
        """归档旧报告"""
        print('='*60)
        print('Archiving Old Reports')
        print('='*60)
        
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        
        now = datetime.now()
        archived = 0
        skipped = 0
        
        for root, dirs, files in os.walk(REPORTS_DIR):
            if 'archive' in root:
                continue
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                
                try:
                    stat = filepath.stat()
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    age_days = (now - mtime).days
                    
                    if age_days < self.config['archive_after_days']:
                        continue
                    
                    # Check if important
                    is_important = any(
                        pattern in file.upper()
                        for pattern in self.config['important_patterns']
                    )
                    
                    if is_important:
                        print(f'Skip (important): {file} ({age_days} days)')
                        skipped += 1
                        continue
                    
                    if dry_run:
                        print(f'Would archive: {file} ({age_days} days)')
                    else:
                        dst = ARCHIVE_DIR / file
                        import shutil
                        shutil.copy2(filepath, dst)
                        print(f'Archived: {file} -> {dst}')
                    
                    archived += 1
                
                except Exception as e:
                    print(f'  Error processing {file}: {e}')
        
        # Update state
        self.state['archived'].append({
            'date': now.isoformat(),
            'count': archived,
            'skipped': skipped,
            'dry_run': dry_run
        })
        self._save_state()
        
        print(f'\nTotal archived: {archived}')
        print(f'Skipped (important): {skipped}')
        
        return {'archived': archived, 'skipped': skipped}
    
    def get_cleanup_suggestions(self):
        """获取清理建议"""
        print('='*60)
        print('Cleanup Suggestions')
        print('='*60)
        
        suggestions = []
        now = datetime.now()
        
        for root, dirs, files in os.walk(REPORTS_DIR):
            if 'archive' in root:
                continue
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                
                try:
                    stat = filepath.stat()
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    age_days = (now - mtime).days
                    size = stat.st_size
                    
                    # Old and small
                    if age_days > 180 and size < 5 * 1024:
                        suggestions.append({
                            'file': str(filepath.relative_to(WORKSPACE)),
                            'reason': 'old_and_small',
                            'age_days': age_days,
                            'size': size,
                            'priority': 'low'
                        })
                    
                    # Very old
                    if age_days > 365:
                        is_important = any(
                            pattern in file.upper()
                            for pattern in self.config['important_patterns']
                        )
                        
                        if not is_important:
                            suggestions.append({
                                'file': str(filepath.relative_to(WORKSPACE)),
                                'reason': 'very_old',
                                'age_days': age_days,
                                'size': size,
                                'priority': 'medium'
                            })
                
                except Exception as e:
                    pass
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        print(f'Total suggestions: {len(suggestions)}')
        
        by_priority = defaultdict(list)
        for s in suggestions:
            by_priority[s['priority']].append(s)
        
        for priority in ['high', 'medium', 'low']:
            items = by_priority[priority]
            if items:
                print(f'\n{priority.upper()} priority: {len(items)}')
                for s in items[:5]:
                    print(f'  {s["file"]} ({s["reason"]}, {s["age_days"]} days)')
        
        return suggestions
    
    def show_stats(self):
        """显示存储统计"""
        print('='*60)
        print('Storage Statistics')
        print('='*60)
        
        if not self.state.get('last_analysis'):
            print('No analysis data. Run --analyze first.')
            return
        
        print(f'Total storage: {self.state["total_size"] / 1024:.1f} KB')
        print(f'Total files: {self.state["total_files"]}')
        print(f'Duplicate groups: {len(self.state.get("duplicates", []))}')
        print(f'Archived reports: {len(self.state.get("archived", []))}')
        print(f'Last analysis: {self.state["last_analysis"]}')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Report Storage Optimizer')
    parser.add_argument('--analyze', action='store_true', help='Analyze storage')
    parser.add_argument('--duplicates', action='store_true', help='Find duplicates')
    parser.add_argument('--archive', action='store_true', help='Archive old reports')
    parser.add_argument('--execute', action='store_true', help='Execute (not dry run)')
    parser.add_argument('--suggestions', action='store_true', help='Get cleanup suggestions')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    optimizer = ReportStorageOptimizer()
    
    if args.analyze:
        optimizer.analyze_storage()
    elif args.duplicates:
        optimizer.find_duplicates()
    elif args.archive:
        optimizer.archive_old_reports(dry_run=not args.execute)
    elif args.suggestions:
        optimizer.get_cleanup_suggestions()
    elif args.stats:
        optimizer.show_stats()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
