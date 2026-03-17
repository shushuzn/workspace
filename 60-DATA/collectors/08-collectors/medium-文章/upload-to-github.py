"""
GitHub 笔记上传脚本
将 GitHub 仓库笔记上传到对应仓库的 Issues 或 Discussions
"""

import os
import json
import re
import base64
import urllib.request
from datetime import datetime
from pathlib import Path

ARCHIVE_DIR = Path("D:/obsidian/Vault/Medium/Archive")
GITHUB_TOKEN = os.environ.get("GITHUB_API_TOKEN", "")
GITHUB_USER = os.environ.get("GITHUB_USER", "")

# 上传配置
UPLOAD_CONFIG = {
    "upload_to": "issues",  # issues / discussions / wiki
    "min_stars": 1000,      # 只上传到 star >= 1000 的仓库
    "auto_label": True,     # 自动添加标签
    "include_abstract": True,  # 包含摘要
}

def parse_github_note(filepath):
    """解析 GitHub 仓库笔记"""
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
    
    # 提取仓库信息
    repo = frontmatter.get("repo", "")
    owner = frontmatter.get("owner", "")
    stars = int(frontmatter.get("stars", 0))
    
    # 提取 README
    readme = ""
    if "## 📄 README" in content:
        readme = content.split("## 📄 README")[1].split("\n\n##")[0].strip()[:3000]
    
    # 提取标签
    tags = frontmatter.get("tags", [])
    if isinstance(tags, str):
        tags = tags.strip("[]").split(", ")
    
    return {
        "title": title,
        "repo": repo,
        "owner": owner,
        "full_name": f"{owner}/{repo}",
        "stars": stars,
        "readme": readme,
        "tags": tags,
        "category": frontmatter.get("category", ""),
        "priority": frontmatter.get("priority", "low"),
        "score": int(frontmatter.get("score", 0)),
        "content": content,
    }

def format_issue_content(note):
    """格式化 Issue 内容"""
    lines = []
    
    lines.append("## 📚 Medium Watcher 笔记同步")
    lines.append("")
    lines.append(f"**仓库**: {note['full_name']}")
    lines.append(f"**Stars**: ⭐ {note['stars']}")
    lines.append(f"**分类**: {note['category']}")
    lines.append(f"**优先级**: {'🔥 高' if note['priority'] == 'high' else '📌 中'}")
    lines.append("")
    
    lines.append("## 📝 摘要")
    lines.append("")
    if note["readme"]:
        lines.append(note["readme"][:1000])
    else:
        lines.append("*自动搜集的仓库笔记*")
    lines.append("")
    
    lines.append("## 🏷️ 标签")
    lines.append("")
    if note["tags"]:
        tags = [t.strip() for t in note["tags"] if t]
        lines.append(" ".join([f"`#{t}`" for t in tags[:10]]))
    lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("*此 Issue 由 Medium Watcher 自动创建*")
    lines.append(f"*同步时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    return "\n".join(lines)

def create_github_issue(note):
    """创建 GitHub Issue"""
    if not GITHUB_TOKEN:
        print(f"[WARN] GitHub Token 未配置，跳过 {note['full_name']}")
        return False
    
    title = f"[Medium Watcher] 📚 {note['title'][:100]}"
    body = format_issue_content(note)
    labels = ["medium-watcher", "auto-sync", note["category"].lower().replace("/", "-")]
    
    url = f"https://api.github.com/repos/{note['full_name']}/issues"
    
    data = {
        "title": title,
        "body": body,
        "labels": labels
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "MediumWatcher/2.5"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        
        print(f"[OK] Issue 创建成功：{result.get('html_url')}")
        return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[ERROR] 创建 Issue 失败 ({e.code}): {error_body[:200]}")
        return False
    except Exception as e:
        print(f"[ERROR] 异常：{e}")
        return False

def upload_notes():
    """上传笔记到 GitHub"""
    stats = {
        "total": 0,
        "selected": 0,
        "uploaded": 0,
        "skipped": 0,
        "errors": []
    }
    
    github_dir = ARCHIVE_DIR / "GitHub-Repos"
    if not github_dir.exists():
        print("[ERROR] GitHub-Repos 目录不存在")
        return stats
    
    for md_file in github_dir.glob("*.md"):
        stats["total"] += 1
        
        try:
            note = parse_github_note(md_file)
            
            # 筛选条件
            if note["stars"] < UPLOAD_CONFIG["min_stars"]:
                stats["skipped"] += 1
                continue
            
            if note["priority"] not in ["high", "medium"]:
                stats["skipped"] += 1
                continue
            
            stats["selected"] += 1
            
            # 创建 Issue
            if create_github_issue(note):
                stats["uploaded"] += 1
            else:
                stats["errors"].append(f"上传失败：{note['full_name']}")
        
        except Exception as e:
            stats["errors"].append(f"{md_file.name}: {e}")
    
    return stats

if __name__ == "__main__":
    print("[INFO] 开始上传笔记到 GitHub")
    print(f"[INFO] 配置：{UPLOAD_CONFIG}")
    print("")
    
    stats = upload_notes()
    
    print("")
    print("[OK] 上传完成")
    print(f"  总笔记数：{stats['total']}")
    print(f"  符合条件：{stats['selected']}")
    print(f"  已上传：{stats['uploaded']}")
    print(f"  已跳过：{stats['skipped']}")
    if stats["errors"]:
        print(f"  错误：{len(stats['errors'])}")
