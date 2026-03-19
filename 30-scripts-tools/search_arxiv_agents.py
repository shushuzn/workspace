#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Search arXiv for AI Agent Research - arXiv AI Agent 研究扫描
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# arXiv API
ARXIV_API = "http://export.arxiv.org/api/query"

# 搜索关键词
SEARCH_QUERIES = [
    "autonomous AI agents",
    "AI assistant human collaboration",
    "agentic workflow automation",
    "self-improving AI systems",
    "multi-agent collaboration",
    "AI task planning execution",
    "human-AI interaction patterns",
    "AI memory systems long-term"
]

def search_arxiv(query, max_results=10):
    """搜索 arXiv"""
    params = {
        'search_query': f'all:{query}',
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    url = f"{ARXIV_API}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read().decode('utf-8')
        return parse_arxiv_response(data, query)
    except Exception as e:
        print(f"❌ 搜索失败 {query}: {e}")
        return []

def parse_arxiv_response(data, query):
    """解析 arXiv XML 响应"""
    import xml.etree.ElementTree as ET
    
    root = ET.fromstring(data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    papers = []
    for entry in root.findall('atom:entry', ns):
        title_elem = entry.find('atom:title', ns)
        summary_elem = entry.find('atom:summary', ns)
        published_elem = entry.find('atom:published', ns)
        id_elem = entry.find('atom:id', ns)
        
        if title_elem is not None and summary_elem is not None:
            title = title_elem.text.strip().replace('\n', ' ')
            summary = summary_elem.text.strip().replace('\n', ' ')
            published = published_elem.text if published_elem is not None else 'Unknown'
            paper_id = id_elem.text if id_elem is not None else 'Unknown'
            
            papers.append({
                'title': title,
                'summary': summary[:500] + '...' if len(summary) > 500 else summary,
                'published': published[:10],
                'arxiv_id': paper_id,
                'query': query
            })
    
    return papers

def generate_inspiration_report(papers):
    """生成灵感报告"""
    print("=" * 70)
    print("📚 arXiv AI Agent 研究扫描")
    print("=" * 70)
    
    print(f"\n📊 搜索统计:")
    print(f"  搜索词数：{len(SEARCH_QUERIES)}")
    print(f"  找到论文：{len(papers)} 篇")
    
    # 按日期分组
    by_year = {}
    for paper in papers:
        year = paper['published'][:4]
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(paper)
    
    print(f"\n📊 年度分布:")
    for year in sorted(by_year.keys(), reverse=True):
        print(f"  {year}: {len(by_year[year])} 篇")
    
    # 显示最新论文
    print(f"\n🏆 最新研究 (Top 20):")
    sorted_papers = sorted(papers, key=lambda x: x['published'], reverse=True)[:20]
    
    for i, paper in enumerate(sorted_papers, 1):
        print(f"\n  {i}. [{paper['published']}] {paper['title'][:80]}...")
        print(f"     arXiv: {paper['arxiv_id']}")
        print(f"     摘要：{paper['summary'][:150]}...")
    
    # 保存报告
    report = {
        'search_date': datetime.now().isoformat(),
        'queries': SEARCH_QUERIES,
        'total_papers': len(papers),
        'papers': papers,
        'by_year': {k: len(v) for k, v in by_year.items()}
    }
    
    report_path = "flow-archive/20260318-universal-workflow-001/arxiv-agent-research.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 报告已保存：{report_path}")
    
    return report

def main():
    """主函数"""
    print("=" * 70)
    print("🔍 arXiv AI Agent 研究扫描")
    print("=" * 70)
    
    all_papers = []
    
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"\n[{i}/{len(SEARCH_QUERIES)}] 搜索：{query}")
        papers = search_arxiv(query, max_results=5)
        all_papers.extend(papers)
        print(f"  ✅ 找到 {len(papers)} 篇")
    
    generate_inspiration_report(all_papers)
    
    print("\n" + "=" * 70)
    print("✅ arXiv 扫描 完成!")
    print("=" * 70)

if __name__ == '__main__':
    main()
