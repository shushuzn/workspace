#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告访问控制系统
=================
管理报告的访问权限、敏感报告保护、访问日志等

功能:
1. 访问控制 - 基于角色的访问控制 (RBAC)
2. 敏感报告 - 识别和保护敏感报告
3. 访问日志 - 记录所有访问尝试
4. 权限审计 - 审计权限使用情况
5. 加密建议 - 识别需要加密的报告

使用:
  python report_access.py --check "report.md"        # 检查访问权限
  python report_access.py --classify                # 分类敏感报告
  python report_access.py --audit                   # 审计访问日志
  python report_access.py --protect "pattern"       # 保护匹配的报告
  python report_access.py --stats                   # 显示统计
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps

WORKSPACE = Path('D:/OpenClaw/workspace')
REPORTS_DIR = WORKSPACE / '21-reports'
ACCESS_CONFIG = WORKSPACE / 'data' / 'report_access_config.json'
ACCESS_LOGS = WORKSPACE / 'data' / 'report_access_logs.json'
PROTECTED_REPORTS = WORKSPACE / 'data' / 'protected_reports.json'


# 访问级别
class AccessLevel:
    PUBLIC = 'public'           # 所有人可访问
    INTERNAL = 'internal'       # 内部人员可访问
    CONFIDENTIAL = 'confidential'  # 机密，仅授权人员
    RESTRICTED = 'restricted'   # 受限，仅特定人员


class ReportAccessController:
    def __init__(self, current_user='default'):
        self.config = self._load_config()
        self.logs = self._load_logs()
        self.protected = self._load_protected()
        self.current_user = current_user
    
    def _load_config(self):
        default_config = {
            'enabled': True,
            'default_level': AccessLevel.PUBLIC,
            'sensitive_patterns': [
                'SECURITY', 'PASSWORD', 'SECRET', 'PRIVATE',
                'CREDENTIAL', 'API_KEY', 'TOKEN', 'AUTH'
            ],
            'confidential_patterns': [
                'FINANCIAL', 'LEGAL', 'HR', 'PERSONNEL',
                'SALARY', 'COMPENSATION', 'REVIEW'
            ],
            'restricted_patterns': [
                'ADMIN', 'ROOT', 'SYSTEM', 'BACKUP'
            ],
            'auto_classify': True,
            'log_access': True,
            'log_retention_days': 90,
            'users': {
                'default': {
                    'role': 'user',
                    'access_levels': [AccessLevel.PUBLIC, AccessLevel.INTERNAL]
                },
                'admin': {
                    'role': 'admin',
                    'access_levels': [AccessLevel.PUBLIC, AccessLevel.INTERNAL, 
                                     AccessLevel.CONFIDENTIAL, AccessLevel.RESTRICTED]
                }
            }
        }
        
        if ACCESS_CONFIG.exists():
            with open(ACCESS_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config
    
    def _load_logs(self):
        if ACCESS_LOGS.exists():
            with open(ACCESS_LOGS, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'logs': [], 'total_access': 0, 'denied_access': 0}
    
    def _save_logs(self):
        # Clean old logs
        cutoff = datetime.now() - timedelta(days=self.config.get('log_retention_days', 90))
        self.logs['logs'] = [
            log for log in self.logs['logs']
            if datetime.fromisoformat(log['timestamp']) > cutoff
        ]
        
        ACCESS_LOGS.parent.mkdir(parents=True, exist_ok=True)
        with open(ACCESS_LOGS, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
    
    def _load_protected(self):
        if PROTECTED_REPORTS.exists():
            with open(PROTECTED_REPORTS, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'protected': [], 'classifications': {}}
    
    def _save_protected(self):
        PROTECTED_REPORTS.parent.mkdir(parents=True, exist_ok=True)
        with open(PROTECTED_REPORTS, 'w', encoding='utf-8') as f:
            json.dump(self.protected, f, indent=2, ensure_ascii=False)
    
    def _log_access(self, filepath, user, allowed, reason=''):
        """记录访问日志"""
        if not self.config.get('log_access', True):
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': str(filepath),
            'user': user,
            'allowed': allowed,
            'reason': reason
        }
        
        self.logs['logs'].append(log_entry)
        self.logs['total_access'] += 1
        if not allowed:
            self.logs['denied_access'] += 1
        
        self._save_logs()
    
    def classify_report(self, filepath):
        """自动分类报告敏感度"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            filepath = WORKSPACE / filepath
        
        if not filepath.exists():
            return None
        
        filename = filepath.name.upper()
        
        # Check patterns
        for pattern in self.config['restricted_patterns']:
            if pattern in filename:
                return AccessLevel.RESTRICTED
        
        for pattern in self.config['confidential_patterns']:
            if pattern in filename:
                return AccessLevel.CONFIDENTIAL
        
        for pattern in self.config['sensitive_patterns']:
            if pattern in filename:
                return AccessLevel.INTERNAL
        
        return AccessLevel.PUBLIC
    
    def protect_report(self, filepath, level=AccessLevel.CONFIDENTIAL, authorized_users=None):
        """保护报告"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            filepath = WORKSPACE / filepath
        
        if not filepath.exists():
            print(f'Report not found: {filepath}')
            return False
        
        filepath_str = str(filepath.relative_to(WORKSPACE))
        
        # Add to protected list
        protection = {
            'file': filepath_str,
            'level': level,
            'authorized_users': authorized_users or ['admin'],
            'protected_at': datetime.now().isoformat(),
            'protected_by': self.current_user
        }
        
        # Check if already protected
        existing = None
        for p in self.protected['protected']:
            if p['file'] == filepath_str:
                existing = p
                break
        
        if existing:
            existing['level'] = level
            existing['authorized_users'] = authorized_users or ['admin']
            existing['updated_at'] = datetime.now().isoformat()
            print(f'Updated protection: {filepath_str} -> {level}')
        else:
            self.protected['protected'].append(protection)
            print(f'Protected: {filepath_str} at {level}')
        
        self.protected['classifications'][filepath_str] = level
        self._save_protected()
        
        return True
    
    def check_access(self, filepath, user=None):
        """检查访问权限"""
        user = user or self.current_user
        filepath = Path(filepath)
        
        if not filepath.exists():
            filepath = WORKSPACE / filepath
        
        if not filepath.exists():
            self._log_access(str(filepath), user, False, 'File not found')
            return False
        
        filepath_str = str(filepath.relative_to(WORKSPACE))
        
        # Get user info
        user_info = self.config['users'].get(user, self.config['users']['default'])
        user_levels = user_info.get('access_levels', [AccessLevel.PUBLIC])
        
        # Check if report is protected
        protection = None
        for p in self.protected['protected']:
            if p['file'] == filepath_str:
                protection = p
                break
        
        # If not protected, classify automatically
        if not protection:
            if self.config.get('auto_classify', True):
                level = self.classify_report(filepath)
                if level != AccessLevel.PUBLIC:
                    self.protect_report(filepath, level)
                    protection = self.protected['protected'][-1]
        
        # Check access
        if protection:
            required_level = protection['level']
            
            # Check if user has required level
            if required_level not in user_levels:
                self._log_access(filepath_str, user, False, f'Insufficient level: {user_info["role"]} < {required_level}')
                return False
            
            # Check if user is authorized
            if user not in protection.get('authorized_users', []):
                if user_info['role'] != 'admin':
                    self._log_access(filepath_str, user, False, 'Not authorized')
                    return False
        
        # Access granted
        self._log_access(filepath_str, user, True, 'Access granted')
        return True
    
    def auto_classify_all(self):
        """自动分类所有报告"""
        print('='*60)
        print('Auto-Classifying Reports')
        print('='*60)
        
        classified = 0
        
        for root, dirs, files in os.walk(REPORTS_DIR):
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                level = self.classify_report(filepath)
                
                if level != AccessLevel.PUBLIC:
                    self.protect_report(filepath, level, ['admin'])
                    classified += 1
                    print(f'  {file} -> {level}')
        
        print(f'\nTotal classified: {classified}')
        return classified
    
    def audit_logs(self, days=7):
        """审计访问日志"""
        print('='*60)
        print(f'Access Audit (Last {days} days)')
        print('='*60)
        
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_logs = [
            log for log in self.logs['logs']
            if datetime.fromisoformat(log['timestamp']) > cutoff
        ]
        
        if not recent_logs:
            print('No recent access logs')
            return
        
        # Statistics
        total = len(recent_logs)
        denied = sum(1 for log in recent_logs if not log['allowed'])
        
        # By user
        by_user = {}
        for log in recent_logs:
            user = log['user']
            by_user[user] = by_user.get(user, 0) + 1
        
        # By file
        by_file = {}
        for log in recent_logs:
            file = log['file']
            by_file[file] = by_file.get(file, 0) + 1
        
        # Denied attempts
        denied_attempts = [log for log in recent_logs if not log['allowed']]
        
        print(f'\nTotal access: {total}')
        print(f'Denied access: {denied} ({denied/total*100:.1f}%)')
        
        print(f'\nBy user:')
        for user, count in sorted(by_user.items(), key=lambda x: -x[1])[:10]:
            print(f'  {user}: {count}')
        
        print(f'\nMost accessed files:')
        for file, count in sorted(by_file.items(), key=lambda x: -x[1])[:10]:
            print(f'  {file}: {count}')
        
        if denied_attempts:
            print(f'\nDenied attempts:')
            for log in denied_attempts[:10]:
                print(f'  {log["timestamp"][:10]} - {log["file"]} ({log["user"]}): {log["reason"]}')
        
        return {
            'total': total,
            'denied': denied,
            'by_user': by_user,
            'by_file': by_file
        }
    
    def show_stats(self):
        """显示访问统计"""
        print('='*60)
        print('Access Control Statistics')
        print('='*60)
        
        protected_count = len(self.protected.get('protected', []))
        classifications = self.protected.get('classifications', {})
        
        # Count by level
        by_level = {}
        for file, level in classifications.items():
            by_level[level] = by_level.get(level, 0) + 1
        
        print(f'Protected reports: {protected_count}')
        print(f'Classifications:')
        for level, count in sorted(by_level.items()):
            print(f'  {level}: {count}')
        
        print(f'\nAccess logs:')
        print(f'  Total access: {self.logs.get("total_access", 0)}')
        print(f'  Denied access: {self.logs.get("denied_access", 0)}')
        
        if self.logs.get('logs'):
            last_log = self.logs['logs'][-1]
            print(f'  Last access: {last_log["timestamp"]}')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Report Access Controller')
    parser.add_argument('--check', type=str, help='Check access for a report')
    parser.add_argument('--classify', action='store_true', help='Auto-classify all reports')
    parser.add_argument('--protect', type=str, help='Protect reports matching pattern')
    parser.add_argument('--audit', action='store_true', help='Audit access logs')
    parser.add_argument('--days', type=int, default=7, help='Days for audit')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--user', type=str, default='default', help='Current user')
    
    args = parser.parse_args()
    
    controller = ReportAccessController(current_user=args.user)
    
    if args.check:
        allowed = controller.check_access(args.check)
        if allowed:
            print(f'Access granted: {args.check}')
        else:
            print(f'Access denied: {args.check}')
    elif args.classify:
        controller.auto_classify_all()
    elif args.protect:
        # Protect reports matching pattern
        pattern = args.protect.upper()
        for root, dirs, files in os.walk(REPORTS_DIR):
            for file in files:
                if pattern in file.upper():
                    filepath = Path(root) / file
                    controller.protect_report(filepath, AccessLevel.CONFIDENTIAL)
    elif args.audit:
        controller.audit_logs(days=args.days)
    elif args.stats:
        controller.show_stats()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
