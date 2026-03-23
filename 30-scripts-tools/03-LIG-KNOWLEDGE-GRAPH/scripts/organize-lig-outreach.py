#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理 LIG 科普笔记 - 去重 + 统一命名
"""

import os
import sys
import hashlib
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

OUTREACH_DIR = Path("D:/OpenClaw/workspace/40-arxiv/lig-outreach")
BACKUP_DIR = Path("D:/OpenClaw/workspace/40-arxiv/Archive/lig-outreach-backup")

def get_file_hash(filepath):
    """计算文件 MD5"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def main():
    # 创建备份
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # 获取所有 MD 文件
    md_files = list(OUTREACH_DIR.glob("*.md"))
    print(f"📁 找到 {len(md_files)} 个 MD 文件")

    # 按内容去重
    hash_to_file = {}
    duplicates = []

    for filepath in md_files:
        file_hash = get_file_hash(filepath)
        if file_hash in hash_to_file:
            duplicates.append((filepath, hash_to_file[file_hash]))
        else:
            hash_to_file[file_hash] = filepath

    print(f"🔄 发现 {len(duplicates)} 个重复文件")

    # 移动重复文件到备份
    for dup, original in duplicates:
        backup_path = BACKUP_DIR / dup.name
        shutil.move(str(dup), str(backup_path))
        print(f"  📦 备份：{dup.name}")

    # 剩余文件重命名
    unique_files = list(OUTREACH_DIR.glob("*.md"))
    print(f"\n✅ 剩余 {len(unique_files)} 个唯一文件")

    # 按内容排序（根据标题提取序号）
    def extract_number(filepath):
        name = filepath.stem
        # 尝试匹配 lig-outreach-XX 或 XX-
        if "lig-outreach-" in name:
            parts = name.split("lig-outreach-")
            if len(parts) > 1 and parts[1].isdigit():
                return int(parts[1])
        # 尝试匹配开头的数字
        if name[0:3].isdigit():
            return int(name.split("-")[0])
        return 999

    unique_files.sort(key=extract_number)

    # 重命名为 lig-outreach-XXX.md
    for i, filepath in enumerate(unique_files, 1):
        new_name = f"lig-outreach-{i:02d}.md"
        new_path = OUTREACH_DIR / new_name
        if filepath.name != new_name:
            shutil.move(str(filepath), str(new_path))
            print(f"  ✏️  重命名：{filepath.name} → {new_name}")

    print(f"\n🎉 整理完成！")
    print(f"📊 最终数量：{len(unique_files)} 篇")
    print(f"📦 备份数量：{len(duplicates)} 篇")

if __name__ == "__main__":
    main()
