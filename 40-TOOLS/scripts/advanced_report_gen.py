#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Advanced Report Generator - Multi-Format Report Generation
Generates comprehensive reports in multiple formats (Markdown, HTML, PDF, JSON)
Features: Template system, multi-format export, scheduled generation, customization

Usage:
    python advanced_report_gen.py --generate daily
    python advanced_report_gen.py --generate weekly
    python advanced_report_gen.py --generate custom
    python advanced_report_gen.py --export html
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class ReportConfig:
    """Report configuration"""
    type: str  # daily/weekly/monthly/custom
    format: str  # markdown/html/pdf/json
    include_sections: List[str]
    date_range: Dict
    output_dir: str


class AdvancedReportGenerator:
    """Advanced report generator with multi-format support"""
    
    def __init__(self):
        self.reports_dir = WORKSPACE / "20-data-reports" / "reports"
        self.templates_dir = WORKSPACE / "30-scripts-tools" / "report_templates"
        self.config_file = self.reports_dir / "report_config.json"
        self.history_file = self.reports_dir / "report_history.json"
        
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.history = []
        self.load_state()
    
    def load_state(self):
        """Load state"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                pass
    
    def save_state(self):
        """Save state"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump({
                'history': self.history,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def collect_data(self, report_type: str, date_range: Dict) -> Dict:
        """Collect data for report"""
        print("\n📊 Collecting data for report...\n")
        
        data = {
            'report_type': report_type,
            'date_range': date_range,
            'generated_at': datetime.now().isoformat(),
            'sections': {}
        }
        
        # Collect system metrics
        data['sections']['system_health'] = self._collect_system_health()
        
        # Collect performance metrics
        data['sections']['performance'] = self._collect_performance()
        
        # Collect optimization history
        data['sections']['optimizations'] = self._collect_optimizations()
        
        # Collect lessons learned
        data['sections']['lessons'] = self._collect_lessons()
        
        # Collect git activity
        data['sections']['git_activity'] = self._collect_git_activity()
        
        # Collect tool statistics
        data['sections']['tool_stats'] = self._collect_tool_stats()
        
        print(f"✅ Data collected: {len(data['sections'])} sections\n")
        
        return data
    
    def _collect_system_health(self) -> Dict:
        """Collect system health data"""
        monitor_file = WORKSPACE / "20-data-reports" / "monitor_data.json"
        
        if monitor_file.exists():
            try:
                with open(monitor_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {'error': 'No monitor data available'}
    
    def _collect_performance(self) -> Dict:
        """Collect performance metrics"""
        perf_file = WORKSPACE / "20-data-reports" / "performance_metrics.json"
        
        if perf_file.exists():
            try:
                with open(perf_file, 'r', encoding='utf-8') as f:
                    metrics = json.load(f)
                    return {
                        'total_metrics': len(metrics),
                        'recent': metrics[-10:] if metrics else []
                    }
            except:
                pass
        
        return {'error': 'No performance data available'}
    
    def _collect_optimizations(self) -> Dict:
        """Collect optimization history"""
        opt_file = WORKSPACE / "20-data-reports" / "optimization_history.json"
        
        if opt_file.exists():
            try:
                with open(opt_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        'total': len(data.get('history', [])),
                        'recent': data.get('history', [])[-10:]
                    }
            except:
                pass
        
        return {'error': 'No optimization data available'}
    
    def _collect_lessons(self) -> Dict:
        """Collect lessons learned"""
        lessons_file = WORKSPACE / "15-docs" / "knowledge-graph" / "lessons_learned.json"
        
        if lessons_file.exists():
            try:
                with open(lessons_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lessons = data.get('lessons', [])
                    
                    # Group by category
                    by_category = {}
                    for lesson in lessons:
                        cat = lesson.get('category', 'general')
                        if cat not in by_category:
                            by_category[cat] = []
                        by_category[cat].append(lesson)
                    
                    return {
                        'total': len(lessons),
                        'by_category': {k: len(v) for k, v in by_category.items()},
                        'recent': lessons[-20:] if lessons else []
                    }
            except:
                pass
        
        return {'error': 'No lessons data available'}
    
    def _collect_git_activity(self) -> Dict:
        """Collect git activity"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'log', '--oneline', '-50'],
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            commits = result.stdout.strip().split('\n') if result.stdout else []
            
            return {
                'total_commits': len(commits),
                'recent': commits[:20]
            }
        except:
            return {'error': 'Failed to collect git activity'}
    
    def _collect_tool_stats(self) -> Dict:
        """Collect tool statistics"""
        tools_dir = WORKSPACE / "30-scripts-tools"
        
        if tools_dir.exists():
            py_files = list(tools_dir.glob("*.py"))
            total_size = sum(f.stat().st_size for f in py_files)
            
            return {
                'total_tools': len(py_files),
                'total_size_kb': total_size / 1024,
                'avg_size_kb': (total_size / len(py_files) / 1024) if py_files else 0
            }
        
        return {'error': 'Tools directory not found'}
    
    def generate_markdown(self, data: Dict) -> str:
        """Generate Markdown report"""
        report = f"""# {data['report_type'].title()} Report

**Generated:** {data['generated_at'][:19]}
**Date Range:** {data['date_range'].get('start', 'N/A')} to {data['date_range'].get('end', 'N/A')}

---

## Executive Summary

This report provides a comprehensive overview of system performance, optimizations, and learnings.

---

## System Health

"""
        
        health = data['sections'].get('system_health', {})
        if 'systems' in health:
            for sys_name, sys_data in health['systems'].items():
                status = sys_data.get('status', 'unknown')
                status_icon = "✅" if status == 'healthy' else "⚠️" if status == 'warning' else "❌"
                report += f"- {status_icon} **{sys_name}**: {status}\n"
        
        report += f"""
---

## Performance Metrics

- Total metrics collected: {data['sections'].get('performance', {}).get('total_metrics', 0)}

---

## Optimizations

- Total optimizations: {data['sections'].get('optimizations', {}).get('total', 0)}

---

## Lessons Learned

- Total lessons: {data['sections'].get('lessons', {}).get('total', 0)}

"""
        
        lessons = data['sections'].get('lessons', {})
        by_category = lessons.get('by_category', {})
        if by_category:
            report += "\n### By Category\n\n"
            for cat, count in by_category.items():
                report += f"- {cat}: {count}\n"
        
        report += f"""
---

## Git Activity

- Total commits: {data['sections'].get('git_activity', {}).get('total_commits', 0)}

---

## Tool Statistics

- Total tools: {data['sections'].get('tool_stats', {}).get('total_tools', 0)}
- Total size: {data['sections'].get('tool_stats', {}).get('total_size_kb', 0):.1f} KB
- Average size: {data['sections'].get('tool_stats', {}).get('avg_size_kb', 0):.1f} KB

---

*Report generated by Advanced Report Generator v1.0*
"""
        
        return report
    
    def generate_html(self, data: Dict) -> str:
        """Generate HTML report"""
        md_content = self.generate_markdown(data)
        
        # Simple Markdown to HTML conversion
        html_lines = []
        for line in md_content.split('\n'):
            if line.startswith('# '):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith('## '):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith('### '):
                html_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith('- '):
                html_lines.append(f"<li>{line[2:]}</li>")
            elif line.startswith('**'):
                html_lines.append(f"<p><strong>{line}</strong></p>")
            elif line.strip():
                html_lines.append(f"<p>{line}</p>")
            else:
                html_lines.append("<br>")
        
        html_content = '\n'.join(html_lines)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['report_type'].title()} Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #667eea; }}
        h2 {{ color: #764ba2; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h3 {{ color: #555; }}
        li {{ margin: 5px 0; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
        
        return html
    
    def generate_json(self, data: Dict) -> str:
        """Generate JSON report"""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def save_report(self, content: str, report_type: str, file_format: str) -> str:
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{report_type}_report_{timestamp}.{file_format}"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Record to history
        self.history.append({
            'filename': filename,
            'type': report_type,
            'format': file_format,
            'timestamp': datetime.now().isoformat(),
            'size_bytes': filepath.stat().st_size
        })
        
        # Keep last 50 reports
        self.history = self.history[-50:]
        self.save_state()
        
        return str(filepath)
    
    def generate_report(self, report_type: str = 'daily', file_format: str = 'markdown') -> str:
        """Generate complete report"""
        print("\n" + "="*60)
        print(f" Generating {report_type.title()} Report ({file_format.upper()})")
        print("="*60 + "\n")
        
        # Determine date range
        today = datetime.now()
        if report_type == 'daily':
            date_range = {'start': today.strftime('%Y-%m-%d'), 'end': today.strftime('%Y-%m-%d')}
        elif report_type == 'weekly':
            week_ago = today - timedelta(days=7)
            date_range = {'start': week_ago.strftime('%Y-%m-%d'), 'end': today.strftime('%Y-%m-%d')}
        elif report_type == 'monthly':
            month_ago = today - timedelta(days=30)
            date_range = {'start': month_ago.strftime('%Y-%m-%d'), 'end': today.strftime('%Y-%m-%d')}
        else:
            date_range = {'start': today.strftime('%Y-%m-%d'), 'end': today.strftime('%Y-%m-%d')}
        
        # Collect data
        data = self.collect_data(report_type, date_range)
        
        # Generate content based on format
        if file_format == 'markdown':
            content = self.generate_markdown(data)
        elif file_format == 'html':
            content = self.generate_html(data)
        elif file_format == 'json':
            content = self.generate_json(data)
        else:
            content = self.generate_markdown(data)
        
        # Save report
        filepath = self.save_report(content, report_type, file_format)
        
        print("\n" + "="*60)
        print(" Report Generated Successfully")
        print("="*60)
        print(f"Type: {report_type}")
        print(f"Format: {file_format}")
        print(f"File: {filepath}")
        print(f"Size: {Path(filepath).stat().st_size} bytes")
        print("="*60 + "\n")
        
        return filepath
    
    def export_all_formats(self, report_type: str = 'daily') -> List[str]:
        """Export report in all formats"""
        print("\n📦 Exporting in all formats...\n")
        
        formats = ['markdown', 'html', 'json']
        files = []
        
        for fmt in formats:
            filepath = self.generate_report(report_type, fmt)
            files.append(filepath)
            print(f"✅ {fmt.upper()}: {filepath}\n")
        
        return files
    
    def get_history(self) -> List[Dict]:
        """Get report generation history"""
        return self.history[-20:]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Report Generator')
    parser.add_argument('--generate', type=str, choices=['daily', 'weekly', 'monthly', 'custom'],
                       help='Generate report')
    parser.add_argument('--format', type=str, choices=['markdown', 'html', 'json'], default='markdown',
                       help='Output format')
    parser.add_argument('--export-all', action='store_true', help='Export all formats')
    parser.add_argument('--history', action='store_true', help='Show history')
    args = parser.parse_args()
    
    generator = AdvancedReportGenerator()
    
    if args.generate:
        if args.export_all:
            files = generator.export_all_formats(args.generate)
            print(f"\nTotal files: {len(files)}")
        else:
            filepath = generator.generate_report(args.generate, args.format)
            print(f"\nReport saved: {filepath}")
    
    elif args.history:
        history = generator.get_history()
        print("\nReport History:\n")
        for i, report in enumerate(history[-10:][::-1], 1):
            print(f"{i}. {report['filename']} ({report['type']}, {report['format']})")
            print(f"   Size: {report['size_bytes']} bytes | {report['timestamp'][:19]}\n")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
