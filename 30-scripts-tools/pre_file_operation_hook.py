#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Pre-File-Operation Hook - 文件操作前强制检查

功能:
- 在任何文件创建/修改/删除前强制运行对比
- 检查是否有现有文件可修改（优先修改现有文件）
- 严格限制报告文件创建（优先更新现有报告）
- 生成检查报告
- 阻止无对比的操作

使用示例:
    python pre_file_operation_hook.py --check "filename.md"
    python pre_file_operation_hook.py --before-create "newfile.md"
    python pre_file_operation_hook.py --before-modify "existing.md"
    python pre_file_operation_hook.py --before-delete "file.md"

作者：Claw [PAW] (Innovator Agent)
日期：2026-03-14
优先级：最高（强制执行）

限制报告创建规则:
- 禁止创建 session-report-*.md 文件（使用单一 learner-notes.md）
- 禁止创建 learning-summary-*.md 文件（更新现有 summary）
- 禁止创建 memory-update-*.md 文件（直接更新 MEMORY.md）
- 优先更新现有文件，不创建新报告
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import subprocess

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 配置
WORKSPACE = Path(__file__).parent.parent
CONFIG_DIR = Path(r"C:\Users\华为\.copaw")
COMPARATOR_SCRIPT = Path(r"str(Path(__file__).parent.parent)\30-scripts-tools\workspace_comparator.py")
CHECK_REPORT_DIR = Path(r"str(Path(__file__).parent.parent)\00-persona-system\pre-operation-checks")

class PreOperationHook:
    """文件操作前检查器"""
    
    def __init__(self):
        self.checks_passed = False
        self.warnings = []
        self.errors = []
        self.suggestions = []
        self.report = {
            'timestamp': None,
            'operation_type': None,
            'target_file': None,
            'checks': [],
            'comparison_result': None,
            'existing_files_scan': None,
            'recommendation': None,
            'allowed': False,
        }
    
    def run_comparison(self) -> Dict:
        """运行文件对比"""
        print("[CHECK] Running workspace comparison...")
        
        if not COMPARATOR_SCRIPT.exists():
            return {'error': 'Comparator script not found'}
        
        try:
            result = subprocess.run(
                [sys.executable, str(COMPARATOR_SCRIPT), '--report'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(WORKSPACE)
            )
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0,
            }
        except Exception as e:
            return {'error': str(e)}
    
    def scan_existing_files(self, pattern: str = "") -> List[Path]:
        """扫描现有文件（优先修改现有文件）"""
        print(f"[CHECK] Scanning existing files (pattern: '{pattern}')...")
        
        existing_files = []
        
        # 扫描工作区
        for ext in ['*.md', '*.py', '*.json', '*.txt', '*.yml', '*.yaml']:
            existing_files.extend(WORKSPACE.rglob(ext))
        
        # 如果提供了模式，过滤
        if pattern:
            existing_files = [f for f in existing_files if pattern.lower() in str(f).lower()]
        
        return existing_files[:50]  # 限制返回数量
    
    def check_before_create(self, new_file_path: str) -> bool:
        """创建文件前检查"""
        print(f"\n[CHECK] Before CREATE: {new_file_path}")
        
        self.report['operation_type'] = 'CREATE'
        self.report['target_file'] = new_file_path
        
        # 检查 0: 严格限制报告文件创建（最高优先级）
        restricted_patterns = [
            'session-report-',
            'learning-summary-',
            'memory-update-',
            'learner-memory-',
            'learner-session-',
        ]
        
        file_name = Path(new_file_path).name.lower()
        for pattern in restricted_patterns:
            if pattern in file_name:
                self.errors.append(
                    f"RESTRICTED: Report file creation blocked ('{pattern}' in filename)"
                )
                self.suggestions.append(
                    "Instead: Update existing files (MEMORY.md, learner-notes.md, etc.)"
                )
                self.suggestions.append(
                    "RULE: Modify existing files > Create new reports"
                )
                print("[FAIL] CREATE BLOCKED - Report file creation restricted")
                return False
        
        # 检查 1: 运行对比
        comparison = self.run_comparison()
        self.report['comparison_result'] = comparison
        
        if not comparison.get('success', False):
            self.errors.append("Comparison failed - cannot proceed")
            return False
        
        # 检查 2: 扫描现有文件（优先修改现有文件）
        existing = self.scan_existing_files(Path(new_file_path).stem)
        self.report['existing_files_scan'] = [str(f) for f in existing[:10]]
        
        if existing:
            self.suggestions.append(
                f"Found {len(existing)} existing files with similar name. "
                "Consider modifying existing file instead of creating new one."
            )
            self.warnings.append("PRIORITY: Modify existing files > Create new files")
        
        # 检查 3: 文件是否已存在
        target = Path(new_file_path)
        if not target.is_absolute():
            target = WORKSPACE / target
        
        if target.exists():
            self.errors.append(f"File already exists: {target}")
            self.suggestions.append("Use --before-modify instead of --before-create")
            return False
        
        # 检查 4: 工作台整洁度
        workspace_files = list(WORKSPACE.rglob('*'))
        if len(workspace_files) > 500:
            self.warnings.append(f"Workspace has {len(workspace_files)} files - consider cleanup")
        
        # 通过检查
        self.checks_passed = len(self.errors) == 0
        
        if self.checks_passed:
            print("[OK] CREATE check PASSED")
        else:
            print("[FAIL] CREATE check FAILED")
        
        return self.checks_passed
    
    def check_before_modify(self, file_path: str) -> bool:
        """修改文件前检查"""
        print(f"\n[CHECK] Before MODIFY: {file_path}")
        
        self.report['operation_type'] = 'MODIFY'
        self.report['target_file'] = file_path
        
        # 检查 1: 文件是否存在
        target = Path(file_path)
        if not target.is_absolute():
            target = WORKSPACE / target
        
        if not target.exists():
            self.errors.append(f"File does not exist: {target}")
            return False
        
        # 检查 2: 运行对比（备份前）
        comparison = self.run_comparison()
        self.report['comparison_result'] = comparison
        
        if not comparison.get('success', False):
            self.errors.append("Comparison failed - cannot proceed")
            return False
        
        # 检查 3: 检查文件重要性
        important_files = ['MEMORY.md', 'PROFILE.md', 'SOUL.md', 'AGENTS.md']
        if target.name in important_files:
            self.warnings.append(f"Critical file: {target.name} - Extra caution required")
        
        # 通过检查
        self.checks_passed = len(self.errors) == 0
        
        if self.checks_passed:
            print("[OK] MODIFY check PASSED")
        else:
            print("[FAIL] MODIFY check FAILED")
        
        return self.checks_passed
    
    def check_before_delete(self, file_path: str) -> bool:
        """删除文件前检查"""
        print(f"\n[CHECK] Before DELETE: {file_path}")
        
        self.report['operation_type'] = 'DELETE'
        self.report['target_file'] = file_path
        
        # 检查 1: 文件是否存在
        target = Path(file_path)
        if not target.is_absolute():
            target = WORKSPACE / target
        
        if not target.exists():
            self.errors.append(f"File does not exist: {target}")
            return False
        
        # 检查 2: 运行对比
        comparison = self.run_comparison()
        self.report['comparison_result'] = comparison
        
        # 检查 3: 禁止删除关键文件
        protected_patterns = ['MEMORY.md', 'PROFILE.md', 'SOUL.md', '.git', '30-scripts-tools']
        for pattern in protected_patterns:
            if pattern in str(target):
                self.errors.append(f"Protected file/path: {pattern} - DELETE NOT ALLOWED")
                return False
        
        # 检查 4: 建议移动到 archive 而非删除
        self.suggestions.append("Consider moving to 90-99-archive/ instead of deleting")
        
        # 通过检查
        self.checks_passed = len(self.errors) == 0
        
        if self.checks_passed:
            print("[OK] DELETE check PASSED (with warnings)")
        else:
            print("[FAIL] DELETE check FAILED")
        
        return self.checks_passed
    
    def generate_report(self) -> Dict:
        """生成检查报告"""
        self.report['timestamp'] = datetime.now().isoformat()
        self.report['allowed'] = self.checks_passed
        self.report['errors'] = self.errors
        self.report['warnings'] = self.warnings
        self.report['suggestions'] = self.suggestions
        
        # 生成建议
        if self.checks_passed:
            if self.warnings:
                self.report['recommendation'] = 'PROCEED_WITH_CAUTION'
            else:
                self.report['recommendation'] = 'PROCEED'
        else:
            self.report['recommendation'] = 'BLOCKED'
        
        return self.report
    
    def save_report(self, save_to_file: bool = False):
        """保存检查报告
        
        Args:
            save_to_file: 是否保存到文件（默认 False，只输出到控制台）
        
        合规说明 [FILE-006]:
        - 默认不创建报告文件（save_to_file=False）
        - 只在控制台输出结果
        - 如需保存，使用 --save 参数（明确指定）
        """
        report = self.generate_report()
        
        # 打印到控制台（总是执行）
        self.print_summary(report)
        
        if save_to_file:
            # 只有明确指定 --save 才创建文件
            CHECK_REPORT_DIR.mkdir(parents=True, exist_ok=True)
            report_file = CHECK_REPORT_DIR / "pre-op-check-latest.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"[REPORT] Saved: {report_file}")
        
        # 打印摘要
        print("\n" + "="*60)
        print("PRE-OPERATION CHECK SUMMARY")
        print("="*60)
        print(f"Operation: {report['operation_type']} - {report['target_file']}")
        status_str = "ALLOWED" if report['allowed'] else "BLOCKED"
        print(f"Status: [{status_str}]")
        print(f"Errors: {len(report['errors'])}")
        print(f"Warnings: {len(report['warnings'])}")
        print(f"Suggestions: {len(report['suggestions'])}")
        
        if report['errors']:
            print("\nErrors:")
            for err in report['errors']:
                print(f"  [ERROR] {err}")
        
        if report['warnings']:
            print("\nWarnings:")
            for warn in report['warnings']:
                print(f"  [WARN] {warn}")
        
        if report['suggestions']:
            print("\nSuggestions:")
            for sug in report['suggestions']:
                print(f"  [INFO] {sug}")
        
        print("="*60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Pre-File-Operation Hook (MANDATORY)')
    parser.add_argument('--check', type=str, help='Check before operation on file')
    parser.add_argument('--before-create', type=str, help='Check before creating file')
    parser.add_argument('--before-modify', type=str, help='Check before modifying file')
    parser.add_argument('--before-delete', type=str, help='Check before deleting file')
    parser.add_argument('--save', action='store_true', help='Save report to file (creates file, use sparingly)')
    
    args = parser.parse_args()
    
    hook = PreOperationHook()
    
    # 合规 [FILE-006]: 默认不创建报告文件，只输出到控制台
    save_to_file = args.save  # 只有明确指定 --save 才创建文件
    
    if args.before_create:
        passed = hook.check_before_create(args.before_create)
        hook.save_report(save_to_file=save_to_file)
        sys.exit(0 if passed else 1)
    
    elif args.before_modify:
        passed = hook.check_before_modify(args.before_modify)
        hook.save_report(save_to_file=save_to_file)
        sys.exit(0 if passed else 1)
    
    elif args.before_delete:
        passed = hook.check_before_delete(args.before_delete)
        hook.save_report(save_to_file=save_to_file)
        sys.exit(0 if passed else 1)
    
    elif args.check:
        # 通用检查
        print("[CHECK] Running general workspace check...")
        comparison = hook.run_comparison()
        existing = hook.scan_existing_files()
        print(f"Comparison: {'[OK] Success' if comparison.get('success') else '[FAIL] Failed'}")
        print(f"Existing files found: {len(existing)}")
        hook.save_report(save_to_file=save_to_file)
    
    else:
        parser.print_help()
        print("\n[INFO] This tool enforces mandatory comparison before file operations")
        print("[INFO] Usage examples:")
        print("  python pre_file_operation_hook.py --before-create newfile.md")
        print("  python pre_file_operation_hook.py --before-modify existing.md")
        print("  python pre_file_operation_hook.py --before-delete oldfile.md")


if __name__ == '__main__':
    main()
