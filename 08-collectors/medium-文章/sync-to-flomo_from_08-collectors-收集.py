"""
Flomo 笔记同步脚本
将精选的 Medium/arXiv/GitHub 笔记同步到 Flomo
"""

import os
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

# 配置
ARCHIVE_DIR = Path("D:/obsidian/Vault/Medium/Archive")
FLOMO_API_URL = os.environ.get("FLOMO_API_URL", "")
FLOMO_TOKEN = os.environ.get("FLOMO_TOKEN", "")

# Flomo 导入配置
FLOMO_CONFIG = {
    "max_notes_per_day": 20,      # 每日最多同步条数
    "min_priority_score": 7,      # 最小优先级分数
    "include_tags": True,         # 包含标签
    "include_links": True,        # 包含链接
}

def parse_note(filepath):
    """解析笔记内容"""
    content = filepath.read_text(encoding="utf-8")
    
    # 提取 Frontmatter
    frontmatter = {}
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if match:
        for line in match.group(1).split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()
    
    # 提取标题
    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else filepath.stem
    
    # 提取摘要/描述
    abstract = ""
    if "## 📝 摘要" in content:
        abstract = content.split("## 📝 摘要")[1].split("\n\n")[0].strip()[:200]
    elif "## 📝 描述" in content:
        abstract = content.split("## 📝 描述")[1].split("\n\n")[0].strip()[:200]
    elif "## 📝 内容摘要" in content:
        abstract = content.split("## 📝 内容摘要")[1].split("\n\n")[0].strip()[:200]
    
    # 提取链接
    source = frontmatter.get("source", "")
    arxiv_id = frontmatter.get("arxiv_id", "")
    repo = frontmatter.get("repo", "")
    
    return {
        "title": title,
        "abstract": abstract,
        "source": source,
        "arxiv_id": arxiv_id,
        "repo": repo,
        "tags": frontmatter.get("tags", []),
        "category": frontmatter.get("category", ""),
        "priority": frontmatter.get("priority", "low"),
        "score": int(frontmatter.get("score", 0)),
        "created": frontmatter.get("created", ""),
    }

def format_flomo_content(note, filepath):
    """格式化 Flomo 内容"""
    lines = []
    
    # 标题
    lines.append(f"📚 {note['title']}")
    lines.append("")
    
    # 摘要
    if note["abstract"]:
        lines.append(f"{note['abstract']}")
        lines.append("")
    
    # 链接
    if note["source"]:
        lines.append(f"🔗 来源：{note['source']}")
    if note["arxiv_id"]:
        lines.append(f"📄 arXiv: https://arxiv.org/abs/{note['arxiv_id']}")
    if note["repo"]:
        lines.append(f"💻 仓库：https://github.com/{note['repo']}")
    
    # 标签
    if note["tags"]:
        tags = note["tags"]
        if isinstance(tags, str):
            tags = tags.strip("[]").split(", ")
        flomo_tags = [f"#{tag.replace('#', '')}" for tag in tags if tag]
        if flomo_tags:
            lines.append("")
            lines.append(" ".join(flomo_tags[:5]))  # 最多 5 个标签
    
    # 分类
    if note["category"]:
        lines.append(f"分类：{note['category']}")
    
    # 优先级
    if note["priority"] == "high":
        lines.append("优先级：🔥 高")
    elif note["priority"] == "medium":
        lines.append("优先级：📌 中")
    
    return "\n".join(lines)

def send_to_flomo(content):
    """发送到 Flomo"""
    if not FLOMO_API_URL or not FLOMO_TOKEN:
        print("[WARN] Flomo API 未配置，跳过发送")
        return False
    
    try:
        url = f"{FLOMO_API_URL}?token={FLOMO_TOKEN}"
        data = {
            "content": content,
            "source": "Medium Watcher"
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        
        return result.get("code") == 0
    except Exception as e:
        print(f"[ERROR] Flomo 发送失败：{e}")
        return False

def sync_notes():
    """同步笔记到 Flomo"""
    stats = {
        "total": 0,
        "selected": 0,
        "sent": 0,
        "skipped": 0,
        "errors": []
    }
    
    # 遍历所有笔记
    for category_dir in ARCHIVE_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        
        for md_file in category_dir.glob("*.md"):
            stats["total"] += 1
            
            try:
                note = parse_note(md_file)
                
                # 筛选条件
                if note["score"] < FLOMO_CONFIG["min_priority_score"]:
                    stats["skipped"] += 1
                    continue
                
                if note["priority"] not in ["high", "medium"]:
                    stats["skipped"] += 1
                    continue
                
                stats["selected"] += 1
                
                # 格式化内容
                content = format_flomo_content(note, md_file)
                
                # 发送到 Flomo
                if send_to_flomo(content):
                    stats["sent"] += 1
                    print(f"[OK] 已同步：{note['title'][:50]}")
                else:
                    stats["errors"].append(f"发送失败：{note['title']}")
            
            except Exception as e:
                stats["errors"].append(f"{md_file.name}: {e}")
    
    return stats

if __name__ == "__main__":
    print("[INFO] 开始同步笔记到 Flomo")
    print(f"[INFO] 配置：{FLOMO_CONFIG}")
    print("")
    
    stats = sync_notes()
    
    print("")
    print("[OK] 同步完成")
    print(f"  总笔记数：{stats['total']}")
    print(f"  符合条件：{stats['selected']}")
    print(f"  已发送：{stats['sent']}")
    print(f"  已跳过：{stats['skipped']}")
    if stats["errors"]:
        print(f"  错误：{len(stats['errors'])}")
