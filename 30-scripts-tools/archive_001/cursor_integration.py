#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenClaw + Cursor IDE 联动配置器
"""

import json
import os
import sys
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(r"D:\OpenClaw\workspace")
CURSOR_CONFIG_DIR = Path(os.environ.get('APPDATA', '')) / "Cursor" / "User"

def check_cursor_installed():
    """检查 Cursor 是否安装"""
    cursor_paths = [
        Path(r"D:\cursor\resources\app\bin\cursor"),
        Path(os.environ.get('LOCALAPPDATA', '')) / "Programs" / "Cursor" / "Cursor.exe",
        Path(r"C:\Program Files\Cursor\Cursor.exe"),
    ]

    for path in cursor_paths:
        if path.exists():
            return True, path

    return False, None

def create_cursor_settings():
    """创建 Cursor 配置"""
    settings_path = CURSOR_CONFIG_DIR / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    # 读取现有设置
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    else:
        settings = {}

    # 添加 OpenClaw 配置
    settings.update({
        "openclaw.workspace": str(WORKSPACE),
        "openclaw.enabled": True,
        "cursor.aiProvider": "anthropic",
        "editor.fontSize": 14,
        "editor.tabSize": 4,
        "files.autoSave": "afterDelay",
    })

    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

    return settings_path

def main():
    print("=" * 50)
    print("OpenClaw + Cursor IDE Integration")
    print("=" * 50)
    print()

    # 1. 检查 Cursor
    print("[1/3] Checking Cursor installation...")
    installed, cursor_path = check_cursor_installed()
    if installed:
        print(f"  [OK] Cursor: {cursor_path}")
    else:
        print("  [FAIL] Cursor not found!")
        print("  Download from: https://cursor.sh")
        return

    # 2. 创建配置
    print("\n[2/3] Creating Cursor settings...")
    try:
        settings_path = create_cursor_settings()
        print(f"  [OK] Settings: {settings_path}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # 3. 说明
    print("\n[3/3] Setup complete!")
    print()
    print("How to use:")
    print("  1. Open Cursor IDE")
    print("  2. Open folder: D:\\OpenClaw\\workspace")
    print("  3. Use Ctrl+K for AI commands")
    print("  4. Use Ctrl+L for chat")
    print()
    print("Shortcut:")
    print('  D:\\cursor\\resources\\app\\bin\\cursor.cmd "D:\\OpenClaw\\workspace"')

if __name__ == "__main__":
    main()
