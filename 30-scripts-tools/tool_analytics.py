#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Analytics - Tool usage analytics and insights

Features:
- Usage statistics tracking
- Performance metrics
- Error rate analysis
- Trend detection
- Recommendations
- Dashboard generation
"""

import os
import sys
import json
import time
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
ANALYTICS_DIR = WORKSPACE / 'data' / 'tool_analytics'
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

class ToolAnalytics:
    """
    Tool usage analytics and insights
    
    Features:
    - Usage tracking
    - Performance metrics
    - Error analysis
    - Trend detection
    - Recommendations
    """
    
    def __init__(self):
        self.registry_file = WORKSPACE / 'data' / 'tool_registry' / 'registry.json'
        self.usage_file = WORKSPACE / 'data' / 'tool_registry' / 'usage_stats.json'
        self.analytics_file = ANALYTICS_DIR / 'analytics.json'
        
        # Data
        self.tools = {}
        self.usage_stats = {}
        self.analytics = {
            'generated': None,
            'metrics': {},
            'trends': {},
            'recommendations': [],
        }
        
        # Load data
        self._load_data()
    
    def _load_data(self):
        """Load registry and usage data"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tools = data.get('tools', {})
        
        if self.usage_file.exists():
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                self.usage_stats = json.load(f)
        
        if self.analytics_file.exists():
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                self.analytics = json.load(f)
    
    def _save_analytics(self):
        """Save analytics to disk"""
        self.analytics['generated'] = datetime.now().isoformat()
        
        with open(self.analytics_file, 'w', encoding='utf-8') as f:
            json.dump(self.analytics, f, indent=2)
    
    def analyze(self) -> Dict:
        """
        Run comprehensive analytics
        
        Returns:
            Analytics results
        """
        print("\n📊 Running Tool Analytics...\n")
        
        # Basic metrics
        self.analytics['metrics'] = self._calculate_metrics()
        
        # Usage trends
        self.analytics['trends'] = self._analyze_trends()
        
        # Recommendations
        self.analytics['recommendations'] = self._generate_recommendations()
        
        # Save
        self._save_analytics()
        
        # Print summary
        self._print_summary()
        
        return self.analytics
    
    def _calculate_metrics(self) -> Dict:
        """Calculate usage metrics"""
        metrics = {
            'total_tools': 0,
            'active_tools': 0,
            'total_executions': 0,
            'total_errors': 0,
            'avg_execution_time_ms': 0,
            'error_rate': 0,
            'most_used': [],
            'least_used': [],
            'slowest': [],
            'error_prone': [],
        }
        
        # Filter active tools
        active_tools = {
            name: data for name, data in self.tools.items()
            if data.get('status') != 'removed'
        }
        
        metrics['total_tools'] = len(self.tools)
        metrics['active_tools'] = len(active_tools)
        
        # Aggregate usage stats
        usage_list = []
        for tool_name, stats in self.usage_stats.items():
            if tool_name not in active_tools:
                continue
            
            runs = stats.get('total_runs', 0)
            errors = stats.get('error_count', 0)
            avg_time = stats.get('avg_execution_time_ms', 0)
            
            metrics['total_executions'] += runs
            metrics['total_errors'] += errors
            
            usage_list.append({
                'name': tool_name,
                'runs': runs,
                'errors': errors,
                'avg_time_ms': avg_time,
                'error_rate': errors / max(1, runs),
            })
        
        # Calculate averages
        valid_times = [u['avg_time_ms'] for u in usage_list if u['avg_time_ms'] > 0]
        if valid_times:
            metrics['avg_execution_time_ms'] = statistics.mean(valid_times)
        else:
            metrics['avg_execution_time_ms'] = 0
        
        if usage_list:
            metrics['error_rate'] = (
                metrics['total_errors'] / max(1, metrics['total_executions'])
            )
        
        # Sort for rankings
        by_usage = sorted(usage_list, key=lambda x: x['runs'], reverse=True)
        by_time = sorted(usage_list, key=lambda x: x['avg_time_ms'], reverse=True)
        by_errors = sorted(usage_list, key=lambda x: x['error_rate'], reverse=True)
        
        metrics['most_used'] = [u['name'] for u in by_usage[:10]]
        metrics['least_used'] = [u['name'] for u in by_usage if u['runs'] == 0][:10]
        metrics['slowest'] = [u['name'] for u in by_time[:10] if u['avg_time_ms'] > 0]
        metrics['error_prone'] = [
            u['name'] for u in by_errors
            if u['error_rate'] > 0.1 and u['runs'] > 0
        ][:10]
        
        return metrics
    
    def _analyze_trends(self) -> Dict:
        """Analyze usage trends"""
        trends = {
            'daily_executions': [],
            'weekly_executions': [],
            'tool_adoption': [],
            'performance_trend': 'stable',
        }
        
        # Group executions by date (simulated - would need timestamped logs)
        # For now, use last_run timestamps
        by_date = defaultdict(int)
        
        for tool_name, stats in self.usage_stats.items():
            last_run = stats.get('last_run')
            if last_run:
                try:
                    date = datetime.fromisoformat(last_run).date()
                    by_date[str(date)] += 1
                except:
                    pass
        
        # Sort by date
        sorted_dates = sorted(by_date.keys())
        trends['daily_executions'] = [
            {'date': d, 'executions': by_date[d]}
            for d in sorted_dates[-30:]  # Last 30 days
        ]
        
        # Weekly aggregation
        weekly = defaultdict(int)
        for date_str, count in by_date.items():
            try:
                date = datetime.fromisoformat(date_str)
                week = date.isocalendar()[1]
                weekly[f"W{week}-{date.year}"] += count
            except:
                pass
        
        trends['weekly_executions'] = [
            {'week': w, 'executions': c}
            for w, c in sorted(weekly.items())[-12:]  # Last 12 weeks
        ]
        
        # Tool adoption (new tools over time)
        by_month = defaultdict(int)
        for tool_name, tool_data in self.tools.items():
            created = tool_data.get('created', '')
            if created:
                try:
                    month = created[:7]  # YYYY-MM
                    by_month[month] += 1
                except:
                    pass
        
        trends['tool_adoption'] = [
            {'month': m, 'new_tools': c}
            for m, c in sorted(by_month.items())[-12:]  # Last 12 months
        ]
        
        # Performance trend (simplified)
        if trends['daily_executions']:
            recent = sum(e['executions'] for e in trends['daily_executions'][-7:])
            older = sum(e['executions'] for e in trends['daily_executions'][-14:-7])
            
            if recent > older * 1.2:
                trends['performance_trend'] = 'increasing'
            elif recent < older * 0.8:
                trends['performance_trend'] = 'decreasing'
            else:
                trends['performance_trend'] = 'stable'
        
        return trends
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        metrics = self.analytics.get('metrics', {})
        
        # High error rate tools
        for tool_name in metrics.get('error_prone', []):
            recommendations.append({
                'type': 'error_reduction',
                'priority': 'high',
                'tool': tool_name,
                'issue': f'High error rate',
                'action': f'Review and fix errors in {tool_name}',
                'impact': 'Improve reliability',
            })
        
        # Slow tools
        for tool_name in metrics.get('slowest', [])[:5]:
            recommendations.append({
                'type': 'performance',
                'priority': 'medium',
                'tool': tool_name,
                'issue': f'Slow execution',
                'action': f'Optimize {tool_name} performance',
                'impact': 'Reduce execution time',
            })
        
        # Unused tools
        unused = metrics.get('least_used', [])
        if len(unused) > 5:
            recommendations.append({
                'type': 'cleanup',
                'priority': 'low',
                'tools': unused,
                'issue': f'{len(unused)} unused tools',
                'action': 'Consider archiving or removing unused tools',
                'impact': 'Reduce maintenance burden',
            })
        
        # Low adoption
        if metrics.get('total_executions', 0) < 100:
            recommendations.append({
                'type': 'adoption',
                'priority': 'medium',
                'issue': 'Low tool usage',
                'action': 'Promote tool usage and integration',
                'impact': 'Increase ROI on tool development',
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations
    
    def _print_summary(self):
        """Print analytics summary"""
        metrics = self.analytics.get('metrics', {})
        trends = self.analytics.get('trends', {})
        recommendations = self.analytics.get('recommendations', [])
        
        print("=" * 80)
        print("📊 TOOL ANALYTICS SUMMARY")
        print("=" * 80)
        
        print(f"\n📈 METRICS:")
        print(f"   Total tools: {metrics.get('total_tools', 0)}")
        print(f"   Active tools: {metrics.get('active_tools', 0)}")
        print(f"   Total executions: {metrics.get('total_executions', 0)}")
        print(f"   Total errors: {metrics.get('total_errors', 0)}")
        print(f"   Avg execution time: {metrics.get('avg_execution_time_ms', 0):.2f} ms")
        print(f"   Error rate: {metrics.get('error_rate', 0):.2%}")
        
        print(f"\n🏆 TOP 5 MOST USED:")
        for i, tool in enumerate(metrics.get('most_used', [])[:5], 1):
            print(f"   {i}. {tool}")
        
        print(f"\n⚠️  TOP 5 ERROR PRONE:")
        for i, tool in enumerate(metrics.get('error_prone', [])[:5], 1):
            print(f"   {i}. {tool}")
        
        print(f"\n📉 TREND: {trends.get('performance_trend', 'unknown').upper()}")
        
        print(f"\n💡 TOP 5 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"   {i}. [{rec['priority'].upper()}] {rec['action']}")
        
        print("\n" + "=" * 80)
    
    def export_report(self, output_file: Path = None) -> Path:
        """Export analytics report"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = ANALYTICS_DIR / f'analytics_report_{timestamp}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analytics, f, indent=2)
        
        print(f"✅ Report exported to: {output_file}")
        return output_file
    
    def generate_dashboard_html(self, output_file: Path = None) -> Path:
        """Generate HTML dashboard"""
        if output_file is None:
            output_file = ANALYTICS_DIR / 'tool_analytics_dashboard.html'
        
        metrics = self.analytics.get('metrics', {})
        recommendations = self.analytics.get('recommendations', [])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tool Analytics Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #4CAF50; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .section {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .recommendation {{ padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50; background: #f9f9f9; }}
        .recommendation.high {{ border-left-color: #f44336; }}
        .recommendation.medium {{ border-left-color: #ff9800; }}
        .recommendation.low {{ border-left-color: #2196F3; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        .trend-increasing {{ color: #4CAF50; }}
        .trend-decreasing {{ color: #f44336; }}
        .trend-stable {{ color: #2196F3; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Tool Analytics Dashboard</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{metrics.get('total_tools', 0)}</div>
                <div class="metric-label">Total Tools</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('active_tools', 0)}</div>
                <div class="metric-label">Active Tools</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('total_executions', 0)}</div>
                <div class="metric-label">Total Executions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('error_rate', 0):.1%}</div>
                <div class="metric-label">Error Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('avg_execution_time_ms', 0):.1f}ms</div>
                <div class="metric-label">Avg Execution Time</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Performance Trend</h2>
            <p class="trend-{trends.get('performance_trend', 'stable')}">
                Status: {trends.get('performance_trend', 'unknown').upper()}
            </p>
        </div>
        
        <div class="section">
            <h2>🏆 Top 10 Most Used Tools</h2>
            <table>
                <tr><th>#</th><th>Tool</th></tr>
                {''.join(f'<tr><td>{i}</td><td>{tool}</td></tr>' for i, tool in enumerate(metrics.get('most_used', [])[:10], 1))}
            </table>
        </div>
        
        <div class="section">
            <h2>⚠️ Error Prone Tools</h2>
            <table>
                <tr><th>#</th><th>Tool</th></tr>
                {''.join(f'<tr><td>{i}</td><td>{tool}</td></tr>' for i, tool in enumerate(metrics.get('error_prone', [])[:10], 1))}
            </table>
        </div>
        
        <div class="section">
            <h2>💡 Recommendations</h2>
            {''.join(f"<div class='recommendation {rec['priority']}'><strong>[{rec['priority'].upper()}]</strong> {rec['action']}</div>" for rec in recommendations[:10])}
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Dashboard generated: {output_file}")
        return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tool Analytics")
    parser.add_argument('--analyze', action='store_true', help='Run analytics')
    parser.add_argument('--report', action='store_true', help='Export report')
    parser.add_argument('--dashboard', action='store_true', help='Generate dashboard')
    args = parser.parse_args()
    
    analytics = ToolAnalytics()
    
    if args.analyze:
        analytics.analyze()
    
    elif args.report:
        analytics.export_report()
    
    elif args.dashboard:
        analytics.generate_dashboard_html()
        print("\n🌐 Opening dashboard...")
        os.startfile(str(analytics.generate_dashboard_html()))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
