#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 仓库整理脚本
整理 github.com/shushuzn/obsidian-sync 仓库结构
"""

import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# ==================== 配置 ====================

REPO_PATH = Path(r"D:\obsidian\Vault")
BACKUP_PATH = Path(r"D:\obsidian\Vault-backup-before-reorg")

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

def backup_repo():
    """备份仓库"""
    print("[0/6] 创建备份...")
    if BACKUP_PATH.exists():
        shutil.rmtree(BACKUP_PATH)
    shutil.copytree(REPO_PATH, BACKUP_PATH, ignore=shutil.ignore_patterns('.git'))
    print(f"  [OK] 备份到：{BACKUP_PATH}")

def clean_root_files():
    """清理根目录散落文件"""
    print("\n[1/6] 整理根目录文件...")
    
    # 创建归档目录
    archive_dirs = {
        'reports': ['AI-Analysis', 'AI-Agents', 'AI-Research', 'MCP-Deep'],
        'collection': ['COLLECTION-SUMMARY'],
        'cron': ['CRON-TASK'],
        'knowledge': ['KNOWLEDGE', 'MEMORY', 'knowledge-index'],
    }
    
    moved = 0
    for file in REPO_PATH.glob("*.md"):
        filename = file.name
        dest_dir = None
        
        for dir_name, prefixes in archive_dirs.items():
            if any(filename.startswith(p) for p in prefixes):
                dest_dir = REPO_PATH / "_archive" / dir_name
                break
        
        if dest_dir:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(dest_dir / filename))
            moved += 1
    
    print(f"  [OK] 移动 {moved} 个文件到 _archive/")

def clean_duplicates():
    """清理重复文件（保留最新版本）"""
    print("\n[2/6] 清理重复文件...")
    
    # 按来源目录处理
    for source_dir in ['Arxiv', 'HackerNews', 'Medium', 'Reddit', 'X-Twitter']:
        dir_path = REPO_PATH / source_dir
        if not dir_path.exists():
            continue
        
        # 按标题分组
        by_title = {}
        for f in dir_path.glob("*.md"):
            # 提取标题（去掉时间戳）
            parts = f.stem.split('-', 2)
            if len(parts) >= 3:
                title = '-'.join(parts[2:])
                if title not in by_title:
                    by_title[title] = []
                by_title[title].append(f)
        
        # 保留最新版本（时间戳最大）
        deleted = 0
        for title, files in by_title.items():
            if len(files) > 1:
                # 按时间戳排序，保留最新
                sorted_files = sorted(files, key=lambda x: x.stem.split('-')[0], reverse=True)
                for old_file in sorted_files[1:]:
                    old_file.unlink()
                    deleted += 1
        
        if deleted > 0:
            print(f"  {source_dir}: 清理 {deleted} 个重复文件")
    
    print(f"  [OK] 重复文件清理完成")

def reorganize_arxiv():
    """重组 Arxiv 目录到新结构"""
    print("\n[3/6] 重组 Arxiv 目录...")
    
    old_arxiv = REPO_PATH / "Arxiv"
    new_arxiv = REPO_PATH / "arxiv" / "daily"
    
    if not old_arxiv.exists():
        print(f"  [SKIP] 旧 Arxiv 目录不存在")
        return
    
    # 按日期迁移
    migrated = 0
    for f in old_arxiv.glob("*.md"):
        # 解析文件名：YYYYMMDD-HHMMSS-Title.md
        parts = f.stem.split('-', 2)
        if len(parts) < 2:
            continue
        
        date_str = parts[0]  # YYYYMMDD
        try:
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            
            # 创建目标目录
            target_dir = new_arxiv / year / month / f"{year}-{month}-{day}" / "csAI"
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 移动文件
            shutil.move(str(f), str(target_dir / f.name))
            migrated += 1
        except Exception as e:
            print(f"  [WARN] 跳过 {f.name}: {e}")
    
    # 删除旧目录
    if old_arxiv.exists() and not any(old_arxiv.iterdir()):
        old_arxiv.rmdir()
    
    print(f"  [OK] 迁移 {migrated} 篇论文到新结构")

def create_readme():
    """创建 README.md"""
    print("\n[4/6] 创建 README.md...")
    
    readme = """# Obsidian Sync - 知识库同步仓库

自动同步多源内容到 Obsidian 知识库

---

## 📊 仓库统计

| 来源 | 文件数 | 最后更新 |
|------|--------|----------|
| Arxiv | ~60 篇 | 2026-03-02 |
| HackerNews | ~20 篇 | 2026-03-02 |
| Medium | ~200+ 篇 | 2026-03-02 |
| Reddit | - | - |
| X-Twitter | - | - |

---

## 📁 目录结构

```
├── arxiv/              # Arxiv 论文（按日期 + 领域分类）
│   └── daily/YYYY/MM/DD/领域/
├── HackerNews/         # HackerNews 文章
├── Medium/             # Medium 文章
│   └── Archive/        # 归档（按主题）
├── Reddit/             # Reddit 帖子
├── X-Twitter/          # Twitter 内容
├── _archive/           # 历史报告归档
│   ├── reports/        # AI 分析报告
│   ├── collection/     # 收集汇总
│   ├── cron/           # 定时任务日志
│   └── knowledge/      # 知识索引
├── memory/             # 每日记忆
├── topics/             # 主题笔记
├── scripts/            # 自动化脚本
└── .obsidian/          # Obsidian 配置
```

---

## 🔧 自动化脚本

### 收集脚本

| 脚本 | 功能 |
|------|------|
| `arxiv-collector-v2.py` | Arxiv 多领域论文收集 |
| `medium-rss-integrated.py` | Medium RSS 收集 |
| `hackernews-collector.py` | HackerNews 收集 |

### 管理脚本

| 脚本 | 功能 |
|------|------|
| `medium-task-manager.py` | 任务队列管理 |
| `arxiv-migrate.py` | 数据迁移 |
| `organize-notes.py` | 笔记整理 |

---

## 🔄 工作流

```
RSS 源 → 收集脚本 → Obsidian → Git Sync → GitHub
```

### 定时任务

- **Arxiv:** 每日 2am
- **Medium:** 每 30 分钟检查
- **HackerNews:** 每日 1 次

---

## 📝 配置

### Medium 收集

- 订阅源：500+ RSS
- 最小分数：6
- 每次最多：10 篇
- 失败重试：3 次

### Arxiv 收集

- 领域：10 个（csAI, csLG, csCV, csCL, csIR, csSE, csDC, csRO, csSY）
- 每次收集：~100 篇
- 自动分类：基于关键词

---

## 📌 相关项目

- **paper2md:** PDF 论文深度解析
- **OpenClaw:** AI 助理框架
- **Obsidian:** 知识库管理

---

*最后更新：2026-03-03*
"""
    
    readme_path = REPO_PATH / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"  [OK] README.md 已创建")

def commit_changes():
    """提交更改"""
    print("\n[5/6] 提交更改到 Git...")
    
    # 添加所有更改
    success, out, err = run_git(["add", "-A"])
    if not success:
        print(f"  [FAIL] 添加失败：{err}")
        return False
    
    # 检查是否有更改
    success, out, err = run_git(["status", "--porcelain"])
    if not out.strip():
        print(f"  [INFO] 没有更改需要提交")
        return True
    
    # 提交
    commit_msg = """refactor: 重组仓库结构

- 整理根目录散落文件到 _archive/
- 清理重复收集的文件
- 重组 Arxiv 到新结构 (daily/YYYY/MM/DD/领域/)
- 添加 README.md 文档
"""
    
    success, out, err = run_git(["commit", "-m", commit_msg])
    if not success:
        print(f"  [FAIL] 提交失败：{err}")
        return False
    
    print(f"  [OK] 提交成功")
    return True

def push_changes():
    """推送到 GitHub"""
    print("\n[6/6] 推送到 GitHub...")
    
    success, out, err = run_git(["push", "-u", "origin", "master"])
    if not success:
        if "Authentication" in err or "authentication" in err.lower():
            print(f"  [WARN] 认证失败，需要配置 GitHub Token")
            print(f"  提示：git config --global credential.helper store")
            return False
        else:
            print(f"  [FAIL] 推送失败：{err}")
            return False
    
    print(f"  [OK] 推送成功")
    print(f"  仓库：https://github.com/shushuzn/obsidian-sync")
    return True

# ==================== 主流程 ====================

def main():
    print("=" * 60)
    print("GitHub 仓库整理")
    print("整理 github.com/shushuzn/obsidian-sync")
    print("=" * 60)
    
    # 备份
    backup_repo()
    
    # 整理根目录
    clean_root_files()
    
    # 清理重复
    clean_duplicates()
    
    # 重组 Arxiv
    reorganize_arxiv()
    
    # 创建 README
    create_readme()
    
    # 提交
    if not commit_changes():
        print("\n[ERROR] 提交失败")
        return False
    
    # 推送
    push_changes()
    
    # 完成
    print("\n" + "=" * 60)
    print("[SUCCESS] 整理完成")
    print(f"  仓库：https://github.com/shushuzn/obsidian-sync")
    print(f"  时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
