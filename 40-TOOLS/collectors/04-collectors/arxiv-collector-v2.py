#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arxiv AI Papers Collector v2.0
Enhanced: Multi-category, Multi-keyword, JSON Output, Auto-deduplication
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import feedparser
import requests
from datetime import datetime
import os
import re
import json

# ============ Configuration ============
PROXY_ADDR = "http://127.0.0.1:7897"
os.environ['HTTP_PROXY'] = PROXY_ADDR
os.environ['HTTPS_PROXY'] = PROXY_ADDR

# Output directories
OUTPUT_DIR_MD = r"D:\obsidian\Vault\Arxiv"
OUTPUT_DIR_JSON = r"D:\OpenClaw\workspace\40-collectors\arxiv\data"

# Categories and Keywords
CATEGORIES = [
    'cs.AI',              # Artificial Intelligence
    'cs.LG',              # Machine Learning
    'cs.CL',              # Computation and Language
    'cs.CV',              # Computer Vision
    'cs.NE',              # Neural and Evolutionary Computing
    'physics.chem-ph',    # Chemical Physics
    'cond-mat.mtrl-sci',  # Materials Science
    'quant-ph'            # Quantum Physics
]

KEYWORDS = [
    'graph neural network molecular',
    'transformer drug discovery',
    'conductivity prediction',
    'machine learning materials science',
    'deep learning protein folding',
    'AI scientific discovery'
]

MAX_PAPERS = 50
ENABLE_DEDUP = True
# ==========================================

# Create directories
os.makedirs(OUTPUT_DIR_MD, exist_ok=True)
os.makedirs(OUTPUT_DIR_JSON, exist_ok=True)

# Deduplication database
SEEN_IDS_FILE = os.path.join(OUTPUT_DIR_JSON, 'seen_ids.json')

def load_seen_ids():
    """Load seen paper IDs"""
    if os.path.exists(SEEN_IDS_FILE):
        with open(SEEN_IDS_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_seen_ids(seen_ids):
    """Save seen paper IDs"""
    with open(SEEN_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(seen_ids), f, indent=2)

def sanitize_filename(title):
    """Clean filename for Windows"""
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = title.replace('&', 'and')
    title = title.replace('?', '')
    title = title.strip()
    title = title[:100]
    return title

def fetch_arxiv_papers(category=None, keyword=None, max_papers=50):
    """Fetch papers from arXiv"""
    if category:
        rss_url = f'https://export.arxiv.org/rss/{category}'
        print(f"[INFO] Fetching category: {category}")
    elif keyword:
        search_query = keyword.replace(' ', '+')
        rss_url = f'http://export.arxiv.org/api/query?search_query=all:{search_query}&max_results={max_papers}'
        print(f"[INFO] Fetching keyword: {keyword}")
    else:
        return []
    
    try:
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        papers = []
        
        for entry in feed.entries[:max_papers]:
            paper_id = entry.id if hasattr(entry, 'id') else entry.link
            
            paper = {
                'id': paper_id,
                'title': entry.title,
                'link': entry.link,
                'summary': entry.get('summary', ''),
                'published': entry.get('published', ''),
                'authors': [a.name for a in entry.get('authors', [])],
                'categories': [t.term for t in entry.get('tags', [])]
            }
            papers.append(paper)
        
        print(f"  [OK] Retrieved {len(papers)} papers")
        return papers
    except Exception as e:
        print(f"  [ERROR] {e}")
        return []

def save_paper_markdown(paper):
    """Save as Markdown (Obsidian)"""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    title_slug = sanitize_filename(paper['title'])[:50]
    filename = f"{timestamp}-{title_slug}.md"
    filepath = os.path.join(OUTPUT_DIR_MD, filename)
    
    authors = ', '.join(paper['authors']) if paper['authors'] else 'Unknown'
    categories = ', '.join(paper['categories']) if paper['categories'] else 'AI'
    
    content = f"""# {paper['title']}

## Metadata
- **Source:** Arxiv
- **Link:** {paper['link']}
- **Authors:** {authors}
- **Categories:** {categories}
- **Published:** {paper['published']}
- **Collected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Abstract

{paper['summary'][:2000]}...

## Tags

#AI #MachineLearning #Research #Arxiv

---
*Auto-collected*
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

def save_papers_json(papers, source):
    """Save as JSON"""
    filename = f"{source.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
    filepath = os.path.join(OUTPUT_DIR_JSON, filename)
    
    data = {
        'source': source,
        'collectedAt': datetime.now().isoformat(),
        'totalPapers': len(papers),
        'papers': papers
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  [SAVE] JSON: {filename}")
    return len(papers)

def main():
    print("=" * 70)
    print("Arxiv AI Papers Collector v2.0")
    print("=" * 70)
    print()
    
    # Load deduplication database
    seen_ids = load_seen_ids() if ENABLE_DEDUP else set()
    print(f"[INFO] Seen papers: {len(seen_ids)}")
    print()
    
    total_new = 0
    total_dup = 0
    
    # Fetch by categories
    print("[CATEGORIES]")
    for category in CATEGORIES:
        papers = fetch_arxiv_papers(category=category, max_papers=MAX_PAPERS)
        
        # Deduplicate
        if ENABLE_DEDUP:
            new_papers = [p for p in papers if p['id'] not in seen_ids]
            dup_count = len(papers) - len(new_papers)
            total_dup += dup_count
            
            for p in new_papers:
                seen_ids.add(p['id'])
        else:
            new_papers = papers
        
        # Save
        for paper in new_papers:
            save_paper_markdown(paper)
        
        total_new += len(new_papers)
        print(f"  New: {len(new_papers)} / Duplicates: {dup_count if ENABLE_DEDUP else 0}")
    
    print()
    
    # Fetch by keywords
    print("[KEYWORDS]")
    for keyword in KEYWORDS:
        papers = fetch_arxiv_papers(keyword=keyword, max_papers=MAX_PAPERS)
        
        # Deduplicate
        if ENABLE_DEDUP:
            new_papers = [p for p in papers if p['id'] not in seen_ids]
            dup_count = len(papers) - len(new_papers)
            total_dup += dup_count
            
            for p in new_papers:
                seen_ids.add(p['id'])
        else:
            new_papers = papers
        
        # Save JSON
        count = save_papers_json(new_papers, keyword)
        total_new += len(new_papers)
    
    print()
    print("=" * 70)
    print(f"[SUMMARY]")
    print(f"  New papers: {total_new}")
    print(f"  Duplicates: {total_dup}")
    print(f"  Total: {total_new + total_dup}")
    print("=" * 70)
    
    # Save deduplication database
    if ENABLE_DEDUP:
        save_seen_ids(seen_ids)
        print(f"[SAVE] Dedup database updated ({len(seen_ids)} papers)")
    
    print()
    print("[SUCCESS] Collection complete!")

if __name__ == '__main__':
    main()
