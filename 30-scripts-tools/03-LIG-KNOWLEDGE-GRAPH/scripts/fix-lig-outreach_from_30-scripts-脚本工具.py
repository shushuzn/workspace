#!/usr/bin/env python3
"""修复 LIG 科普笔记命名 - 安全版本"""

import os
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

OUTREACH_DIR = Path("D:/OpenClaw/workspace/40-arxiv/lig-outreach")

def main():
    files = list(OUTREACH_DIR.glob("*.md"))
    print(f"找到 {len(files)} 个文件")
    
    # 分离两种命名
    old_style = [f for f in files if f.stem.startswith(tuple(str(i) for i in range(10))) and "-" in f.stem and not f.stem.startswith("lig-outreach")]
    new_style = [f for f in files if f.stem.startswith("lig-outreach-")]
    
    print(f"旧格式 (001-xxx.md): {len(old_style)} 个")
    print(f"新格式 (lig-outreach-XX.md): {len(new_style)} 个")
    
    # 删除旧格式（保留新格式）
    for f in old_style:
        print(f"删除：{f.name}")
        f.unlink()
    
    # 重命名新格式统一为 2 位数字
    remaining = list(OUTREACH_DIR.glob("lig-outreach-*.md"))
    remaining.sort(key=lambda x: int(x.stem.split("-")[1]) if x.stem.split("-")[1].isdigit() else 999)
    
    for i, f in enumerate(remaining, 1):
        old_num = int(f.stem.split("-")[1]) if f.stem.split("-")[1].isdigit() else 999
        if old_num != i:
            new_name = f"lig-outreach-{i:02d}.md"
            print(f"重命名：{f.name} → {new_name}")
            f.rename(OUTREACH_DIR / new_name)
    
    final = list(OUTREACH_DIR.glob("lig-outreach-*.md"))
    print(f"\n完成！共 {len(final)} 篇")

if __name__ == "__main__":
    main()
