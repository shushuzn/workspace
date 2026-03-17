#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git Pre-Commit Hook - 运营者检查
运营者原则：
  1. 禁止自动生成报告文件
  2. 禁止编码错误（必须 UTF-8）
  3. 禁止敏感文件提交

安装：
  python 35-scripts-tools/install-git-hooks.py
  
使用：
  自动在 git commit 时执行
  
禁用：
  git commit --no-verify
"""

import subprocess
import sys
import os
import io
import shutil

# 修复 Windows 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 报告文件关键词（命中即阻止）
BLOCKED_PATTERNS = [
    '-report-',
    'operations-report',
    'multi-persona',
    'brainstorm',
    'file-organization-plan',
    '-cleanup-',
    '-scan-',
]

# 白名单（允许的文件）
WHITELIST = [
    'README.md',
    'INDEX.md',
    '.gitignore',
]

# 敏感文件模式
SENSITIVE_PATTERNS = [
    '.env',
    'aliyun',
    'access_key',
    'secret',
    '.tiff',
]

# 允许中文文件名的目录
ALLOW_CHINESE_PATH = [
    '10-RESEARCH/',
    '99-archive/',
    '90-TESTS/',
]

# 文本文件扩展名
TEXT_EXTENSIONS = [
    '.py', '.md', '.txt', '.json', '.yaml', '.yml',
    '.js', '.ts', '.tsx', '.jsx', '.vue', '.html', '.css',
    '.sh', '.bat', '.cmd', '.ps1',
]

# 二进制文件扩展名
BINARY_EXTENSIONS = [
    '.png', '.jpg', '.jpeg', '.gif', '.ico',
    '.pdf', '.zip', '.tar', '.gz',
    '.pyc', '.pyo', '.so', '.dll',
]


def get_staged_files():
    """获取暂存区文件列表"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except Exception as e:
        print(f"❌ 获取暂存文件失败：{e}")
        return []


def is_binary_file(file_path):
    """判断是否为二进制文件"""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in BINARY_EXTENSIONS


def check_encoding(file_path):
    """检查文件编码"""
    if not os.path.exists(file_path):
        return 'OK', None
    
    if is_binary_file(file_path):
        return 'SKIP', '二进制文件'
    
    try:
        # 检查 BOM 头
        with open(file_path, 'rb') as f:
            bom = f.read(3)
            if bom == b'\xef\xbb\xbf':
                return 'ERROR', f'BOM 头 (应使用 UTF-8 without BOM)'
        
        # 尝试用 UTF-8 读取
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
            return 'OK', 'UTF-8 验证通过'
        except UnicodeDecodeError:
            return 'ERROR', f'编码错误：无法用 UTF-8 读取'
        
    except Exception as e:
        return 'ERROR', f'检查失败：{str(e)}'


def check_chinese_filename(file_path):
    """检查中文文件名"""
    for allowed_path in ALLOW_CHINESE_PATH:
        if file_path.startswith(allowed_path):
            return 'OK', '允许目录'
    
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in file_path)
    
    if has_chinese:
        return 'WARNING', f'中文文件名：{file_path} (建议英文)'
    
    return 'OK', None


def check_file(file_path):
    """检查单个文件（报告 + 敏感）"""
    # 检查敏感文件
    for pattern in SENSITIVE_PATTERNS:
        if pattern.lower() in file_path.lower():
            return 'BLOCKED', f'敏感文件：{file_path}'
    
    # 检查 21-reports/ 目录
    if file_path.startswith('21-reports/'):
        # 白名单检查
        for allowed in WHITELIST:
            if allowed in file_path:
                return 'OK', None
        
        # 阻止模式检查
        for pattern in BLOCKED_PATTERNS:
            if pattern in file_path.lower():
                return 'BLOCKED', f'自动生成报告：{file_path}'
        
        # 其他报告文件警告
        return 'WARNED', f'21-reports 新增：{file_path}'
    
    return 'OK', None


def main():
    print("🔍 运营者检查：报告文件 + 编码...")
    print()
    
    staged_files = get_staged_files()
    
    blocked_files = []
    warned_files = []
    encoding_errors = []
    filename_warnings = []
    
    for file_path in staged_files:
        # 检查报告文件 + 敏感文件
        status, message = check_file(file_path)
        if status == 'BLOCKED':
            blocked_files.append(message)
        elif status == 'WARNED':
            warned_files.append(message)
        
        # 检查编码
        status, message = check_encoding(file_path)
        if status == 'ERROR':
            encoding_errors.append(f"[编码] {file_path}: {message}")
        
        # 检查中文文件名
        status, message = check_chinese_filename(file_path)
        if status == 'WARNING':
            filename_warnings.append(message)
    
    # 处理阻止的文件
    if blocked_files:
        print()
        print("=" * 60)
        print("❌ 阻止提交：自动生成的报告文件/敏感文件")
        print("=" * 60)
        print()
        for msg in blocked_files:
            print(f"  - {msg}")
        print()
        print("解决方案:")
        print("  1. 删除文件：git reset HEAD <file> && rm <file>")
        print("  2. 或手动确认后使用：git commit --no-verify")
        print()
        print("=" * 60)
        sys.exit(1)
    
    # 处理编码错误
    if encoding_errors:
        print()
        print("=" * 60)
        print("❌ 编码错误：必须修复后才能提交")
        print("=" * 60)
        print()
        for error in encoding_errors:
            print(f"  - {error}")
        print()
        print("解决方案:")
        print("  1. 用 VSCode 打开文件，右下角选择 'UTF-8' 保存")
        print("  2. 或用 Notepad++ → 编码 → 转为 UTF-8 无 BOM")
        print("  3. 然后重新添加：git add <file>")
        print()
        print("=" * 60)
        sys.exit(1)
    
    # 处理警告文件
    all_warnings = warned_files + filename_warnings
    if all_warnings:
        print()
        print("=" * 60)
        print("⚠️  警告：建议修复，但可强制提交")
        print("=" * 60)
        print()
        for warning in all_warnings[:10]:
            print(f"  - {warning}")
        if len(all_warnings) > 10:
            print(f"  ... 还有 {len(all_warnings) - 10} 个警告")
        print()
        print("强制提交：git commit --no-verify")
        print("=" * 60)
        print()
    
    print("✅ 运营者检查通过")
    sys.exit(0)


if __name__ == '__main__':
    main()
