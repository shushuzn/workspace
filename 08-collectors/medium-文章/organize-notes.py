"""
Obsidian 资料整理脚本
自动分类 Medium 文章、arXiv 论文、GitHub 仓库
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("D:/obsidian/Vault/Medium")
ARCHIVE_DIR = OUTPUT_DIR / "Archive"

# 创建分类目录
CATEGORIES = ["AI-ML", "NLP", "Computer-Vision", "Data-Science", "GitHub-Repos", "Medium-Articles", "Reports"]

def organize_notes():
    """整理笔记到分类目录"""
    
    # 创建目录
    for cat in CATEGORIES:
        (ARCHIVE_DIR / cat).mkdir(parents=True, exist_ok=True)
    
    stats = {
        "total": 0,
        "moved": 0,
        "by_category": {},
        "errors": []
    }
    
    # 遍历所有 Markdown 文件
    for md_file in OUTPUT_DIR.glob("*.md"):
        if md_file.name.startswith(".") or md_file.name in ["ROADMAP.md", "Medium-Watcher-Status.md"]:
            continue
        
        stats["total"] += 1
        
        try:
            content = md_file.read_text(encoding="utf-8")
            
            # 判断类型
            if "arxiv_id:" in content:
                file_type = "arxiv"
            elif "repo:" in content:
                file_type = "github"
            elif "source:" in content and "medium.com" in content:
                file_type = "medium"
            elif "type:" in content:
                if "report" in content:
                    file_type = "report"
                elif "status" in content:
                    file_type = "status"
                else:
                    file_type = "other"
            else:
                file_type = "other"
            
            # 提取分类标签
            category = "Other"
            if "category:" in content:
                match = re.search(r"category:\s*(\S+)", content)
                if match:
                    category = match.group(1)
            
            # 移动文件
            if file_type == "arxiv":
                target_dir = ARCHIVE_DIR / "AI-ML" if "AI" in category or "ML" in category else ARCHIVE_DIR / category
            elif file_type == "github":
                target_dir = ARCHIVE_DIR / "GitHub-Repos"
            elif file_type == "medium":
                target_dir = ARCHIVE_DIR / "Medium-Articles"
            elif file_type == "report":
                target_dir = ARCHIVE_DIR / "Reports"
            else:
                target_dir = ARCHIVE_DIR / "Other"
            
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / md_file.name
            
            if not target_file.exists():
                shutil.move(str(md_file), str(target_file))
                stats["moved"] += 1
                stats["by_category"][str(target_dir.name)] = stats["by_category"].get(str(target_dir.name), 0) + 1
            else:
                stats["errors"].append(f"File exists: {md_file.name}")
        
        except Exception as e:
            stats["errors"].append(f"{md_file.name}: {e}")
    
    return stats

if __name__ == "__main__":
    stats = organize_notes()
    print(f"[OK] 整理完成")
    print(f"  总文件数：{stats['total']}")
    print(f"  已移动：{stats['moved']}")
    print(f"  分类统计：{stats['by_category']}")
    if stats["errors"]:
        print(f"  错误：{len(stats['errors'])}")
