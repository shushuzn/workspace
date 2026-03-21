import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
临时文件清理器 v1.0

功能：
1. 清理 tool_result/ 目录中的临时文件
2. 清理过期的 session 文件
3. 清理压缩日志
4. 生成清理报告

使用：
  py temp_file_cleaner.py --check
  py temp_file_cleaner.py --clean
  py temp_file_cleaner.py --auto
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class TempFileCleaner:
    """临时文件清理器"""

    # 清理规则
    CLEANUP_RULES = {
        'tool_result': {
            'path': 'tool_result',
            'max_age_days': 7,
            'max_size_mb': 50,
            'file_pattern': '*.txt'
        },
        'session_temp': {
            'path': '13-memory',
            'max_age_days': 1,
            'file_pattern': 'session_temp.json'
        },
        'compression_log': {
            'path': '13-memory',
            'max_age_days': 30,
            'file_pattern': 'compression_log.json'
        },
        'task_temp': {
            'path': '13-memory',
            'max_age_days': 1,
            'file_pattern': 'task_temp.json'
        },
        'execution_states': {
            'path': 'flow-archive',
            'max_age_days': 30,
            'file_pattern': 'execution-state.json'
        }
    }

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.cleanup_log = self.workspace / '13-memory/cleanup_log.jsonl'

    def check_cleanup_needed(self) -> Dict:
        """检查是否需要清理"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'needs_cleanup': False,
            'items': [],
            'total_size': 0,
            'total_size_mb': 0
        }

        for rule_name, rule in self.CLEANUP_RULES.items():
            target_path = self.workspace / rule['path']

            if not target_path.exists():
                continue

            if target_path.is_file():
                files = [target_path]
            elif target_path.is_dir():
                pattern = rule.get('file_pattern', '*')
                files = list(target_path.glob(pattern))
            else:
                continue

            rule_size = 0
            old_files = []

            for f in files:
                if f.is_file():
                    size = f.stat().st_size
                    rule_size += size

                    # 检查文件年龄
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    age = datetime.now() - mtime
                    max_age = timedelta(days=rule.get('max_age_days', 7))

                    if age > max_age:
                        old_files.append({
                            'path': str(f.relative_to(self.workspace)),
                            'size': size,
                            'age_days': age.days
                        })

            result['total_size'] += rule_size

            # 检查是否需要清理
            max_size = rule.get('max_size_mb', 0) * 1024 * 1024
            if old_files or (max_size > 0 and rule_size > max_size):
                result['needs_cleanup'] = True
                result['items'].append({
                    'rule': rule_name,
                    'path': str(target_path.relative_to(self.workspace)),
                    'size': rule_size,
                    'size_mb': round(rule_size / 1024 / 1024, 2),
                    'old_files_count': len(old_files),
                    'old_files': old_files[:10]  # 只显示前 10 个
                })

        result['total_size_mb'] = round(result['total_size'] / 1024 / 1024, 2)

        return result

    def cleanup(self, auto: bool = False) -> Dict:
        """执行清理"""
        check_result = self.check_cleanup_needed()

        result = {
            'timestamp': datetime.now().isoformat(),
            'cleaned': [],
            'skipped': [],
            'errors': [],
            'space_freed': 0
        }

        for item in check_result['items']:
            if auto and item['old_files_count'] == 0:
                # 自动模式只清理过期文件
                continue

            target_path = self.workspace / item['path']

            try:
                if target_path.is_file():
                    size = target_path.stat().st_size
                    target_path.unlink()
                    result['cleaned'].append({
                        'path': item['path'],
                        'type': 'file',
                        'size': size
                    })
                    result['space_freed'] += size

                elif target_path.is_dir() and item['old_files_count'] > 0:
                    # 只清理过期文件
                    rule_name = item['rule']
                    rule = self.CLEANUP_RULES[rule_name]
                    pattern = rule.get('file_pattern', '*')
                    max_age_days = rule.get('max_age_days', 7)

                    for f in target_path.glob(pattern):
                        if f.is_file():
                            mtime = datetime.fromtimestamp(f.stat().st_mtime)
                            age = datetime.now() - mtime

                            if age > timedelta(days=max_age_days):
                                size = f.stat().st_size
                                f.unlink()
                                result['cleaned'].append({
                                    'path': str(f.relative_to(self.workspace)),
                                    'type': 'old_file',
                                    'size': size,
                                    'age_days': age.days
                                })
                                result['space_freed'] += size

            except Exception as e:
                result['errors'].append({
                    'path': item['path'],
                    'error': str(e)
                })

        result['space_freed_kb'] = round(result['space_freed'] / 1024, 2)
        result['space_freed_mb'] = round(result['space_freed'] / 1024 / 1024, 2)

        # 记录清理日志
        self._log_cleanup(result)

        return result

    def _log_cleanup(self, result: Dict):
        """记录清理日志"""
        log_entry = {
            'timestamp': result['timestamp'],
            'cleaned_count': len(result['cleaned']),
            'space_freed_kb': result['space_freed_kb'],
            'errors_count': len(result['errors'])
        }

        with open(self.cleanup_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def generate_report(self) -> str:
        """生成清理报告"""
        check_result = self.check_cleanup_needed()

        report = []
        report.append("=" * 60)
        report.append("临时文件清理报告")
        report.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")

        if check_result['needs_cleanup']:
            report.append(f"[需要清理] 发现 {len(check_result['items'])} 个清理项")
            report.append("")
            report.append("清理项:")
            report.append("-" * 60)

            for item in check_result['items']:
                report.append(
                    f"  {item['rule']:<20} "
                    f"{item['size_mb']:>6.2f}MB  "
                    f"{item['old_files_count']:>3} 个过期文件"
                )
                for old_file in item['old_files'][:3]:
                    report.append(
                        f"    - {old_file['path']} "
                        f"({old_file['age_days']}天前)"
                    )

            report.append("-" * 60)
            report.append(f"总计: {check_result['total_size_mb']:.2f}MB")
            report.append("")
            report.append("执行: py temp_file_cleaner.py --clean")
        else:
            report.append("[OK] 无需清理")
            report.append(f"当前临时文件大小: {check_result['total_size_mb']:.2f}MB")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py temp_file_cleaner_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py temp_file_cleaner_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

主函数"""
    cleaner = TempFileCleaner()

    import sys

    if len(sys.argv) < 2:
        print(cleaner.generate_report())
        return

    command = sys.argv[1]

    if command == '--check':
        result = cleaner.check_cleanup_needed()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--clean':
        result = cleaner.cleanup(auto=False)
        print(f"\n清理完成:")
        print(f"  清理文件: {len(result['cleaned'])} 个")
        print(f"  释放空间: {result['space_freed_kb']:.2f}KB")
        if result['errors']:
            print(f"  错误: {len(result['errors'])} 个")

    elif command == '--auto':
        result = cleaner.cleanup(auto=True)
        print(f"自动清理完成: {len(result['cleaned'])} 个文件")

    elif command == '--report':
        print(cleaner.generate_report())

    else:
        print(f"未知命令: {command}")
        print("用法:")
        print("  py temp_file_cleaner.py --check   检查清理需求")
        print("  py temp_file_cleaner.py --clean   执行清理")
        print("  py temp_file_cleaner.py --auto    自动清理")


if __name__ == "__main__":
    main()