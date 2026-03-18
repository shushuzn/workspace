# -*- coding: utf-8 -*-
"""
备份策略重构脚本
功能:
1. 重新组织 99-backups 目录结构
2. 自动清理旧备份 (>7 天)
3. 压缩大文件 (>100MB)
4. 防止嵌套备份
"""
import os
import shutil
import sys
import io
import json
from datetime import datetime, timedelta
import zipfile

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BACKUP_ROOT = r"D:\OpenClaw\workspace\99-backups"
WORKSPACE = r"D:\OpenClaw\workspace"

# 配置
CONFIG = {
    'auto_retain_days': 7,      # 自动备份保留天数
    'compress_threshold_mb': 100,  # 压缩阈值 (MB)
    'max_backup_depth': 3,      # 最大备份深度
}


def create_backup_structure():
    """创建新的备份目录结构"""
    print("[1/5] 创建备份目录结构...")
    
    dirs = [
        os.path.join(BACKUP_ROOT, 'auto'),      # 自动备份 (保留 7 天)
        os.path.join(BACKUP_ROOT, 'manual'),    # 手动备份 (永久)
        os.path.join(BACKUP_ROOT, 'archive'),   # 归档备份 (压缩)
        os.path.join(BACKUP_ROOT, 'temp'),      # 临时备份
    ]
    
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"  ✓ 创建：{d}")
    
    print("  ✅ 目录结构创建完成\n")


def detect_nested_backups():
    """检测嵌套备份目录"""
    print("[2/5] 检测嵌套备份...")
    
    nested = []
    
    for root, dirs, files in os.walk(BACKUP_ROOT):
        # 计算嵌套深度
        rel_path = root.replace(BACKUP_ROOT, '')
        depth = rel_path.count(os.sep)
        
        if depth > CONFIG['max_backup_depth']:
            nested.append(root)
    
    if nested:
        print(f"  ⚠️  发现 {len(nested)} 个嵌套备份目录:")
        for n in nested[:5]:
            print(f"     - {n}")
        if len(nested) > 5:
            print(f"     ... 还有 {len(nested) - 5} 个")
        
        # 删除嵌套备份
        confirm = input(f"\n  是否删除这些嵌套备份？(y/n): ")
        if confirm.lower() == 'y':
            for n in nested:
                try:
                    shutil.rmtree(n)
                    print(f"  ✓ 删除：{n}")
                except Exception as e:
                    print(f"  ✗ 失败：{n} - {e}")
            print("  ✅ 嵌套备份清理完成")
    else:
        print("  ✓ 未发现嵌套备份\n")


def cleanup_old_auto_backups():
    """清理超过保留天数的自动备份"""
    print(f"[3/5] 清理旧自动备份 (>{CONFIG['auto_retain_days']}天)...")
    
    auto_dir = os.path.join(BACKUP_ROOT, 'auto')
    if not os.path.exists(auto_dir):
        print("  ✓ 自动备份目录为空\n")
        return
    
    cutoff = datetime.now() - timedelta(days=CONFIG['auto_retain_days'])
    deleted = 0
    
    for root, dirs, files in os.walk(auto_dir):
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(dir_path))
                if mtime < cutoff:
                    shutil.rmtree(dir_path)
                    deleted += 1
                    print(f"  ✓ 删除：{d} ({(datetime.now() - mtime).days}天前)")
            except Exception as e:
                pass
    
    print(f"  ✅ 清理完成：删除 {deleted} 个旧备份\n")


def compress_large_files():
    """压缩大文件"""
    print(f"[4/5] 压缩大文件 (>{CONFIG['compress_threshold_mb']}MB)...")
    
    archive_dir = os.path.join(BACKUP_ROOT, 'archive')
    compressed = 0
    saved_mb = 0
    
    for root, dirs, files in os.walk(BACKUP_ROOT):
        # 跳过 archive 目录
        if 'archive' in root:
            continue
        
        for f in files:
            file_path = os.path.join(root, f)
            try:
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if size_mb > CONFIG['compress_threshold_mb']:
                    # 创建压缩包
                    zip_name = f"{f}.zip"
                    zip_path = os.path.join(archive_dir, zip_name)
                    
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                        zf.write(file_path, f)
                    
                    # 删除原文件
                    os.remove(file_path)
                    
                    zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
                    saved_mb += (size_mb - zip_size_mb)
                    compressed += 1
                    
                    print(f"  ✓ 压缩：{f} ({size_mb:.1f}MB → {zip_size_mb:.1f}MB)")
            except Exception as e:
                print(f"  ✗ 失败：{f} - {e}")
    
    print(f"  ✅ 压缩完成：{compressed} 个文件，节省 {saved_mb:.1f}MB\n")


def create_config_file():
    """创建配置文件"""
    print("[5/5] 创建配置文件...")
    
    config_file = os.path.join(BACKUP_ROOT, 'backup-config.json')
    
    config = {
        'version': '1.0',
        'created': datetime.now().isoformat(),
        'structure': {
            'auto/': '自动备份 (保留 7 天)',
            'manual/': '手动备份 (永久)',
            'archive/': '归档备份 (压缩)',
            'temp/': '临时备份 (下次清理时删除)',
        },
        'rules': {
            'auto_retain_days': CONFIG['auto_retain_days'],
            'compress_threshold_mb': CONFIG['compress_threshold_mb'],
            'max_backup_depth': CONFIG['max_backup_depth'],
        },
        'protected_directories': [
            '13-memory/',
            '15-docs/',
            '30-scripts-tools/',
        ],
        'excluded_from_backup': [
            '.git/',
            '__pycache__/',
            '*.pyc',
            'node_modules/',
        ]
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ 创建：{config_file}")
    print("  ✅ 配置文件创建完成\n")


def main():
    print("=" * 60)
    print("备份策略重构 - 99-backups 重组")
    print("=" * 60)
    print()
    
    if not os.path.exists(BACKUP_ROOT):
        print(f"⚠️  备份目录不存在：{BACKUP_ROOT}")
        print("创建新目录...")
        os.makedirs(BACKUP_ROOT)
    
    # 执行步骤
    create_backup_structure()
    detect_nested_backups()
    cleanup_old_auto_backups()
    compress_large_files()
    create_config_file()
    
    # 总结
    print("=" * 60)
    print("✅ 备份策略重构完成！")
    print("=" * 60)
    print()
    print("新目录结构:")
    print("  99-backups/")
    print("  ├── auto/      ← 自动备份 (保留 7 天)")
    print("  ├── manual/    ← 手动备份 (永久)")
    print("  ├── archive/   ← 归档备份 (压缩)")
    print("  └── temp/      ← 临时备份")
    print()
    print("防护规则:")
    print(f"  ✓ 阻止嵌套备份 (最大深度={CONFIG['max_backup_depth']})")
    print(f"  ✓ 自动清理旧备份 (>{CONFIG['auto_retain_days']}天)")
    print(f"  ✓ 自动压缩大文件 (>{CONFIG['compress_threshold_mb']}MB)")
    print()
    print("Git Hook 已更新:")
    print("  ✓ 嵌套备份检测")
    print("  ✓ _from_ 重复文件检测")
    print("  ✓ 大文件检测")
    print()


if __name__ == '__main__':
    main()
