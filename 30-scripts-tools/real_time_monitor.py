#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Real-time Monitor - Core System Iteration
Live system metrics with web dashboard
Features: CPU/MEM/DISK/Network, tool activity, auto-refresh, alerts

Usage:
    python real_time_monitor.py --dashboard
    python real_time_monitor.py --metrics
    python real_time_monitor.py --alert --cpu 80
"""

import os
import sys
import json
import time
import argparse
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from http.server import HTTPServer, BaseHTTPRequestHandler

# Workspace root
WORKSPACE = Path(__file__).parent.parent
METRICS_FILE = WORKSPACE / "20-data-reports" / "metrics" / "realtime.json"
ALERTS_FILE = WORKSPACE / "20-data-reports" / "metrics" / "alerts.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class RealTimeMonitor:
    """Real-time system monitoring"""
    
    def __init__(self):
        self.metrics_history = []
        self.alerts = []
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'tool_errors': 5
        }
        self._init_metrics_dir()
    
    def _init_metrics_dir(self):
        """Initialize metrics directory"""
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def collect_metrics(self) -> Dict:
        """Collect current system metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'tools': {},
            'automation': {}
        }
        
        # System metrics
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.5)
            metrics['system']['cpu_percent'] = cpu_percent
            
            # Memory
            mem = psutil.virtual_memory()
            metrics['system']['memory_percent'] = mem.percent
            metrics['system']['memory_used_gb'] = round(mem.used / (1024**3), 2)
            metrics['system']['memory_total_gb'] = round(mem.total / (1024**3), 2)
            
            # Disk
            disk = psutil.disk_usage(str(WORKSPACE))
            metrics['system']['disk_percent'] = disk.percent
            metrics['system']['disk_free_gb'] = round(disk.free / (1024**3), 2)
            
            # Network
            net = psutil.net_io_counters()
            metrics['system']['bytes_sent'] = net.bytes_sent
            metrics['system']['bytes_recv'] = net.bytes_recv
        
        except ImportError:
            metrics['system'] = {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'error': 'psutil not installed'
            }
        
        # Tool metrics
        tools_dir = WORKSPACE / "30-scripts-tools"
        py_files = list(tools_dir.glob("*.py"))
        
        metrics['tools'] = {
            'total': len(py_files),
            'total_size_kb': round(sum(f.stat().st_size for f in py_files) / 1024, 2),
            'largest': self._get_largest_tools(py_files, 5)
        }
        
        # Automation metrics
        metrics['automation'] = {
            'active_workflows': 4,
            'pending_tasks': 0,
            'last_heartbeat': self._get_last_heartbeat(),
            'cache_hit_rate': self._get_cache_stats()
        }
        
        # Check alerts
        self._check_alerts(metrics)
        
        # Save metrics
        self._save_metrics(metrics)
        
        return metrics
    
    def _get_largest_tools(self, py_files: List[Path], limit: int = 5) -> List[Dict]:
        """Get largest tool files"""
        sorted_files = sorted(py_files, key=lambda f: f.stat().st_size, reverse=True)
        
        return [
            {
                'name': f.name,
                'size_kb': round(f.stat().st_size / 1024, 2)
            }
            for f in sorted_files[:limit]
        ]
    
    def _get_last_heartbeat(self) -> str:
        """Get last heartbeat time"""
        heartbeat_file = WORKSPACE / "HEARTBEAT.md"
        if heartbeat_file.exists():
            mtime = datetime.fromtimestamp(heartbeat_file.stat().st_mtime)
            return mtime.strftime('%Y-%m-%d %H:%M:%S')
        return 'Never'
    
    def _get_cache_stats(self) -> float:
        """Get cache hit rate"""
        stats_file = WORKSPACE / "50-cache" / "cache_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    hits = stats.get('hits', 0)
                    misses = stats.get('misses', 0)
                    total = hits + misses
                    return round(hits / total * 100, 2) if total > 0 else 0
            except:
                pass
        return 0
    
    def _check_alerts(self, metrics: Dict):
        """Check for alert conditions"""
        system = metrics.get('system', {})
        
        # CPU alert
        if system.get('cpu_percent', 0) > self.alert_thresholds['cpu_percent']:
            self._create_alert('HIGH_CPU', f"CPU usage: {system['cpu_percent']}%", 'warning')
        
        # Memory alert
        if system.get('memory_percent', 0) > self.alert_thresholds['memory_percent']:
            self._create_alert('HIGH_MEMORY', f"Memory usage: {system['memory_percent']}%", 'warning')
        
        # Disk alert
        if system.get('disk_percent', 0) > self.alert_thresholds['disk_percent']:
            self._create_alert('HIGH_DISK', f"Disk usage: {system['disk_percent']}%", 'critical')
    
    def _create_alert(self, alert_type: str, message: str, severity: str):
        """Create an alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }
        
        self.alerts.append(alert)
        self._save_alerts()
        
        print(f"\n🚨 ALERT [{severity.upper()}]: {message}")
    
    def _save_metrics(self, metrics: Dict):
        """Save metrics to file"""
        # Add to history
        self.metrics_history.append(metrics)
        
        # Keep last 100 entries
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        # Save
        with open(METRICS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'current': metrics,
                'history': self.metrics_history[-20:]  # Last 20 for trends
            }, f, indent=2, ensure_ascii=False)
    
    def _save_alerts(self):
        """Save alerts to file"""
        with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'alerts': self.alerts[-50:],  # Last 50 alerts
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        metrics = self.collect_metrics()
        system = metrics.get('system', {})
        tools = metrics.get('tools', {})
        automation = metrics.get('automation', {})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Real-time Monitor</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 12px; color: #666; }}
        .status-ok {{ color: #22c55e; }}
        .status-warning {{ color: #f59e0b; }}
        .status-critical {{ color: #ef4444; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; font-size: 18px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Real-time System Monitor</h1>
        <p>Last updated: {metrics['timestamp'][:19].replace('T', ' ')}</p>
        
        <div class="card">
            <h2>System Resources</h2>
            <div class="metric">
                <div class="metric-value">{system.get('cpu_percent', 0):.1f}%</div>
                <div class="metric-label">CPU Usage</div>
            </div>
            <div class="metric">
                <div class="metric-value">{system.get('memory_percent', 0):.1f}%</div>
                <div class="metric-label">Memory Usage</div>
            </div>
            <div class="metric">
                <div class="metric-value">{system.get('disk_percent', 0):.1f}%</div>
                <div class="metric-label">Disk Usage</div>
            </div>
            <div class="metric">
                <div class="metric-value">{system.get('memory_used_gb', 0):.1f} GB</div>
                <div class="metric-label">Memory Used</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Tool Statistics</h2>
            <div class="metric">
                <div class="metric-value">{tools.get('total', 0)}</div>
                <div class="metric-label">Total Tools</div>
            </div>
            <div class="metric">
                <div class="metric-value">{tools.get('total_size_kb', 0):.0f} KB</div>
                <div class="metric-label">Total Code</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Automation Status</h2>
            <div class="metric">
                <div class="metric-value">{automation.get('active_workflows', 0)}</div>
                <div class="metric-label">Active Workflows</div>
            </div>
            <div class="metric">
                <div class="metric-value">{automation.get('cache_hit_rate', 0):.1f}%</div>
                <div class="metric-label">Cache Hit Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{automation.get('last_heartbeat', 'N/A')}</div>
                <div class="metric-label">Last Heartbeat</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Alerts</h2>
            <p>{len(self.alerts)} active alerts</p>
        </div>
    </div>
</body>
</html>"""
        
        return html


class MonitorHandler(BaseHTTPRequestHandler):
    """HTTP handler for monitor dashboard"""
    
    def __init__(self, *args, monitor=None, **kwargs):
        self.monitor = monitor
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            html = self.monitor.get_dashboard_html()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        
        elif self.path == '/metrics':
            metrics = self.monitor.collect_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(metrics, indent=2).encode('utf-8'))
        
        elif self.path == '/alerts':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'alerts': self.monitor.alerts}, indent=2).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def main():
    parser = argparse.ArgumentParser(description='Real-time Monitor')
    parser.add_argument('--dashboard', action='store_true', help='Start web dashboard')
    parser.add_argument('--metrics', action='store_true', help='Show current metrics')
    parser.add_argument('--alert', action='store_true', help='Check alerts')
    parser.add_argument('--cpu', type=int, help='CPU alert threshold')
    parser.add_argument('--port', type=int, default=8081, help='Dashboard port')
    args = parser.parse_args()
    
    monitor = RealTimeMonitor()
    
    if args.dashboard:
        if args.cpu:
            monitor.alert_thresholds['cpu_percent'] = args.cpu
        
        print(f"\n🌐 Dashboard: http://localhost:{args.port}")
        print("Auto-refresh: 5 seconds")
        print("Press Ctrl+C to stop\n")
        
        # Create handler with monitor reference
        def handler(*args, **kwargs):
            MonitorHandler(*args, monitor=monitor, **kwargs)
        
        server = HTTPServer(('0.0.0.0', args.port), handler)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[MONITOR] Stopped")
    
    if args.metrics:
        metrics = monitor.collect_metrics()
        print("\n" + "=" * 60)
        print("Current Metrics")
        print("=" * 60)
        
        system = metrics.get('system', {})
        print(f"\nSystem:")
        print(f"  CPU: {system.get('cpu_percent', 0):.1f}%")
        print(f"  Memory: {system.get('memory_percent', 0):.1f}%")
        print(f"  Disk: {system.get('disk_percent', 0):.1f}%")
        
        tools = metrics.get('tools', {})
        print(f"\nTools:")
        print(f"  Total: {tools.get('total', 0)}")
        print(f"  Code Size: {tools.get('total_size_kb', 0)} KB")
        
        automation = metrics.get('automation', {})
        print(f"\nAutomation:")
        print(f"  Cache Hit Rate: {automation.get('cache_hit_rate', 0):.1f}%")
        print(f"  Last Heartbeat: {automation.get('last_heartbeat', 'N/A')}")
        
        print("=" * 60)
    
    if args.alert:
        monitor.collect_metrics()
        print(f"\nActive Alerts: {len(monitor.alerts)}")
        
        if args.cpu:
            monitor.alert_thresholds['cpu_percent'] = args.cpu
            print(f"CPU threshold set to {args.cpu}%")
    
    if not any([args.dashboard, args.metrics, args.alert]):
        parser.print_help()


if __name__ == "__main__":
    main()
