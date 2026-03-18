#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git Hook 安装脚本 v2

安装运营者 Git Pre-Commit Hook:
  - 报告文件阻止
  - 编码检查 (UTF-8)
  - 敏感文件阻止
  - 大文件阻止 (>50MB)
  - 嵌套备份检测
  - 中文文件名警告
  - 批判者 v5.0 审查集成

安装:
  python 30-scripts-tools/install-git-hooks.py
  
使用:
  自动在 git commit 时执行
  
禁用:
  git commit --no-verify
"""

import subprocess
import sys
import os
import io
import shutil
from pathlib import Path

# 修复 Windows 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
GIT_DIR = WORKSPACE / '.git'
HOOKS_DIR = GIT_DIR / 'hooks'
HOOK_SOURCE = WORKSPACE / '30-scripts-tools' / 'git-pre-commit-hook.py'
HOOK_DEST = HOOKS_DIR / 'pre-commit'


def install_hook():
    """安装 Git Hook"""
    print("="*60)
    print("Git Hook 安装脚本 v2")
    print("="*60)
    print()
    
    # 检查 .git 目录
    if not GIT_DIR.exists():
        print("[ERROR] .git 目录不存在")
        print("        请先运行：git init")
        return 1
    
    # 创建 hooks 目录
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 检查源文件
    if not HOOK_SOURCE.exists():
        print(f"[ERROR] Hook 源文件不存在：{HOOK_SOURCE}")
        return 1
    
    # 复制 Hook 文件
    try:
        shutil.copy2(HOOK_SOURCE, HOOK_DEST)
        print(f"[OK] 复制 Hook: {HOOK_SOURCE} → {HOOK_DEST}")
    except Exception as e:
        print(f"[ERROR] 复制失败：{e}")
        return 1
    
    # 设置执行权限 (Unix)
    if sys.platform != 'win32':
        try:
            os.chmod(HOOK_DEST, 0o755)
            print("[OK] 设置执行权限")
        except Exception as e:
            print(f"[WARN] 权限设置失败：{e}")
    
    # 创建包装脚本 (Windows)
    if sys.platform == 'win32':
        bat_content = f"""@echo off
chcp 65001 >nul
py "{HOOK_DEST}" %*
"""
        bat_path = HOOKS_DIR / 'pre-commit.bat'
        try:
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            print(f"[OK] 创建 Windows 包装：{bat_path}")
        except Exception as e:
            print(f"[WARN] 创建包装失败：{e}")
    
    print()
    print("="*60)
    print("✅ Git Hook 安装成功!")
    print("="*60)
    print()
    print("功能:")
    print("  - 阻止报告文件提交 (-report-*.md)")
    print("  - 阻止敏感文件提交 (.env, aliyun, etc.)")
    print("  - 阻止大文件提交 (>50MB)")
    print("  - 编码检查 (UTF-8 without BOM)")
    print("  - 嵌套备份检测 (>5 层)")
    print("  - 中文文件名警告")
    print("  - 批判者 v5.0 审查集成 (git_operation)")
    print()
    print("测试:")
    print("  git commit -m \"test\"")
    print()
    print("跳过:")
    print("  git commit --no-verify")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(install_hook())
