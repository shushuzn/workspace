#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具优化执行器
1. 合并多版本工具
2. 迁移测试文件到 92-tests/
3. 清理空文件
"""

import os
import sys
import io
import shutil
from pathlib import Path
from datetime import datetime

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path(__file__).parent.parent / "30-scripts-tools"
TESTS_DIR = Path(__file__).parent.parent / "92-tests"

def merge_duplicate_versions():
    """合并多版本工具"""
    print("\n" + "="*60)
    print("🔧 合并多版本工具")
    print("="*60)
    
    duplicates = {
        'config_center': ('config_center.py', 'config_center_v2.py'),
        'test_feishu_tools': ('test_feishu_tools.py', 'test_feishu_tools_v2.py'),
        'unified_dashboard': ('unified_dashboard.py', 'unified_dashboard_v3.py'),
        'workflow_engine': ('workflow_engine.py', 'workflow_engine_v2.py'),
    }
    
    merged = 0
    for base_name, (old_file, new_file) in duplicates.items():
        old_path = TOOLS_DIR / old_file
        new_path = TOOLS_DIR / new_file
        
        if old_path.exists() and new_path.exists():
            old_size = old_path.stat().st_size
            new_size = new_path.stat().st_size
            
            # 保留新版本，删除旧版本
            print(f"\n{base_name}:")
            print(f"  删除：{old_file} ({old_size/1024:.1f}KB)")
            print(f"  保留：{new_file} ({new_size/1024:.1f}KB)")
            
            # 备份旧版本
            backup_dir = TOOLS_DIR.parent / "99-backups" / f"tool-optimization-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old_path, backup_dir / old_file)
            
            # 删除旧版本
            old_path.unlink()
            merged += 1
            print(f"  ✅ 已删除 (备份到 {backup_dir})")
        elif new_path.exists():
            print(f"\n{base_name}: 仅新版本存在，跳过")
        else:
            print(f"\n{base_name}: 文件不存在，跳过")
    
    return merged

def migrate_test_files():
    """迁移测试文件到 92-tests/"""
    print("\n" + "="*60)
    print("📦 迁移测试文件")
    print("="*60)
    
    test_files = list(TOOLS_DIR.glob("test_*.py"))
    
    if not test_files:
        print("\n无测试文件可迁移")
        return 0
    
    # 创建目标目录
    target_dir = TESTS_DIR / "tools-tests"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    migrated = 0
    for test_file in test_files:
        if test_file.name == 'test_feishu_tools.py':
            # 这个已经被删除了
            continue
        
        src = test_file
        dst = target_dir / test_file.name
        
        print(f"\n迁移：{test_file.name}")
        shutil.copy2(src, dst)
        src.unlink()
        migrated += 1
        print(f"  ✅ {src.parent} → {dst.parent}")
    
    return migrated

def cleanup_empty_files():
    """清理空文件"""
    print("\n" + "="*60)
    print("🗑️  清理空文件")
    print("="*60)
    
    empty_files = [f for f in TOOLS_DIR.glob("*.py") if f.stat().st_size == 0]
    
    cleaned = 0
    for empty_file in empty_files:
        print(f"\n删除空文件：{empty_file.name}")
        empty_file.unlink()
        cleaned += 1
    
    if not empty_files:
        print("\n✅ 无空文件")
    
    return cleaned

def main():
    print("="*60)
    print("🚀 工具优化执行")
    print("="*60)
    
    # 1. 合并多版本
    merged = merge_duplicate_versions()
    
    # 2. 迁移测试文件
    migrated = migrate_test_files()
    
    # 3. 清理空文件
    cleaned = cleanup_empty_files()
    
    # 总结
    print("\n" + "="*60)
    print("✅ 优化完成！")
    print("="*60)
    print(f"合并版本：{merged} 组")
    print(f"迁移测试：{migrated} 个")
    print(f"清理空文件：{cleaned} 个")
    print(f"\n下一步：运行 git add -A && git commit -m '优化：工具精简'")

if __name__ == "__main__":
    main()
