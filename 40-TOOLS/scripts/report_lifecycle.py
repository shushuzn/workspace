#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告生命周期管理
=================
管理报告从创建到归档/删除的完整生命周期

阶段:
- 创建 (0-7 天): 新创建，活跃使用
- 活跃 (7-30 天): 频繁访问，高价值
- 归档 (30-90 天): 低访问，保留参考
- 删除 (>90 天): 过期，可删除 (重要报告除外)

使用:
  python report_lifecycle.py --scan          # 扫描报告状态
  python report_lifecycle.py --archive       # 执行归档
  python report_lifecycle.py --cleanup       # 清理过期报告
  python report_lifecycle.py --status        # 查看状态统计
"""

import os
import sys
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path('D:/OpenClaw/workspace')
REPORTS_DIR = WORKSPACE / '21-reports'
ARCHIVE_DIR = WORKSPACE / '21-reports' / 'archive'
LIFECYCLE_CONFIG = WORKSPACE / 'data' / 'report_lifecycle_config.json'
LIFECYCLE_STATE = WORKSPACE / 'data' / 'report_lifecycle_state.json'


class ReportLifecycleManager:
    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
    
    def _load_config(self):
        default_config = {
            'stages': {
                'new': {'days': 7, 'action': 'keep'},
                'active': {'days': 30, 'action': 'keep'},
                'archive': {'days': 90, 'action': 'archive'},
                'delete': {'days': 999, 'action': 'delete'}
            },
            'important_reports': [
                'PRODUCTION', 'COMPLETE', 'FINAL', 'SECURITY'
            ],
            'exclude_patterns': [
                'MEMORY.md', 'HEARTBEAT.md', 'SOUL.md'
            ],
            'archive_dir': str(ARCHIVE_DIR),
            'dry_run': True
        }
        
        if LIFECYCLE_CONFIG.exists():
            with open(LIFECYCLE_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config
    
    def _load_state(self):
        if LIFECYCLE_STATE.exists():
            with open(LIFECYCLE_STATE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'last_scan': None, 'reports': []}
    
    def _save_state(self):
        LIFECYCLE_STATE.parent.mkdir(parents=True, exist_ok=True)
        with open(LIFECYCLE_STATE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def scan_reports(self):
        """扫描所有报告，确定生命周期阶段"""
        print('='*60)
        print('Report Lifecycle Scan')
        print('='*60)
        
        reports = []
        now = datetime.now()
        
        for root, dirs, files in os.walk(REPORTS_DIR):
            if 'archive' in root:
                continue
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                age_days = (now - mtime).days
                
                # Determine stage
                if age_days <= self.config['stages']['new']['days']:
                    stage = 'new'
                elif age_days <= self.config['stages']['active']['days']:
                    stage = 'active'
                elif age_days <= self.config['stages']['archive']['days']:
                    stage = 'archive'
                else:
                    stage = 'delete'
                
                # Check if important
                is_important = any(pattern in file.upper() for pattern in self.config['important_reports'])
                
                report_info = {
                    'file': str(filepath.relative_to(WORKSPACE)),
                    'age_days': age_days,
                    'stage': stage,
                    'important': is_important,
                    'mtime': mtime.isoformat(),
                    'action': 'keep' if is_important else self.config['stages'][stage]['action']
                }
                
                reports.append(report_info)
        
        self.state['last_scan'] = now.isoformat()
        self.state['reports'] = reports
        self._save_state()
        
        # Print summary
        stages = {}
        for r in reports:
            stage = r['stage']
            stages[stage] = stages.get(stage, 0) + 1
        
        print(f'Total reports: {len(reports)}')
        print(f'Stages: {stages}')
        print(f'Important: {sum(1 for r in reports if r["important"])}')
        
        return reports
    
    def archive_reports(self, dry_run=True):
        """归档过期报告"""
        print('='*60)
        print('Report Archiving')
        print('='*60)
        
        if not self.state.get('reports'):
            print('No scan data. Run --scan first.')
            return
        
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        
        archived = 0
        for report in self.state['reports']:
            if report['stage'] != 'archive':
                continue
            if report['important']:
                print(f'Skip (important): {report["file"]}')
                continue
            
            src = WORKSPACE / report['file']
            if not src.exists():
                continue
            
            if dry_run:
                print(f'Would archive: {report["file"]}')
            else:
                dst = ARCHIVE_DIR / src.name
                shutil.copy2(src, dst)
                print(f'Archived: {report["file"]} -> {dst}')
            
            archived += 1
        
        print(f'Total archived: {archived}')
        return archived
    
    def cleanup_reports(self, dry_run=True):
        """清理过期报告"""
        print('='*60)
        print('Report Cleanup')
        print('='*60)
        
        if not self.state.get('reports'):
            print('No scan data. Run --scan first.')
            return
        
        deleted = 0
        for report in self.state['reports']:
            if report['stage'] != 'delete':
                continue
            if report['important']:
                print(f'Skip (important): {report["file"]}')
                continue
            
            src = WORKSPACE / report['file']
            if not src.exists():
                continue
            
            if dry_run:
                print(f'Would delete: {report["file"]}')
            else:
                src.unlink()
                print(f'Deleted: {report["file"]}')
            
            deleted += 1
        
        print(f'Total deleted: {deleted}')
        return deleted
    
    def show_status(self):
        """显示生命周期状态统计"""
        print('='*60)
        print('Report Lifecycle Status')
        print('='*60)
        
        if not self.state.get('reports'):
            print('No scan data. Run --scan first.')
            return
        
        stages = {}
        important = 0
        total_size = 0
        
        for report in self.state['reports']:
            stage = report['stage']
            stages[stage] = stages.get(stage, 0) + 1
            if report['important']:
                important += 1
            
            filepath = WORKSPACE / report['file']
            if filepath.exists():
                total_size += filepath.stat().st_size
        
        print(f'Total reports: {len(self.state["reports"])}')
        print(f'Stages:')
        for stage, count in sorted(stages.items()):
            print(f'  {stage}: {count}')
        print(f'Important reports: {important}')
        print(f'Total size: {total_size / 1024:.1f} KB')
        print(f'Last scan: {self.state["last_scan"]}')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Report Lifecycle Manager')
    parser.add_argument('--scan', action='store_true', help='Scan reports')
    parser.add_argument('--archive', action='store_true', help='Archive old reports')
    parser.add_argument('--cleanup', action='store_true', help='Delete expired reports')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--execute', action='store_true', help='Execute (not dry run)')
    
    args = parser.parse_args()
    
    manager = ReportLifecycleManager()
    
    if args.scan:
        manager.scan_reports()
    elif args.archive:
        manager.archive_reports(dry_run=not args.execute)
    elif args.cleanup:
        manager.cleanup_reports(dry_run=not args.execute)
    elif args.status:
        manager.show_status()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
