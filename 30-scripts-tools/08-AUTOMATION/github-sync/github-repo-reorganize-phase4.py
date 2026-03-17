#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 仓库整理 - Phase 4 (最终清理)
整理根目录剩余散落文件
"""

import subprocess
import shutil
from pathlib import Path

# ==================== 配置 ====================

REPO_PATH = Path(r"D:\obsidian\Vault")

# ==================== 工具函数 ====================

def run_git(args, cwd=REPO_PATH):
    """运行 git 命令"""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=60
    )
    return result.returncode == 0, result.stdout, result.stderr

def final_cleanup():
    """最终清理根目录"""
    print("\n[最终清理] 整理根目录剩余文件...")
    
    # 分类规则
    categories = {
        '_archive/collection/': ['SYNC-STATUS', 'RSS_COLLECTION'],
        '_archive/knowledge/': ['知识图谱'],
    }
    
    moved = 0
    for md_file in REPO_PATH.glob("*.md"):
        filename = md_file.name
        dest_dir = None
        
        for dir_path, prefixes in categories.items():
            if any(filename.startswith(p) for p in prefixes):
                dest_dir = REPO_PATH / dir_path
                break
        
        if dest_dir:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(md_file), str(dest_dir / filename))
            moved += 1
            print(f"  移动：{filename} → {dest_dir.relative_to(REPO_PATH)}")
    
    print(f"  [OK] 移动 {moved} 个文件")
    return moved

def list_final_root():
    """列出最终根目录文件"""
    print("\n[根目录文件列表]")
    
    files = []
    for f in REPO_PATH.glob("*"):
        if f.is_file() and not f.name.startswith('.'):
            files.append(f.name)
    
    print(f"  保留 {len(files)} 个文件:")
    for name in sorted(files):
        print(f"    - {name}")
    
    return files

def commit_and_push():
    """提交并推送"""
    print("\n[Git] 提交最终清理...")
    
    success, out, err = run_git(["add", "-A"])
    if not success:
        print(f"  [FAIL] 添加失败：{err}")
        return False
    
    success, out, err = run_git(["status", "--porcelain"])
    if not out.strip():
        print(f"  [INFO] 无更改")
        return True
    
    commit_msg = """refactor: 最终根目录清理 (Phase 4)

- 移动 SYNC-STATUS 文件到 _archive/collection/
- 移动 RSS_COLLECTION_REPORT 到 _archive/collection/
- 移动 知识图谱.md 到 _archive/knowledge/
- 保留核心配置文件在根目录
"""
    
    success, out, err = run_git(["commit", "-m", commit_msg])
    if not success:
        print(f"  [FAIL] 提交失败：{err}")
        return False
    
    print(f"  [OK] 提交成功")
    
    print("\n[Git] 推送到 GitHub...")
    success, out, err = run_git(["push"])
    if not success:
        print(f"  [WARN] 推送失败：{err}")
        return False
    
    print(f"  [OK] 推送成功")
    return True

# ==================== 主流程 ====================

def main():
    print("=" * 60)
    print("GitHub 仓库整理 - Phase 4 (最终清理)")
    print("=" * 60)
    
    # 最终清理
    final_cleanup()
    
    # 列出根目录
    list_final_root()
    
    # 提交推送
    commit_and_push()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 仓库整理全部完成!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
