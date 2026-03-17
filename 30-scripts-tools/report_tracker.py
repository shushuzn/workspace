#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告消费追踪系统
=================
追踪报告的阅读次数、引用关系、使用统计等

功能:
1. 阅读计数 - 追踪报告被访问/阅读次数
2. 引用追踪 - 追踪报告间的引用关系
3. 使用统计 - 统计报告的使用频率和模式
4. 热门报告 - 识别最常被访问的报告
5. 引用图谱 - 可视化报告间的引用网络

使用:
  python report_tracker.py --track "report.md"      # 追踪阅读
  python report_tracker.py --cite "from.md" "to.md" # 记录引用
  python report_tracker.py --stats                  # 显示统计
  python report_tracker.py --popular                # 显示热门报告
  python report_tracker.py --graph                  # 生成引用图谱
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path('D:/OpenClaw/workspace')
REPORTS_DIR = WORKSPACE / '21-reports'
TRACKING_CONFIG = WORKSPACE / 'data' / 'report_tracking_config.json'
TRACKING_STATE = WORKSPACE / 'data' / 'report_tracking_state.json'
CITATIONS_FILE = WORKSPACE / 'data' / 'report_citations.json'


class ReportConsumptionTracker:
    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
        self.citations = self._load_citations()
    
    def _load_config(self):
        default_config = {
            'enabled': True,
            'track_reads': True,
            'track_citations': True,
            'track_time_spent': False,
            'auto_detect_citations': True,
            'citation_patterns': [
                r'\[([^\]]+)\]\(([^\)]+\.md)\)',  # Markdown links
                r'See\s+([^\s]+\.md)',             # "See report.md"
                r'参考\s+([^\s]+\.md)',            # "参考 report.md"
                r'REPORT-([^\s]+)',                # "REPORT-XXX"
            ],
            'popular_threshold': 10,  # Views to be considered popular
            'retention_days': 90  # How long to keep tracking data
        }
        
        if TRACKING_CONFIG.exists():
            with open(TRACKING_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config
    
    def _load_state(self):
        if TRACKING_STATE.exists():
            with open(TRACKING_STATE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'reports': {},
            'last_updated': None,
            'total_views': 0,
            'total_reports': 0
        }
    
    def _save_state(self):
        self.state['last_updated'] = datetime.now().isoformat()
        TRACKING_STATE.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACKING_STATE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def _load_citations(self):
        if CITATIONS_FILE.exists():
            with open(CITATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'citations': [], 'graph': {}}
    
    def _save_citations(self):
        CITATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CITATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.citations, f, indent=2, ensure_ascii=False)
    
    def track_view(self, filepath, user='system'):
        """追踪报告阅读"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            # Try relative to workspace
            filepath = WORKSPACE / filepath
            if not filepath.exists():
                print(f'Report not found: {filepath}')
                return False
        
        filepath_str = str(filepath.relative_to(WORKSPACE))
        
        # Initialize report tracking if needed
        if filepath_str not in self.state['reports']:
            self.state['reports'][filepath_str] = {
                'views': 0,
                'unique_viewers': [],
                'first_view': None,
                'last_view': None,
                'view_history': [],
                'citations_made': [],
                'citations_received': []
            }
        
        report_data = self.state['reports'][filepath_str]
        
        # Update view count
        report_data['views'] += 1
        self.state['total_views'] += 1
        
        # Update timestamps
        now = datetime.now().isoformat()
        if not report_data['first_view']:
            report_data['first_view'] = now
        report_data['last_view'] = now
        
        # Add to history
        report_data['view_history'].append({
            'timestamp': now,
            'user': user
        })
        
        # Keep history manageable (last 100 views)
        if len(report_data['view_history']) > 100:
            report_data['view_history'] = report_data['view_history'][-100:]
        
        # Track unique viewers
        if user not in report_data['unique_viewers']:
            report_data['unique_viewers'].append(user)
        
        self._save_state()
        
        return True
    
    def track_citation(self, from_file, to_file):
        """追踪报告引用"""
        from_file = Path(from_file)
        to_file = Path(to_file)
        
        # Normalize paths
        try:
            from_path = str(from_file.relative_to(WORKSPACE))
        except ValueError:
            from_path = str(from_file)
        
        try:
            to_path = str(to_file.relative_to(WORKSPACE))
        except ValueError:
            to_path = str(to_file)
        
        # Check if citation already exists
        for citation in self.citations['citations']:
            if citation['from'] == from_path and citation['to'] == to_path:
                print(f'Citation already exists: {from_path} -> {to_path}')
                return False
        
        # Add citation
        citation = {
            'from': from_path,
            'to': to_path,
            'timestamp': datetime.now().isoformat(),
            'type': 'explicit'
        }
        
        self.citations['citations'].append(citation)
        
        # Update graph
        if from_path not in self.citations['graph']:
            self.citations['graph'][from_path] = []
        self.citations['graph'][from_path].append(to_path)
        
        # Update report state
        if from_path in self.state['reports']:
            if to_path not in self.state['reports'][from_path]['citations_made']:
                self.state['reports'][from_path]['citations_made'].append(to_path)
        
        if to_path in self.state['reports']:
            if from_path not in self.state['reports'][to_path]['citations_received']:
                self.state['reports'][to_path]['citations_received'].append(from_path)
        
        self._save_citations()
        self._save_state()
        
        print(f'Tracked citation: {from_path} -> {to_path}')
        return True
    
    def auto_detect_citations(self):
        """自动检测报告间的引用"""
        print('Auto-detecting citations...')
        
        citations_found = 0
        
        for root, dirs, files in os.walk(REPORTS_DIR):
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find all markdown links to .md files
                    for pattern in self.config['citation_patterns']:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if isinstance(match, tuple):
                                # Markdown link: [text](url)
                                linked_file = match[1]
                            else:
                                linked_file = match
                            
                            # Clean up the filename
                            linked_file = linked_file.split('#')[0]  # Remove anchors
                            
                            # Check if it's a report file
                            if linked_file.endswith('.md'):
                                # Try to find the actual file
                                target_path = None
                                
                                # Try direct path
                                if (WORKSPACE / linked_file).exists():
                                    target_path = linked_file
                                else:
                                    # Try in reports directory
                                    for r_root, r_dirs, r_files in os.walk(REPORTS_DIR):
                                        if linked_file in r_files:
                                            target_path = str(Path(r_root) / linked_file)
                                            break
                                
                                if target_path:
                                    self.track_citation(filepath, WORKSPACE / target_path)
                                    citations_found += 1
                
                except Exception as e:
                    print(f'  Error scanning {file}: {e}')
        
        print(f'Found {citations_found} citations')
        return citations_found
    
    def get_popular_reports(self, limit=10):
        """获取热门报告"""
        if not self.state.get('reports'):
            return []
        
        # Sort by views
        sorted_reports = sorted(
            self.state['reports'].items(),
            key=lambda x: x[1]['views'],
            reverse=True
        )
        
        popular = []
        for filepath, data in sorted_reports[:limit]:
            popular.append({
                'file': filepath,
                'views': data['views'],
                'unique_viewers': len(data['unique_viewers']),
                'last_view': data['last_view']
            })
        
        return popular
    
    def get_citation_graph(self):
        """获取引用图谱"""
        return self.citations['graph']
    
    def show_stats(self):
        """显示消费统计"""
        print('='*60)
        print('Report Consumption Statistics')
        print('='*60)
        
        if not self.state.get('reports'):
            print('No tracking data yet')
            return
        
        total_reports = len(self.state['reports'])
        total_views = self.state['total_views']
        
        # Calculate average views
        avg_views = total_views / total_reports if total_reports > 0 else 0
        
        # Find most viewed
        most_viewed = max(
            self.state['reports'].items(),
            key=lambda x: x[1]['views'],
            default=(None, {'views': 0})
        )
        
        # Find most cited
        most_cited = max(
            self.state['reports'].items(),
            key=lambda x: len(x[1].get('citations_received', [])),
            default=(None, {'citations_received': []})
        )
        
        # Citations total
        total_citations = len(self.citations.get('citations', []))
        
        print(f'Total reports tracked: {total_reports}')
        print(f'Total views: {total_views}')
        print(f'Average views per report: {avg_views:.1f}')
        print(f'Total citations: {total_citations}')
        print(f'\nMost viewed report:')
        if most_viewed[0]:
            print(f'  {most_viewed[0]} ({most_viewed[1]["views"]} views)')
        print(f'\nMost cited report:')
        if most_cited[0]:
            cite_count = len(most_cited[1].get('citations_received', []))
            print(f'  {most_cited[0]} ({cite_count} citations)')
        
        # Popular reports
        print(f'\nTop 5 popular reports:')
        popular = self.get_popular_reports(5)
        for i, report in enumerate(popular, 1):
            print(f'  {i}. {report["file"]} ({report["views"]} views)')
    
    def generate_graph_report(self):
        """生成引用图谱报告"""
        print('='*60)
        print('Citation Graph Report')
        print('='*60)
        
        graph = self.get_citation_graph()
        
        if not graph:
            print('No citation data')
            return
        
        print('\nCitation relationships:')
        for source, targets in graph.items():
            print(f'\n{source}')
            for target in targets:
                print(f'  -> {target}')
        
        # Find orphan reports (no citations in or out)
        all_sources = set(graph.keys())
        all_targets = set()
        for targets in graph.values():
            all_targets.update(targets)
        
        orphan_reports = []
        for filepath in self.state['reports'].keys():
            if filepath not in all_sources and filepath not in all_targets:
                orphan_reports.append(filepath)
        
        print(f'\nOrphan reports (no citations): {len(orphan_reports)}')
        for report in orphan_reports[:10]:
            print(f'  {report}')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Report Consumption Tracker')
    parser.add_argument('--track', type=str, help='Track a report view')
    parser.add_argument('--cite', nargs=2, metavar=('FROM', 'TO'), help='Track citation')
    parser.add_argument('--auto-detect', action='store_true', help='Auto-detect citations')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--popular', action='store_true', help='Show popular reports')
    parser.add_argument('--graph', action='store_true', help='Show citation graph')
    
    args = parser.parse_args()
    
    tracker = ReportConsumptionTracker()
    
    if args.track:
        success = tracker.track_view(args.track)
        if success:
            print(f'Tracked view: {args.track}')
    elif args.cite:
        tracker.track_citation(args.cite[0], args.cite[1])
    elif args.auto_detect:
        tracker.auto_detect_citations()
    elif args.stats:
        tracker.show_stats()
    elif args.popular:
        print('Popular reports:')
        popular = tracker.get_popular_reports(10)
        for i, report in enumerate(popular, 1):
            print(f'{i}. {report["file"]} - {report["views"]} views')
    elif args.graph:
        tracker.generate_graph_report()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
