#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Metrics Tracker - Quality Metrics Tracking System

Usage:
    py metrics-tracker.py --record 92    # Record score
    py metrics-tracker.py --trend 7      # View 7-day trend
    py metrics-tracker.py --report       # Generate weekly report
    py metrics-tracker.py --status       # Current status
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Config
WORKSPACE = Path(r"D:\OpenClaw\workspace")
METRICS_FILE = WORKSPACE / "13-memory" / "metrics.json"
REPORTS_DIR = WORKSPACE / "21-reports"

class MetricsTracker:
    def __init__(self):
        self.metrics_file = METRICS_FILE
        self.reports_dir = REPORTS_DIR
        self.data = self._load_data()
    
    def _load_data(self):
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"scores": [], "alerts": [], "created": datetime.now().isoformat()}
    
    def _save_data(self):
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def record_score(self, score, task_type="general", notes=""):
        if not 0 <= score <= 100:
            print(f"[ERROR] Score must be 0-100")
            return False
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "task_type": task_type,
            "notes": notes
        }
        
        self.data["scores"].append(entry)
        
        # Check for anomalies (drop > 10%)
        if len(self.data["scores"]) > 1:
            prev_score = self.data["scores"][-2]["score"]
            drop = prev_score - score
            if drop > 10:
                alert = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "score_drop",
                    "message": f"Score drop warning: {prev_score} -> {score} (-{drop})",
                    "severity": "high" if drop > 20 else "medium"
                }
                self.data["alerts"].append(alert)
                print(f"[WARNING] {alert['message']}")
        
        self._save_data()
        print(f"[OK] Recorded score: {score}/100 ({task_type})")
        return True
    
    def get_trend(self, days=7):
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            s for s in self.data["scores"]
            if datetime.fromisoformat(s["timestamp"]) >= cutoff
        ]
        
        if not recent:
            return None
        
        scores = [s["score"] for s in recent]
        return {
            "period": f"{days} days",
            "count": len(scores),
            "avg": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "trend": scores[-1] - scores[0] if len(scores) > 1 else 0,
            "scores": scores
        }
    
    def print_trend(self, days=7):
        trend = self.get_trend(days)
        
        if not trend or trend["count"] == 0:
            print(f"[INFO] No data in past {days} days")
            return
        
        print(f"\n{'='*60}")
        print(f"Quality Metrics Trend - Past {trend['period']}")
        print(f"{'='*60}")
        print(f"Data points: {trend['count']}")
        print(f"Average: {trend['avg']:.1f}")
        print(f"Max: {trend['max']}")
        print(f"Min: {trend['min']}")
        
        trend_arrow = "+" if trend['trend'] > 0 else "" if trend['trend'] < 0 else "="
        print(f"Trend: {trend_arrow}{trend['trend']:+d}")
        
        # ASCII chart
        print(f"\nTrend chart:")
        for i, score in enumerate(trend["scores"]):
            bar = "#" * (score // 5)
            print(f"  {i+1:2d}. {bar} {score}")
        
        print(f"{'='*60}\n")
    
    def generate_report(self):
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        trend_7 = self.get_trend(7)
        trend_30 = self.get_trend(30)
        
        report = f"""# Quality Metrics Weekly Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Overview (7 days)

"""
        if trend_7 and trend_7["count"] > 0:
            report += f"""- **Evaluations:** {trend_7['count']}
- **Average:** {trend_7['avg']:.1f}/100
- **Max:** {trend_7['max']}
- **Min:** {trend_7['min']}
- **Trend:** {trend_7['trend']:+d}
"""
        else:
            report += "- No data\n"
        
        report += f"""
---

## Overview (30 days)

"""
        if trend_30 and trend_30["count"] > 0:
            report += f"""- **Evaluations:** {trend_30['count']}
- **Average:** {trend_30['avg']:.1f}/100
- **Max:** {trend_30['max']}
- **Min:** {trend_30['min']}
- **Trend:** {trend_30['trend']:+d}
"""
        else:
            report += "- No data\n"
        
        recent_alerts = [
            a for a in self.data["alerts"]
            if datetime.fromisoformat(a["timestamp"]) >= datetime.now() - timedelta(days=7)
        ]
        
        report += f"""
---

## Alerts (This week)

"""
        if recent_alerts:
            for alert in recent_alerts:
                report += f"- [{alert['severity'].upper()}] {alert['message']}\n"
        else:
            report += "- No alerts\n"
        
        report += f"""
---

## Recent Scores

| Time | Score | Type | Notes |
|------|-------|------|-------|
"""
        for entry in reversed(self.data["scores"][-10:]):
            ts = datetime.fromisoformat(entry["timestamp"]).strftime('%m-%d %H:%M')
            report += f"| {ts} | {entry['score']} | {entry['task_type']} | {entry['notes'][:20]} |\n"
        
        report_file = self.reports_dir / f"metrics-weekly-{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"[OK] Report generated: {report_file}")
        print(report)
    
    def print_status(self):
        print(f"\n{'='*60}")
        print(f"Metrics Tracker Status")
        print(f"{'='*60}")
        print(f"Data file: {self.metrics_file}")
        print(f"Total records: {len(self.data['scores'])}")
        print(f"Total alerts: {len(self.data['alerts'])}")
        
        if self.data["scores"]:
            latest = self.data["scores"][-1]
            print(f"Latest score: {latest['score']}/100 ({latest['task_type']})")
            print(f"Updated: {latest['timestamp']}")
        
        trend_7 = self.get_trend(7)
        if trend_7 and trend_7["count"] > 0:
            print(f"7-day avg: {trend_7['avg']:.1f}")
            trend_arrow = "+" if trend_7['trend'] > 0 else "" if trend_7['trend'] < 0 else "="
            print(f"7-day trend: {trend_arrow}{trend_7['trend']:+d}")
        
        print(f"{'='*60}\n")


def main():
    tracker = MetricsTracker()
    
    if len(sys.argv) < 2:
        print(__doc__)
        tracker.print_status()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "--record" or cmd == "-r":
        if len(sys.argv) < 3:
            print("Usage: py metrics-tracker.py --record <score> [task_type] [notes]")
            return
        score = int(sys.argv[2])
        task_type = sys.argv[3] if len(sys.argv) > 3 else "general"
        notes = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        tracker.record_score(score, task_type, notes)
    
    elif cmd == "--trend" or cmd == "-t":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        tracker.print_trend(days)
    
    elif cmd == "--report" or cmd == "-r":
        tracker.generate_report()
    
    elif cmd == "--status" or cmd == "-s":
        tracker.print_status()
    
    elif cmd == "--help" or cmd == "-h":
        print(__doc__)
    
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        print("Use --help for usage")


if __name__ == "__main__":
    main()
