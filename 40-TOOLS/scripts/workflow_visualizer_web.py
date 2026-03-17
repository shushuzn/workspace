#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Visualizer Web - Enhanced
Interactive workflow visualization with real-time execution
Features: DAG visualization, live progress, execution history, metrics

Usage:
    python workflow_visualizer_web.py --serve
    python workflow_visualizer_web.py --port 8082
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict
import threading

# Workspace root
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / "30-scripts-tools"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class WorkflowVisualizerWeb:
    """Web-based workflow visualizer"""
    
    def __init__(self):
        self.execution_log = []
        self._load_log()
    
    def _load_log(self):
        """Load execution log"""
        log_file = WORKSPACE / "20-data-reports" / "workflow_execution_log.json"
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    self.execution_log = json.load(f)
            except:
                pass
    
    def _save_log(self):
        """Save execution log"""
        log_file = WORKSPACE / "20-data-reports" / "workflow_execution_log.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.execution_log[-100:], f, indent=2, ensure_ascii=False)
    
    def get_workflows(self) -> Dict:
        """Get all workflows"""
        workflows = {
            'daily_brief': {
                'name': 'Daily Research Brief',
                'description': 'Generate daily research brief',
                'steps': 7,
                'status': 'ready'
            },
            'data_collection': {
                'name': 'Multi-Source Data Collection',
                'description': 'Collect from arXiv, GitHub, Medium',
                'steps': 4,
                'status': 'ready'
            },
            'quality_check': {
                'name': 'Quality Assurance',
                'description': 'Run all quality checks',
                'steps': 4,
                'status': 'ready'
            },
            'system_maintenance': {
                'name': 'System Maintenance',
                'description': 'Cache cleanup + self-healing',
                'steps': 4,
                'status': 'ready'
            }
        }
        return workflows
    
    def get_metrics(self) -> Dict:
        """Get workflow metrics"""
        metrics_file = WORKSPACE / "20-data-reports" / "workflow_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'total_executions': 0,
            'successful': 0,
            'failed': 0,
            'avg_duration': 0,
            'success_rate': 0
        }
    
    def get_html(self) -> str:
        """Generate main HTML page"""
        workflows = self.get_workflows()
        metrics = self.get_metrics()
        
        success_rate = (
            metrics['successful'] / metrics['total_executions'] * 100
            if metrics['total_executions'] > 0 else 0
        )
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workflow Visualizer</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: rgba(255,255,255,0.95); border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
        .header h1 {{ color: #667eea; font-size: 32px; margin-bottom: 10px; }}
        .header p {{ color: #666; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .metric-card {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 36px; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
        .workflows {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .workflow-card {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 25px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s; }}
        .workflow-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 32px rgba(0,0,0,0.15); }}
        .workflow-card h3 {{ color: #333; margin-bottom: 10px; }}
        .workflow-card p {{ color: #666; font-size: 14px; margin-bottom: 15px; }}
        .workflow-meta {{ display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 13px; }}
        .meta-item {{ color: #888; }}
        .meta-item strong {{ color: #667eea; }}
        .btn {{ display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; text-decoration: none; transition: opacity 0.3s; }}
        .btn:hover {{ opacity: 0.9; }}
        .btn-secondary {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .status {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
        .status-ready {{ background: #d4edda; color: #155724; }}
        .status-running {{ background: #fff3cd; color: #856404; }}
        .status-completed {{ background: #d1ecf1; color: #0c5460; }}
        .history {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 25px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
        .history h2 {{ color: #333; margin-bottom: 20px; }}
        .history-table {{ width: 100%; border-collapse: collapse; }}
        .history-table th, .history-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        .history-table th {{ background: #f8f9fa; color: #333; font-weight: 600; }}
        .history-table tr:hover {{ background: #f8f9fa; }}
        .chart-container {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab {{ padding: 10px 20px; background: rgba(255,255,255,0.5); border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }}
        .tab.active {{ background: white; color: #667eea; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Workflow Visualizer</h1>
            <p>Real-time workflow orchestration and monitoring</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{metrics['total_executions']}</div>
                <div class="metric-label">Total Executions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['successful']}</div>
                <div class="metric-label">Successful</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['failed']}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{success_rate:.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['avg_duration']:.1f}s</div>
                <div class="metric-label">Avg Duration</div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('workflows')">Workflows</button>
            <button class="tab" onclick="showTab('history')">History</button>
            <button class="tab" onclick="showTab('analytics')">Analytics</button>
        </div>
        
        <div id="workflows" class="tab-content">
            <div class="workflows">
"""
        
        for wf_id, wf in workflows.items():
            html += f"""
                <div class="workflow-card">
                    <h3>{wf['name']}</h3>
                    <p>{wf['description']}</p>
                    <div class="workflow-meta">
                        <span class="meta-item">Steps: <strong>{wf['steps']}</strong></span>
                        <span class="meta-item">Status: <span class="status status-ready">{wf['status']}</span></span>
                    </div>
                    <button class="btn" onclick="runWorkflow('{wf_id}')">▶️ Run</button>
                    <button class="btn btn-secondary" onclick="visualizeWorkflow('{wf_id}')" style="margin-left: 10px;">📊 Visualize</button>
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <div id="history" class="tab-content" style="display: none;">
            <div class="history">
                <h2>Execution History</h2>
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>Workflow</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody id="history-body">
                        <tr><td colspan="4" style="text-align: center; color: #888;">No executions yet</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="analytics" class="tab-content" style="display: none;">
            <div class="chart-container">
                <h2>Execution Trends</h2>
                <canvas id="trendChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).style.display = 'block';
            event.target.classList.add('active');
        }}
        
        function runWorkflow(workflowId) {{
            fetch('/api/run/' + workflowId, {{ method: 'POST' }})
                .then(r => r.json())
                .then(data => {{
                    alert('Workflow started: ' + workflowId);
                    loadHistory();
                }});
        }}
        
        function visualizeWorkflow(workflowId) {{
            window.open('/visualize/' + workflowId, '_blank');
        }}
        
        function loadHistory() {{
            fetch('/api/history')
                .then(r => r.json())
                .then(data => {{
                    const tbody = document.getElementById('history-body');
                    if (data.length === 0) {{
                        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #888;">No executions yet</td></tr>';
                        return;
                    }}
                    tbody.innerHTML = data.map(exec => `
                        <tr>
                            <td>${{exec.workflow_id}}</td>
                            <td><span class="status status-${{exec.success ? 'completed' : 'failed'}}">${{exec.success ? '✅ Success' : '❌ Failed'}}</span></td>
                            <td>${{exec.duration.toFixed(2)}}s</td>
                            <td>${{new Date(exec.timestamp).toLocaleString()}}</td>
                        </tr>
                    `).join('');
                }});
        }}
        
        // Load history on page load
        loadHistory();
        
        // Auto-refresh every 10 seconds
        setInterval(loadHistory, 10000);
    </script>
</body>
</html>"""
        
        return html


class VisualizerHandler(BaseHTTPRequestHandler):
    """HTTP handler for visualizer"""
    
    def __init__(self, *args, visualizer=None, **kwargs):
        self.visualizer = visualizer
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            html = self.visualizer.get_html()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        
        elif self.path == '/api/history':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.visualizer.execution_log[-20:]).encode('utf-8'))
        
        elif self.path == '/api/metrics':
            metrics = self.visualizer.get_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(metrics).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith('/api/run/'):
            workflow_id = self.path.split('/')[-1]
            
            # Execute workflow
            import subprocess
            cmd = [sys.executable, str(TOOLS_DIR / 'workflow_engine_v2.py'), '--run', workflow_id]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                execution = {
                    'workflow_id': workflow_id,
                    'success': result.returncode == 0,
                    'duration': 0,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.visualizer.execution_log.append(execution)
                self.visualizer._save_log()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(execution).encode('utf-8'))
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def main():
    parser = argparse.ArgumentParser(description='Workflow Visualizer Web')
    parser.add_argument('--serve', action='store_true', help='Start web server')
    parser.add_argument('--port', type=int, default=8082, help='Server port')
    args = parser.parse_args()
    
    visualizer = WorkflowVisualizerWeb()
    
    if args.serve:
        print(f"\n🌐 Workflow Visualizer: http://localhost:{args.port}")
        print("Auto-refresh: 10 seconds")
        print("Press Ctrl+C to stop\n")
        
        def handler(*args, **kwargs):
            VisualizerHandler(*args, visualizer=visualizer, **kwargs)
        
        server = HTTPServer(('0.0.0.0', args.port), handler)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[VISUALIZER] Stopped")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
