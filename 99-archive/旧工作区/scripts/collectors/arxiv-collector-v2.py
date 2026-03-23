#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arxiv AI Papers Collector v2
Collects latest AI/ML papers from arxiv.org and saves to Obsidian vault
集成目录自动化 + 多领域支持 + 任务日志
"""

import feedparser
import requests
from datetime import datetime
import os
import re
import json
import subprocess
import sys
from pathlib import Path

# Windows UTF-8 兼容
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ==================== 配置 ====================

VAULT_PATH = r"D:\obsidian\Vault"
SYNC_ROOT = "arxiv"
SCRIPTS_DIR = Path(__file__).parent
SETUP_SCRIPT = SCRIPTS_DIR / "arxiv-sync-setup.ps1"

# 完整计算机科学领域列表 (arXiv cs.* 所有子类别)
CATEGORIES = [
    # 核心 AI/ML
    'cs.AI',   # 人工智能
    'cs.LG',   # 机器学习
    'cs.CV',   # 计算机视觉与模式识别
    'cs.CL',   # 计算与语言语言学
    'cs.IR',   # 信息检索
    'cs.NE',   # 神经网络与进化计算

    # 系统与架构
    'cs.AR',   # 计算机架构
    'cs.DC',   # 分布式/并行/集群计算
    'cs.ES',   # 嵌入式系统
    'cs.NI',   # 网络与互联网架构
    'cs.OS',   # 操作系统
    'cs.PF',   # 性能评估

    # 软件工程与开发
    'cs.SE',   # 软件工程
    'cs.PL',   # 编程语言
    'cs.CR',   # 密码学与安全

    # 理论与数学
    'cs.CC',   # 计算复杂性
    'cs.CE',   # 计算工程/实践/工具
    'cs.CG',   # 计算几何
    'cs.DM',   # 离散数学
    'cs.DS',   # 数据结构与算法
    'cs.LO',   # 逻辑与计算机科学
    'cs.IT',   # 信息与编码理论
    'cs.MS',   # 数学软件

    # 应用与交叉
    'cs.RO',   # 机器人学
    'cs.SY',   # 系统与控制
    'cs.MA',   # 多智能体系统
    'cs.GT',   # 博弈论
    'cs.DB',   # 数据库
    'cs.HC',   # 人机交互

    # 其他 cs 领域
    'cs.CY',   # 计算机与社会
    'cs.DL',   # 数字图书馆
    'cs.ET',   # 新兴技术
    'cs.GL',   # 通用文献

    # 相关交叉学科
    'stat.ML', # 统计学机器学习
    'eess.SY', # 电气/电子系统工程
    'eess.SP', # 信号处理
    'q-bio.QM',# 定量生物学
    'q-fin.ST',# 定量金融
]

DOMAIN_MAP = {
    'cs.AI': 'csAI', 'cs.LG': 'csLG', 'cs.CV': 'csCV',
    'cs.CL': 'csCL', 'cs.IR': 'csIR', 'cs.NE': 'csNE',
    'cs.AR': 'csAR', 'cs.DC': 'csDC', 'cs.ES': 'csES',
    'cs.NI': 'csNI', 'cs.OS': 'csOS', 'cs.PF': 'csPF',
    'cs.SE': 'csSE', 'cs.PL': 'csPL', 'cs.CR': 'csCR',
    'cs.CC': 'csCC', 'cs.CE': 'csCE', 'cs.CG': 'csCG',
    'cs.DM': 'csDM', 'cs.DS': 'csDS', 'cs.LO': 'csLO',
    'cs.IT': 'csIT', 'cs.MS': 'csMS',
    'cs.RO': 'csRO', 'cs.SY': 'csSY', 'cs.MA': 'csMA',
    'cs.GT': 'csGT', 'cs.DB': 'csDB', 'cs.HC': 'csHC',
    'cs.CY': 'csCY', 'cs.DL': 'csDL', 'cs.ET': 'csET',
    'cs.GL': 'csGL',
    'stat.ML': 'csLG', 'eess.SY': 'eessSY', 'eess.SP': 'eessSP',
    'q-bio.QM': 'qBio', 'q-fin.ST': 'qFin',
}

MAX_PAPERS_PER_CATEGORY = 10

# ==================== 工具函数 ====================

def get_today_date():
    return datetime.now().strftime('%Y-%m-%d')

def get_date_path(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    return Path(VAULT_PATH) / SYNC_ROOT / "daily" / date.strftime('%Y') / date.strftime('%m') / date_str

def ensure_daily_structure(date_str):
    if not SETUP_SCRIPT.exists():
        print(f"[WARN] Setup script not found, using fallback mode")
        return create_fallback_structure(date_str)

    try:
        cmd = [
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", str(SETUP_SCRIPT),
            "-CreateDaily",
            "-Date", date_str,
            "-VaultPath", VAULT_PATH,
            "-SyncRoot", SYNC_ROOT
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8')
        if result.returncode == 0:
            print(f"[OK] Directory structure created")
            return True
        else:
            print(f"[WARN] PowerShell script warning: {result.stderr}")
            return create_fallback_structure(date_str)
    except Exception as e:
        print(f"[WARN] Script call failed: {e}, using fallback")
        return create_fallback_structure(date_str)

def create_fallback_structure(date_str):
    date_path = get_date_path(date_str)
    date_path.mkdir(parents=True, exist_ok=True)
    for domain in set(DOMAIN_MAP.values()):
        (date_path / domain).mkdir(exist_ok=True)
    logs_path = date_path / "logs"
    logs_path.mkdir(exist_ok=True)
    print(f"[OK] Fallback mode created: {date_path}")
    return True

def sanitize_filename(title):
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = title.replace('&', 'and')
    title = title.replace(':', '-')
    title = title[:80]
    return title.strip()

def extract_abstract(description):
    if 'Abstract: ' in description:
        return description.split('Abstract: ')[1].split('\n')[0].strip()
    return description.strip()

def get_domain_from_categories(categories):
    for cat in categories:
        term = cat.term if hasattr(cat, 'term') else str(cat)
        if term in DOMAIN_MAP:
            return DOMAIN_MAP[term]
    return 'csAI'

def extract_arxiv_id(link):
    '''从 arxiv 链接提取 arxiv ID (例如：2602.23681)'''
    match = re.search(r'arxiv[.]org/abs/(\d+\.\d+)', link)
    if match:
        return match.group(1)
    return None

def check_paper_exists(arxiv_id, date_str):
    '''检查论文是否已存在于今日目录中'''
    if not arxiv_id:
        return False, None

    date_path = get_date_path(date_str)
    if not date_path.exists():
        return False, None

    # 遍历所有领域目录
    for domain_dir in date_path.iterdir():
        if not domain_dir.is_dir() or domain_dir.name in ['logs']:
            continue

        # 检查该领域下是否已有此 arxiv ID 的论文
        for md_file in domain_dir.glob('*.md'):
            # 从文件名或内容中检查 arxiv ID
            if arxiv_id in md_file.name:
                return True, str(md_file)
            # 或者检查文件内容中的链接
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    if f'arxiv.org/abs/{arxiv_id}' in file_content:
                        return True, str(md_file)
            except Exception:
                pass

    return False, None

# ==================== 核心功能 ====================

def fetch_arxiv_papers(category='cs.AI', max_papers=20):
    rss_url = f'https://export.arxiv.org/rss/{category}'
    try:
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        papers = []
        for entry in feed.entries[:max_papers]:
            paper = {
                'title': entry.title,
                'link': entry.link,
                'description': entry.description,
                'published': entry.get('published', ''),
                'authors': entry.get('authors', []),
                'categories': entry.get('tags', []),
                'source_category': category
            }
            papers.append(paper)
        return papers
    except Exception as e:
        print(f"[ERROR] Fetch {category} failed: {e}")
        return []

def save_paper(paper, date_str):
    # 去重检查：检查论文是否已存在
    arxiv_id = extract_arxiv_id(paper['link'])
    if arxiv_id:
        exists, existing_path = check_paper_exists(arxiv_id, date_str)
        if exists:
            print(f"[SKIP] Paper already exists: {arxiv_id} -> {existing_path}")
            return None, None

    domain = get_domain_from_categories(paper['categories'])
    date_path = get_date_path(date_str)
    domain_path = date_path / domain
    domain_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%H%M%S')
    title_slug = sanitize_filename(paper['title'])[:50]
    filename = f"{timestamp}-{title_slug}.md"
    filepath = domain_path / filename

    abstract = extract_abstract(paper['description'])
    authors = ', '.join([a.name for a in paper['authors']]) if paper['authors'] else 'Unknown'
    categories = ', '.join([t.term for t in paper['categories']]) if paper['categories'] else paper['source_category']

    content = f"""---
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tags: [arxiv, {domain.lower()}]
source: arxiv
category: {categories}
---

# {paper['title']}

## Metadata
- **Source:** Arxiv
- **Link:** {paper['link']}
- **Authors:** {authors}
- **Categories:** {categories}
- **Original:** {paper['source_category']}
- **Published:** {paper['published']}
- **Collected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Domain:** {domain}

## Abstract

{abstract}

## Notes

<!-- Add your notes here -->

## Tags

#{domain} #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath, domain

def update_status_log(date_str, stats):
    date_path = get_date_path(date_str)
    logs_path = date_path / "logs"
    logs_path.mkdir(parents=True, exist_ok=True)
    status_file = logs_path / f"{date_str}-status.md"

    content = f"""---
updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tags: [arxiv, log, status]
---

# Sync Status - {date_str}

## Statistics

| Metric | Value |
|--------|-------|
| Total | {stats['total']} |
| Saved | {stats['saved']} |
| Failed | {stats['failed']} |
| Domains | {len(stats['by_domain'])} |

## By Domain

| Domain | Count |
|--------|-------|
"""

    for domain, count in sorted(stats['by_domain'].items(), key=lambda x: (x[0] is None, x[0] or '')):
        domain_name = domain if domain else 'Uncategorized'
        content += f"| {domain_name} | {count} |\n"

    content += f"""
## Last Update

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Raw Data

```json
{json.dumps(stats, ensure_ascii=False, indent=2)}
```
"""

    with open(status_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] Status log updated: {status_file}")

def update_summary(date_str, papers_data):
    date_path = get_date_path(date_str)
    summary_file = date_path / f"{date_str}-summary.md"

    by_domain = {}
    for paper, domain in papers_data:
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(paper)

    content = f"""---
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tags: [arxiv, summary, {date_str}]
---

# {date_str} Paper Summary

## Statistics

- **Total:** {len(papers_data)}
- **Domains:** {len(by_domain)}
- **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## By Domain

"""

    for domain in sorted(by_domain.keys(), key=lambda x: (x is None, x or '')):
        domain_name = domain if domain else 'Uncategorized'
        papers = by_domain[domain]
        content += f"### {domain_name} ({len(papers)} papers)\n\n"
        for i, paper in enumerate(papers[:5], 1):
            title = paper['title']
            link = paper['link']
            content += f"{i}. [{title}]({link})\n"
        if len(papers) > 5:
            content += f"\n... and {len(papers) - 5} more\n"
        content += "\n"

    content += """
## Key Papers

<!-- Mark key papers manually -->

## Tags

<!-- Auto-generated tags -->

---
*Auto-generated*
"""

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] Summary updated: {summary_file}")

# ==================== PDF 下载器集成 ====================

def download_pdfs_for_date(date_str, papers_list):
    """为指定日期的论文批量下载 PDF"""
    arxiv_ids = [p['arxiv_id'] for p in papers_list]
    try:
        from pdf_downloader import batch_download
        print(f"\n[PDF Download] Starting for {len(arxiv_ids)} papers...")
        result = batch_download(arxiv_ids, date_str)
        return result
    except Exception as e:
        print(f"[PDF Download] Error: {e}")
        return {'success': 0, 'failed': len(arxiv_ids)}

# ==================== 主流程 ====================

def main():
    print("=" * 60)
    print("Arxiv AI Papers Collector v2")
    print("Multi-domain + Auto directory")
    print("=" * 60)

    date_str = get_today_date()
    print(f"\nDate: {date_str}")

    # 1. Ensure directory
    print("\n[1/4] Creating directory structure...")
    ensure_daily_structure(date_str)

    # 2. Fetch papers
    print(f"\n[2/4] Fetching papers ({len(CATEGORIES)} domains)...")
    all_papers = []
    for category in CATEGORIES:
        papers = fetch_arxiv_papers(category, MAX_PAPERS_PER_CATEGORY)
        print(f"  {category}: {len(papers)} papers")
        all_papers.extend(papers)

    print(f"\nTotal: {len(all_papers)} papers")

    # 3. Save papers
    print(f"\n[3/4] Saving papers...")
    stats = {
        'total': len(all_papers),
        'saved': 0,
        'failed': 0,
        'by_domain': {},
    }

    papers_data = []
    for paper in all_papers:
        try:
            filepath, domain = save_paper(paper, date_str)
            stats['saved'] += 1
            stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
            papers_data.append((paper, domain))
            print(f"  [OK] {domain}: {sanitize_filename(paper['title'])[:40]}...")
        except Exception as e:
            stats['failed'] += 1
            print(f"  [FAIL] {paper['title'][:40]}... - {e}")

    # 4. Download PDFs (新增：自动下载 PDF)
    print(f"\n[4/5] Downloading PDFs...")
    try:
        arxiv_ids = [p['arxiv_id'] for p in all_papers]
        from pdf_downloader import batch_download
        batch_download(arxiv_ids, date_str)
        print(f"  [OK] PDF download complete")
    except Exception as e:
        print(f"  [WARN] PDF download failed: {e}")

    # 5. Update logs
    print(f"\n[5/5] Updating logs...")
    update_status_log(date_str, stats)
    update_summary(date_str, papers_data)

    # Output
    print("\n" + "=" * 60)
    print(f"[SUCCESS] Collection complete")
    print(f"  Total: {stats['total']}")
    print(f"  Saved: {stats['saved']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Domains: {len(stats['by_domain'])}")
    print(f"\n  Path: {get_date_path(date_str)}")
    print("=" * 60)

    return stats

if __name__ == '__main__':
    main()
