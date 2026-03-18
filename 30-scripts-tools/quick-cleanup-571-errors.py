#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Pre-Check 快速清理 - 处理 571 个错误
只处理 P0 问题：敏感文件 + BOM 头（研究目录中文文件名保留）
"""

import os
import sys
import io
import shutil
from pathlib import Path
from datetime import datetime

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
BACKUP_DIR = WORKSPACE / "99-backups" / f"precheck-quick-cleanup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def create_backup_dir():
    """创建备份目录"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📦 备份目录：{BACKUP_DIR}")
    return BACKUP_DIR

def fix_bom_file(file_path):
    """修复单个文件的 BOM 头"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        if data[:3] == b'\xef\xbb\xbf':
            with open(file_path, 'wb') as f:
                f.write(data[3:])
            return True
        return False
    except Exception as e:
        return False

# 敏感文件列表（从 git-precheck 输出提取）
SENSITIVE_FILES = [
    # 阿里云相关
    "30-scripts-tools/01-SETUP/setup-aliyun-ecs.bat",
    "30-scripts-tools/01-SETUP/setup-aliyun-ecs.py",
    # Medium 归档（包含敏感内容）
    "08-collectors/medium-文章/Medium/Archive/2026-03-05/2026-03-05_2603.05494v1_Censored-LLMs-as-a-Natural-Testbed-for-Secret-Know.md",
    "08-collectors/medium-文章/Medium/Archive/2026-03-06/medium-2026-03-06-El-Arma-Secreta-que-transformar-la-gerencia-de-pr.md",
    # Twitter 归档
    "08-collectors/twitter-推特/daily/2026/2026-03/2026-03-02/20260302-201508-AnthropicAI-Pinned A statement on the comments from Secretary of War Pet.md",
]

# BOM 头文件（研究目录除外，只处理配置/工具文件）
BOM_FILES_TO_FIX = [
    "TOOLS.md",
    "USER.md",
    "AGENTS.md",
    "SOUL.md",
    "HEARTBEAT.md",
]

def cleanup_sensitive_files():
    """清理敏感文件"""
    print("\n" + "="*60)
    print("🔒 清理敏感文件")
    print("="*60)
    
    deleted = 0
    for file_str in SENSITIVE_FILES:
        file_path = WORKSPACE / file_str
        if file_path.exists():
            # 备份
            rel_path = file_path.relative_to(WORKSPACE)
            backup_path = BACKUP_DIR / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # 删除
            file_path.unlink()
            print(f"  ✅ 删除：{rel_path}")
            deleted += 1
        else:
            print(f"  ⏭️  不存在：{file_str}")
    
    print(f"\n删除了 {deleted} 个敏感文件")
    return deleted

def fix_bom_batch():
    """批量修复 BOM 头"""
    print("\n" + "="*60)
    print("🔧 修复 BOM 头文件")
    print("="*60)
    
    fixed = 0
    for file_str in BOM_FILES_TO_FIX:
        file_path = WORKSPACE / file_str
        if file_path.exists():
            if fix_bom_file(file_path):
                print(f"  ✅ 修复：{file_path.relative_to(WORKSPACE)}")
                fixed += 1
            else:
                print(f"  ⏭️  无需修复：{file_path.relative_to(WORKSPACE)}")
    
    print(f"\n修复了 {fixed} 个 BOM 文件")
    return fixed

def main():
    print("="*60)
    print("Git Pre-Check 快速清理 - 处理 571 错误")
    print("="*60)
    
    backup_dir = create_backup_dir()
    
    # 1. 清理敏感文件
    deleted = cleanup_sensitive_files()
    
    # 2. 修复 BOM 头
    fixed = fix_bom_batch()
    
    print("\n" + "="*60)
    print("✅ 清理完成！")
    print("="*60)
    print(f"备份位置：{backup_dir}")
    print(f"删除敏感文件：{deleted} 个")
    print(f"修复 BOM 头：{fixed} 个")
    print("\n下一步：运行 git-precheck.py --all 验证")

if __name__ == "__main__":
    main()
