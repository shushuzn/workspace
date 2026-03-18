#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理 60-DATA 中的敏感文件
目标：减少 90 个敏感文件错误
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
BACKUP_DIR = WORKSPACE / "99-backups" / f"data-cleanup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def create_backup_dir():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📦 备份目录：{BACKUP_DIR}")
    return BACKUP_DIR

def scan_sensitive_files():
    """扫描 60-DATA 中的敏感文件"""
    print("\n🔍 扫描 60-DATA 中的敏感文件...")
    
    sensitive_patterns = [
        'aliyun',
        'ali-cloud',
        'access_key',
        'secret_key',
        'credential',
    ]
    
    sensitive_files = []
    data_dir = WORKSPACE / "60-DATA"
    
    if not data_dir.exists():
        print("  ⏭️ 60-DATA 目录不存在")
        return []
    
    for file_path in data_dir.rglob("*"):
        if file_path.is_file():
            file_str = str(file_path).lower()
            # 检查敏感模式
            for pattern in sensitive_patterns:
                if pattern in file_str:
                    sensitive_files.append(file_path)
                    break
            # 检查 Medium/Twitter 归档
            if 'medium' in file_str or 'twitter' in file_str or '推特' in file_str:
                if file_path not in sensitive_files:
                    sensitive_files.append(file_path)
    
    print(f"  发现 {len(sensitive_files)} 个敏感文件")
    return sensitive_files

def cleanup_sensitive_files(file_list):
    """清理敏感文件"""
    print(f"\n🗑️  清理 {len(file_list)} 个敏感文件...")
    
    deleted = 0
    for file_path in file_list[:100]:  # 限制 100 个
        try:
            rel_path = file_path.relative_to(WORKSPACE)
            
            # 备份
            backup_path = BACKUP_DIR / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # 删除
            file_path.unlink()
            print(f"  ✅ {rel_path}")
            deleted += 1
        except Exception as e:
            print(f"  ❌ 失败 {file_path}: {e}")
    
    return deleted

def main():
    print("="*60)
    print("清理 60-DATA 敏感文件")
    print("="*60)
    
    backup_dir = create_backup_dir()
    
    # 扫描
    sensitive_files = scan_sensitive_files()
    
    if not sensitive_files:
        print("\n✅ 无需清理")
        return
    
    # 清理
    deleted = cleanup_sensitive_files(sensitive_files)
    
    print("\n" + "="*60)
    print("✅ 清理完成！")
    print("="*60)
    print(f"备份位置：{backup_dir}")
    print(f"删除文件：{deleted} 个")
    print("\n下一步：运行 git-precheck.py --all 验证")

if __name__ == "__main__":
    main()
