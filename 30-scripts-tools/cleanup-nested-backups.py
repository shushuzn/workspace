#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理嵌套备份目录 (99-backups 除外)
"""

import sys
import io
import subprocess
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent

def main():
    print("=" * 60)
    print("清理嵌套备份目录")
    print("=" * 60)
    
    # 查找所有 backups 目录 (排除 99-backups)
    print("\n扫描备份目录...")
    backup_dirs = []
    
    for dir_path in WORKSPACE.rglob("backups"):
        if dir_path.is_dir() and '99-backups' not in str(dir_path):
            # 检查是否是嵌套备份 (路径中有时间戳)
            parent = dir_path.parent
            if any(c.isdigit() for c in str(parent)) or 'backup' in str(parent).lower():
                backup_dirs.append(dir_path)
    
    print(f"发现 {len(backup_dirs)} 个嵌套备份目录")
    
    if not backup_dirs:
        print("✅ 无需清理")
        return
    
    print("\n按 Ctrl+C 取消，或等待 3 秒后继续...")
    import time
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    # 删除目录
    deleted = 0
    for dir_path in backup_dirs:
        try:
            print(f"  🗑️ {dir_path.relative_to(WORKSPACE)}")
            subprocess.run(
                f'rmdir /s /q "{dir_path}"',
                shell=True,
                check=False
            )
            deleted += 1
        except Exception as e:
            print(f"    ⚠️ 删除失败：{e}")
    
    print(f"\n清理完成：{deleted} 个目录")

if __name__ == "__main__":
    main()
