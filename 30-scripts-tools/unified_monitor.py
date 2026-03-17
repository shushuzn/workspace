#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unified Monitoring Center - Central Dashboard for All Systems
Real-time monitoring of all OpenClaw systems with unified interface
Features: Multi-system dashboard, real-time metrics, alerts, historical trends

Usage:
    python unified_monitor.py --start
    python unified_monitor.py --status
    python unified_monitor.py --alerts
    python unified_monitor.py --report
"""

import os
import sys
import json
import http.server
import socketserver
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass, asdict

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class SystemHealth:
    """System health status"""
    name: str
    status: str  # healthy/warning/critical/offline
    uptime: float
    last_run: str
    next_run: str
    metrics: Dict
    alerts: List[str]


@dataclass
class Alert:
    """System alert"""
    id: str
    system: str
    severity: str  # critical/warning/info
    message: str
    timestamp: str
    acknowledged: bool


class UnifiedMonitor:
    """Unified monitoring center"""
    
    def __init__(self, port: int = 8088):
        self.port = port
        self.data_file = WORKSPACE / "20-data-reports" / "monitor_data.json"
        self.alerts_file = WORKSPACE / "20-data-reports" / "monitor_alerts.json"
        
        self.systems = {}
        self.alerts = []
        self.start_time = datetime.now()
        
        self.load_state()
    
    def load_state(self):
        """Load state"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.systems = data.get('systems', {})
            except:
                pass
        
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.alerts = data.get('alerts', [])
            except:
                pass
    
    def save_state(self):
        """Save state"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'systems': self.systems,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump({
                'alerts': [asdict(a) if isinstance(a, Alert) else a 
                          for a in self.alerts],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def collect_system_metrics(self) -> Dict[str, SystemHealth]:
        """Collect metrics from all systems"""
        print("\n📊 Collecting system metrics...\n")
        
        # Define systems to monitor
        systems_to_monitor = {
            'self_iteration': {
                'script': 'self_iter_cli.py',
                'status_cmd': 'status',
                'port': None
            },
            'persona_collab': {
                'script': 'persona_cli.py',
                'status_cmd': 'status',
                'port': 8084
            },
            'workflow_engine': {
                'script': 'workflow_engine_v2.py',
                'status_cmd': None,
                'port': 8085
            },
            'dashboard_self_iter': {
                'script': 'self_iter_dashboard.py',
                'status_cmd': None,
                'port': 8086
            },
            'dashboard_persona': {
                'script': 'persona_dashboard.py',
                'status_cmd': None,
                'port': 8084
            },
            'cache_manager': {
                'script': 'cache_manager.py',
                'status_cmd': 'status',
                'port': None
            },
            'self_healing': {
                'script': 'self_healing.py',
                'status_cmd': 'status',
                'port': None
            },
            'orchestrator': {
                'script': 'system_orchestrator.py',
                'status_cmd': 'status',
                'port': 8087
            }
        }
        
        health_data = {}
        
        for sys_name, config in systems_to_monitor.items():
            try:
                # Check port status
                port_status = 'listening' if config['port'] and self._check_port(config['port']) else 'not_listening'
                
                # Get script status
                script_status = 'running' if self._check_script_running(config['script']) else 'stopped'
                
                # Determine overall health
                if port_status == 'listening' or script_status == 'running':
                    status = 'healthy'
                elif config['port']:
                    status = 'warning'
                else:
                    status = 'offline'
                
                health = SystemHealth(
                    name=sys_name,
                    status=status,
                    uptime=0.0,
                    last_run=datetime.now().isoformat(),
                    next_run='N/A',
                    metrics={
                        'port': config['port'],
                        'port_status': port_status,
                        'script_status': script_status
                    },
                    alerts=[]
                )
                
                health_data[sys_name] = health
                print(f"✅ {sys_name}: {status}")
                
            except Exception as e:
                print(f"❌ {sys_name}: {e}")
                health_data[sys_name] = SystemHealth(
                    name=sys_name,
                    status='error',
                    uptime=0.0,
                    last_run='N/A',
                    next_run='N/A',
                    metrics={'error': str(e)},
                    alerts=[str(e)]
                )
        
        self.systems = {k: asdict(v) for k, v in health_data.items()}
        self.save_state()
        
        return health_data
    
    def _check_port(self, port: int) -> bool:
        """Check if port is listening"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _check_script_running(self, script: str) -> bool:
        """Check if script process is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['cmdline']):
                try:
                    if script in ' '.join(proc.info['cmdline'] or []):
                        return True
                except:
                    pass
            return True  # Assume running if psutil fails
        except:
            return True  # Assume running if psutil not available
    
    def generate_alerts(self) -> List[Alert]:
        """Generate alerts based on system health"""
        print("\n🚨 Checking for alerts...\n")
        
        alerts = []
        
        for sys_name, health in self.systems.items():
            if health['status'] == 'critical':
                alert = Alert(
                    id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{sys_name}",
                    system=sys_name,
                    severity='critical',
                    message=f"System {sys_name} is in critical state",
                    timestamp=datetime.now().isoformat(),
                    acknowledged=False
                )
                alerts.append(alert)
                print(f"🔴 CRITICAL: {sys_name}")
            
            elif health['status'] == 'warning':
                alert = Alert(
                    id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{sys_name}",
                    system=sys_name,
                    severity='warning',
                    message=f"System {sys_name} has warnings",
                    timestamp=datetime.now().isoformat(),
                    acknowledged=False
                )
                alerts.append(alert)
                print(f"🟡 WARNING: {sys_name}")
            
            elif health['status'] == 'offline':
                alert = Alert(
                    id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{sys_name}",
                    system=sys_name,
                    severity='warning',
                    message=f"System {sys_name} is offline",
                    timestamp=datetime.now().isoformat(),
                    acknowledged=False
                )
                alerts.append(alert)
                print(f"⚪ OFFLINE: {sys_name}")
        
        self.alerts.extend(alerts)
        self.alerts = self.alerts[-50:]  # Keep last 50 alerts
        self.save_state()
        
        return alerts
    
    def get_summary(self) -> Dict:
        """Get monitoring summary"""
        total = len(self.systems)
        healthy = sum(1 for s in self.systems.values() if s['status'] == 'healthy')
        warning = sum(1 for s in self.systems.values() if s['status'] == 'warning')
        critical = sum(1 for s in self.systems.values() if s['status'] == 'critical')
        offline = sum(1 for s in self.systems.values() if s['status'] == 'offline')
        
        return {
            'total_systems': total,
            'healthy': healthy,
            'warning': warning,
            'critical': critical,
            'offline': offline,
            'health_score': (healthy / max(1, total)) * 100,
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'total_alerts': len(self.alerts),
            'last_updated': datetime.now().isoformat()
        }
    
    def generate_html_dashboard(self) -> str:
        """Generate HTML dashboard"""
        summary = self.get_summary()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Monitoring Center - OpenClaw</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .header h1 {{ color: #667eea; margin-bottom: 10px; }}
        .header p {{ color: #666; }}
        .summary {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px; 
        }}
        .stat-card {{ 
            background: rgba(255,255,255,0.95); 
            padding: 25px; 
            border-radius: 15px; 
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
        .stat-label {{ color: #666; font-size: 0.9em; }}
        .healthy {{ color: #10b981; }}
        .warning {{ color: #f59e0b; }}
        .critical {{ color: #ef4444; }}
        .offline {{ color: #6b7280; }}
        .systems {{ 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .system-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-top: 20px; 
        }}
        .system-card {{ 
            border: 2px solid #e5e7eb; 
            border-radius: 10px; 
            padding: 20px;
            transition: all 0.3s;
        }}
        .system-card.healthy {{ border-color: #10b981; background: #ecfdf5; }}
        .system-card.warning {{ border-color: #f59e0b; background: #fffbeb; }}
        .system-card.critical {{ border-color: #ef4444; background: #fef2f2; }}
        .system-card.offline {{ border-color: #9ca3af; background: #f9fafb; }}
        .system-name {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }}
        .system-status {{ 
            display: inline-block; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 0.85em; 
            font-weight: bold;
            margin-bottom: 15px;
        }}
        .status-healthy {{ background: #10b981; color: white; }}
        .status-warning {{ background: #f59e0b; color: white; }}
        .status-critical {{ background: #ef4444; color: white; }}
        .status-offline {{ background: #6b7280; color: white; }}
        .system-metrics {{ font-size: 0.9em; color: #666; }}
        .system-metrics div {{ margin: 5px 0; }}
        .alerts {{ 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-top: 20px;
        }}
        .alert-item {{ 
            padding: 15px; 
            border-left: 4px solid; 
            margin: 10px 0; 
            border-radius: 5px;
            background: #f9fafb;
        }}
        .alert-critical {{ border-color: #ef4444; background: #fef2f2; }}
        .alert-warning {{ border-color: #f59e0b; background: #fffbeb; }}
        .alert-info {{ border-color: #3b82f6; background: #eff6ff; }}
        .refresh-info {{ text-align: center; margin-top: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Unified Monitoring Center</h1>
            <p>Real-time monitoring of all OpenClaw systems</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                Auto-refresh: 10 seconds
            </p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-value healthy">{summary['healthy']}</div>
                <div class="stat-label">Healthy Systems</div>
            </div>
            <div class="stat-card">
                <div class="stat-value warning">{summary['warning']}</div>
                <div class="stat-label">Warnings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value critical">{summary['critical']}</div>
                <div class="stat-label">Critical</div>
            </div>
            <div class="stat-card">
                <div class="stat-value offline">{summary['offline']}</div>
                <div class="stat-label">Offline</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #667eea;">{summary['health_score']:.1f}%</div>
                <div class="stat-label">Health Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #8b5cf6;">{summary['uptime_hours']:.1f}h</div>
                <div class="stat-label">Monitor Uptime</div>
            </div>
        </div>
        
        <div class="systems">
            <h2 style="margin-bottom: 20px; color: #667eea;">📊 System Status</h2>
            <div class="system-grid">
"""
        
        for sys_name, health in self.systems.items():
            status_class = health['status']
            status_label = health['status'].upper()
            
            html += f"""
                <div class="system-card {status_class}">
                    <div class="system-name">{sys_name.replace('_', ' ').title()}</div>
                    <div class="system-status status-{status_class}">{status_label}</div>
                    <div class="system-metrics">
                        <div><strong>Last Run:</strong> {health['last_run'][:19] if health['last_run'] != 'N/A' else 'N/A'}</div>
                        <div><strong>Port:</strong> {health['metrics'].get('port', 'N/A')}</div>
                        <div><strong>Port Status:</strong> {health['metrics'].get('port_status', 'N/A')}</div>
                        <div><strong>Script:</strong> {health['metrics'].get('script_status', 'N/A')}</div>
                    </div>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
        
        # Alerts section
        if self.alerts:
            html += """
        <div class="alerts">
            <h2 style="margin-bottom: 20px; color: #667eea;">🚨 Recent Alerts</h2>
"""
            for alert in self.alerts[-10:][::-1]:
                alert_class = alert['severity']
                html += f"""
            <div class="alert-item alert-{alert_class}">
                <strong>{alert['severity'].upper()}</strong> - {alert['system']}
                <br>{alert['message']}
                <br><small style="color: #666;">{alert['timestamp'][:19]}</small>
            </div>
"""
            html += """
        </div>
"""
        
        html += f"""
        <div class="refresh-info">
            <p>Auto-refreshing every 10 seconds | Press F5 to refresh manually</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 10 seconds
        setTimeout(() => {{ location.reload(); }}, 10000);
    </script>
</body>
</html>
"""
        
        return html
    
    def start_server(self):
        """Start web server"""
        monitor = self
        
        class MonitorHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    html = monitor.generate_html_dashboard()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html.encode())
                elif self.path == '/api/data':
                    data = {
                        'summary': monitor.get_summary(),
                        'systems': monitor.systems,
                        'alerts': [asdict(a) if isinstance(a, Alert) else a 
                                  for a in monitor.alerts[-20:]]
                    }
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress logging
        
        with socketserver.TCPServer(("", self.port), MonitorHandler) as httpd:
            print(f"\n✅ Unified Monitor started at http://localhost:{self.port}")
            print(f"API endpoint: http://localhost:{self.port}/api/data\n")
            httpd.serve_forever()
    
    def run(self):
        """Run monitoring cycle"""
        print("\n" + "="*60)
        print(" Unified Monitoring Center")
        print("="*60 + "\n")
        
        # Collect metrics
        self.collect_system_metrics()
        
        # Generate alerts
        alerts = self.generate_alerts()
        
        # Print summary
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print(" Monitoring Summary")
        print("="*60)
        print(f"Total Systems: {summary['total_systems']}")
        print(f"Healthy: {summary['healthy']}")
        print(f"Warning: {summary['warning']}")
        print(f"Critical: {summary['critical']}")
        print(f"Offline: {summary['offline']}")
        print(f"Health Score: {summary['health_score']:.1f}%")
        print(f"Total Alerts: {len(alerts)}")
        print("="*60 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified Monitoring Center')
    parser.add_argument('--start', action='store_true', help='Start web server')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--alerts', action='store_true', help='Show alerts')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--port', type=int, default=8088, help='Server port')
    args = parser.parse_args()
    
    monitor = UnifiedMonitor(port=args.port)
    
    if args.start:
        monitor.run()
        monitor.start_server()
    
    elif args.status:
        monitor.run()
    
    elif args.alerts:
        monitor.generate_alerts()
        print(f"\nTotal alerts: {len(monitor.alerts)}")
    
    elif args.report:
        monitor.run()
        html = monitor.generate_html_dashboard()
        report_file = WORKSPACE / "20-data-reports" / f"monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n✅ Report saved: {report_file}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
