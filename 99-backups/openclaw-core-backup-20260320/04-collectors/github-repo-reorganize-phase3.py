#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 仓库整理 - Phase 3
整理远程仓库的 .md 和 .py 文件
"""

import subprocess
import shutil
from pathlib import Path
from datetime import datetime

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

def organize_root_md_files():
    """整理根目录 .md 文件"""
    print("\n[1/4] 整理根目录 .md 文件...")

    # 分类规则
    categories = {
        '_archive/reports/': ['AI-Analysis', 'AI-Agents', 'AI-Research', 'MCP-Deep', 'AI-System'],
        '_archive/collection/': ['COLLECTION-SUMMARY'],
        '_archive/cron/': ['CRON-TASK', 'CRON-STATUS'],
        '_archive/knowledge/': ['KNOWLEDGE', 'knowledge-index'],
        'memory/': ['MEMORY'],
    }

    moved = 0
    for md_file in REPO_PATH.glob("*.md"):
        filename = md_file.name
        dest_dir = None

        for dir_path, prefixes in categories.items():
            if any(filename.startswith(p) for p in prefixes):
                dest_dir = REPO_PATH / dir_path
                break

        if dest_dir and dest_dir != md_file.parent:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(md_file), str(dest_dir / filename))
            moved += 1
            print(f"  移动：{filename} → {dest_dir.relative_to(REPO_PATH)}")

    print(f"  [OK] 移动 {moved} 个 .md 文件")
    return moved

def organize_root_py_files():
    """整理根目录 .py 文件"""
    print("\n[2/4] 整理根目录 .py 文件...")

    scripts_dir = REPO_PATH / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    moved = 0
    for py_file in REPO_PATH.glob("*.py"):
        shutil.move(str(py_file), str(scripts_dir / py_file.name))
        moved += 1
        print(f"  移动：{py_file.name} → scripts/")

    print(f"  [OK] 移动 {moved} 个 .py 文件到 scripts/")
    return moved

def organize_subdir_files():
    """整理子目录下的散落文件"""
    print("\n[3/4] 整理子目录散落文件...")

    # 整理 AI-Research 目录
    ai_research = REPO_PATH / "AI-Research"
    if ai_research.exists():
        # 移动 .py 文件到 scripts/
        for py_file in ai_research.glob("*.py"):
            scripts_dir = REPO_PATH / "scripts"
            shutil.move(str(py_file), str(scripts_dir / py_file.name))
            print(f"  移动：AI-Research/{py_file.name} → scripts/")

    # 整理 _archive 目录
    archive = REPO_PATH / "_archive"
    if archive.exists():
        # 确保子目录存在
        for subdir in ['reports', 'collection', 'cron', 'knowledge']:
            (archive / subdir).mkdir(exist_ok=True)

    print(f"  [OK] 子目录整理完成")

def create_scripts_readme():
    """创建 scripts/README.md"""
    print("\n[4/4] 创建 scripts/README.md...")

    # 扫描脚本
    scripts_dir = REPO_PATH / "scripts"
    collectors = []
    managers = []
    utils = []

    for py_file in scripts_dir.glob("*.py"):
        name = py_file.name
        if 'collector' in name.lower():
            collectors.append(name)
        elif 'manager' in name.lower() or 'task' in name.lower():
            managers.append(name)
        else:
            utils.append(name)

    readme = """# Scripts - 自动化脚本集合

## 📁 分类

### 收集脚本 (Collectors)

| 脚本 | 功能 |
|------|------|
"""

    for script in sorted(collectors):
        readme += f"| `{script}` | 内容收集 |\n"

    readme += """
### 管理脚本 (Managers)

| 脚本 | 功能 |
|------|------|
"""

    for script in sorted(managers):
        readme += f"| `{script}` | 任务管理 |\n"

    readme += """
### 工具脚本 (Utils)

| 脚本 | 功能 |
|------|------|
"""

    for script in sorted(utils):
        readme += f"| `{script}` | 工具 |\n"

    readme += """
## 🔧 使用方式

```bash
# 收集 Arxiv 论文
python scripts/arxiv-collector-v2.py

# 整理 Medium 文章
python scripts/medium-rss-integrated.py

# GitHub 同步
python scripts/arxiv-sync-github.py
```

## 📝 配置

大部分脚本使用默认配置，部分需要配置文件：

- `medium-rss-config.json` - Medium RSS 订阅源
- `medium_tasks.json` - 任务队列

---

*最后更新：2026-03-03*
"""

    readme_path = scripts_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)

    print(f"  [OK] scripts/README.md 已创建 ({len(collectors) +len(managers) +len(utils)} 个脚本)")

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
    commit_msg = """refactor: 整理根目录散落文件 (Phase 3)

- 移动根目录 .md 文件到 _archive/ 分类目录
- 移动根目录 .py 文件到 scripts/
- 整理 AI-Research/ 子目录
- 创建 scripts/README.md
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
    print("GitHub 仓库整理 - Phase 3")
    print("整理根目录 .md 和 .py 文件")
    print("=" * 60)

    # 整理根目录 .md
    organize_root_md_files()

    # 整理根目录 .py
    organize_root_py_files()

    # 整理子目录
    organize_subdir_files()

    # 创建 README
    create_scripts_readme()

    # 提交推送
    commit_and_push()

    # 完成
    print("\n" + "=" * 60)
    print("[SUCCESS] Phase 3 整理完成")
    print("=" * 60)

    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
