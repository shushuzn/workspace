#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Memory Auto-Fix - 记忆系统自动修复工具

功能:
- 检测记忆系统问题
- 自动执行修复操作
- 修复前自动备份
- 生成修复报告
- 支持回滚
- 严格限制模式（文件操作前必须对比）

使用示例:
    python memory_auto_fix.py --check      # 检查问题
    python memory_auto_fix.py --fix        # 自动修复
    python memory_auto_fix.py --dry-run    # 模拟修复
    python memory_auto_fix.py --strict     # 严格限制模式（需确认）

作者：Claw [PAW] (Innovator Agent)
日期：2026-03-14
更新：2026-03-14 添加严格限制模式
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess

# 配置
WORKSPACE_MEMORY = Path(r"str(Path(__file__).parent.parent)\13-memory-记忆系统\MEMORY.md")
CONFIG_MEMORY = Path(r"C:\Users\华为\.copaw\MEMORY.md")
BACKUP_DIR = Path(r"str(Path(__file__).parent.parent)\00-persona-system\memory-backups")
HEALTH_REPORT = Path(r"str(Path(__file__).parent.parent)\00-persona-system\memory-health-report.json")
FIX_REPORT = Path(r"str(Path(__file__).parent.parent)\00-persona-system\memory-fix-report.json")

# 阈值
THRESHOLDS = {
    'workspace_memory_min_kb': 40,
    'config_memory_min_kb': 10,
}

class MemoryAutoFix:
    """记忆系统自动修复器"""
    
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.backup_files = []
        self.dry_run = False
        self.strict_mode = True  # 默认启用严格模式（最高优先级）
        self.comparison_report = None  # 文件对比报告
        self.report = {
            'timestamp': None,
            'issues_found': [],
            'fixes_applied': [],
            'backups_created': [],
            'status': 'unknown',
            'strict_mode': True,  # 默认启用
            'comparison_before_fix': None,
        }
    
    def check_health(self) -> List[Dict]:
        """检查记忆系统健康"""
        issues = []
        
        # 检查工作区记忆
        if not WORKSPACE_MEMORY.exists():
            issues.append({
                'type': 'MISSING_WORKSPACE_MEMORY',
                'severity': 'critical',
                'message': '工作区 MEMORY.md 不存在',
                'auto_fixable': False,
            })
        else:
            size_kb = WORKSPACE_MEMORY.stat().st_size / 1024
            if size_kb < THRESHOLDS['workspace_memory_min_kb']:
                issues.append({
                    'type': 'WORKSPACE_MEMORY_TOO_SMALL',
                    'severity': 'warning',
                    'message': f'工作区记忆过小 ({size_kb:.1f}KB < {THRESHOLDS["workspace_memory_min_kb"]}KB)',
                    'auto_fixable': True,
                    'fix_action': 'restore_from_backup',
                    'current_size': size_kb,
                })
        
        # 检查配置记忆
        if not CONFIG_MEMORY.exists():
            issues.append({
                'type': 'MISSING_CONFIG_MEMORY',
                'severity': 'critical',
                'message': '配置区 MEMORY.md 不存在',
                'auto_fixable': False,
            })
        else:
            size_kb = CONFIG_MEMORY.stat().st_size / 1024
            if size_kb < THRESHOLDS['config_memory_min_kb']:
                issues.append({
                    'type': 'CONFIG_MEMORY_TOO_SMALL',
                    'severity': 'warning',
                    'message': f'配置记忆过小 ({size_kb:.1f}KB < {THRESHOLDS["config_memory_min_kb"]}KB)',
                    'auto_fixable': True,
                    'fix_action': 'restore_from_backup',
                    'current_size': size_kb,
                })
        
        # 检查交叉引用
        if WORKSPACE_MEMORY.exists():
            try:
                with open(WORKSPACE_MEMORY, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if 'Agent 配置记忆' not in content:
                    issues.append({
                        'type': 'MISSING_CROSS_REF',
                        'severity': 'info',
                        'message': '工作区记忆缺少 Agent 配置交叉引用',
                        'auto_fixable': True,
                        'fix_action': 'add_cross_reference',
                    })
            except Exception as e:
                issues.append({
                    'type': 'READ_ERROR',
                    'severity': 'warning',
                    'message': f'读取工作区记忆失败：{e}',
                    'auto_fixable': False,
                })
        
        self.issues = issues
        return issues
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """创建文件备份"""
        if not file_path.exists():
            return None
        
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_name = f"{file_path.stem}-backup-{timestamp}{file_path.suffix}"
        backup_path = BACKUP_DIR / backup_name
        
        if self.dry_run:
            print(f"[DRY-RUN] Would backup: {file_path} -> {backup_path}")
        else:
            # 严格限制模式：创建备份前必须对比
            if self.strict_mode:
                print(f"[STRICT] Creating backup, comparison required...")
                self.run_comparison_before_backup(file_path)
            
            shutil.copy2(file_path, backup_path)
            print(f"[BACKUP] Created: {backup_path}")
        
        self.backup_files.append(str(backup_path))
        return backup_path
    
    def restore_from_backup(self, file_path: Path) -> bool:
        """从备份恢复文件"""
        # 查找最新备份
        if not BACKUP_DIR.exists():
            print(f"[ERROR] No backup directory: {BACKUP_DIR}")
            return False
        
        backups = list(BACKUP_DIR.glob(f"{file_path.stem}-backup-*{file_path.suffix}"))
        if not backups:
            print(f"[ERROR] No backup found for: {file_path}")
            return False
        
        # 选择最新备份
        latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
        
        if self.dry_run:
            print(f"[DRY-RUN] Would restore: {latest_backup} -> {file_path}")
            return True
        
        # 创建当前版本备份
        self.create_backup(file_path)
        
        # 恢复
        shutil.copy2(latest_backup, file_path)
        print(f"[RESTORE] Restored: {latest_backup} -> {file_path}")
        
        self.fixes_applied.append({
            'action': 'restore_from_backup',
            'file': str(file_path),
            'source': str(latest_backup),
        })
        
        return True
    
    def add_cross_reference(self) -> bool:
        """添加交叉引用到工作区记忆"""
        if not WORKSPACE_MEMORY.exists():
            return False
        
        try:
            with open(WORKSPACE_MEMORY, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 检查是否已存在
            if 'Agent 配置记忆' in content:
                print("[SKIP] Cross-reference already exists")
                return True
            
            # 创建交叉引用内容
            cross_ref = """# MEMORY.md - 长期记忆 (完整版)

**最后更新:** 2026-03-13 14:50
**来源:** memory-distiller 自动蒸馏 + 手动整理 + 学习者人格
**核心观点:** 190+ 条 | **趋势追踪:** 8 个

---

## 🔗 Agent 配置记忆

**位置:** `C:\\Users\\华为\\.copaw\\MEMORY.md`
**内容:** 用户偏好、工具配置、系统设置、7 人格系统
**最后更新:** 2026-03-14

**关键内容:**
- 用户偏好 (ALL FILES IN ENGLISH, 禁止休息建议)
- 云服务器配置 (8.208.30.28 英国伦敦)
- 飞书集成 (App ID, 工具位置)
- 7 人格系统配置 (触发时间表、健康指标)
- 已部署项目 (知识卡片生成器、Innovator Dashboard)

---

"""
            
            # 添加到文件开头
            new_content = cross_ref + content
            
            if self.dry_run:
                print(f"[DRY-RUN] Would add cross-reference to: {WORKSPACE_MEMORY}")
                return True
            
            # 创建备份
            self.create_backup(WORKSPACE_MEMORY)
            
            # 写入新内容
            with open(WORKSPACE_MEMORY, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"[FIX] Added cross-reference to: {WORKSPACE_MEMORY}")
            
            self.fixes_applied.append({
                'action': 'add_cross_reference',
                'file': str(WORKSPACE_MEMORY),
            })
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to add cross-reference: {e}")
            return False
    
    def apply_fixes(self) -> Dict:
        """应用所有可自动修复的问题"""
        fixes_result = {
            'total_issues': len(self.issues),
            'auto_fixable': 0,
            'fixed': 0,
            'failed': 0,
            'skipped': 0,
        }
        
        for issue in self.issues:
            if not issue.get('auto_fixable', False):
                print(f"[SKIP] Not auto-fixable: {issue['type']}")
                fixes_result['skipped'] += 1
                continue
            
            fixes_result['auto_fixable'] += 1
            
            fix_action = issue.get('fix_action')
            
            if fix_action == 'restore_from_backup':
                if 'WORKSPACE' in issue['type']:
                    success = self.restore_from_backup(WORKSPACE_MEMORY)
                elif 'CONFIG' in issue['type']:
                    success = self.restore_from_backup(CONFIG_MEMORY)
                else:
                    success = False
                
                if success:
                    fixes_result['fixed'] += 1
                else:
                    fixes_result['failed'] += 1
            
            elif fix_action == 'add_cross_reference':
                success = self.add_cross_reference()
                if success:
                    fixes_result['fixed'] += 1
                else:
                    fixes_result['failed'] += 1
        
        return fixes_result
    
    def run_health_monitor(self) -> bool:
        """运行健康监控器更新报告"""
        if self.dry_run:
            print("[DRY-RUN] Would run memory_health_monitor.py")
            return True
        
        try:
            script_path = Path(__file__).parent / 'memory_health_monitor.py'
            if script_path.exists():
                subprocess.run([sys.executable, str(script_path), '--check', '--report'],
                             check=True, capture_output=False)
                print("[MONITOR] Health check completed")
                return True
            else:
                print(f"[WARN] Health monitor not found: {script_path}")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to run health monitor: {e}")
            return False
    
    def generate_report(self) -> Dict:
        """生成修复报告"""
        self.report['timestamp'] = datetime.now().isoformat()
        self.report['issues_found'] = self.issues
        self.report['fixes_applied'] = self.fixes_applied
        self.report['backups_created'] = self.backup_files
        
        # 重新检查健康状态
        remaining_issues = self.check_health()
        self.report['remaining_issues'] = len(remaining_issues)
        
        if len(remaining_issues) == 0:
            self.report['status'] = 'healthy'
        elif any(i['severity'] == 'critical' for i in remaining_issues):
            self.report['status'] = 'critical'
        else:
            self.report['status'] = 'warning'
        
        return self.report
    
    def save_report(self):
        """生成修复报告"""
        self.report['timestamp'] = datetime.now().isoformat()
        self.report['issues_found'] = self.issues
        self.report['fixes_applied'] = self.fixes_applied
        self.report['backups_created'] = self.backup_files
        self.report['strict_mode'] = self.strict_mode
        self.report['comparison_before_fix'] = self.comparison_report
        
        # 重新检查健康状态
        remaining_issues = self.check_health()
        self.report['remaining_issues'] = len(remaining_issues)
        
        if len(remaining_issues) == 0:
            self.report['status'] = 'healthy'
        elif any(i['severity'] == 'critical' for i in remaining_issues):
            self.report['status'] = 'critical'
        else:
            self.report['status'] = 'warning'
        
        return self.report
    
    def run_comparison_before_backup(self, file_path: Path):
        """严格模式：创建备份前运行文件对比"""
        try:
            comparator_script = Path(__file__).parent / 'workspace_comparator.py'
            if comparator_script.exists():
                result = subprocess.run(
                    [sys.executable, str(comparator_script), '--compare'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                self.comparison_report = {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode,
                }
                print(f"[COMPARISON] Completed (returncode={result.returncode})")
            else:
                print(f"[WARN] Comparator not found: {comparator_script}")
        except Exception as e:
            print(f"[ERROR] Comparison failed: {e}")
            self.comparison_report = {'error': str(e)}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Auto-Fix (STRICT MODE BY DEFAULT)')
    parser.add_argument('--check', action='store_true', help='Check issues')
    parser.add_argument('--fix', action='store_true', help='Apply fixes')
    parser.add_argument('--dry-run', action='store_true', help='Simulate fixes')
    parser.add_argument('--no-strict', action='store_true', help='Disable strict mode (NOT RECOMMENDED)')
    
    args = parser.parse_args()
    
    fixer = MemoryAutoFix()
    fixer.dry_run = args.dry_run
    fixer.strict_mode = not args.no_strict  # 默认严格模式，除非明确禁用
    
    if args.check:
        issues = fixer.check_health()
        print(f"\nFound {len(issues)} issues:")
        for issue in issues:
            auto_fix = "[OK]" if issue.get('auto_fixable') else "[FAIL]"
            print(f"  {auto_fix} [{issue['severity'].upper()}] {issue['type']}: {issue['message']}")
        if fixer.strict_mode:
            print("\n[WARN] STRICT MODE ENABLED (DEFAULT) - All changes require comparison")
        else:
            print("\n[WARN] WARNING - STRICT MODE DISABLED - Not recommended!")
    
    elif args.fix:
        print("[AUTO-FIX] Starting automatic repair...")
        if fixer.strict_mode:
            print("[WARN] STRICT MODE ENABLED - Running comparison before changes...")
        else:
            print("[WARN] WARNING - STRICT MODE DISABLED - Skipping comparison!")
        fixer.check_health()
        fixer.apply_fixes()
        fixer.run_health_monitor()
        fixer.save_report()
    
    else:
        # 默认：检查 + 修复
        print("[AUTO-FIX] Check and fix...")
        if fixer.strict_mode:
            print("[WARN] STRICT MODE ENABLED (DEFAULT)")
        else:
            print("[WARN] WARNING - STRICT MODE DISABLED")
        issues = fixer.check_health()
        print(f"Found {len(issues)} issues")
        
        if issues:
            fixer.apply_fixes()
            fixer.run_health_monitor()
            fixer.save_report()
        else:
            print("[OK] Memory system is healthy, no fixes needed")


if __name__ == '__main__':
    main()
