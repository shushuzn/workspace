#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast Load - 快速加载核心上下文
跳过所有非必要文件，只加载 AI 需要的核心文件
"""

import sys
import io
from pathlib import Path

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
CORE_FILES = [
    "SOUL.md",
    "USER.md", 
    "AGENTS.md",
    "TOOLS.md",
    "HEARTBEAT.md",
    "13-memory/MEMORY.md",
]

DAILY_NOTES = "13-memory/2026-03-18.md"

def load_file(path):
    """加载单个文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"❌ 无法加载 {path}: {e}"

def main():
    print("=" * 60)
    print("Fast Load - 快速加载核心上下文")
    print("=" * 60)
    
    total_size = 0
    
    # 加载核心文件
    for file in CORE_FILES:
        path = WORKSPACE / file
        if path.exists():
            size = path.stat().st_size
            total_size += size
            print(f"✅ {file}: {size/1024:.1f}KB")
        else:
            print(f"❌ {file}: 不存在")
    
    # 加载今日笔记
    daily_path = WORKSPACE / DAILY_NOTES
    if daily_path.exists():
        size = daily_path.stat().st_size
        total_size += size
        print(f"✅ {DAILY_NOTES}: {size/1024:.1f}KB")
    
    print("=" * 60)
    print(f"总大小：{total_size/1024:.1f}KB ({total_size/1024/1024:.2f}MB)")
    print(f"Token 估算：~{total_size/4:.0f} tokens")
    print("=" * 60)
    
    # 对比全工作区
    all_files = list(WORKSPACE.rglob("*"))
    all_files = [f for f in all_files if f.is_file() and '99-backups' not in str(f)]
    total_workspace = sum(f.stat().st_size for f in all_files)
    
    print(f"\n全工作区：{total_workspace/1024/1024:.2f}MB")
    print(f"节省：{(1 - total_size/total_workspace) * 100:.1f}%")
    print(f"速度提升：{total_workspace/total_size:.1f}x")

if __name__ == "__main__":
    main()
