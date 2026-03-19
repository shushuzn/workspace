#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具调用规则审查脚本
检查代码是否遵守：
1. 禁止重写工具
2. 统一调用（通过 tool_executor）
3. 工具必须注册
"""

import os
import re
import json
import sys
import io
from pathlib import Path

# 设置 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / "30-scripts-tools"
REGISTRY_FILE = SCRIPTS_DIR / "tools_registry.json"

# 排除文件
EXCLUDE_FILES = [
    'tool_executor.py',
    'auto_execute_workflow.py',
    'register_tools.py',
    'check_tool_rules.py',
    'fix_tool_commands.py',
    'execute_step_fixed.py',
]

def load_registry():
    """加载工具注册表"""
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_registered_tools():
    """获取已注册的工具 ID 列表"""
    registry = load_registry()
    return set(registry.get('tools', {}).keys())

def get_all_py_files():
    """获取所有 Python 文件"""
    py_files = []
    for root, dirs, files in os.walk(SCRIPTS_DIR):
        # 排除子目录
        if '99-' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py') and file not in EXCLUDE_FILES:
                py_files.append(Path(root) / file)
    return py_files

def check_direct_tool_calls(file_path):
    """检查直接调用工具脚本"""
    violations = []
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    
    # 模式：subprocess.run 直接调用 .py 文件
    patterns = [
        r"subprocess\.run\(\[.*?['\"]py['\"].*?\.py",
        r"subprocess\.run\(\[.*?python.*?\.py",
        r"os\.system\(['\"].*?\.py",
        r"subprocess\.call\(\[.*?['\"]py['\"].*?\.py",
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # 检查是否调用了 tool_executor
            if 'tool_executor' not in match.group():
                violations.append({
                    'type': 'direct_tool_call',
                    'line': content[:match.start()].count('\n') + 1,
                    'code': match.group()[:100],
                    'rule': '统一调用原则：所有工具只能通过 tool_executor.py 调用'
                })
    
    return violations

def check_tool_modification(file_path):
    """检查重写/修改工具脚本"""
    violations = []
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    
    # 模式：写入 .py 文件
    patterns = [
        r"open\(['\"].*?\.py['\"].*?['\"]w['\"]",
        r"open\(['\"].*?\.py['\"].*?['\"]a['\"]",
        r"write\(.*?\.py",
        r"shutil\.copy.*?\.py",
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # 排除配置文件和测试文件
            if 'tools_registry.json' in match.group() or 'test' in str(file_path).lower():
                continue
            violations.append({
                'type': 'tool_modification',
                'line': content[:match.start()].count('\n') + 1,
                'code': match.group()[:100],
                'rule': '禁止重写工具原则：所有工具脚本禁止被其他脚本重写或修改'
            })
    
    return violations

def check_unregistered_tools():
    """检查未注册的工具"""
    registered = get_registered_tools()
    
    # 获取所有 .py 文件（不含 .pyc 和 _ 开头）
    py_files = [f.stem.replace('-', '_') for f in SCRIPTS_DIR.glob('*.py') 
                if not f.name.startswith('_') and f.stem not in EXCLUDE_FILES]
    
    unregistered = set(py_files) - registered
    
    violations = []
    for tool_id in unregistered:
        violations.append({
            'type': 'unregistered_tool',
            'tool_id': tool_id,
            'rule': '工具注册原则：新工具必须注册到 tools_registry.json'
        })
    
    return violations

def main():
    print("="*60)
    print("工具调用规则审查")
    print("="*60)
    print()
    
    all_violations = []
    
    # 检查所有 Python 文件
    py_files = get_all_py_files()
    print(f"[INFO] 检查 {len(py_files)} 个 Python 文件...")
    
    for py_file in py_files:
        # 检查直接调用
        violations = check_direct_tool_calls(py_file)
        for v in violations:
            v['file'] = str(py_file.relative_to(WORKSPACE))
            all_violations.append(v)
        
        # 检查工具修改
        violations = check_tool_modification(py_file)
        for v in violations:
            v['file'] = str(py_file.relative_to(WORKSPACE))
            all_violations.append(v)
    
    # 检查未注册工具
    unregistered = check_unregistered_tools()
    for v in unregistered:
        v['file'] = 'N/A'
        all_violations.append(v)
    
    # 输出结果
    print()
    if not all_violations:
        print("✅ 无违规！所有代码遵守工具调用规则")
    else:
        print(f"🚨 发现 {len(all_violations)} 个违规项")
        print()
        
        # 分类统计
        by_type = {}
        for v in all_violations:
            t = v['type']
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(v)
        
        for vtype, violations in by_type.items():
            print(f"\n{vtype.upper()} ({len(violations)} 个):")
            print("-" * 60)
            for v in violations[:5]:  # 只显示前 5 个
                print(f"  文件：{v.get('file', 'N/A')}")
                if 'line' in v:
                    print(f"  行号：{v['line']}")
                if 'code' in v:
                    print(f"  代码：{v['code']}...")
                if 'tool_id' in v:
                    print(f"  工具：{v['tool_id']}")
                print(f"  规则：{v['rule']}")
                print()
            
            if len(violations) > 5:
                print(f"  ... 还有 {len(violations) - 5} 个违规")
    
    print()
    print("="*60)
    print(f"审查完成：{len(all_violations)} 个违规项")
    print("="*60)
    
    return 0 if not all_violations else 1

if __name__ == '__main__':
    sys.exit(main())
