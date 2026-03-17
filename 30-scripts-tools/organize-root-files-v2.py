#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
根目录散落文件整理工具
移动根目录的非核心文件到正确位置
"""

import os
import sys
import io
import shutil
from pathlib import Path

# 修复 Windows 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 工作区根目录
WORKSPACE = r'D:\OpenClaw\workspace'

# 核心保留文件（留在根目录）
CORE_FILES = [
    'README.md',
    'AGENTS.md',
    'SOUL.md',
    'USER.md',
    'TOOLS.md',
    'HEARTBEAT.md',
    'TODO.md',
    'MEMORY.md',
    'LICENSE',
    'requirements.txt',
    '.gitignore',
    '.gitattributes',
]

# 文件归类规则
RULES = {
    # 配置文件 → 01-CONFIG/
    '01-CONFIG/': [
        '.autonomous_config.json',
        '.decision_log.json',
        '.health_history.json',
        'DOMAIN-CONFIG.md',
        'FELIXXII-DOMAIN-CONFIG.md',
    ],
    # 文档 → 15-docs/
    '15-docs/': [
        '7AM-RISK-WARNING-20260314.md',
        'QUICK-REFERENCE.md',
    ],
    # 数据文件 → 60-DATA/context/
    '60-DATA/context/': [
        'feishu_receive_ids.json',
    ],
}

def main():
    moved = []
    
    for target_dir, files in RULES.items():
        target_path = os.path.join(WORKSPACE, target_dir)
        
        # 确保目标目录存在
        os.makedirs(target_path, exist_ok=True)
        
        for file in files:
            src = os.path.join(WORKSPACE, file)
            dst = os.path.join(target_path, file)
            
            if os.path.exists(src):
                # 如果目标已存在，添加序号
                if os.path.exists(dst):
                    base, ext = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(dst):
                        new_name = f"{base}_{counter}{ext}"
                        dst = os.path.join(target_path, new_name)
                        counter += 1
                
                shutil.move(src, dst)
                moved.append((src, dst))
                print(f"✓ {file} → {target_dir}")
    
    print(f"\n✅ 完成：移动了 {len(moved)} 个文件")
    return moved

if __name__ == '__main__':
    main()
