#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动备份工具 - 修改文件前自动备份
"""
import shutil
import json
from pathlib import Path
from datetime import datetime

BACKUP_DIR = Path("99-backups/auto")

def auto_backup(file_path: str) -> dict:
    """自动备份文件"""

    src = Path(file_path)
    if not src.exists():
        return {
            "status": "skip",
            "reason": "文件不存在",
            "file": file_path
        }

    # 创建备份目录
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"{src.stem}_{timestamp}{src.suffix}"
    dst = BACKUP_DIR / backup_name

    # 执行备份
    shutil.copy2(src, dst)

    return {
        "status": "success",
        "original": str(src),
        "backup": str(dst),
        "size": dst.stat().st_size,
        "timestamp": timestamp
    }

def main():
    import sys

    if len(sys.argv) < 2:
        # 测试模式
        print("自动备份工具测试")
        print("=" * 60)

        test_files = [
            "30-scripts-tools/tools_registry.json",
            "flow-archive/20260318-universal-workflow-001/execution-state.json",
            "non_existent_file.txt"
        ]

        for f in test_files:
            result = auto_backup(f)
            print(f"\n文件：{f}")
            print(f"状态：{result['status']}")
            if result['status'] == 'success':
                print(f"备份：{result['backup']}")

        return 0

    # 实际备份模式
    file_path = sys.argv[1]
    result = auto_backup(file_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if result['status'] == 'success' else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
