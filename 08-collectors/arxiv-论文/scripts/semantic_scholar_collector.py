#!/usr/bin/env python3
"""
Semantic Scholar API 集成 - 获取真实引用数据
用于提升学科学术段位系统的"学术影响力"维度准确性

API 文档：https://api.semanticscholar.org/api-docs/
- 无需 API Key (免费层：100 请求/100ms)
- 支持论文搜索、引用数、h-index 等

使用:
    python semantic_scholar_collector.py --query "laser induced graphene"
    python semantic_scholar_collector.py --paper-id 10.1021/acsnano.5c21102
"""
import requests
import json
import time
import sys
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Windows UTF-8 兼容
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class SemanticScholarAPI:
    """Semantic Scholar API 客户端"""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    RATE_LIMIT = 100  # 请求/100ms
    TIMEOUT = 30

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json'
        })
        self.last_request_time = 0

    def _rate_limit(self):
        """遵守速率限制"""
        elapsed = (time.time() - self.last_request_time) * 1000  # ms
        if elapsed < 100:
            time.sleep((100 - elapsed) / 1000)
        self.last_request_time = time.time()

    def search_papers(self, query: str, limit: int = 20) -> List[Dict]:
        """搜索论文"""
        endpoint = f"{self.BASE_URL}/paper/search"
        params = {
            'query': query,
            'limit': limit,
            'fields': 'title,authors,venue,year,citationCount,influentialCitationCount,publicationDate,externalIds'
        }

        self._rate_limit()
        try:
            response = self.session.get(endpoint, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            print(f"[WARN] 搜索失败：{e}")
            return []

    def get_citation_by_search(self, title: str) -> int:
        """通过标题搜索获取引用数 (更可靠)"""
        results = self.search_papers(title[:200], limit=1)
        if results:
            return results[0].get('citationCount', 0)
        return 0

    def batch_get_citations_by_search(self, papers: List[Dict], max_papers: int = 30) -> Dict[str, int]:
        """通过标题搜索批量获取引用数"""
        results = {}
        for i, paper in enumerate(papers[:max_papers]):
            title = paper.get('title', '')
            if title:
                citations = self.get_citation_by_search(title)
                results[title] = citations
                print(f"[{i +1}/{min(len(papers), max_papers)}] {citations} cites - {title[:60]}...")
                time.sleep(0.12)  # 遵守速率限制
        return results


def collect_citation_data(domain: str, existing_papers: List[Dict]) -> Dict[str, Any]:
    """收集引用数据"""
    print(f"[INFO] 开始收集 {domain} 领域引用数据...")

    api = SemanticScholarAPI()

    # 通过标题搜索获取引用数 (更可靠)
    print(f"[INFO] 使用标题搜索方式获取引用数...")
    citation_data = api.batch_get_citations_by_search(existing_papers, max_papers=30)

    # 计算统计数据
    total_citations = sum(citation_data.values())
    papers_with_citations = len([c for c in citation_data.values() if c > 0])
    avg_citations = total_citations / len(citation_data) if citation_data else 0
    max_citations = max(citation_data.values()) if citation_data else 0
    h_index = calculate_h_index(list(citation_data.values()))

    # 估算总引用 (基于采样)
    if len(existing_papers) > 30:
        scale_factor = len(existing_papers) / 30
        estimated_total = int(total_citations * scale_factor)
    else:
        estimated_total = total_citations

    return {
        'total_papers': len(existing_papers),
        'sampled_papers': len(citation_data),
        'papers_with_citations': papers_with_citations,
        'total_citations_sampled': total_citations,
        'estimated_total_citations': estimated_total,
        'average_citations': round(avg_citations, 2),
        'max_citations': max_citations,
        'h_index': h_index,
        'citation_data': citation_data,
        'collected_at': datetime.now().isoformat()
    }


def calculate_h_index(citations: List[int]) -> int:
    """计算 h-index"""
    citations_sorted = sorted(citations, reverse=True)
    h = 0
    for i, c in enumerate(citations_sorted, 1):
        if c >= i:
            h = i
        else:
            break
    return h


def calculate_impact_xp(citation_stats: Dict) -> int:
    """计算学术影响力 XP (0-10000)"""
    # 多维度评分
    paper_count_xp = min(2000, citation_stats['total_papers'] * 20)  # 最多 2000
    citation_count_xp = min(3000, citation_stats.get('estimated_total_citations', 0) * 2)  # 最多 3000
    avg_citation_xp = min(2000, citation_stats['average_citations'] * 50)  # 最多 2000
    h_index_xp = min(2000, citation_stats['h_index'] * 100)  # 最多 2000
    coverage_xp = min(1000, (citation_stats['papers_with_citations'] / max(1, citation_stats['sampled_papers'])) * 1000)

    total_xp = paper_count_xp + citation_count_xp + avg_citation_xp + h_index_xp + coverage_xp
    return min(10000, int(total_xp))


def main():
    domain = sys.argv[1] if len(sys.argv) > 1 else 'LIG'

    print(f"[INFO] Semantic Scholar 引用数据收集器")
    print(f"[INFO] 领域：{domain}")

    # 加载已有论文数据
    workspace = Path(__file__).parent.parent
    papers_file = workspace / "40-arxiv" / f"{domain.lower()}-papers-cache.json"

    if not papers_file.exists():
        print(f"[ERROR] 未找到论文数据：{papers_file}")
        sys.exit(1)

    with open(papers_file, 'r', encoding='utf-8-sig') as f:
        papers_data = json.load(f)
        papers = papers_data if isinstance(papers_data, list) else papers_data.get('papers', [])

    print(f"[INFO] 加载 {len(papers)} 篇论文")

    # 收集引用数据
    citation_stats = collect_citation_data(domain, papers)

    # 计算 XP
    impact_xp = calculate_impact_xp(citation_stats)

    print(f"\n[摘要] {domain} 领域引用统计:")
    print(f"  总论文数：{citation_stats['total_papers']}")
    print(f"  有引用论文：{citation_stats['papers_with_citations']}")
    print(f"  总引用数：{citation_stats['total_citations']}")
    print(f"  平均引用：{citation_stats['average_citations']}")
    print(f"  最高引用：{citation_stats['max_citations']}")
    print(f"  h-index: {citation_stats['h_index']}")
    print(f"  学术影响力 XP: {impact_xp}/10000")

    # 保存结果
    output_dir = workspace / "21-reports"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_path = output_dir / f"{domain}-citation-data-{timestamp}.json"

    with open(output_path, 'w', encoding='utf-8-sig') as f:
        json.dump({
            'domain': domain,
            'citation_stats': citation_stats,
            'impact_xp': impact_xp
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] 数据已保存：{output_path}")

    # 更新领域数据收集器
    print(f"\n[INFO] 更新领域数据文件...")
    latest_domain_data = sorted((workspace / "21-reports").glob(f"{domain}-domain-data-*.json"))[-1]
    if latest_domain_data.exists():
        with open(latest_domain_data, 'r', encoding='utf-8-sig') as f:
            domain_data = json.load(f)

        # 更新 impact 维度
        domain_data['impact'] = {
            'annual_papers': citation_stats['total_papers'],
            'citations': citation_stats['total_citations'],
            'h_index': citation_stats['h_index'],
            'average_citations': citation_stats['average_citations'],
            'xp': impact_xp
        }

        # 覆盖保存
        with open(latest_domain_data, 'w', encoding='utf-8-sig') as f:
            json.dump(domain_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] 已更新：{latest_domain_data.name}")


if __name__ == "__main__":
    main()
