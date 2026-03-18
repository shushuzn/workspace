#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Pre-Check 问题批量清理工具
清理 P0 问题：BOM 头 + 报告文件 + 嵌套备份
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
BACKUP_DIR = WORKSPACE / "99-backups" / f"precheck-cleanup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def create_backup_dir():
    """创建备份目录"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"备份目录：{BACKUP_DIR}")
    return BACKUP_DIR

def fix_bom_file(file_path):
    """修复单个文件的 BOM 头"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # 检查是否有 BOM
        if data[:3] == b'\xef\xbb\xbf':
            # 移除 BOM
            with open(file_path, 'wb') as f:
                f.write(data[3:])
            return True
        return False
    except Exception as e:
        print(f"  ❌ 修复失败 {file_path}: {e}")
        return False

def fix_bom_batch(file_list):
    """批量修复 BOM"""
    print(f"\n修复 BOM 头 ({len(file_list)} 个文件)...")
    fixed = 0
    
    for file_str in file_list[:507]:  # 限制 507 个
        file_path = WORKSPACE / file_str
        if file_path.exists() and file_path.suffix in ['.md', '.txt', '.py', '.json']:
            if fix_bom_file(file_path):
                fixed += 1
                if fixed <= 10:
                    print(f"  ✅ {file_path.relative_to(WORKSPACE)}")
    
    print(f"  修复完成：{fixed}/{len(file_list)}")
    return fixed

def delete_report_files(report_list):
    """删除报告文件"""
    print(f"\n删除报告文件 ({len(report_list)} 个)...")
    deleted = 0
    
    for file_str in report_list:
        # 清理文件名 (移除"敏感文件："等前缀)
        if ':' in file_str:
            file_str = file_str.split(':')[-1].strip()
        file_path = WORKSPACE / file_str
        if file_path.exists():
            try:
                # 备份
                rel_path = file_path.relative_to(WORKSPACE)
                backup_path = BACKUP_DIR / rel_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                # 删除
                file_path.unlink()
                deleted += 1
                if deleted <= 10:
                    print(f"  🗑️ {rel_path}")
            except Exception as e:
                print(f"  ⚠️ 删除失败 {file_str}: {e}")
    
    print(f"  删除完成：{deleted}/{len(report_list)}")
    return deleted

def cleanup_nested_backups(nested_list):
    """清理嵌套备份 - 使用 del 命令"""
    print(f"\n清理嵌套备份 ({len(nested_list)} 个)...")
    
    # 提取顶层备份目录
    backup_dirs = set()
    for item in nested_list:
        parts = item.split('\\')
        if 'backups' in parts or 'backup' in parts:
            idx = parts.index('backups') if 'backups' in parts else parts.index('backup')
            backup_dir = '\\'.join(parts[:idx+2])  # backups + 时间戳
            backup_dirs.add(backup_dir)
    
    print(f"  发现 {len(backup_dirs)} 个嵌套备份目录")
    
    deleted = 0
    import subprocess
    for backup_dir in backup_dirs:
        dir_path = WORKSPACE / backup_dir
        if dir_path.exists() and dir_path.is_dir():
            print(f"  🗑️ {backup_dir}")
            try:
                # 使用 Windows del 命令删除 (处理只读文件)
                subprocess.run(
                    f'rmdir /s /q "{dir_path}"',
                    shell=True,
                    check=False
                )
                deleted += 1
            except Exception as e:
                print(f"    ⚠️ 删除失败：{e}")
    
    print(f"  清理完成：{deleted} 个目录")
    return deleted

def main():
    print("=" * 60)
    print("Git Pre-Check 问题批量清理")
    print("=" * 60)
    
    # 检查参数
    execute = len(sys.argv) > 1 and sys.argv[1] == "--execute"
    
    if not execute:
        print("\n⚠️  演示模式 - 不会实际修改文件")
        print("\n实际执行请添加 --execute 参数:")
        print("  py 30-scripts-tools/cleanup-precheck-issues.py --execute")
        return
    
    print("\n🔴 执行模式 - 将实际修改文件")
    print("备份目录将创建在：99-backups/precheck-cleanup-YYYYMMDD-HHMMSS/")
    print("\n按 Ctrl+C 取消，或等待 3 秒后继续...")
    import time
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    # 创建备份
    backup_dir = create_backup_dir()
    
    # 运行 git-precheck.py 获取问题列表
    print("\n扫描问题...")
    import subprocess
    result = subprocess.run(
        ["py", "30-scripts-tools/git-precheck.py", "--all"],
        capture_output=True,
        text=True,
        cwd=str(WORKSPACE),
        encoding='utf-8',
        errors='replace'
    )
    output = result.stdout if result.stdout else ""
    if result.stderr:
        output += result.stderr
    
    # 解析问题
    bom_files = []
    report_files = []
    nested_backups = []
    
    current_section = None
    for line in output.split('\n'):
        if '编码' in line and ':' in line:
            current_section = 'bom'
        elif '报告/敏感' in line or '报告文件' in line:
            current_section = 'report'
        elif '嵌套备份' in line:
            current_section = 'nested'
        
        if line.strip().startswith('- ') and current_section:
            file_path = line.strip()[2:].split(':')[0].strip()
            if file_path and not file_path.startswith('$'):
                if current_section == 'bom' and 'BOM' in line:
                    bom_files.append(file_path)
                elif current_section == 'report':
                    report_files.append(file_path)
                elif current_section == 'nested' and '备份目录' in line:
                    # 提取目录路径
                    parts = line.split('): ')
                    if len(parts) > 1:
                        nested_backups.append(parts[1].strip())
    
    print(f"\n发现问题:")
    print(f"  BOM 头：{len(bom_files)} 个")
    print(f"  报告文件：{len(report_files)} 个")
    print(f"  嵌套备份：{len(nested_backups)} 个")
    
    # 执行清理
    if bom_files:
        fix_bom_batch(bom_files)
    
    if report_files:
        delete_report_files(report_files)
    
    if nested_backups:
        cleanup_nested_backups(nested_backups)
    
    print("\n" + "=" * 60)
    print("✅ 清理完成！")
    print("=" * 60)
    print(f"\n备份位置：{backup_dir}")
    print("\n验证清理结果:")
    print("  py 30-scripts-tools/git-precheck.py --all")

if __name__ == "__main__":
    main()
