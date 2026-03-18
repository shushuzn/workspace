#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Performance Monitor Dashboard - Real-Time Performance Monitoring
Features: CPU/Memory/Disk/Network monitoring, alerts, historical analysis, Web UI

Usage:
    python perf_dashboard.py --start
    python perf_dashboard.py --port 8089
    python perf_dashboard.py --alert
"""

import os
import sys
import json
import time
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import socketserver

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class SystemMetrics:
    """System metrics snapshot"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    load_average: float


@dataclass
class Alert:
    """System alert"""
    timestamp: str
    level: str  # critical/warning/info
    metric: str
    value: float
    threshold: float
    message: str


@dataclass
class PerformanceReport:
    """Performance analysis report"""
    period: str
    avg_cpu: float
    avg_memory: float
    avg_disk: float
    peak_cpu: float
    peak_memory: float
    peak_disk: float
    alerts_count: int
    recommendations: List[str]


class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self):
        self.data_dir = WORKSPACE / "20-data-reports" / "performance"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.data_dir / "metrics.json"
        self.alerts_file = self.data_dir / "alerts.json"
        
        self.metrics_history: List[SystemMetrics] = []
        self.alerts: List[Alert] = []
        
        # Thresholds
        self.thresholds = {
            'cpu_critical': 90,
            'cpu_warning': 70,
            'memory_critical': 90,
            'memory_warning': 80,
            'disk_critical': 90,
            'disk_warning': 80
        }
        
        self.load_state()
    
    def load_state(self):
        """Load monitoring state"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.metrics_history = [SystemMetrics(**m) for m in data.get('history', [])[-100:]]
        
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.alerts = [Alert(**a) for a in data.get('alerts', [])[-50:]]
    
    def save_state(self):
        """Save monitoring state"""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump({
                'history': [asdict(m) for m in self.metrics_history[-100:]],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump({
                'alerts': [asdict(a) for a in self.alerts[-50:]],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / 1024 / 1024 / 1024
        memory_total_gb = memory.total / 1024 / 1024 / 1024
        
        # Disk
        disk = psutil.disk_usage(str(WORKSPACE))
        disk_percent = disk.percent
        disk_used_gb = disk.used / 1024 / 1024 / 1024
        disk_total_gb = disk.total / 1024 / 1024 / 1024
        
        # Network
        network = psutil.net_io_counters()
        network_sent_mb = network.bytes_sent / 1024 / 1024
        network_recv_mb = network.bytes_recv / 1024 / 1024
        
        # Process count
        process_count = len(psutil.pids())
        
        # Load average (Windows doesn't have load average, use CPU instead)
        load_average = cpu_percent
        
        metrics = SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_gb=round(memory_used_gb, 2),
            memory_total_gb=round(memory_total_gb, 2),
            disk_percent=disk_percent,
            disk_used_gb=round(disk_used_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            network_sent_mb=round(network_sent_mb, 2),
            network_recv_mb=round(network_recv_mb, 2),
            process_count=process_count,
            load_average=round(load_average, 1)
        )
        
        self.metrics_history.append(metrics)
        
        # Check thresholds
        self.check_alerts(metrics)
        
        # Save periodically
        if len(self.metrics_history) % 10 == 0:
            self.save_state()
        
        return metrics
    
    def check_alerts(self, metrics: SystemMetrics):
        """Check for threshold violations"""
        # CPU
        if metrics.cpu_percent >= self.thresholds['cpu_critical']:
            self.create_alert('critical', 'cpu', metrics.cpu_percent, 
                            self.thresholds['cpu_critical'],
                            f"CPU usage critical: {metrics.cpu_percent}%")
        elif metrics.cpu_percent >= self.thresholds['cpu_warning']:
            self.create_alert('warning', 'cpu', metrics.cpu_percent,
                            self.thresholds['cpu_warning'],
                            f"CPU usage high: {metrics.cpu_percent}%")
        
        # Memory
        if metrics.memory_percent >= self.thresholds['memory_critical']:
            self.create_alert('critical', 'memory', metrics.memory_percent,
                            self.thresholds['memory_critical'],
                            f"Memory usage critical: {metrics.memory_percent}%")
        elif metrics.memory_percent >= self.thresholds['memory_warning']:
            self.create_alert('warning', 'memory', metrics.memory_percent,
                            self.thresholds['memory_warning'],
                            f"Memory usage high: {metrics.memory_percent}%")
        
        # Disk
        if metrics.disk_percent >= self.thresholds['disk_critical']:
            self.create_alert('critical', 'disk', metrics.disk_percent,
                            self.thresholds['disk_critical'],
                            f"Disk usage critical: {metrics.disk_percent}%")
        elif metrics.disk_percent >= self.thresholds['disk_warning']:
            self.create_alert('warning', 'disk', metrics.disk_percent,
                            self.thresholds['disk_warning'],
                            f"Disk usage high: {metrics.disk_percent}%")
    
    def create_alert(self, level: str, metric: str, value: float, 
                    threshold: float, message: str):
        """Create system alert"""
        # Don't duplicate recent alerts
        if self.alerts:
            last_alert = self.alerts[-1]
            if (last_alert.metric == metric and 
                last_alert.level == level and
                datetime.fromisoformat(last_alert.timestamp) > 
                datetime.now() - timedelta(minutes=5)):
                return
        
        alert = Alert(
            timestamp=datetime.now().isoformat(),
            level=level,
            metric=metric,
            value=round(value, 1),
            threshold=threshold,
            message=message
        )
        
        self.alerts.append(alert)
        
        # Print alert
        icon = "🔴" if level == 'critical' else "🟡" if level == 'warning' else "🔵"
        print(f"\n{icon} ALERT: {message}")
    
    def get_current_metrics(self) -> Dict:
        """Get current metrics"""
        if not self.metrics_history:
            self.collect_metrics()
        
        latest = self.metrics_history[-1]
        
        return {
            'cpu': latest.cpu_percent,
            'memory': latest.memory_percent,
            'disk': latest.disk_percent,
            'network_sent': latest.network_sent_mb,
            'network_recv': latest.network_recv_mb,
            'processes': latest.process_count,
            'timestamp': latest.timestamp
        }
    
    def get_history(self, hours: int = 1) -> List[Dict]:
        """Get metrics history"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        return [
            asdict(m) for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) > cutoff
        ]
    
    def generate_report(self, hours: int = 24) -> PerformanceReport:
        """Generate performance report"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        history = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) > cutoff
        ]
        
        if not history:
            return PerformanceReport(
                period=f"{hours}h",
                avg_cpu=0, avg_memory=0, avg_disk=0,
                peak_cpu=0, peak_memory=0, peak_disk=0,
                alerts_count=0, recommendations=[]
            )
        
        avg_cpu = sum(m.cpu_percent for m in history) / len(history)
        avg_memory = sum(m.memory_percent for m in history) / len(history)
        avg_disk = sum(m.disk_percent for m in history) / len(history)
        
        peak_cpu = max(m.cpu_percent for m in history)
        peak_memory = max(m.memory_percent for m in history)
        peak_disk = max(m.disk_percent for m in history)
        
        alerts_count = sum(
            1 for a in self.alerts
            if datetime.fromisoformat(a.timestamp) > cutoff
        )
        
        # Generate recommendations
        recommendations = []
        
        if avg_cpu > 70:
            recommendations.append("Consider optimizing CPU-intensive tasks")
        if avg_memory > 80:
            recommendations.append("Memory usage high, consider increasing RAM or optimizing memory usage")
        if avg_disk > 80:
            recommendations.append("Disk space low, consider cleanup or expansion")
        if alerts_count > 10:
            recommendations.append(f"High alert count ({alerts_count}), investigate root causes")
        
        if not recommendations:
            recommendations.append("System performance is healthy")
        
        report = PerformanceReport(
            period=f"{hours}h",
            avg_cpu=round(avg_cpu, 1),
            avg_memory=round(avg_memory, 1),
            avg_disk=round(avg_disk, 1),
            peak_cpu=round(peak_cpu, 1),
            peak_memory=round(peak_memory, 1),
            peak_disk=round(peak_disk, 1),
            alerts_count=alerts_count,
            recommendations=recommendations
        )
        
        return report
    
    def get_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recent alerts"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        return [
            asdict(a) for a in self.alerts
            if datetime.fromisoformat(a.timestamp) > cutoff
        ]


class DashboardHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for dashboard"""
    
    monitor = None
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_dashboard()
        elif self.path == '/api/metrics':
            self.send_json(self.monitor.get_current_metrics())
        elif self.path == '/api/history':
            hours = int(self.path.split('?')[-1].split('=')[1]) if '?' in self.path else 1
            self.send_json({'history': self.monitor.get_history(hours)})
        elif self.path == '/api/alerts':
            hours = int(self.path.split('?')[-1].split('=')[1]) if '?' in self.path else 24
            self.send_json({'alerts': self.monitor.get_alerts(hours)})
        elif self.path == '/api/report':
            hours = int(self.path.split('?')[-1].split('=')[1]) if '?' in self.path else 24
            report = self.monitor.generate_report(hours)
            self.send_json(asdict(report))
        else:
            self.send_error(404)
    
    def send_dashboard(self):
        """Send dashboard HTML"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Performance Monitor Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-title {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
        .metric-unit {
            font-size: 0.5em;
            color: #999;
        }
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        .alerts-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid;
        }
        .alert-critical {
            background: #fee;
            border-color: #f44;
        }
        .alert-warning {
            background: #ffa;
            border-color: #fa0;
        }
        .alert-info {
            background: #eef;
            border-color: #44f;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        .status-good { background: #4c4; }
        .status-warning { background: #fa0; }
        .status-critical { background: #f44; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .last-update {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Performance Monitor Dashboard</h1>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">
                    <span class="status-indicator status-good" id="cpu-status"></span>
                    CPU Usage
                </div>
                <div class="metric-value" id="cpu-value">--<span class="metric-unit">%</span></div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">
                    <span class="status-indicator status-good" id="memory-status"></span>
                    Memory Usage
                </div>
                <div class="metric-value" id="memory-value">--<span class="metric-unit">%</span></div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">
                    <span class="status-indicator status-good" id="disk-status"></span>
                    Disk Usage
                </div>
                <div class="metric-value" id="disk-value">--<span class="metric-unit">%</span></div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Processes</div>
                <div class="metric-value" id="process-value">--</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="metricsChart"></canvas>
        </div>
        
        <div class="alerts-container">
            <h2 style="margin-bottom: 15px;">🔔 Recent Alerts</h2>
            <div id="alerts-list">Loading...</div>
        </div>
        
        <div class="last-update">
            Last updated: <span id="last-update">--</span> | Auto-refresh: 5s
        </div>
    </div>
    
    <script>
        // Chart setup
        const ctx = document.getElementById('metricsChart').getContext('2d');
        const metricsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'CPU %',
                        data: [],
                        borderColor: '#ff6384',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Memory %',
                        data: [],
                        borderColor: '#36a2eb',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Disk %',
                        data: [],
                        borderColor: '#ffce56',
                        backgroundColor: 'rgba(255, 206, 86, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'System Metrics (Last Hour)',
                        font: { size: 16 }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // Update metrics
        async function updateMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                // Update cards
                document.getElementById('cpu-value').innerHTML = data.cpu.toFixed(1) + '<span class="metric-unit">%</span>';
                document.getElementById('memory-value').innerHTML = data.memory.toFixed(1) + '<span class="metric-unit">%</span>';
                document.getElementById('disk-value').innerHTML = data.disk.toFixed(1) + '<span class="metric-unit">%</span>';
                document.getElementById('process-value').textContent = data.processes;
                
                // Update status indicators
                updateStatus('cpu-status', data.cpu);
                updateStatus('memory-status', data.memory);
                updateStatus('disk-status', data.disk);
                
                // Update chart
                const now = new Date().toLocaleTimeString();
                if (metricsChart.data.labels.length > 60) {
                    metricsChart.data.labels.shift();
                    metricsChart.data.datasets[0].data.shift();
                    metricsChart.data.datasets[1].data.shift();
                    metricsChart.data.datasets[2].data.shift();
                }
                metricsChart.data.labels.push(now);
                metricsChart.data.datasets[0].data.push(data.cpu);
                metricsChart.data.datasets[1].data.push(data.memory);
                metricsChart.data.datasets[2].data.push(data.disk);
                metricsChart.update();
                
                // Update timestamp
                document.getElementById('last-update').textContent = new Date().toLocaleString();
                
            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }
        
        // Update status indicator
        function updateStatus(elementId, value) {
            const element = document.getElementById(elementId);
            element.classList.remove('status-good', 'status-warning', 'status-critical');
            
            if (value >= 90) {
                element.classList.add('status-critical');
            } else if (value >= 70) {
                element.classList.add('status-warning');
            } else {
                element.classList.add('status-good');
            }
        }
        
        // Update alerts
        async function updateAlerts() {
            try {
                const response = await fetch('/api/alerts?hours=1');
                const data = await response.json();
                
                const alertsList = document.getElementById('alerts-list');
                
                if (data.alerts.length === 0) {
                    alertsList.innerHTML = '<p style="color: #4c4;">✅ No recent alerts</p>';
                } else {
                    alertsList.innerHTML = data.alerts.slice(-5).reverse().map(alert => `
                        <div class="alert alert-${alert.level}">
                            <strong>${alert.timestamp.substring(11, 19)}</strong> - ${alert.message}
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error fetching alerts:', error);
            }
        }
        
        // Initial update
        updateMetrics();
        updateAlerts();
        
        // Auto-refresh
        setInterval(updateMetrics, 5000);
        setInterval(updateAlerts, 10000);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress logging"""
        pass


class PerformanceDashboard:
    """Performance dashboard server"""
    
    def __init__(self, port: int = 8089):
        self.port = port
        self.monitor = PerformanceMonitor()
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        """Start dashboard server"""
        print("\n" + "="*60)
        print(" Starting Performance Monitor Dashboard")
        print("="*60 + "\n")
        
        DashboardHandler.monitor = self.monitor
        
        self.server = socketserver.TCPServer(("", self.port), DashboardHandler)
        
        self.running = True
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"  Dashboard URL: http://localhost:{self.port}")
        print(f"  API Endpoints:")
        print(f"    - GET /api/metrics - Current metrics")
        print(f"    - GET /api/history - Historical data")
        print(f"    - GET /api/alerts - Recent alerts")
        print(f"    - GET /api/report - Performance report")
        print(f"\n  Press Ctrl+C to stop\n")
        
        # Start metrics collection
        self.collect_loop()
    
    def collect_loop(self):
        """Collect metrics in loop"""
        try:
            while self.running:
                self.monitor.collect_metrics()
                time.sleep(5)  # Collect every 5 seconds
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop dashboard server"""
        print("\nStopping dashboard...")
        
        self.running = False
        
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        self.monitor.save_state()
        
        print("Dashboard stopped\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Performance Monitor Dashboard')
    parser.add_argument('--start', action='store_true', help='Start dashboard')
    parser.add_argument('--port', type=int, default=8089, help='Server port')
    parser.add_argument('--collect', action='store_true', help='Collect metrics once')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--alerts', action='store_true', help='Show alerts')
    args = parser.parse_args()
    
    dashboard = PerformanceDashboard(args.port)
    
    if args.start:
        dashboard.start()
    
    elif args.collect:
        monitor = PerformanceMonitor()
        metrics = monitor.collect_metrics()
        print(json.dumps(asdict(metrics), indent=2))
    
    elif args.report:
        monitor = PerformanceMonitor()
        report = monitor.generate_report()
        print(json.dumps(asdict(report), indent=2))
    
    elif args.alerts:
        monitor = PerformanceMonitor()
        alerts = monitor.get_alerts()
        print(json.dumps(alerts, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
