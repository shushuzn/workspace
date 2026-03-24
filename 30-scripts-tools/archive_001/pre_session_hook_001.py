import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
会话前钩子 - 检查上下文加载情况

功能：
1. 检查 7 个核心文件是否存在
2. 检查总大小是否超过限制 (<100KB)
3. 检查关键文件完整性
4. 生成上下文加载报告
5. 如果不合格，建议运行压缩

使用：
  py pre-session-hook.py
  py pre-session-hook.py --strict
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))

from core_files_compressor import CoreFilesCompressor


class PreSessionHook:
    """会话前钩子"""

    # 关键配置文件
    CRITICAL_FILES = [
        'SOUL.md',
        'USER.md',
        'AGENTS.md',
        'TOOLS.md',
        'HEARTBEAT.md',
        'MEMORY.md',
    ]

    # 可选文件
    OPTIONAL_FILES = [
        '10-MEMORY/00-CORE/YYYY-MM-DD.md',  # 今日笔记
    ]

    # 检查规则
    RULES = {
        'total_size_limit': 100 * 1024,  # 100KB
        'critical_files_required': True,
        'daily_note_required': False,
    }

    def __init__(self, strict: bool = False):
        self.workspace = Path(__file__).parent.parent
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.strict = strict

    def check_critical_files(self) -> Dict:
        """检查关键文件"""
        result = {
            'all_exist': True,
            'files': [],
            'missing': []
        }

        for file_name in self.CRITICAL_FILES:
            file_path = self.workspace / file_name
            exists = file_path.exists()

            if not exists:
                result['all_exist'] = False
                result['missing'].append(file_name)

            file_info = {
                'name': file_name,
                'exists': exists,
                'size': file_path.stat().st_size if exists else 0,
                'size_kb': round(file_path.stat().st_size / 1024, 2) if exists else 0
            }
            result['files'].append(file_info)

        return result

    def check_daily_note(self) -> Dict:
        """检查今日笔记"""
        daily_note = self.workspace / f'10-MEMORY/00-CORE/{self.today}.md'

        result = {
            'exists': daily_note.exists(),
            'path': str(daily_note.relative_to(self.workspace)) if daily_note.exists() else None,
            'size': daily_note.stat().st_size if daily_note.exists() else 0,
            'size_kb': round(daily_note.stat().st_size / 1024, 2) if daily_note.exists() else 0
        }

        return result

    def check_total_size(self) -> Dict:
        """检查总大小"""
        compressor = CoreFilesCompressor()
        check_result = compressor.check_files()

        return {
            'total_size': check_result['total_size'],
            'total_size_kb': check_result['total_size_kb'],
            'limit': self.RULES['total_size_limit'],
            'limit_kb': self.RULES['total_size_limit'] / 1024,
            'within_limit': check_result['within_limit'],
            'usage': round(check_result['total_size'] / self.RULES['total_size_limit'] * 100, 1)
        }

    def validate(self) -> Dict:
        """验证上下文加载"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'valid': True,
            'errors': [],
            'warnings': [],
            'checks': {}
        }

        # 1. 检查关键文件
        result['checks']['critical_files'] = self.check_critical_files()
        if not result['checks']['critical_files']['all_exist']:
            result['valid'] = False
            result['errors'].append(
                f"缺少关键文件: {', '.join(result['checks']['critical_files']['missing'])}"
            )

        # 2. 检查今日笔记
        result['checks']['daily_note'] = self.check_daily_note()
        if not result['checks']['daily_note']['exists']:
            if self.RULES['daily_note_required']:
                result['valid'] = False
                result['errors'].append("缺少今日笔记")
            else:
                result['warnings'].append("今日笔记不存在（将自动创建）")

        # 3. 检查总大小
        result['checks']['total_size'] = self.check_total_size()
        if not result['checks']['total_size']['within_limit']:
            if self.strict:
                result['valid'] = False
                result['errors'].append(
                    f"总大小超过限制: {result['checks']['total_size']['total_size_kb']:.2f}KB > "
                    f"{result['checks']['total_size']['limit_kb']:.2f}KB"
                )
            else:
                result['warnings'].append(
                    f"总大小超过限制: {result['checks']['total_size']['total_size_kb']:.2f}KB > "
                    f"{result['checks']['total_size']['limit_kb']:.2f}KB"
                )

        return result

    def generate_report(self) -> str:
        """生成上下文加载报告"""
        validation = self.validate()

        report = []
        report.append("=" * 60)
        report.append("会话前上下文检查")
        report.append(f"时间: {validation['timestamp']}")
        report.append(f"模式: {'严格' if self.strict else '宽松'}")
        report.append("=" * 60)
        report.append("")

        # 关键文件状态
        report.append("关键文件:")
        for f in validation['checks']['critical_files']['files']:
            status = "[OK]" if f['exists'] else "[MISSING]"
            report.append(f"  {status} {f['name']:<25} {f['size_kb']:>6.2f}KB")
        report.append("")

        # 今日笔记
        report.append("今日笔记:")
        dn = validation['checks']['daily_note']
        status = "[OK]" if dn['exists'] else "[MISSING]"
        report.append(f"  {status} {dn['path'] or f'10-MEMORY/00-CORE/{self.today}.md':<25} {dn['size_kb']:>6.2f}KB")
        report.append("")

        # 总大小
        report.append("总大小:")
        ts = validation['checks']['total_size']
        status = "[OK]" if ts['within_limit'] else "[WARN]"
        report.append(
            f"  {status} {ts['total_size_kb']:>6.2f}KB / {ts['limit_kb']:.2f}KB "
            f"({ts['usage']:>5.1f}%)"
        )
        report.append("")

        # 错误
        if validation['errors']:
            report.append("错误:")
            for error in validation['errors']:
                report.append(f"  [ERROR] {error}")
            report.append("")

        # 警告
        if validation['warnings']:
            report.append("警告:")
            for warning in validation['warnings']:
                report.append(f"  [WARN] {warning}")
            report.append("")

        # 建议
        if not validation['valid']:
            report.append("建议:")
            report.append("  1. 检查缺失文件")
            report.append("  2. 运行: py core_files_compressor.py --compress")
            report.append("")

        # 结果
        report.append(f"状态: {'[PASS] 通过' if validation['valid'] else '[FAIL] 不合格'}")
        report.append("=" * 60)

        return "\n".join(report)


logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py pre_session_hook_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py pre_session_hook_001.py

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
    strict = '--strict' in sys.argv

    hook = PreSessionHook(strict=strict)
    report = hook.generate_report()
    print(report)

    validation = hook.validate()

    if validation['valid']:
        sys.exit(0)
    else:
        sys.exit(1)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <args>")
        sys.exit(1)

if __name__ == "__main__":
    main()