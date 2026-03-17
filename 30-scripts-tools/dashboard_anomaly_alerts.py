#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Dashboard Anomaly Alerts Widget
Real-time anomaly detection alerts

Usage:
    python dashboard_anomaly_alerts.py --preview
    python dashboard_anomaly_alerts.py --push
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Config
ANOMALY_LOG = Path(r"D:\OpenClaw\workspace\20-data-reports\anomaly-log.json")
DASHBOARD_OUTPUT = Path(r"D:\OpenClaw\workspace\20-data-reports\dashboard-anomaly-alerts.json")
CLOUD_DASHBOARD_URL = "https://felixxii.xyz/api/anomalies"

class AnomalyAlertsWidget:
    """Anomaly alerts widget for Dashboard"""
    
    def __init__(self):
        self.anomalies = self._load_anomalies()
    
    def _load_anomalies(self) -> List[Dict]:
        """Load anomaly log"""
        if ANOMALY_LOG.exists():
            with open(ANOMALY_LOG, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('anomalies', [])
        return []
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active (unresolved) alerts"""
        return [a for a in self.anomalies if not a.get('resolved', False)]
    
    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        total = len(self.anomalies)
        active = len(self.get_active_alerts())
        resolved = total - active
        
        # By severity
        critical = sum(1 for a in self.anomalies if a.get('severity') == 'critical')
        high = sum(1 for a in self.anomalies if a.get('severity') == 'high')
        medium = sum(1 for a in self.anomalies if a.get('severity') == 'medium')
        low = sum(1 for a in self.anomalies if a.get('severity') == 'low')
        
        # By type
        by_type = {}
        for a in self.anomalies:
            atype = a.get('type', 'unknown')
            by_type[atype] = by_type.get(atype, 0) + 1
        
        # Resolution rate
        resolution_rate = round(resolved / total * 100, 1) if total > 0 else 0
        
        # Average resolution time (hours)
        resolution_times = []
        for a in self.anomalies:
            if a.get('resolved') and a.get('detected_at') and a.get('resolved_at'):
                try:
                    detected = datetime.fromisoformat(a['detected_at'])
                    resolved_at = datetime.fromisoformat(a['resolved_at'])
                    hours = (resolved_at - detected).total_seconds() / 3600
                    resolution_times.append(hours)
                except:
                    pass
        
        avg_resolution = round(sum(resolution_times) / len(resolution_times), 1) if resolution_times else 0
        
        return {
            'total': total,
            'active': active,
            'resolved': resolved,
            'by_severity': {
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': low
            },
            'by_type': by_type,
            'resolution_rate': f"{resolution_rate}%",
            'avg_resolution_hours': avg_resolution
        }
    
    def get_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity"""
        emoji_map = {
            'critical': '🚨',
            'high': '[WARN]',
            'medium': '🟡',
            'low': 'ℹ️'
        }
        return emoji_map.get(severity, '❓')
    
    def generate_widget(self) -> Dict:
        """Generate dashboard widget"""
        stats = self.get_alert_stats()
        active = self.get_active_alerts()[:5]  # Top 5 active
        
        # Determine overall status
        if stats['by_severity']['critical'] > 0:
            overall_status = 'critical'
            status_emoji = '🚨'
        elif stats['by_severity']['high'] > 0:
            overall_status = 'high'
            status_emoji = '[WARN]'
        elif stats['active'] > 0:
            overall_status = 'warning'
            status_emoji = '🟡'
        else:
            overall_status = 'healthy'
            status_emoji = '[OK]'
        
        widget = {
            'widget': 'anomaly_alerts',
            'version': '1.0',
            'updated_at': datetime.now().isoformat(),
            'status': {
                'value': overall_status,
                'emoji': status_emoji,
                'message': f"{stats['active']} active alerts"
            },
            'summary': {
                'total_alerts': stats['total'],
                'active_alerts': stats['active'],
                'resolved_alerts': stats['resolved'],
                'resolution_rate': stats['resolution_rate'],
                'avg_resolution': f"{stats['avg_resolution_hours']}h"
            },
            'severity_breakdown': stats['by_severity'],
            'active_alerts': [
                {
                    'id': a.get('id', 'N/A'),
                    'type': a.get('type', 'unknown'),
                    'severity': a.get('severity', 'medium'),
                    'emoji': self.get_severity_emoji(a.get('severity', 'medium')),
                    'description': a.get('description', '')[:60],
                    'detected_at': a.get('detected_at', ''),
                    'impact': a.get('impact', 'unknown')
                }
                for a in active
            ],
            'trend': self._calculate_trend()
        }
        
        return widget
    
    def _calculate_trend(self) -> str:
        """Calculate anomaly trend"""
        if len(self.anomalies) < 2:
            return 'stable'
        
        # Compare last 10 vs previous 10
        recent = self.anomalies[-10:] if len(self.anomalies) >= 10 else self.anomalies
        previous = self.anomalies[-20:-10] if len(self.anomalies) >= 20 else []
        
        if not previous:
            return 'new'
        
        recent_active = sum(1 for a in recent if not a.get('resolved', False))
        prev_active = sum(1 for a in previous if not a.get('resolved', False))
        
        if recent_active < prev_active - 2:
            return 'improving ↘'
        elif recent_active > prev_active + 2:
            return 'worsening ↗'
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
        
        stats = widget['summary']
        status = widget['status']
        
        print(f"[OK] Anomaly alerts saved to {DASHBOARD_OUTPUT}")
        print(f"   Status: {status['emoji']} {status['message']}")
        print(f"   Total: {stats['total_alerts']} | Active: {stats['active_alerts']} | Resolved: {stats['resolved_alerts']}")
        print(f"   Resolution rate: {stats['resolution_rate']}")
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
    parser = argparse.ArgumentParser(description='Dashboard Anomaly Alerts Widget')
    parser.add_argument('--preview', action='store_true', help='Preview in console')
    parser.add_argument('--push', action='store_true', help='Push to cloud dashboard')
    parser.add_argument('--save', action='store_true', help='Save to file')
    
    args = parser.parse_args()
    
    widget = AnomalyAlertsWidget()
    
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
