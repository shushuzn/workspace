#!/usr/bin/env python3
"""
Arxiv AI Papers Collector
Collects latest AI/ML papers from arxiv.org and saves to Obsidian vault
"""

import feedparser
import requests
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import os
import re

# ============ 代理配置 (Clash) ============
# 解决 Python 进程无法继承系统代理的问题
PROXY_ADDR = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = PROXY_ADDR
os.environ["HTTPS_PROXY"] = PROXY_ADDR
# ==========================================

OUTPUT_DIR = r"D:\obsidian\Vault\Arxiv"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def sanitize_filename(title):
    """Remove invalid characters from filename"""
    title = re.sub(r'[<>:"/\\|？*]', "", title)
    title = title.replace("&", "and")
    title = title[:100]  # Limit length
    return title.strip()


def fetch_arxiv_papers(category="cs.AI", max_papers=20):
    """Fetch latest papers from arxiv"""
    rss_url = f"https://export.arxiv.org/rss/{category}"

    try:
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        papers = []

        for entry in feed.entries[:max_papers]:
            paper = {
                "title": entry.title,
                "link": entry.link,
                "description": entry.description,
                "published": entry.get("published", ""),
                "authors": entry.get("authors", []),
                "categories": entry.get("tags", []),
            }
            papers.append(paper)

        return papers
    except Exception as e:
        print(f"Error fetching arxiv: {e}")
        return []


def save_paper(paper):
    """Save paper as markdown note"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    title_slug = sanitize_filename(paper["title"])[:50]
    filename = f"{timestamp}-{title_slug}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Extract abstract from description
    abstract = paper["description"]
    if "Abstract: " in abstract:
        abstract = abstract.split("Abstract: ")[1].split("\n")[0]

    authors = (
        ", ".join([a.name for a in paper["authors"]]) if paper["authors"] else "Unknown"
    )
    categories = (
        ", ".join([t.term for t in paper["categories"]])
        if paper["categories"]
        else "cs.AI"
    )

    content = f"""# {paper["title"]}

## 元数据
- **来源:** Arxiv
- **链接:** {paper["link"]}
- **作者:** {authors}
- **分类:** {categories}
- **发布日期:** {paper["published"]}
- **抓取时间:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 摘要

{abstract}

## 标签

#AI #MachineLearning #Research #Arxiv

---
*自动收集*
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filename


def main():
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize", "--auto"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        return

    print("[OK] Critic Review Passed")

    print("=" * 60)
    print("Arxiv AI Papers Collector")
    print("=" * 60)

    papers = fetch_arxiv_papers("cs.AI", max_papers=15)

    if not papers:
        print("No papers found or error occurred")
        return

    print(f"Found {len(papers)} papers")

    new_count = 0
    for paper in papers:
        filename = save_paper(paper)
        new_count += 1
        print(f"  Saved: {filename}")

    print(f"\n[SUCCESS] Collected {new_count} new papers")
    print("=" * 60)


if __name__ == "__main__":
    main()
