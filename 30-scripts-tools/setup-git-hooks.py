#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安装 Git Hooks 脚本
用法：python 30-scripts-tools/install-git-hooks.py
"""

import os
import shutil
import sys
import io

# 修复 Windows 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def main():
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hooks_dir = os.path.join(workspace, '.git', 'hooks')
    source_file = os.path.join(workspace, '30-scripts-tools', 'install-git-hooks.py')
    target_file = os.path.join(hooks_dir, 'pre-commit')
    
    # 检查 .git 目录
    if not os.path.exists(hooks_dir):
        print("❌ 错误：.git/hooks 目录不存在")
        print("   请确认这是 Git 仓库")
        sys.exit(1)
    
    # 复制文件
    print(f"📦 安装 Git Hook...")
    print(f"   源文件：{source_file}")
    print(f"   目标：{target_file}")
    
    # 创建副本作为 pre-commit
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(target_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    
    # 设置执行权限（Unix）
    if os.name != 'nt':
        os.chmod(target_file, 0o755)
    
    print()
    print("✅ Git Hook 安装成功！")
    print()
    print("功能:")
    print("  1. 禁止自动生成报告文件")
    print("  2. 禁止编码错误（必须 UTF-8）")
    print("  3. 禁止敏感文件提交（.env, 密钥等）")
    print("  4. 警告中文文件名")
    print()
    print("禁用：git commit --no-verify")
    print()

if __name__ == '__main__':
    main()
