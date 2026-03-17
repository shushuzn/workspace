#!/usr/bin/env python3
"""
使用 arxiv-daily 技能监控 LIG 文献
"""
import arxiv
import json
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("arXiv LIG 文献监控")
print("=" * 70)

# 搜索关键词
query = "laser-induced graphene"
print(f"\n搜索：{query}")

# 搜索 arXiv
search = arxiv.Search(
    query=query,
    max_results=20,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

papers = []
for result in search.results():
    paper = {
        'title': result.title,
        'authors': [a.name for a in result.authors],
        'published': result.published.strftime('%Y-%m-%d'),
        'arxiv_id': result.entry_id.split('/')[-1],
        'pdf_url': result.pdf_url,
        'abstract': result.summary[:200] + '...'
    }
    papers.append(paper)
    print(f"\n[{paper['published']}] {paper['title'][:60]}...")
    print(f"  Authors: {', '.join(paper['authors'][:3])}{' et al.' if len(paper['authors']) > 3 else ''}")
    print(f"  arXiv: {paper['arxiv_id']}")

# 保存结果
output_dir = Path("research/data/arxiv-lig")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f"arxiv_lig_{datetime.now().strftime('%Y%m%d')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'search_query': query,
        'search_date': datetime.now().isoformat(),
        'n_results': len(papers),
        'papers': papers
    }, f, indent=2, ensure_ascii=False)

print(f"\n[OK] 结果已保存：{output_file}")
print(f"  找到论文：{len(papers)} 篇")
