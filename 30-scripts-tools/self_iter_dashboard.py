#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Self-Iteration Dashboard - Real-time Visualization
Web dashboard for monitoring self-iteration progress
Features: Real-time metrics, charts, history, recommendations

Usage:
    python self_iter_dashboard.py --start
    python self_iter_dashboard.py --port 8086
"""

import os
import sys
import json
import http.server
import socketserver
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from urllib.parse import urlparse, parse_qs

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class SelfIterationDashboard:
    """Generate self-iteration dashboard HTML"""
    
    def __init__(self):
        self.state_file = WORKSPACE / "20-data-reports" / "self_iteration_state.json"
        self.meta_file = WORKSPACE / "20-data-reports" / "meta_learning_state.json"
        self.evolution_file = WORKSPACE / "20-data-reports" / "evolution_state.json"
        self.history_file = WORKSPACE / "20-data-reports" / "heartbeat_self_iter_history.json"
    
    def load_data(self) -> Dict:
        """Load all self-iteration data"""
        data = {
            'self_iteration': {},
            'meta_learning': {},
            'evolution': {},
            'history': []
        }
        
        # Load self-iteration state
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data['self_iteration'] = json.load(f)
            except:
                pass
        
        # Load meta-learning state
        if self.meta_file.exists():
            try:
                with open(self.meta_file, 'r', encoding='utf-8') as f:
                    data['meta_learning'] = json.load(f)
            except:
                pass
        
        # Load evolution state
        if self.evolution_file.exists():
            try:
                with open(self.evolution_file, 'r', encoding='utf-8') as f:
                    data['evolution'] = json.load(f)
            except:
                pass
        
        # Load history
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data['history'] = json.load(f)
            except:
                pass
        
        return data
    
    def generate_html(self) -> str:
        """Generate dashboard HTML"""
        data = self.load_data()
        
        # Calculate metrics
        total_improvements = data['self_iteration'].get('total_improvements', 0)
        total_events = data['meta_learning'].get('total_events', 0)
        total_patterns = data['meta_learning'].get('total_patterns', 0)
        generation = data['evolution'].get('generation', 0)
        avg_fitness = data['evolution'].get('avg_fitness', 0)
        
        history = data.get('history', [])
        total_runs = len(history)
        success_rate = sum(1 for h in history if h.get('success', False)) / max(1, total_runs) * 100
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Self-Iteration Dashboard</title>
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
        .header h1 {{ 
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{ color: #666; font-size: 1.1em; }}
        .metrics-grid {{ 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .metric-card:hover {{ transform: translateY(-5px); }}
        .metric-card h3 {{ 
            color: #888;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .metric-card .value {{ 
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-card .subtitle {{ 
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .chart-card {{
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .chart-card h3 {{
            color: #667eea;
            margin-bottom: 20px;
        }}
        .status-section {{
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .status-section h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        .status-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .status-item:last-child {{ border-bottom: none; }}
        .status-label {{ color: #666; }}
        .status-value {{ font-weight: bold; color: #333; }}
        .status-value.good {{ color: #27ae60; }}
        .status-value.warning {{ color: #f39c12; }}
        .status-value.bad {{ color: #e74c3c; }}
        .auto-refresh {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(255,255,255,0.95);
            padding: 15px 25px;
            border-radius: 30px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            font-size: 0.9em;
            color: #666;
        }}
        @media (max-width: 768px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
            .metric-card .value {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Self-Iteration Dashboard</h1>
            <p>Real-time monitoring of meta-cognitive evolution system</p>
            <p style="margin-top: 10px; color: #999;">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Improvements</h3>
                <div class="value">{total_improvements}</div>
                <div class="subtitle">Identified & tracked</div>
            </div>
            <div class="metric-card">
                <h3>Learning Events</h3>
                <div class="value">{total_events}</div>
                <div class="subtitle">{total_patterns} patterns</div>
            </div>
            <div class="metric-card">
                <h3>Evolution Generation</h3>
                <div class="value">{generation}</div>
                <div class="subtitle">Avg fitness: {avg_fitness:.1f}</div>
            </div>
            <div class="metric-card">
                <h3>Execution History</h3>
                <div class="value">{total_runs}</div>
                <div class="subtitle">Success rate: {success_rate:.1f}%</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📈 Execution History</h3>
                <canvas id="historyChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>🎯 System Metrics</h3>
                <canvas id="metricsChart"></canvas>
            </div>
        </div>
        
        <div class="status-section">
            <h3>📊 System Status</h3>
            <div class="status-item">
                <span class="status-label">Self-Iteration Engine</span>
                <span class="status-value {'good' if total_improvements > 0 else 'warning'}">{'✅ Active' if total_improvements > 0 else '⚠️ No Data'}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Meta-Learning System</span>
                <span class="status-value {'good' if total_events > 0 else 'warning'}">{'✅ Active' if total_events > 0 else '⚠️ No Data'}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Evolution Engine</span>
                <span class="status-value {'good' if generation > 0 else 'warning'}">{'✅ Active' if generation > 0 else '⚠️ No Data'}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Overall Health</span>
                <span class="status-value {'good' if success_rate > 80 else 'warning' if success_rate > 50 else 'bad'}">
                    {'✅ Excellent' if success_rate > 80 else '⚠️ Moderate' if success_rate > 50 else '❌ Needs Attention'}
                </span>
            </div>
        </div>
        
        <div class="auto-refresh">
            🔄 Auto-refresh in <span id="countdown">10</span>s
        </div>
    </div>
    
    <script>
        // History chart data
        const historyData = {history};
        const ctx1 = document.getElementById('historyChart').getContext('2d');
        new Chart(ctx1, {{
            type: 'line',
            data: {{
                labels: historyData.slice(-20).map(h => new Date(h.timestamp).toLocaleTimeString()),
                datasets: [{{
                    label: 'Duration (s)',
                    data: historyData.slice(-20).map(h => h.duration),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: true }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
        
        // Metrics chart
        const ctx2 = document.getElementById('metricsChart').getContext('2d');
        new Chart(ctx2, {{
            type: 'doughnut',
            data: {{
                labels: ['Improvements', 'Events', 'Patterns', 'Generations'],
                datasets: [{{
                    data: [{total_improvements}, {total_events}, {total_patterns}, {generation}],
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // Auto-refresh countdown
        let countdown = 10;
        setInterval(() => {{
            countdown--;
            document.getElementById('countdown').textContent = countdown;
            if (countdown <= 0) {{
                location.reload();
            }}
        }}, 1000);
    </script>
</body>
</html>
"""
        return html


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for dashboard"""
    
    def __init__(self, *args, dashboard=None, **kwargs):
        self.dashboard = dashboard
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            # Serve dashboard
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = self.dashboard.generate_html()
            self.wfile.write(html.encode('utf-8'))
        
        elif parsed_path.path == '/api/data':
            # Serve JSON data
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = self.dashboard.load_data()
            self.wfile.write(json.dumps(data, indent=2, default=str).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()


def run_dashboard(port: int = 8086):
    """Start dashboard server"""
    dashboard = SelfIterationDashboard()
    
    # Create custom handler with dashboard instance
    def handler(*args, **kwargs):
        return DashboardHandler(*args, dashboard=dashboard, **kwargs)
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n{'='*60}")
        print(f" Self-Iteration Dashboard")
        print(f"{'='*60}")
        print(f" URL: http://localhost:{port}")
        print(f" API: http://localhost:{port}/api/data")
        print(f"{'='*60}\n")
        
        # Open browser
        webbrowser.open(f"http://localhost:{port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard stopped.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Self-Iteration Dashboard')
    parser.add_argument('--start', action='store_true', help='Start dashboard server')
    parser.add_argument('--port', type=int, default=8086, help='Port number')
    parser.add_argument('--generate', action='store_true', help='Generate HTML file')
    args = parser.parse_args()
    
    dashboard = SelfIterationDashboard()
    
    if args.start:
        run_dashboard(args.port)
    
    elif args.generate:
        html = dashboard.generate_html()
        output_file = WORKSPACE / "20-data-reports" / "self_iter_dashboard.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Dashboard saved to: {output_file}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
