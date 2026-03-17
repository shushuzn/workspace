#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
安全目录检查 - 防止文件创建在错误位置
用法：python safedir.py <文件路径>
"""

import os
import sys
from pathlib import Path

# 定义允许的路径
WORKSPACE = str(Path(__file__).parent.parent)
CONFIG = r"C:\Users\华为\.copaw"

# C 盘只允许这些配置文件
ALLOWED_CONFIG_FILES = ["MEMORY.md", "SOUL.md", "PROFILE.md", "AGENTS.md", "HEARTBEAT.md"]

def check_path(file_path: str, auto_fix: bool = False) -> tuple:
    """
    检查路径是否合法
    
    Returns:
        (bool, str): (是否合法，建议的正确路径)
    """
    path = Path(file_path).resolve()
    path_str = str(path)
    
    # 检查是否在配置目录
    if path_str.startswith(CONFIG):
        file_name = path.name
        if file_name not in ALLOWED_CONFIG_FILES:
            # 需要移动到工作区
            correct_path = Path(WORKSPACE) / file_name
            return False, str(correct_path)
        return True, None
    
    # 检查是否在工作区
    if path_str.startswith(WORKSPACE):
        return True, None
    
    # 其他位置 - 建议移动到工作区
    file_name = path.name
    correct_path = Path(WORKSPACE) / file_name
    return False, str(correct_path)

def main():
    if len(sys.argv) < 2:
        print("🔒 安全目录检查工具")
        print("=" * 50)
        print(f"工作区：{WORKSPACE}")
        print(f"配置区：{CONFIG} (仅限配置文件)")
        print(f"允许的配置文件：{ALLOWED_CONFIG_FILES}")
        print("=" * 50)
        print("用法：python safedir.py <文件路径> [--auto-fix]")
        print("示例：python safedir.py C:\\Users\\华为\\.copaw\\test.md")
        sys.exit(0)
    
    file_path = sys.argv[1]
    auto_fix = "--auto-fix" in sys.argv
    
    print(f"\n[SEARCH] 检查路径：{file_path}")
    
    is_valid, correct_path = check_path(file_path, auto_fix)
    
    if is_valid:
        print(f"[OK] 路径合法：{file_path}")
        sys.exit(0)
    else:
        print(f"[FAIL] 路径不合法！")
        print(f"   建议位置：{correct_path}")
        
        if auto_fix:
            # 自动移动文件
            if os.path.exists(file_path):
                print(f"\n🔄 正在移动文件...")
                os.makedirs(os.path.dirname(correct_path), exist_ok=True)
                os.rename(file_path, correct_path)
                print(f"[OK] 文件已移动到：{correct_path}")
                sys.exit(0)
            else:
                print(f"[WARN] 文件不存在，无法移动")
                sys.exit(1)
        else:
            print(f"\n[IDEA] 提示：使用 --auto-fix 自动移动文件")
            print(f"   示例：python safedir.py {file_path} --auto-fix")
            sys.exit(1)

if __name__ == "__main__":
    main()
