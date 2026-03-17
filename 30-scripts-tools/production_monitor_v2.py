#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Production Monitor v2 - Unified Production Monitoring System

Integrates:
- System health monitoring
- Predictive alerting
- Auto-fix orchestration
- Trend analysis
- Web dashboard

Usage:
    python production_monitor_v2.py --start
    python production_monitor_v2.py --status
    python production_monitor_v2.py --demo
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
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Import components
try:
    from predictive_alerting_engine import PredictiveAlertingEngine
    from auto_fix_orchestrator import AutoFixOrchestrator
    from trend_analyzer_pro import TrendAnalyzer
except ImportError:
    print("⚠️ Warning: Some components not found. Running in limited mode.")
    PredictiveAlertingEngine = None
    AutoFixOrchestrator = None
    TrendAnalyzer = None


@dataclass
class SystemStatus:
    """System status"""
    name: str
    status: str  # healthy/warning/critical/offline
    health_score: float
    uptime_hours: float
    last_check: str
    metrics: Dict


class ProductionMonitor:
    """Unified production monitoring system"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.data_dir = WORKSPACE / "20-data-reports"
        self.state_file = self.data_dir / "production_monitor_state.json"
        
        # Components
        self.alert_engine = PredictiveAlertingEngine() if PredictiveAlertingEngine else None
        self.fix_orchestrator = AutoFixOrchestrator() if AutoFixOrchestrator else None
        self.trend_analyzer = TrendAnalyzer() if TrendAnalyzer else None
        
        # Systems to monitor
        self.systems = {
            'memory_core': {'status': 'unknown', 'health': 0},
            'autonomous_engine': {'status': 'unknown', 'health': 0},
            'persona_system': {'status': 'unknown', 'health': 0},
            'feishu_integration': {'status': 'unknown', 'health': 0},
            'arxiv_collector': {'status': 'unknown', 'health': 0},
            'distillation_system': {'status': 'unknown', 'health': 0},
        }
        
        self.start_time = datetime.now()
        self.check_history = []
        
        self.load_state()
    
    def load_state(self):
        """Load state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.systems = data.get('systems', self.systems)
            except:
                pass
    
    def save_state(self):
        """Save state"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({
                'systems': self.systems,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def check_system(self, name: str) -> SystemStatus:
        """Check system health"""
        # In real implementation: check actual system
        # For demo: simulate health check
        
        import random
        health = random.uniform(85, 100)
        
        if health >= 95:
            status = 'healthy'
        elif health >= 80:
            status = 'warning'
        else:
            status = 'critical'
        
        self.systems[name] = {
            'status': status,
            'health': health
        }
        
        self.save_state()
        
        return SystemStatus(
            name=name,
            status=status,
            health_score=health,
            uptime_hours=(datetime.now() - self.start_time).total_seconds() / 3600,
            last_check=datetime.now().isoformat(),
            metrics={
                'cpu': random.uniform(20, 60),
                'memory': random.uniform(40, 70),
                'errors': random.randint(0, 5)
            }
        )
    
    def run_health_check(self) -> Dict:
        """Run health check on all systems"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'systems': {},
            'overall_health': 0,
            'healthy_count': 0,
            'warning_count': 0,
            'critical_count': 0
        }
        
        total_health = 0
        
        for system_name in self.systems.keys():
            status = self.check_system(system_name)
            results['systems'][system_name] = asdict(status)
            
            total_health += status.health_score
            
            if status.status == 'healthy':
                results['healthy_count'] += 1
            elif status.status == 'warning':
                results['warning_count'] += 1
            else:
                results['critical_count'] += 1
        
        results['overall_health'] = total_health / len(self.systems)
        
        # Add to history
        self.check_history.append(results)
        if len(self.check_history) > 100:
            self.check_history = self.check_history[-100:]
        
        # Run predictive analysis if available
        if self.alert_engine:
            # Add metrics to alert engine
            for system_name, status in results['systems'].items():
                self.alert_engine.add_metric(system_name, 'health', status['health_score'])
                self.alert_engine.add_metric(system_name, 'cpu', status['metrics']['cpu'])
                self.alert_engine.add_metric(system_name, 'memory', status['metrics']['memory'])
            
            # Run analysis
            self.alert_engine.analyze()
        
        # Run auto-fix if available
        if self.fix_orchestrator:
            # Check for issues
            for system_name, status in results['systems'].items():
                if status['status'] == 'critical':
                    issue = self.fix_orchestrator.detect_issue(
                        system_name, 'health', 
                        status['health_score'], 
                        threshold=80
                    )
                    if issue:
                        self.fix_orchestrator.execute_fix(issue)
        
        # Run trend analysis if available
        if self.trend_analyzer:
            self.trend_analyzer.analyze_all()
        
        return results
    
    def get_dashboard_data(self) -> Dict:
        """Get data for dashboard"""
        return {
            'status': 'operational',
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'systems': self.systems,
            'overall_health': sum(s['health'] for s in self.systems.values()) / len(self.systems),
            'recent_checks': self.check_history[-10:],
            'predictions': self.alert_engine.get_status()['recent_predictions'] if self.alert_engine else [],
            'recent_fixes': self.fix_orchestrator.get_status()['recent_actions'] if self.fix_orchestrator else [],
            'trends': self.trend_analyzer.get_status()['recent_trends'] if self.trend_analyzer else []
        }
    
    def get_status(self) -> Dict:
        """Get monitor status"""
        return {
            'status': 'operational',
            'port': self.port,
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'systems_monitored': len(self.systems),
            'components': {
                'alert_engine': self.alert_engine is not None,
                'fix_orchestrator': self.fix_orchestrator is not None,
                'trend_analyzer': self.trend_analyzer is not None
            }
        }


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for dashboard"""
    
    monitor = None
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self.generate_dashboard()
            self.wfile.write(html.encode('utf-8'))
        
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = self.monitor.get_dashboard_data()
            self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
        
        else:
            super().do_GET()
    
    def generate_dashboard(self) -> str:
        """Generate HTML dashboard"""
        data = self.monitor.get_dashboard_data()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🎯 Production Monitor v2</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #666; font-size: 16px; margin-bottom: 15px; }}
        .system {{ display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee; }}
        .system:last-child {{ border-bottom: none; }}
        .system-name {{ font-weight: 600; }}
        .system-status {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
        .status-healthy {{ background: #d4edda; color: #155724; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        .status-critical {{ background: #f8d7da; color: #721c24; }}
        .metric {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .health-bar {{ width: 100%; height: 10px; background: #eee; border-radius: 5px; overflow: hidden; margin-top: 10px; }}
        .health-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #ffc107, #dc3545); transition: width 0.3s; }}
        .prediction {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid #ffc107; }}
        .fix-action {{ background: #d4edda; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid #28a745; }}
        .refresh {{ position: fixed; bottom: 20px; right: 20px; background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Production Monitor v2</h1>
        
        <div class="grid">
            <!-- Overall Health -->
            <div class="card">
                <h2>Overall Health</h2>
                <div class="metric">{data['overall_health']:.1f}%</div>
                <div class="health-bar">
                    <div class="health-fill" style="width: {data['overall_health']}%"></div>
                </div>
                <div class="metric-label">Uptime: {data['uptime_hours']:.1f} hours</div>
            </div>
            
            <!-- Systems Status -->
            <div class="card">
                <h2>Systems Status</h2>
                {''.join([f'''
                <div class="system">
                    <span class="system-name">{name}</span>
                    <span class="system-status status-{status['status']}">{status['status'].upper()}</span>
                </div>
                ''' for name, status in data['systems'].items()])}
            </div>
            
            <!-- Predictions -->
            <div class="card">
                <h2>🔮 Predictive Alerts</h2>
                {''.join([f'<div class="prediction">⚠️ {p.get("system", "Unknown")}: {p.get("probability", 0)*100:.0f}% failure probability</div>' for p in data['predictions'][-3:]]) or '<div style="color: #999;">No predictions</div>'}
            </div>
            
            <!-- Recent Fixes -->
            <div class="card">
                <h2>🔧 Auto-Fixes</h2>
                {''.join([f'<div class="fix-action">✅ {f.get("action", "Unknown")}: {f.get("status", "unknown").upper()}</div>' for f in data['recent_fixes'][-3:]]) or '<div style="color: #999;">No recent fixes</div>'}
            </div>
        </div>
        
        <!-- Health Chart -->
        <div class="card">
            <h2>📊 Health Trend (Last 10 Checks)</h2>
            <canvas id="healthChart" height="80"></canvas>
        </div>
    </div>
    
    <div class="refresh" onclick="location.reload()">🔄 Refresh</div>
    
    <script>
        // Health chart
        const ctx = document.getElementById('healthChart').getContext('2d');
        const checks = {json.dumps(data['recent_checks'][-10:])};
        
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: checks.map((_, i) => `Check ${{i+1}}`),
                datasets: [{{
                    label: 'Overall Health (%)',
                    data: checks.map(c => c.overall_health),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: false, min: 50, max: 100 }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
        
        // Auto refresh every 10 seconds
        setTimeout(() => location.reload(), 10000);
    </script>
</body>
</html>
"""
        return html


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Production Monitor v2')
    parser.add_argument('--start', action='store_true', help='Start web dashboard')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--check', action='store_true', help='Run health check')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--port', type=int, default=8080, help='Dashboard port')
    
    args = parser.parse_args()
    
    monitor = ProductionMonitor(port=args.port)
    
    if args.demo:
        print("=" * 70)
        print("🎯 Production Monitor v2 - Demo")
        print("=" * 70)
        
        # Check components
        print("\n[1] Component Status:")
        status = monitor.get_status()
        for component, available in status['components'].items():
            icon = "✅" if available else "❌"
            print(f"  {icon} {component}")
        
        # Run health check
        print("\n[2] Running health check...")
        results = monitor.run_health_check()
        print(f"[OK] Health check complete:")
        print(f"  - Overall health: {results['overall_health']:.1f}%")
        print(f"  - Healthy: {results['healthy_count']}/{len(results['systems'])}")
        print(f"  - Warning: {results['warning_count']}")
        print(f"  - Critical: {results['critical_count']}")
        
        # Show system status
        print("\n[3] System Status:")
        for name, data in results['systems'].items():
            health = data.get('health', 0)
            status = data.get('status', 'unknown')
            status_icon = "✅" if status == 'healthy' else "⚠️" if status == 'warning' else "❌"
            print(f"  {status_icon} {name}: {health:.1f}%")
        
        # Show predictions
        if monitor.alert_engine:
            print("\n[4] Predictive Alerts:")
            predictions = monitor.alert_engine.get_status()['recent_predictions']
            if predictions:
                for pred in predictions[-3:]:
                    print(f"  🔮 {pred['system']}: {pred['probability']*100:.0f}% failure probability")
            else:
                print("  ℹ️ No predictions")
        
        # Show dashboard URL
        print("\n[5] Dashboard:")
        print(f"  🌐 http://localhost:{monitor.port}")
        print(f"  🔄 Auto-refresh: 10 seconds")
        
        print("\n" + "=" * 70)
        print("✅ Demo complete - Production Monitor v2 OPERATIONAL")
        print("=" * 70)
        print("\nTo start dashboard: python production_monitor_v2.py --start")
    
    elif args.start:
        print(f"Starting dashboard on http://localhost:{monitor.port}")
        print("Press Ctrl+C to stop")
        
        DashboardHandler.monitor = monitor
        
        with socketserver.TCPServer(("", monitor.port), DashboardHandler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nDashboard stopped")
    
    elif args.check:
        print("Running health check...")
        results = monitor.run_health_check()
        print(json.dumps(results, indent=2))
    
    elif args.status:
        print("Monitor Status:")
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
