#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Critical Checks - 关键审查项验证

两项零分检查:
1. 创建的工具必须在 tools_registry.json 注册
2. 中文必须用 UTF-8 编码

Usage:
    py critical_checks.py --verify
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime


def check_tool_registered(tool_name: str) -> dict:
    """检查工具是否已注册"""
    registry_file = Path('30-scripts-tools/tools_registry.json')
    
    if not registry_file.exists():
        return {
            'passed': False,
            'message': f'tools_registry.json not found',
            'tool': tool_name,
            'penalty': '零分 - 工具未注册'
        }
    
    try:
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        tools = registry.get('tools', {})
        
        if tool_name in tools:
            return {
                'passed': True,
                'message': f'Tool {tool_name} is registered',
                'tool': tool_name,
                'tool_id': tools[tool_name]['tool_id'],
                'command': tools[tool_name]['command']
            }
        else:
            return {
                'passed': False,
                'message': f'Tool {tool_name} NOT found in registry',
                'tool': tool_name,
                'penalty': '零分 - 工具未注册'
            }
    except Exception as e:
        return {
            'passed': False,
            'message': f'Error reading registry: {e}',
            'tool': tool_name,
            'penalty': '零分 - 工具未注册'
        }


def check_utf8_encoding(file_path: str) -> dict:
    """检查文件 UTF-8 编码"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含中文
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in content)
        
        if has_chinese:
            return {
                'passed': True,
                'message': f'UTF-8 encoding valid (contains Chinese)',
                'file': file_path,
                'size': len(content),
                'chinese_chars': sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
            }
        else:
            return {
                'passed': True,
                'message': f'UTF-8 encoding valid (no Chinese)',
                'file': file_path,
                'size': len(content)
            }
    except UnicodeDecodeError as e:
        return {
            'passed': False,
            'message': f'UTF-8 decoding failed: {e}',
            'file': file_path,
            'penalty': '零分 - 编码错误'
        }
    except Exception as e:
        return {
            'passed': False,
            'message': f'Error reading file: {e}',
            'file': file_path,
            'penalty': '零分 - 编码错误'
        }


def scan_new_tools() -> list:
    """扫描新创建的工具（本次会话 session_temp.json 追踪）"""
    scripts_dir = Path('30-scripts-tools')
    registry_file = scripts_dir / 'tools_registry.json'
    session_temp = scripts_dir / 'session_temp.json'
    
    # 获取已注册的工具
    registered_tools = set()
    if registry_file.exists():
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            for tool_id in registry.get('tools', {}).keys():
                registered_tools.add(tool_id)
    
    # 获取本次会话创建的工具
    session_tools = []
    if session_temp.exists():
        with open(session_temp, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
            # 从会话数据中提取新创建的工具
            created_tools = session_data.get('created_tools', [])
            session_tools.extend(created_tools)
    
    # 检查这些工具是否已注册
    unregistered = []
    for tool_name in session_tools:
        if tool_name not in registered_tools:
            py_file = scripts_dir / f"{tool_name.replace('-', '_')}.py"
            if py_file.exists():
                unregistered.append({
                    'file': str(py_file),
                    'tool_name': tool_name,
                    'registered': False
                })
    
    return unregistered


def scan_py_files_for_encoding() -> list:
    """扫描 Python 文件编码"""
    scripts_dir = Path('30-scripts-tools')
    files_with_issues = []
    
    for py_file in scripts_dir.glob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError:
            files_with_issues.append({
                'file': str(py_file),
                'issue': 'UTF-8 decoding failed'
            })
    
    return files_with_issues


def main():
    import argparse
    
    # 修复中文编码
    if sys.platform == 'win32':
        import io
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    parser = argparse.ArgumentParser(description='Critical Checks Verification')
    parser.add_argument('--verify', action='store_true', help='Run verification')
    parser.add_argument('--tool', type=str, help='Check specific tool registration')
    parser.add_argument('--file', type=str, help='Check specific file encoding')
    
    args = parser.parse_args()
    
    if args.verify:
        print("=" * 70)
        print("CRITICAL CHECKS VERIFICATION")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # 检查 1: 工具注册
        print("[CRITICAL-001] 创建的工具必须在 tools_registry.json 注册")
        print("-" * 70)
        new_tools = scan_new_tools()
        if new_tools:
            print(f"[FAIL] Found {len(new_tools)} unregistered tools:")
            for tool in new_tools:
                print(f"  - {tool['tool_name']} ({tool['file']})")
            print("Penalty: 零分 - 工具未注册")
        else:
            print("[PASS] All tools are registered")
        print()
        
        # 检查 2: UTF-8 编码
        print("[CRITICAL-002] 中文必须用 UTF-8 编码")
        print("-" * 70)
        encoding_issues = scan_py_files_for_encoding()
        if encoding_issues:
            print(f"[FAIL] Found {len(encoding_issues)} files with encoding issues:")
            for issue in encoding_issues:
                print(f"  - {issue['file']}: {issue['issue']}")
            print("Penalty: 零分 - 编码错误")
        else:
            print("[PASS] All files have valid UTF-8 encoding")
        print()
        
        # 总结
        print("=" * 70)
        total_fail = len(new_tools) + len(encoding_issues)
        if total_fail == 0:
            print("[SUCCESS] All critical checks passed!")
            sys.exit(0)
        else:
            print(f"[FAILED] {total_fail} critical check(s) failed")
            print("Penalty: 零分")
            sys.exit(1)
    
    elif args.tool:
        result = check_tool_registered(args.tool)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result['passed'] else 1)
    
    elif args.file:
        result = check_utf8_encoding(args.file)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result['passed'] else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
