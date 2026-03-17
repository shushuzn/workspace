#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv Paper Collector
Automatically collect and classify papers from arXiv API

Usage:
    python arxiv_collector.py [--categories CATEGORIES] [--limit LIMIT] [--classify]
"""

import sys
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class ArxivCollector:
    """Collect papers from arXiv API"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.categories = {
            "CNT": ["cond-mat.mes-hall", "cond-mat.supr-con"],
            "AI": ["cs.AI", "cs.LG", "cs.CL"],
            "Agent": ["cs.AI", "cs.MA"],
            "ML": ["cs.LG", "stat.ML"]
        }
        
    def search(self, categories: list = None, limit: int = 50, 
               days_back: int = 1) -> list:
        """Search arXiv for papers"""
        if not categories:
            categories = list(self.categories.keys())
        
        papers = []
        
        for category in categories:
            arxiv_cats = self.categories.get(category, [category])
            
            for cat in arxiv_cats:
                # Build query
                search_query = f"cat:{cat}"
                start = 0
                max_results = min(limit, 100)
                
                try:
                    response = requests.get(
                        self.base_url,
                        params={
                            'search_query': search_query,
                            'start': start,
                            'max_results': max_results,
                            'sortBy': 'submittedDate',
                            'sortOrder': 'descending'
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        parsed = self._parse_response(response.text, category)
                        papers.extend(parsed)
                    
                    time.sleep(0.5)  # Be nice to API
                    
                except Exception as e:
                    print(f"[ERROR] Failed to fetch {cat}: {e}")
        
        return papers
    
    def _parse_response(self, xml_text: str, category: str) -> list:
        """Parse arXiv XML response"""
        papers = []
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_text)
            
            # Atom namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                paper = {
                    'title': self._get_text(entry, 'atom:title', ns),
                    'summary': self._get_text(entry, 'atom:summary', ns),
                    'authors': [a.text for a in entry.findall('atom:author/atom:name', ns)],
                    'published': self._get_text(entry, 'atom:published', ns),
                    'arxiv_id': self._get_text(entry, 'atom:id', ns),
                    'category': category,
                    'collected_at': datetime.now().isoformat()
                }
                papers.append(paper)
                
        except Exception as e:
            print(f"[ERROR] Parse failed: {e}")
        
        return papers
    
    def _get_text(self, element, tag: str, ns: dict) -> str:
        """Get text from XML element"""
        elem = element.find(tag, ns)
        return elem.text.strip() if elem is not None and elem.text else ""
    
    def save(self, papers: list, output_dir: str = None):
        """Save papers to JSON file"""
        if not output_dir:
            output_dir = Path(__file__).parent.parent / '40-collectors'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'arxiv_papers_{timestamp}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        print(f"[SAVE] {len(papers)} papers saved to {output_file}")
        return output_file


class PaperClassifier:
    """Classify papers by relevance"""
    
    def __init__(self):
        self.keywords = {
            "CNT": ["carbon nanotube", "nanotube", "conductivity", "CNT"],
            "AI": ["artificial intelligence", "neural network", "deep learning", "AI"],
            "Agent": ["agent", "multi-agent", "autonomous", "LLM agent"],
            "ML": ["machine learning", "training", "model", "optimization"]
        }
    
    def classify(self, papers: list) -> list:
        """Classify papers by relevance score"""
        for paper in papers:
            score = self._calculate_relevance(paper)
            paper['relevance_score'] = score
            paper['relevance_level'] = self._get_level(score)
        
        # Sort by relevance
        papers.sort(key=lambda x: x['relevance_score'], reverse=True)
        return papers
    
    def _calculate_relevance(self, paper: dict) -> float:
        """Calculate relevance score (0-100)"""
        title = paper.get('title', '').lower()
        summary = paper.get('summary', '').lower()
        category = paper.get('category', '')
        
        score = 0
        keywords = self.keywords.get(category, [])
        
        # Title match (high weight)
        for kw in keywords:
            if kw.lower() in title:
                score += 20
        
        # Summary match (medium weight)
        for kw in keywords:
            if kw.lower() in summary:
                score += 5
        
        # Cap at 100
        return min(score, 100)
    
    def _get_level(self, score: float) -> str:
        """Get relevance level from score"""
        if score >= 80:
            return "HIGH"
        elif score >= 50:
            return "MEDIUM"
        else:
            return "LOW"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='arXiv Paper Collector')
    parser.add_argument('--categories', type=str, nargs='+', 
                       default=['CNT', 'AI', 'Agent', 'ML'],
                       help='Categories to collect')
    parser.add_argument('--limit', type=int, default=50,
                       help='Max papers per category')
    parser.add_argument('--classify', action='store_true',
                       help='Classify papers by relevance')
    parser.add_argument('--save', action='store_true',
                       help='Save to file')
    parser.add_argument('--json', action='store_true',
                       help='Output JSON')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("[ARXIV] Starting paper collection")
    print("=" * 60)
    
    # Collect
    collector = ArxivCollector()
    papers = collector.search(categories=args.categories, limit=args.limit)
    
    print(f"[COLLECT] {len(papers)} papers collected")
    
    # Classify
    if args.classify:
        classifier = PaperClassifier()
        papers = classifier.classify(papers)
        
        high_count = sum(1 for p in papers if p.get('relevance_level') == 'HIGH')
        print(f"[CLASSIFY] {high_count} HIGH relevance papers")
    
    # Save
    if args.save:
        collector.save(papers)
    
    # Output
    if args.json:
        print(json.dumps(papers[:10], indent=2, ensure_ascii=False))
    else:
        print(f"\n[SUMMARY] Total: {len(papers)} papers")
        if papers:
            print(f"Top paper: {papers[0].get('title', 'N/A')[:80]}")


if __name__ == '__main__':
    main()
