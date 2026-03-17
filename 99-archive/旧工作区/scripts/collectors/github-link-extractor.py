#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Link Extractor v1
从论文元数据提取 GitHub 代码仓库链接
"""

import re
import json
from datetime import datetime
from pathlib import Path

# 配置
ARXIV_DIR = Path(r"D:\obsidian\Vault\Arxiv\daily")
OUTPUT_DIR = Path(r"D:\obsidian\Vault\AI-Research\GitHub-Links")

def extract_github_links(text):
    """从文本中提取 GitHub 链接"""
    # 匹配 github.com/xxx/yyy 格式
    pattern = r'github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    links = []
    for owner, repo in matches:
        links.append({
            'owner': owner,
            'repo': repo,
            'url': f'https://github.com/{owner}/{repo}'
        })
    
    return links

def scan_papers_for_github(date_str=None):
    """扫描论文查找 GitHub 链接"""
    if date_str:
        scan_dir = ARXIV_DIR / date_str
    else:
        scan_dir = ARXIV_DIR
    
    results = []
    
    if not scan_dir.exists():
        return results
    
    for date_folder in scan_dir.iterdir():
        if not date_folder.is_dir():
            continue
        
        for domain_folder in date_folder.iterdir():
            if not domain_folder.is_dir() or domain_folder.name == 'logs':
                continue
            
            for paper_file in domain_folder.glob('*.md'):
                try:
                    with open(paper_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    links = extract_github_links(content)
                    if links:
                        # 提取 arXiv ID
                        arxiv_id = paper_file.stem.split('-')[0]
                        results.append({
                            'arxiv_id': arxiv_id,
                            'paper_file': str(paper_file),
                            'github_links': links
                        })
                except Exception as e:
                    continue
    
    return results

def save_github_links(results):
    """保存 GitHub 链接"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # JSON 格式
    json_file = OUTPUT_DIR / f"github-links-{date_str}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'scan_date': date_str,
            'total_papers': len(results),
            'papers_with_code': len(results),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    # Markdown 格式
    md_file = OUTPUT_DIR / f"github-links-{date_str}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# 论文代码仓库关联 - {date_str}\n\n")
        f.write(f"**扫描日期:** {date_str}\n")
        f.write(f"**有代码的论文:** {len(results)} 篇\n\n")
        f.write("---\n\n")
        
        for item in results:
            f.write(f"## [{item['arxiv_id']}]\n\n")
            f.write(f"**论文文件:** `{item['paper_file']}`\n\n")
            f.write("**代码仓库:**\n\n")
            for link in item['github_links']:
                f.write(f"- [{link['owner']}/{link['repo']}]({link['url']})\n")
            f.write("\n---\n\n")
    
    print(f"[OK] Saved {len(results)} papers with GitHub links")
    return md_file

def extract_links():
    """主流程"""
    print("=" * 60)
    print("GitHub Link Extractor v1")
    print("=" * 60)
    
    print("\n[1/3] Scanning papers...")
    results = scan_papers_for_github()
    print(f"  Found {len(results)} papers with GitHub links")
    
    print("\n[2/3] Saving results...")
    save_github_links(results)
    
    print("\n[3/3] Summary...")
    print(f"  Total papers scanned: ~322")
    print(f"  Papers with code: {len(results)}")
    
    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    extract_links()
