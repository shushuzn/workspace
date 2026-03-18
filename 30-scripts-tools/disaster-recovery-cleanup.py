# -*- coding: utf-8 -*-
"""
灾难恢复清理脚本 - 清理 folder-organizer 嵌套备份
"""
import os
import shutil
import sys
import io

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def clean_nested_backups():
    """删除嵌套的备份目录"""
    base_dir = r"D:\OpenClaw\workspace\99-backups\folder-organizer"
    
    if not os.path.exists(base_dir):
        print("[OK] 备份目录不存在，无需清理")
        return
    
    # 扫描所有子目录
    nested_dirs = []
    for root, dirs, files in os.walk(base_dir):
        # 检测嵌套深度 (>2 层就是异常)
        depth = root.replace(base_dir, '').count(os.sep)
        if depth > 2:
            nested_dirs.append(root)
    
    if not nested_dirs:
        print("[OK] 未发现嵌套备份")
        return
    
    print(f"[WARN] 发现 {len(nested_dirs)} 个嵌套备份目录")
    
    # 删除整个 folder-organizer 目录（都是嵌套重复）
    print(f"[DEL]  删除：{base_dir}")
    shutil.rmtree(base_dir)
    print("[OK] 嵌套备份已删除")

def clean_duplicate_from_files():
    """清理 _from_ 重复文件"""
    workspace = r"D:\OpenClaw\workspace"
    deleted = 0
    
    for root, dirs, files in os.walk(workspace):
        # 跳过 .git 和 99-backups
        if '.git' in root or '99-backups' in root:
            continue
        
        for file in files:
            if '_from_' in file:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted += 1
                    print(f"[DEL]  删除：{file_path}")
                except Exception as e:
                    print(f"[FAIL] {file_path} - {e}")
    
    print(f"\n[OK] 清理完成：删除 {deleted} 个重复文件")

if __name__ == "__main__":
    print("=" * 60)
    print("灾难恢复清理 - 清理嵌套备份和重复文件")
    print("=" * 60)
    
    print("\n[1/2] 清理嵌套备份...")
    clean_nested_backups()
    
    print("\n[2/2] 清理 _from_ 重复文件...")
    clean_duplicate_from_files()
    
    print("\n" + "=" * 60)
    print("[OK] 灾难恢复清理完成！")
    print("=" * 60)
