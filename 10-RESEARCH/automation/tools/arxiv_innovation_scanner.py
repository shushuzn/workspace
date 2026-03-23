#!/usr/bin/env python3
"""arXiv Innovation Scanner - Fetch latest AI agent papers"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import xml.etree.ElementTree as ET

def fetch_arxiv_papers(query, max_results=15):
    """Fetch papers from arXiv API"""
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results
    }

    response = requests.get(base_url, params=params, timeout=30)
    response.raise_for_status()

    # Parse XML
    root = ET.fromstring(response.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    papers = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns).text.strip()
        summary = entry.find("atom:summary", ns).text.strip()
        published = entry.find("atom:published", ns).text
        arxiv_id = entry.find("atom:id", ns).text

        # Get authors
        authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]

        papers.append({
            "title": title,
            "summary": summary,
            "published": published[:10],  # YYYY-MM-DD
            "arxiv_id": arxiv_id.split("/")[-1],
            "authors": authors[:3]  # Top 3 authors
        })

    return papers

def analyze_innovation(papers):
    """Analyze papers for innovation opportunities"""
    print("\n" + "=" *80)
    print("📚 arXiv Innovation Analysis")
    print("=" *80)

    innovations = []
    for i, paper in enumerate(papers, 1):
        print(f"\n[{i}/{len(papers)}] {paper['title']}")
        print(f"    Published: {paper['published']} | arXiv:{paper['arxiv_id']}")
        print(f"    Authors: {', '.join(paper['authors'])}")
        print(f"    Summary: {paper['summary'][:200]}...")

        # Extract innovation potential
        summary_lower = paper['summary'].lower()
        keywords = {
            "memory": "Memory system",
            "context": "Context management",
            "agent": "Agent architecture",
            "planning": "Planning/reasoning",
            "tool": "Tool use",
            "multi": "Multi-agent",
            "learning": "Learning/adaptation",
            "efficient": "Efficiency optimization"
        }

        detected = [v for k, v in keywords.items() if k in summary_lower]
        if detected:
            print(f"    💡 Innovation: {', '.join(detected)}")
            innovations.append({
                "paper": paper,
                "themes": detected
            })

    return innovations

if __name__ == "__main__":
    print("🔍 Scanning arXiv for AI Agent Memory/Context papers...")

    # Search queries
    queries = [
        "ti:agent AND ti:memory",
        "ti:agent AND ti:context",
        "ti:LLM AND ti:planning",
        "all:autonomous agent memory"
    ]

    all_papers = []
    for query in queries:
        try:
            papers = fetch_arxiv_papers(query, max_results=5)
            all_papers.extend(papers)
        except Exception as e:
            print(f"⚠️ Query '{query}' failed: {e}")

    # Remove duplicates by arxiv_id
    seen = set()
    unique_papers = []
    for p in all_papers:
        if p['arxiv_id'] not in seen:
            seen.add(p['arxiv_id'])
            unique_papers.append(p)

    print(f"\n✅ Found {len(unique_papers)} unique papers")

    # Analyze
    innovations = analyze_innovation(unique_papers[:10])

    print(f"\n🎯 Total innovation opportunities: {len(innovations)}")
    print("=" *80)
