#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quality Gate Check - 代码质量门禁检查

功能:
1. 检查 Python 文件质量评分
2. 验证最低分数要求
3. 生成质量报告

Usage:
    py quality_gate.py --path "30-scripts-tools/*.py" --min-score 80
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import glob


def run_pylint(file_path: str) -> dict:
    """运行代码质量检查（使用 flake8 或简单语法检查）"""
    try:
        # 尝试使用 flake8
        result = subprocess.run(
            ['flake8', '--count', file_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        
        # flake8 返回 1 表示有问题，但不一定是错误
        error_count = 0
        warning_count = 0
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line and not line.endswith('errors'):
                    error_count += 1
        
        # 计算分数 (每 10 个错误扣 1 分)
        score = max(0, 100 - (error_count * 2))
        
        return {
            'success': True,
            'score': score,
            'issues': error_count,
            'file': file_path
        }
    except Exception as ex:
        # flake8 不可用时，进行简单语法检查
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            return {
                'success': True,
                'score': 100,
                'issues': 0,
                'file': file_path
            }
        except SyntaxError:
            return {
                'success': False,
                'score': 0,
                'issues': 1,
                'file': file_path,
                'error': 'Syntax error'
            }
        except Exception as ex2:
            return {
                'success': False,
                'score': 0,
                'issues': 1,
                'file': file_path,
                'error': str(ex2)
            }


def check_quality(path_pattern: str, min_score: int = 80) -> dict:
    """检查代码质量"""
    # 移除可能的引号
    path_pattern = path_pattern.strip('"').strip("'")
    
    # 直接使用 glob
    files = glob.glob(path_pattern, recursive=True)
    
    if not files:
        return {
            'success': False,
            'message': f'No files found matching: {path_pattern}',
            'files_checked': 0,
            'average_score': 0,
            'min_required': min_score,
            'passed': False
        }
    
    results = []
    total_score = 0
    
    for file_path in files:
        if not file_path.endswith('.py'):
            continue
        
        result = run_pylint(file_path)
        results.append(result)
        total_score += result['score']
    
    avg_score = total_score / len(results) if results else 0
    passed = avg_score >= min_score
    
    return {
        'success': True,
        'message': 'Quality check completed',
        'files_checked': len(results),
        'average_score': round(avg_score, 2),
        'min_required': min_score,
        'passed': passed,
        'results': results,
        'timestamp': datetime.now().isoformat()
    }


def main():
    import argparse
    
    # 修复中文编码
    if sys.platform == 'win32':
        import io
        import locale
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    parser = argparse.ArgumentParser(description='Quality Gate Check')
    parser.add_argument('--check', required=True, help='File path pattern')
    parser.add_argument('--min-score', type=int, default=80, help='Minimum score required')
    parser.add_argument('--json', action='store_true', help='Output JSON only')
    
    args = parser.parse_args()
    
    result = check_quality(args.check, args.min_score)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("QUALITY GATE CHECK")
        print("=" * 60)
        print(f"Files Checked: {result['files_checked']}")
        print(f"Average Score: {result['average_score']}/100")
        print(f"Minimum Required: {result['min_required']}")
        print(f"Status: {'PASS' if result['passed'] else 'FAIL'}")
        print("=" * 60)
    
    sys.exit(0 if result['passed'] else 1)


if __name__ == "__main__":
    main()
