#!/usr/bin/env python3
"""
🧹 报告清理执行脚本

实际删除重复报告和归档旧报告
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def get_report_files(root_dir):
    """获取所有报告文件"""
    report_files = []
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.copaw', '90-archive', '99-archive'}
    
    for path in Path(root_dir).rglob('*REPORT*.md'):
        if any(exclude in str(path) for exclude in exclude_dirs):
            continue
        report_files.append(path)
    
    # 也查找包含 report 的文件（小写）
    for path in Path(root_dir).rglob('*report*.md'):
        if any(exclude in str(path) for exclude in exclude_dirs):
            if path not in report_files:
                report_files.append(path)
    
    return report_files


def calculate_file_hash(file_path):
    """计算文件哈希值"""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except:
        return None


def find_duplicates(file_list):
    """查找重复文件"""
    hash_map = defaultdict(list)
    
    for file_path in file_list:
        file_hash = calculate_file_hash(file_path)
        if file_hash:
            hash_map[file_hash].append(file_path)
    
    # 只保留有重复的
    duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
    
    return duplicates


def select_file_to_keep(file_list):
    """选择要保留的文件（基于路径优先级）"""
    # 优先级规则：
    # 1. 优先保留在标准目录的（21-reports, 30-scripts-tools）
    # 2. 优先保留路径短的
    # 3. 优先保留不含中文的
    
    def score(path):
        s = 0
        path_str = str(path).lower()
        
        # 优先目录
        if '21-reports' in path_str:
            s -= 100
        if '30-scripts-tools' in path_str:
            s -= 100
        if '06-research' in path_str and '研究' not in str(path):
            s -= 50
        
        # 惩罚中文路径
        if any('\u4e00' <= c <= '\u9fff' for c in str(path)):
            s += 50
        
        # 惩罚长路径
        s += len(str(path))
        
        # 惩罚 backup
        if 'backup' in path_str:
            s += 1000
        
        return s
    
    return min(file_list, key=score)


def create_backup(file_path, backup_dir):
    """创建备份"""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_name = f"{file_path.name}-{timestamp}.backup"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def cleanup_duplicates(duplicates, dry_run=True, backup=True):
    """清理重复文件"""
    results = {
        'total_groups': len(duplicates),
        'files_to_delete': [],
        'files_to_keep': [],
        'backed_up': [],
        'deleted': [],
        'errors': []
    }
    
    backup_dir = Path('backup/reports-cleanup')
    
    for hash_val, files in duplicates.items():
        # 选择要保留的文件
        keep = select_file_to_keep(files)
        delete = [f for f in files if f != keep]
        
        results['files_to_keep'].append(keep)
        results['files_to_delete'].extend(delete)
        
        if not dry_run:
            # 实际删除
            for file_path in delete:
                try:
                    if backup:
                        # 先备份
                        backup_path = create_backup(file_path, backup_dir)
                        results['backed_up'].append((file_path, backup_path))
                    
                    # 删除文件
                    file_path.unlink()
                    results['deleted'].append(file_path)
                    print(f"  [OK] Deleted: {file_path}")
                    
                except Exception as e:
                    results['errors'].append((file_path, str(e)))
                    print(f"  [ERROR] Failed to delete {file_path}: {e}")
    
    return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Report Cleanup Execution')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup')
    parser.add_argument('--yes', '-y', action='store_true', help='Auto confirm')
    parser.add_argument('--root', default='D:\\OpenClaw\\workspace', help='Root directory')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Report Cleanup Execution")
    print("=" * 60)
    
    if args.dry_run:
        print("\n[WARN] Mode: DRY RUN (preview only, no actual deletion)")
    else:
        print("\n[WARN] Mode: ACTUAL CLEANUP (will delete files!)")
        if not args.yes:
            response = input("\nContinue? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled")
                return
    
    # 扫描报告
    print(f"\n[1/4] Scanning report files...")
    files = get_report_files(args.root)
    print(f"  Found {len(files)} report files")
    
    # 查找重复
    print(f"\n[2/4] Finding duplicates...")
    duplicates = find_duplicates(files)
    print(f"  Found {len(duplicates)} duplicate groups")
    
    # 计算可删除数量
    total_to_delete = sum(len(files) - 1 for files in duplicates.values())
    print(f"  Estimated deletion: {total_to_delete} files")
    
    # 显示部分重复组
    print(f"\n[3/4] Duplicate examples:")
    for i, (hash_val, dup_files) in enumerate(list(duplicates.items())[:5], 1):
        print(f"\n  Group {i}:")
        for f in dup_files:
            print(f"    - {f.name} ({len(str(f.parent))} chars)")
    
    # 执行清理
    if args.dry_run:
        print(f"\n[4/4] Skipping execution (dry run)")
    else:
        print(f"\n[4/4] Executing cleanup...")
        results = cleanup_duplicates(
            duplicates,
            dry_run=False,
            backup=not args.no_backup
        )
        
        print(f"\n{'=' * 60}")
        print("Cleanup Results:")
        print(f"  Duplicate groups: {results['total_groups']}")
        print(f"  Deleted: {len(results['deleted'])} files")
        print(f"  Backed up: {len(results['backed_up'])} files")
        print(f"  Errors: {len(results['errors'])}")
        
        if results['errors']:
            print(f"\nError details:")
            for file_path, error in results['errors'][:10]:
                print(f"  - {file_path}: {error}")
    
    # 生成报告
    print(f"\n{'=' * 60}")
    print("Next Steps:")
    if args.dry_run:
        print("  1. Review duplicate list above")
        print("  2. Run without --dry-run to execute")
        print("  3. Check backup directory: backup/reports-cleanup/")
    else:
        print("  1. Review deletion results")
        print("  2. Verify backup files")
        print("  3. Update report index")
        print("  4. Commit git changes")
    
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
