#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials Science Collector v1
材料科学论文收集器
"""

import feedparser
from datetime import datetime
from pathlib import Path

# 配置
VAULT_PATH = Path(r"D:\obsidian\Vault")
MATERIALS_DIR = VAULT_PATH / "Materials"

# arXiv 材料学类别
MATERIALS_CATEGORIES = [
    'cond-mat.mtrl-sci',    # 材料科学
    'cond-mat.soft',         # 软物质
    'cond-mat.mes-hall',     # 介观与纳米霍尔
    'cond-mat.str-el',       # 强关联电子
    'cond-mat.supr-con',     # 超导
    'cond-mat.dis-nn',       # 无序与神经网络
    'cond-mat.stat-mech',    # 统计力学
    'physics.chem-ph',       # 化学物理
    'physics.comp-ph',       # 计算物理
]

MAX_PAPERS_PER_CATEGORY = 15

def fetch_arxiv_papers(category, max_papers=15):
    """从 arXiv 获取论文"""
    url = f"https://export.arxiv.org/rss/{category}"
    feed = feedparser.parse(url)
    
    papers = []
    for entry in feed.entries[:max_papers]:
        paper = {
            'arxiv_id': entry.id.split('/')[-1].replace('v1', ''),
            'title': entry.title,
            'authors': [author.name for author in entry.authors],
            'categories': [tag.term for tag in entry.tags],
            'abstract': entry.summary,
            'link': entry.link,
            'published': entry.published,
        }
        papers.append(paper)
    
    return papers

def save_materials_paper(paper, date_str):
    """保存材料学论文"""
    date_dir = MATERIALS_DIR / "daily" / date_str[:4] / date_str[:7] / date_str
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # 按领域分类
    domain = paper['categories'][0].split('.')[-1] if '.' in paper['categories'][0] else 'materials'
    domain_dir = date_dir / domain
    domain_dir.mkdir(exist_ok=True)
    
    # 清理 arXiv ID (移除冒号等非法字符)
    safe_id = paper['arxiv_id'].replace(':', '_').replace('v1', '').replace('v2', '')
    # 清理标题 (移除 Windows 文件名非法字符)
    safe_title = paper['title'][:50].replace(':', '-').replace('?', '').replace('/', '-').replace('\\', '-')
    
    # 保存为 Markdown
    filename = f"{safe_id}-{safe_title}.md"
    filepath = domain_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"---\n")
        f.write(f"arxiv_id: {paper['arxiv_id']}\n")
        f.write(f"title: {paper['title']}\n")
        f.write(f"authors: {', '.join(paper['authors'])}\n")
        f.write(f"categories: {', '.join(paper['categories'])}\n")
        f.write(f"published: {paper['published']}\n")
        f.write(f"link: {paper['link']}\n")
        f.write(f"---\n\n")
        f.write(f"# {paper['title']}\n\n")
        f.write(f"**arXiv:** [{paper['arxiv_id']}]({paper['link']})\n\n")
        f.write(f"**作者:** {', '.join(paper['authors'])}\n\n")
        f.write(f"**类别:** {', '.join(paper['categories'])}\n\n")
        f.write(f"## 摘要\n\n{paper['abstract']}\n\n")
    
    return filepath

def collect_materials():
    """收集材料学论文"""
    print("=" * 60)
    print("Materials Science Collector v1")
    print("=" * 60)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"\nDate: {date_str}")
    print(f"Categories: {len(MATERIALS_CATEGORIES)}")
    print("-" * 60)
    
    all_papers = []
    for category in MATERIALS_CATEGORIES:
        print(f"\nFetching {category}...")
        papers = fetch_arxiv_papers(category, MAX_PAPERS_PER_CATEGORY)
        print(f"  Found {len(papers)} papers")
        
        for paper in papers:
            try:
                save_materials_paper(paper, date_str)
                all_papers.append(paper)
            except Exception as e:
                print(f"  [ERROR] {paper['arxiv_id']}: {e}")
    
    print("-" * 60)
    print(f"\n[COMPLETE] Total: {len(all_papers)} papers")
    print(f"Save dir: {MATERIALS_DIR / 'daily' / date_str[:4] / date_str[:7] / date_str}")
    print("=" * 60)

if __name__ == "__main__":
    collect_materials()
