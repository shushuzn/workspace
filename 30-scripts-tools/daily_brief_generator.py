#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Research Brief Generator
Collect from multiple sources and generate daily brief

Usage:
    python daily_brief_generator.py [--sources SOURCES] [--send]
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class BriefCollector:
    """Collect from multiple sources"""
    
    def __init__(self):
        self.sources = {
            'arxiv': self._collect_arxiv,
            'github': self._collect_github,
            'system': self._collect_system_logs
        }
    
    def collect_all(self) -> dict:
        """Collect from all sources"""
        brief = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'sources': {}
        }
        
        for source_name, collector in self.sources.items():
            try:
                print(f"[COLLECT] {source_name}...")
                brief['sources'][source_name] = collector()
            except Exception as e:
                print(f"[ERROR] {source_name} failed: {e}")
                brief['sources'][source_name] = {'error': str(e)}
        
        return brief
    
    def _collect_arxiv(self) -> dict:
        """Collect arXiv papers"""
        # Import collector
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from arxiv_collector import ArxivCollector, PaperClassifier
            
            collector = ArxivCollector()
            papers = collector.search(limit=20)
            
            classifier = PaperClassifier()
            papers = classifier.classify(papers)
            
            return {
                'count': len(papers),
                'high_relevance': sum(1 for p in papers if p.get('relevance_level') == 'HIGH'),
                'top_papers': papers[:5]
            }
        except Exception as e:
            return {'error': str(e), 'count': 0}
    
    def _collect_github(self) -> dict:
        """Collect GitHub trending"""
        # Mock for now - can integrate with GitHub API
        return {
            'count': 0,
            'trending_projects': [],
            'note': 'GitHub API integration pending'
        }
    
    def _collect_system_logs(self) -> dict:
        """Collect system execution logs"""
        # Read recent decision logs
        log_file = Path(__file__).parent.parent / '.decision_log.json'
        
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                return {
                    'decisions_count': len(logs),
                    'recent_decisions': logs[-5:] if logs else []
                }
            except:
                pass
        
        return {'decisions_count': 0}


class BriefSummarizer:
    """Summarize brief using AI"""
    
    def summarize(self, brief: dict) -> str:
        """Generate summary text"""
        date = brief.get('date', 'Unknown')
        
        summary = f"""📰 *Daily Research Brief*
📅 Date: {date}

"""
        
        # arXiv section
        arxiv = brief.get('sources', {}).get('arxiv', {})
        if arxiv.get('count', 0) > 0:
            summary += f"""📚 *arXiv Papers*
Total: {arxiv.get('count', 0)} | High Relevance: {arxiv.get('high_relevance', 0)}

"""
            top_papers = arxiv.get('top_papers', [])
            for i, paper in enumerate(top_papers[:5], 1):
                title = paper.get('title', 'N/A')[:60]
                score = paper.get('relevance_score', 0)
                summary += f"{i}. {title} (Score: {score})\n"
            summary += "\n"
        
        # System logs section
        system = brief.get('sources', {}).get('system', {})
        if system.get('decisions_count', 0) > 0:
            summary += f"""🤖 *System Activity*
Decisions: {system.get('decisions_count', 0)}

"""
        
        summary += "---\nGenerated automatically by OpenClaw"
        
        return summary


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily Brief Generator')
    parser.add_argument('--sources', type=str, nargs='+',
                       default=['arxiv', 'github', 'system'],
                       help='Sources to collect from')
    parser.add_argument('--send', action='store_true',
                       help='Send to Feishu')
    parser.add_argument('--json', action='store_true',
                       help='Output JSON')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("[BRIEF] Generating daily research brief")
    print("=" * 60)
    
    # Collect
    collector = BriefCollector()
    brief = collector.collect_all()
    
    # Summarize
    summarizer = BriefSummarizer()
    summary = summarizer.summarize(brief)
    
    # Output
    if args.json:
        print(json.dumps(brief, indent=2, ensure_ascii=False))
    else:
        print(summary)
    
    # Send
    if args.send:
        try:
            from feishu_report_generator import FeishuReportGenerator
            generator = FeishuReportGenerator()
            result = generator.send_report('daily', summary)
            print(f"\n[SEND] {result}")
        except Exception as e:
            print(f"[ERROR] Send failed: {e}")


if __name__ == '__main__':
    main()
