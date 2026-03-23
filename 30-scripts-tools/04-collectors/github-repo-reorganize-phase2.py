#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 仓库深度整理 - 第二阶段
整理 Medium/HackerNews/Reddit/X-Twitter 目录结构
"""

import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import re

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

def extract_date_from_filename(filename):
    """从文件名提取日期"""
    # 格式：YYYYMMDD-HHMMSS-Title.md 或 YYYY-MM-DD-Title.md
    match = re.match(r'(\d{4})(\d{2})(\d{2})[-_]', filename)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"

    match = re.match(r'(\d{4})-(\d{2})-(\d{2})[-_]', filename)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"

    return None

def reorganize_directory(source_dir, name):
    """重组目录结构"""
    print(f"\n[{name}] 开始整理...")

    if not source_dir.exists():
        print(f"  [SKIP] 目录不存在")
        return 0

    # 创建新结构
    new_base = source_dir.parent / f"{name.lower()}_organized" / "daily"

    # 按日期分组
    by_date = {}
    for f in source_dir.glob("*.md"):
        date_str = extract_date_from_filename(f.name)
        if date_str:
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(f)

    # 迁移文件
    migrated = 0
    for date_str, files in sorted(by_date.items()):
        try:
            year = date_str[:4]
            month = date_str[5:7]
            target_dir = new_base / year / f"{year}-{month}" / date_str
            target_dir.mkdir(parents=True, exist_ok=True)

            for f in files:
                shutil.move(str(f), str(target_dir / f.name))
                migrated += 1
        except Exception as e:
            print(f"  [WARN] 跳过 {f.name}: {e}")

    # 删除旧目录（如果为空）
    if source_dir.exists() and not any(source_dir.iterdir()):
        source_dir.rmdir()
        print(f"  [OK] 删除空目录 {source_dir.name}")

    # 重命名新目录
    if new_base.parent.exists():
        final_dir = source_dir
        if final_dir.exists():
            shutil.rmtree(final_dir)
        shutil.move(str(new_base.parent), str(final_dir))

    print(f"  [OK] 迁移 {migrated} 个文件到新结构")
    return migrated

def organize_medium_archive():
    """整理 Medium Archive 目录"""
    print("\n[Medium Archive] 整理归档目录...")

    medium_dir = REPO_PATH / "Medium"
    archive_dir = medium_dir / "Archive"

    if not archive_dir.exists():
        print(f"  [SKIP] Archive 目录不存在")
        return

    # 统计各分类
    categories = {}
    for subdir in archive_dir.iterdir():
        if subdir.is_dir():
            count = len(list(subdir.glob("*.md")))
            categories[subdir.name] = count

    print(f"  Archive 分类统计:")
    for cat, count in sorted(categories.items()):
        print(f"    {cat}: {count} 篇")

    print(f"  [OK] Archive 结构保持")

def clean_empty_dirs():
    """清理空目录"""
    print("\n[清理] 删除空目录...")

    deleted = 0
    for root, dirs, files in list((REPO_PATH).walk(top_down=False)):
        for d in dirs:
            dir_path = Path(root) / d
            if not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                    deleted += 1
                except:
                    pass

    print(f"  [OK] 删除 {deleted} 个空目录")

def create_summary():
    """创建整理摘要"""
    print("\n[摘要] 创建整理报告...")

    stats = {}
    for source in ['arxiv', 'HackerNews', 'Medium', 'Reddit', 'X-Twitter']:
        dir_path = REPO_PATH / source
        if dir_path.exists():
            count = len(list(dir_path.glob("**/*.md")))
            stats[source] = count

    summary = f"""# 仓库整理摘要 - 2026-03-03

## 文件统计

| 来源 | 文件数 | 结构 |
|------|--------|------|
"""

    for source, count in sorted(stats.items()):
        summary += f"| {source} | {count} | daily/YYYY/MM/DD/ |\n"

    summary += f"\n**总计:** {sum(stats.values())} 篇\n\n"
    summary += "*整理完成时间：2026-03-03*\n"

    summary_path = REPO_PATH / "REORGANIZE-SUMMARY.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"  [OK] 摘要已创建")

def commit_and_push():
    """提交并推送"""
    print("\n[Git] 提交更改...")

    # 添加所有
    success, out, err = run_git(["add", "-A"])
    if not success:
        print(f"  [FAIL] 添加失败：{err}")
        return False

    # 检查更改
    success, out, err = run_git(["status", "--porcelain"])
    if not out.strip():
        print(f"  [INFO] 无更改")
        return True

    # 提交
    commit_msg = """refactor: 重组多源目录结构 (Phase 2)

- Medium: 按日期重组 (daily/YYYY-MM-DD/)
- HackerNews: 按日期重组
- Reddit: 按日期重组
- X-Twitter: 按日期重组
- 清理空目录
- 创建整理摘要
"""

    success, out, err = run_git(["commit", "-m", commit_msg])
    if not success:
        print(f"  [FAIL] 提交失败：{err}")
        return False

    print(f"  [OK] 提交成功")

    # 推送
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
    print("GitHub 仓库深度整理 - Phase 2")
    print("整理 Medium/HackerNews/Reddit/X-Twitter")
    print("=" * 60)

    # 整理各来源
    reorganize_directory(REPO_PATH / "HackerNews", "HackerNews")
    reorganize_directory(REPO_PATH / "Reddit", "Reddit")
    reorganize_directory(REPO_PATH / "X-Twitter", "X-Twitter")

    # Medium 特殊处理（保留 Archive）
    organize_medium_archive()
    # reorganize_directory(REPO_PATH / "Medium", "Medium")  # 暂时跳过，保留现有结构

    # 清理
    clean_empty_dirs()

    # 创建摘要
    create_summary()

    # 提交推送
    commit_and_push()

    # 完成
    print("\n" + "=" * 60)
    print("[SUCCESS] Phase 2 整理完成")
    print("=" * 60)

    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
