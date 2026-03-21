import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速加载验证器 - 验证 7 个核心文件加载
根据 AGENTS.md 中的规范检查上下文加载效率
"""

import os
from pathlib import Path

def check_core_files():
    """检查 7 个核心文件"""
    workspace = Path(__file__).parent.parent
    
    core_files = [
        'SOUL.md',
        'USER.md', 
        'AGENTS.md',
        'TOOLS.md',
        'HEARTBEAT.md',
        'MEMORY.md',
        '13-memory/2026-03-20.md'  # 今日笔记
    ]
    
    total_size = 0
    results = []
    
    print("=" * 60)
    print("核心文件加载检查")
    print("=" * 60)
    
    for file_path in core_files:
        full_path = workspace / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            total_size += size
            status = "[OK]" if size < 20000 else "[WARN]"  # 警告超过 20KB 的文件
            results.append(f"{status} {file_path:<35} {size:>6,} bytes")
        else:
            results.append(f"[MISSING] {file_path:<35} MISSING")
    
    for r in results:
        print(r)
    
    print("=" * 60)
    
    # 计算统计
    total_kb = total_size / 1024
    
    print(f"\n总大小: {total_size:,} bytes ({total_kb:.1f} KB)")
    
    # 目标: <100KB
    if total_kb < 100:
        print(f"状态: [OK] 符合目标 (<100KB)")
    else:
        print(f"状态: [FAIL] 超过目标 (>100KB)")
    
    # 速度提升计算 (假设全工作区 560MB)
    workspace_size_mb = 560
    compressed_size_kb = total_kb
    speed_improvement = (workspace_size_mb * 1024) / compressed_size_kb
    
    print(f"速度提升: {speed_improvement:.0f}x (相比全工作区扫描)")
    print("=" * 60)
    
    return total_size

if __name__ == "__main__":
    check_core_files()