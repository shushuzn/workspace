#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Observability - Real-time metrics and dashboard
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
OBS_DIR = WORKSPACE / 'data' / 'cache_observability'
OBS_DIR.mkdir(parents=True, exist_ok=True)

class CacheMetrics:
    """Collect and analyze cache performance metrics"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        
        # Time-series metrics
        self.latency_history: deque = deque(maxlen=window_size)
        self.hit_rate_history: deque = deque(maxlen=window_size)
        self.query_history: deque = deque(maxlen=window_size)
        self.tier_distribution_history: deque = deque(maxlen=window_size)
        
        # Aggregated metrics
        self.total_queries = 0
        self.total_hits = 0
        self.total_misses = 0
        
        # Latency percentiles
        self.latencies: List[float] = []
        
        # Tier-specific metrics
        self.tier_metrics: Dict[str, Dict] = {
            'CRITICAL': {'hits': 0, 'misses': 0, 'latency_sum': 0},
            'HIGH': {'hits': 0, 'misses': 0, 'latency_sum': 0},
            'MEDIUM': {'hits': 0, 'misses': 0, 'latency_sum': 0},
            'LOW': {'hits': 0, 'misses': 0, 'latency_sum': 0},
        }
        
        # Anomaly detection
        self.anomalies: List[Dict] = []
        
        # Start time
        self.start_time = datetime.now()
    
    def record_query(self, query: str, cache_hit: bool, 
                     latency_ms: float, tier: str = None):
        """
        Record a cache query
        
        Args:
            query: Search query
            cache_hit: Whether cache was hit
            latency_ms: Query latency in milliseconds
            tier: Cache tier (CRITICAL/HIGH/MEDIUM/LOW)
        """
        timestamp = datetime.now()
        
        self.total_queries += 1
        
        if cache_hit:
            self.total_hits += 1
        else:
            self.total_misses += 1
        
        # Record latency
        self.latencies.append(latency_ms)
        self.latency_history.append({
            'timestamp': timestamp.isoformat(),
            'latency_ms': latency_ms,
        })
        
        # Record hit rate (rolling window)
        recent_queries = list(self.query_history)[-100:] + [cache_hit]
        if len(recent_queries) > 100:
            recent_queries = recent_queries[-100:]
        
        hit_rate = sum(1 for q in recent_queries if q) / len(recent_queries) * 100
        self.hit_rate_history.append({
            'timestamp': timestamp.isoformat(),
            'hit_rate': hit_rate,
        })
        
        # Record query
        self.query_history.append({
            'timestamp': timestamp.isoformat(),
            'query': query,
            'cache_hit': cache_hit,
            'latency_ms': latency_ms,
            'tier': tier,
        })
        
        # Update tier metrics
        if tier and tier in self.tier_metrics:
            if cache_hit:
                self.tier_metrics[tier]['hits'] += 1
            else:
                self.tier_metrics[tier]['misses'] += 1
            self.tier_metrics[tier]['latency_sum'] += latency_ms
    
    def get_latency_percentiles(self) -> Dict:
        """Get latency percentiles"""
        if not self.latencies:
            return {}
        
        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)
        
        return {
            'p50': sorted_latencies[int(n * 0.50)] if n > 0 else 0,
            'p75': sorted_latencies[int(n * 0.75)] if n > 0 else 0,
            'p90': sorted_latencies[int(n * 0.90)] if n > 0 else 0,
            'p95': sorted_latencies[int(n * 0.95)] if n > 0 else 0,
            'p99': sorted_latencies[int(n * 0.99)] if n > 0 else 0,
            'avg': sum(sorted_latencies) / n if n > 0 else 0,
            'min': sorted_latencies[0] if n > 0 else 0,
            'max': sorted_latencies[-1] if n > 0 else 0,
        }
    
    def get_current_hit_rate(self, window: int = 100) -> float:
        """Get current hit rate (rolling window)"""
        recent = list(self.query_history)[-window:]
        if not recent:
            return 0.0
        
        hits = sum(1 for q in recent if q.get('cache_hit', False))
        return hits / len(recent) * 100
    
    def get_tier_performance(self) -> Dict:
        """Get performance metrics per tier"""
        tier_perf = {}
        
        for tier, metrics in self.tier_metrics.items():
            total = metrics['hits'] + metrics['misses']
            hit_rate = (metrics['hits'] / total * 100) if total > 0 else 0
            avg_latency = (metrics['latency_sum'] / total) if total > 0 else 0
            
            tier_perf[tier] = {
                'total_queries': total,
                'hits': metrics['hits'],
                'misses': metrics['misses'],
                'hit_rate_percent': round(hit_rate, 2),
                'avg_latency_ms': round(avg_latency, 3),
            }
        
        return tier_perf
    
    def detect_anomalies(self) -> List[Dict]:
        """Detect performance anomalies"""
        anomalies = []
        
        # Check latency spike
        latencies = [h['latency_ms'] for h in self.latency_history][-100:]
        if len(latencies) >= 10:
            avg_latency = sum(latencies) / len(latencies)
            recent_latency = latencies[-1] if latencies else 0
            
            if recent_latency > avg_latency * 3:  # 3x spike
                anomalies.append({
                    'type': 'LATENCY_SPIKE',
                    'severity': 'HIGH',
                    'message': f'Latency spike detected: {recent_latency:.2f}ms (avg: {avg_latency:.2f}ms)',
                    'timestamp': datetime.now().isoformat(),
                })
        
        # Check hit rate drop
        hit_rates = [h['hit_rate'] for h in self.hit_rate_history][-100:]
        if len(hit_rates) >= 10:
            avg_hit_rate = sum(hit_rates) / len(hit_rates)
            recent_hit_rate = hit_rates[-1] if hit_rates else 0
            
            if recent_hit_rate < avg_hit_rate * 0.5:  # 50% drop
                anomalies.append({
                    'type': 'HIT_RATE_DROP',
                    'severity': 'MEDIUM',
                    'message': f'Hit rate drop: {recent_hit_rate:.2f}% (avg: {avg_hit_rate:.2f}%)',
                    'timestamp': datetime.now().isoformat(),
                })
        
        self.anomalies.extend(anomalies)
        
        # Keep only recent anomalies
        if len(self.anomalies) > 100:
            self.anomalies = self.anomalies[-50:]
        
        return anomalies
    
    def get_summary(self) -> Dict:
        """Get metrics summary"""
        uptime = datetime.now() - self.start_time
        
        return {
            'uptime': str(uptime),
            'total_queries': self.total_queries,
            'total_hits': self.total_hits,
            'total_misses': self.total_misses,
            'overall_hit_rate_percent': round(
                self.total_hits / self.total_queries * 100 if self.total_queries > 0 else 0, 2
            ),
            'current_hit_rate_percent': round(self.get_current_hit_rate(), 2),
            'latency_percentiles': self.get_latency_percentiles(),
            'tier_performance': self.get_tier_performance(),
            'anomalies_detected': len(self.anomalies),
            'recent_anomalies': self.anomalies[-5:],
        }


class CacheObservabilityDashboard:
    """
    Real-time observability dashboard for cache performance
    
    Features:
    - Real-time metrics collection
    - Latency tracking (percentiles)
    - Hit rate monitoring
    - Tier performance analysis
    - Anomaly detection
    - Alert generation
    - HTML dashboard export
    """
    
    def __init__(self, metrics: CacheMetrics = None):
        self.metrics = metrics or CacheMetrics()
        
        # Alert thresholds
        self.thresholds = {
            'latency_p95_warning': 100,    # ms
            'latency_p95_critical': 500,   # ms
            'hit_rate_warning': 50,        # %
            'hit_rate_critical': 20,       # %
        }
        
        # Alerts
        self.alerts: List[Dict] = []
    
    def record(self, query: str, cache_hit: bool, 
               latency_ms: float, tier: str = None):
        """Record a cache query"""
        self.metrics.record_query(query, cache_hit, latency_ms, tier)
        
        # Check thresholds
        self._check_thresholds(latency_ms, cache_hit)
    
    def _check_thresholds(self, latency_ms: float, cache_hit: bool):
        """Check alert thresholds"""
        percentiles = self.metrics.get_latency_percentiles()
        hit_rate = self.metrics.get_current_hit_rate()
        
        # Latency alerts
        p95 = percentiles.get('p95', 0)
        
        if p95 > self.thresholds['latency_p95_critical']:
            self._add_alert('CRITICAL', 'LATENCY', f'P95 latency {p95:.2f}ms > {self.thresholds["latency_p95_critical"]}ms')
        elif p95 > self.thresholds['latency_p95_warning']:
            self._add_alert('WARNING', 'LATENCY', f'P95 latency {p95:.2f}ms > {self.thresholds["latency_p95_warning"]}ms')
        
        # Hit rate alerts
        if hit_rate < self.thresholds['hit_rate_critical']:
            self._add_alert('CRITICAL', 'HIT_RATE', f'Hit rate {hit_rate:.2f}% < {self.thresholds["hit_rate_critical"]}%')
        elif hit_rate < self.thresholds['hit_rate_warning']:
            self._add_alert('WARNING', 'HIT_RATE', f'Hit rate {hit_rate:.2f}% < {self.thresholds["hit_rate_warning"]}%')
    
    def _add_alert(self, severity: str, alert_type: str, message: str):
        """Add alert"""
        # Avoid duplicate alerts
        for alert in self.alerts[-10:]:
            if alert['message'] == message:
                return
        
        self.alerts.append({
            'severity': severity,
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
        })
        
        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-50:]
    
    def get_status(self) -> Dict:
        """Get current system status"""
        summary = self.metrics.get_summary()
        
        # Determine overall status
        status = 'HEALTHY'
        
        p95 = summary['latency_percentiles'].get('p95', 0)
        hit_rate = summary['current_hit_rate_percent']
        
        if p95 > self.thresholds['latency_p95_critical'] or hit_rate < self.thresholds['hit_rate_critical']:
            status = 'CRITICAL'
        elif p95 > self.thresholds['latency_p95_warning'] or hit_rate < self.thresholds['hit_rate_warning']:
            status = 'WARNING'
        
        return {
            'status': status,
            'summary': summary,
            'active_alerts': len([a for a in self.alerts if a['timestamp'] > (datetime.now() - timedelta(minutes=5)).isoformat()]),
            'recent_alerts': self.alerts[-5:],
        }
    
    def export_dashboard(self, output_file: Path = None) -> Path:
        """Export HTML dashboard"""
        if output_file is None:
            output_file = OBS_DIR / 'cache_dashboard.html'
        
        status = self.get_status()
        summary = status['summary']
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cache Observability Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ 
            color: white; 
            text-align: center; 
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .status-banner {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .status-HEALTHY {{ background: #10b981; color: white; }}
        .status-WARNING {{ background: #f59e0b; color: white; }}
        .status-CRITICAL {{ background: #ef4444; color: white; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .tier-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .tier-table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }}
        .tier-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        .tier-table tr:hover {{
            background: #f5f5f5;
        }}
        .alert-box {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .alert {{
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        .alert-CRITICAL {{
            background: #fee;
            border-color: #ef4444;
        }}
        .alert-WARNING {{
            background: #fff3cd;
            border-color: #f59e0b;
        }}
        .timestamp {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 20px;
        }}
        .progress-bar {{
            background: #e5e7eb;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Cache Observability Dashboard</h1>
        
        <div class="status-banner status-{status['status']}">
            <h2>System Status: {status['status']}</h2>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>📊 Total Queries</h3>
                <div class="metric-value">{summary['total_queries']:,}</div>
                <div class="metric-label">Since startup</div>
            </div>
            
            <div class="metric-card">
                <h3>🎯 Overall Hit Rate</h3>
                <div class="metric-value">{summary['overall_hit_rate_percent']}%</div>
                <div class="metric-label">All time</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {summary['overall_hit_rate_percent']}%"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>⚡ Current Hit Rate</h3>
                <div class="metric-value">{summary['current_hit_rate_percent']}%</div>
                <div class="metric-label">Last 100 queries</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {summary['current_hit_rate_percent']}%"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>⏱️ P95 Latency</h3>
                <div class="metric-value">{summary['latency_percentiles'].get('p95', 0):.2f}ms</div>
                <div class="metric-label">95th percentile</div>
            </div>
            
            <div class="metric-card">
                <h3>📈 Avg Latency</h3>
                <div class="metric-value">{summary['latency_percentiles'].get('avg', 0):.2f}ms</div>
                <div class="metric-label">Mean response time</div>
            </div>
            
            <div class="metric-card">
                <h3>🔔 Active Alerts</h3>
                <div class="metric-value">{status['active_alerts']}</div>
                <div class="metric-label">Last 5 minutes</div>
            </div>
        </div>
        
        <h3 style="color: white; margin-bottom: 15px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">📋 Tier Performance</h3>
        <table class="tier-table">
            <thead>
                <tr>
                    <th>Tier</th>
                    <th>Queries</th>
                    <th>Hits</th>
                    <th>Misses</th>
                    <th>Hit Rate</th>
                    <th>Avg Latency</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for tier, perf in summary['tier_performance'].items():
            html += f"""
                <tr>
                    <td><strong>{tier}</strong></td>
                    <td>{perf['total_queries']:,}</td>
                    <td>{perf['hits']:,}</td>
                    <td>{perf['misses']:,}</td>
                    <td>{perf['hit_rate_percent']}%</td>
                    <td>{perf['avg_latency_ms']:.3f}ms</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <div class="alert-box">
            <h3 style="color: #667eea; margin-bottom: 15px;">🚨 Recent Alerts</h3>
"""
        
        if status['recent_alerts']:
            for alert in status['recent_alerts']:
                html += f"""
            <div class="alert alert-{alert['severity']}">
                <strong>{alert['severity']} - {alert['type']}</strong>: {alert['message']}
                <br><small>{alert['timestamp']}</small>
            </div>
"""
        else:
            html += "<p>No recent alerts. System operating normally.</p>"
        
        html += f"""
        </div>
        
        <div class="timestamp">
            Dashboard generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            Uptime: {summary['uptime']}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 10 seconds
        setTimeout(() => location.reload(), 10000);
    </script>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Dashboard exported to: {output_file}")
        return output_file
    
    def get_recommendations(self) -> List[str]:
        """Get optimization recommendations based on metrics"""
        recommendations = []
        summary = self.metrics.get_summary()
        
        # Hit rate recommendations
        hit_rate = summary['overall_hit_rate_percent']
        if hit_rate < 30:
            recommendations.append("⚠️  Very low hit rate. Consider increasing cache size or TTL.")
        elif hit_rate < 50:
            recommendations.append("⚠️  Low hit rate. Review tier assignment and TTL settings.")
        elif hit_rate > 90:
            recommendations.append("✅ Excellent hit rate! Cache is well-optimized.")
        
        # Latency recommendations
        p95 = summary['latency_percentiles'].get('p95', 0)
        if p95 > 500:
            recommendations.append("⚠️  High P95 latency. Consider optimizing slower cache layers.")
        elif p95 > 100:
            recommendations.append("⚠️  Moderate latency. Review tier performance.")
        elif p95 < 10:
            recommendations.append("✅ Excellent latency! System is highly responsive.")
        
        # Tier-specific recommendations
        tier_perf = summary['tier_performance']
        
        for tier, perf in tier_perf.items():
            if perf['total_queries'] > 0:
                if perf['hit_rate_percent'] < 30:
                    recommendations.append(f"⚠️  {tier} tier has low hit rate ({perf['hit_rate_percent']}%). Consider tuning.")
                elif perf['hit_rate_percent'] > 90:
                    recommendations.append(f"✅ {tier} tier performing excellently ({perf['hit_rate_percent']}% hit rate).")
        
        # Anomaly recommendations
        if summary['anomalies_detected'] > 10:
            recommendations.append(f"⚠️  High number of anomalies detected ({summary['anomalies_detected']}). Investigate root cause.")
        
        return recommendations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cache Observability")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--dashboard', action='store_true', help='Export dashboard')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    args = parser.parse_args()
    
    metrics = CacheMetrics()
    dashboard = CacheObservabilityDashboard(metrics)
    
    if args.demo:
        print("\n🔍 Cache Observability Demo")
        print("=" * 80)
        
        # Simulate queries
        print("\n📊 Simulating cache queries...\n")
        
        import random
        tiers = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        queries = [
            "memory optimization",
            "security config",
            "workflow automation",
            "neural embedding",
            "cache tier",
        ]
        
        for i in range(200):
            query = random.choice(queries)
            cache_hit = random.random() > 0.3  # 70% hit rate
            latency = random.uniform(1, 50) if cache_hit else random.uniform(50, 200)
            tier = random.choice(tiers)
            
            dashboard.record(query, cache_hit, latency, tier)
            
            if (i + 1) % 50 == 0:
                print(f"Recorded {i + 1} queries...")
        
        # Get status
        print("\n📈 System Status:")
        status = dashboard.get_status()
        
        print(f"Status: {status['status']}")
        print(f"Total queries: {status['summary']['total_queries']}")
        print(f"Overall hit rate: {status['summary']['overall_hit_rate_percent']}%")
        print(f"Current hit rate: {status['summary']['current_hit_rate_percent']}%")
        print(f"P95 latency: {status['summary']['latency_percentiles'].get('p95', 0):.2f}ms")
        print(f"Active alerts: {status['active_alerts']}")
        
        # Get recommendations
        print("\n💡 Recommendations:")
        for rec in dashboard.get_recommendations():
            print(f"   {rec}")
        
        # Export dashboard
        if args.dashboard:
            dashboard.export_dashboard()
        
        print("\n✅ Demo complete!")
    
    elif args.dashboard:
        dashboard.export_dashboard()
    
    elif args.stats:
        status = dashboard.get_status()
        print("\n📊 Cache Observability Statistics")
        print("=" * 80)
        
        summary = status['summary']
        print(f"Status: {summary['status']}")
        print(f"Uptime: {summary['uptime']}")
        print(f"Total queries: {summary['total_queries']}")
        print(f"Overall hit rate: {summary['overall_hit_rate_percent']}%")
        print(f"Current hit rate: {summary['current_hit_rate_percent']}%")
        
        print("\nLatency Percentiles:")
        for key, val in summary['latency_percentiles'].items():
            print(f"   {key}: {val:.2f}ms")
        
        print("\nTier Performance:")
        for tier, perf in summary['tier_performance'].items():
            print(f"   {tier}: {perf['hit_rate_percent']}% hit rate, {perf['avg_latency_ms']:.3f}ms avg latency")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
