#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Feishu Report Generator
Generate and send formatted reports to Feishu

Usage:
    python feishu_report_generator.py --type [heartbeat|daily|weekly] [--data DATA]
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class FeishuReportGenerator:
    """Generate formatted reports for Feishu"""
    
    def __init__(self):
        self.notifier = None
        
    def _init_notifier(self):
        """Lazy load Feishu notifier"""
        if self.notifier is None:
            try:
                from feishu_api import FeishuNotifier
                self.notifier = FeishuNotifier()
            except ImportError:
                print("[WARNING] feishu_api not found, notifications disabled")
                return False
        return True
    
    def generate_heartbeat_report(self, workflow_result: dict) -> str:
        """Generate HEARTBEAT workflow report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        success_rate = workflow_result.get('success_rate', 0)
        duration = workflow_result.get('total_duration', 0)
        persona_count = workflow_result.get('persona_count', 0)
        success_count = workflow_result.get('success_count', 0)
        
        # Emoji based on success rate
        if success_rate >= 90:
            emoji = "[OK]"
        elif success_rate >= 70:
            emoji = "[WARN]"
        else:
            emoji = "[FAIL]"
        
        report = f"""
{emoji} *HEARTBEAT Workflow Report*
⏰ Time: {timestamp}
⏱️ Duration: {duration:.2f}s
[CHART] Success Rate: {success_rate:.1f}%
[TARGET] Personas: {success_count}/{persona_count}

*Persona Status:*
"""
        
        # Add persona details
        results = workflow_result.get('results', {})
        for persona, result in results.items():
            status_icon = "[OK]" if result.get('status') == 'success' else "[FAIL]"
            duration_str = f"({result.get('duration', 0):.1f}s)" if result.get('duration') else ""
            report += f"{status_icon} {persona.capitalize()} {duration_str}\n"
        
        return report.strip()
    
    def generate_daily_brief(self, data: dict) -> str:
        """Generate daily research brief"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""
📰 *Daily Research Brief*
📅 Date: {timestamp}

*New Papers:* {data.get('new_papers', 0)}
*High Relevance:* {data.get('high_relevance', 0)}
*GitHub Trending:* {data.get('trending_projects', 0)}

*Top Papers:*
"""
        
        papers = data.get('top_papers', [])
        for i, paper in enumerate(papers[:5], 1):
            report += f"{i}. {paper.get('title', 'N/A')} (Score: {paper.get('score', 0)})\n"
        
        return report.strip()
    
    def send_report(self, report_type: str, content: str):
        """Send report via Feishu"""
        if not self._init_notifier():
            return {"status": "error", "message": "Notifier not available"}
        
        try:
            return self.notifier.send_text(content)
        except Exception as e:
            return {"status": "error", "message": str(e)}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Feishu Report Generator')
    parser.add_argument('--type', type=str, required=True, 
                       choices=['heartbeat', 'daily', 'weekly'],
                       help='Report type')
    parser.add_argument('--data', type=str, help='JSON data string')
    parser.add_argument('--send', action='store_true', help='Send to Feishu')
    
    args = parser.parse_args()
    
    generator = FeishuReportGenerator()
    
    if args.data:
        data = json.loads(args.data)
    else:
        data = {}
    
    if args.type == 'heartbeat':
        content = generator.generate_heartbeat_report(data)
    elif args.type == 'daily':
        content = generator.generate_daily_brief(data)
    else:
        content = f"Weekly Report\n{json.dumps(data, indent=2)}"
    
    print(content)
    
    if args.send:
        result = generator.send_report(args.type, content)
        print(f"\n[SEND] {result}")


if __name__ == '__main__':
    main()
