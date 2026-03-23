#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""设置 Cursor 为默认代码编辑器"""

import os
import sys
import winreg
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

CURSOR_PATH = r"D:\cursor\resources\app\bin\cursor.cmd"
WORKSPACE = r"D:\OpenClaw\workspace"

# 代码文件扩展名
CODE_EXTENSIONS = [
    ('.py', 'Python'),
    ('.js', 'JavaScript'),
    ('.ts', 'TypeScript'),
    ('.jsx', 'React JSX'),
    ('.tsx', 'React TSX'),
    ('.html', 'HTML'),
    ('.css', 'CSS'),
    ('.json', 'JSON'),
    ('.md', 'Markdown'),
    ('.txt', 'Text'),
    ('.yaml', 'YAML'),
    ('.yml', 'YAML'),
    ('.xml', 'XML'),
    ('.sh', 'Shell'),
    ('.bat', 'Batch'),
    ('.ps1', 'PowerShell'),
]

def set_default_app(ext, app_path):
    """设置文件关联"""
    try:
        # 使用 ftype 和 assoc 设置文件关联
        ext_name = ext.lstrip('.')

        # 设置文件类型关联
        cmd_ftype = f'ftype Cursor.{ext_name}="{app_path}" "%1"'
        os.system(cmd_ftype)

        # 设置扩展名关联
        cmd_assoc = f'assoc {ext}=Cursor.{ext_name}'
        os.system(cmd_assoc)

        return True
    except Exception as e:
        print(f"  [FAIL] {ext}: {e}")
        return False

def create_cursor_shortcuts():
    """创建桌面快捷方式"""
    import win32com.client

    desktop = Path(os.environ['USERPROFILE']) / 'Desktop'
    cursor_exe = r"D:\cursor\resources\cursor.exe"

    shortcuts = []

    # Cursor 快捷方式
    try:
        shell = win32com.client.Dispatch("WScript.Shell")

        # 主快捷方式
        shortcut = shell.CreateShortCut(str(desktop / "Cursor IDE.lnk"))
        shortcut.Targetpath = cursor_exe
        shortcut.WorkingDirectory = WORKSPACE
        shortcut.Description = "Cursor IDE - OpenClaw Workspace"
        shortcut.Save()
        shortcuts.append("Cursor IDE.lnk")
    except Exception as e:
        print(f"  [SKIP] Shortcut: {e}")

    return shortcuts

def add_to_path():
    """添加到 PATH"""
    try:
        # 获取用户 PATH
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Environment", 0, winreg.KEY_READ)
        path_value, _ = winreg.QueryValueEx(key, "Path")
        winreg.CloseKey(key)

        # 添加 Cursor 到 PATH
        cursor_bin = r"D:\cursor\resources\app\bin"
        if cursor_bin not in path_value:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Environment", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ,
                             path_value + ";" + cursor_bin)
            winreg.CloseKey(key)
            return True
        return False
    except Exception as e:
        print(f"  [FAIL] PATH: {e}")
        return False

def main():
    print("=" * 50)
    print("Set Cursor as Default Editor")
    print("=" * 50)
    print()

    # 1. 创建快捷方式
    print("[1/3] Creating desktop shortcuts...")
    shortcuts = create_cursor_shortcuts()
    if shortcuts:
        print(f"  [OK] Created: {', '.join(shortcuts)}")
    else:
        print("  [SKIP] No shortcuts created")

    # 2. 添加到 PATH
    print("\n[2/3] Adding Cursor to PATH...")
    if add_to_path():
        print("  [OK] Added to PATH")
        print("  Note: You may need to restart terminals")
    else:
        print("  [SKIP] Already in PATH or failed")

    # 3. 提示文件关联
    print("\n[3/3] File associations...")
    print("  To set Cursor as default for code files:")
    print("  1. Right-click any .py/.js file")
    print("  2. Choose 'Open with' → 'Choose another app'")
    print("  3. Select Cursor and check 'Always use this app'")
    print()
    print("  Or run (as admin):")
    print(f'    ftype Cursor.py="D:\\cursor\\resources\\app\\bin\\cursor.cmd" "%1"')
    print()

    print("=" * 50)
    print("Done!")
    print("=" * 50)

if __name__ == "__main__":
    main()
