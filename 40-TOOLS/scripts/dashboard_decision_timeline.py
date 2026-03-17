#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Dashboard Decision Timeline Widget
Real-time decision history visualization

Usage:
    python dashboard_decision_timeline.py --preview
    python dashboard_decision_timeline.py --push
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Config
DECISION_LOG = Path(r"D:\OpenClaw\workspace\20-data-reports\decision-log.json")
DASHBOARD_OUTPUT = Path(r"D:\OpenClaw\workspace\20-data-reports\dashboard-decision-timeline.json")
CLOUD_DASHBOARD_URL = "https://felixxii.xyz/api/decisions"

class DecisionTimelineWidget:
    """Decision timeline widget for Dashboard"""
    
    def __init__(self):
        self.decisions = self._load_decisions()
    
    def _load_decisions(self) -> List[Dict]:
        """Load decision log"""
        if DECISION_LOG.exists():
            with open(DECISION_LOG, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('decisions', [])
        return []
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get recent decisions"""
        return self.decisions[-limit:]
    
    def get_decision_stats(self) -> Dict:
        """Get decision statistics"""
        total = len(self.decisions)
        
        # Count by type
        by_type = {}
        for d in self.decisions:
            dtype = d.get('type', 'unknown')
            by_type[dtype] = by_type.get(dtype, 0) + 1
        
        # Count by outcome
        approved = sum(1 for d in self.decisions if d.get('outcome') == 'approved')
        rejected = sum(1 for d in self.decisions if d.get('outcome') == 'rejected')
        pending = sum(1 for d in self.decisions if d.get('outcome') == 'pending')
        
        # Auto vs Manual
        auto = sum(1 for d in self.decisions if d.get('auto_approved', False))
        manual = total - auto
        
        return {
            'total': total,
            'by_type': by_type,
            'by_outcome': {
                'approved': approved,
                'rejected': rejected,
                'pending': pending
            },
            'auto_vs_manual': {
                'auto': auto,
                'manual': manual
            },
            'approval_rate': round(approved / total * 100, 1) if total > 0 else 0
        }
    
    def generate_widget(self) -> Dict:
        """Generate dashboard widget"""
        stats = self.get_decision_stats()
        recent = self.get_recent_decisions(5)
        
        widget = {
            'widget': 'decision_timeline',
            'version': '1.0',
            'updated_at': datetime.now().isoformat(),
            'summary': {
                'total_decisions': stats['total'],
                'approval_rate': f"{stats['approval_rate']}%",
                'auto_rate': f"{round(stats['auto_vs_manual']['auto'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0}%"
            },
            'outcomes': stats['by_outcome'],
            'recent_decisions': [
                {
                    'id': d.get('id', 'N/A'),
                    'type': d.get('type', 'unknown'),
                    'description': d.get('description', '')[:50],
                    'outcome': d.get('outcome', 'pending'),
                    'timestamp': d.get('timestamp', ''),
                    'auto': d.get('auto_approved', False)
                }
                for d in recent
            ],
            'trend': self._calculate_trend()
        }
        
        return widget
    
    def _calculate_trend(self) -> str:
        """Calculate decision trend"""
        if len(self.decisions) < 2:
            return 'stable'
        
        # Compare last 10 vs previous 10
        recent = self.decisions[-10:] if len(self.decisions) >= 10 else self.decisions
        previous = self.decisions[-20:-10] if len(self.decisions) >= 20 else []
        
        if not previous:
            return 'new'
        
        recent_rate = sum(1 for d in recent if d.get('outcome') == 'approved') / len(recent)
        prev_rate = sum(1 for d in previous if d.get('outcome') == 'approved') / len(previous)
        
        if recent_rate > prev_rate + 0.1:
            return 'improving ↗'
        elif recent_rate < prev_rate - 0.1:
            return 'declining ↘'
        else:
            return 'stable →'
    
    def preview(self):
        """Preview widget in console"""
        widget = self.generate_widget()
        print(json.dumps(widget, indent=2, ensure_ascii=False))
    
    def save(self):
        """Save widget to file"""
        widget = self.generate_widget()
        
        with open(DASHBOARD_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(widget, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Decision timeline saved to {DASHBOARD_OUTPUT}")
        print(f"   Total decisions: {widget['summary']['total_decisions']}")
        print(f"   Approval rate: {widget['summary']['approval_rate']}")
        print(f"   Trend: {widget['trend']}")
    
    def push_to_dashboard(self):
        """Push to cloud dashboard"""
        import requests
        
        widget = self.generate_widget()
        
        try:
            response = requests.post(
                CLOUD_DASHBOARD_URL,
                json=widget,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[OK] Pushed to Dashboard: {CLOUD_DASHBOARD_URL}")
            else:
                print(f"[WARN] Dashboard returned {response.status_code}")
        except Exception as e:
            print(f"[FAIL] Push failed: {e}")


def main():
    parser = argparse.ArgumentParser(description='Dashboard Decision Timeline Widget')
    parser.add_argument('--preview', action='store_true', help='Preview in console')
    parser.add_argument('--push', action='store_true', help='Push to cloud dashboard')
    parser.add_argument('--save', action='store_true', help='Save to file')
    
    args = parser.parse_args()
    
    widget = DecisionTimelineWidget()
    
    if args.preview:
        widget.preview()
    elif args.push:
        widget.push_to_dashboard()
    elif args.save:
        widget.save()
    else:
        # Default: save
        widget.save()


if __name__ == '__main__':
    main()
