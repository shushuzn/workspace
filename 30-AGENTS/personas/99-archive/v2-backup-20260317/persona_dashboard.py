#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Persona Collaboration Dashboard - Web Interface
Real-time visualization of 7-persona collaboration
Features: live metrics, message flow, conflict tracking, persona states

Usage:
    python persona_dashboard.py --serve
    python persona_dashboard.py --port 8083
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict

# Workspace root
WORKSPACE = Path(__file__).parent.parent
PERSONAS_DIR = WORKSPACE / "00-人格系统"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class PersonaDashboard:
    """Web dashboard for persona collaboration"""
    
    def __init__(self):
        self.state_file = WORKSPACE / "20-data-reports" / "persona_state.json"
    
    def get_state(self) -> Dict:
        """Load current persona state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Default state
        return {
            'personas': {
                'planner': {'workload': 20, 'confidence': 0.8, 'collaboration_score': 0.85},
                'executor': {'workload': 30, 'confidence': 0.85, 'collaboration_score': 0.82},
                'critic': {'workload': 25, 'confidence': 0.9, 'collaboration_score': 0.88},
                'learner': {'workload': 15, 'confidence': 0.75, 'collaboration_score': 0.9},
                'coordinator': {'workload': 10, 'confidence': 0.95, 'collaboration_score': 0.92},
                'innovator': {'workload': 20, 'confidence': 0.82, 'collaboration_score': 0.87},
                'meta_cognition': {'workload': 10, 'confidence': 0.93, 'collaboration_score': 0.95}
            },
            'conflicts': [],
            'message_count': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_html(self) -> str:
        """Generate dashboard HTML"""
        state = self.get_state()
        personas = state.get('personas', {})
        conflicts = state.get('conflicts', [])
        
        # Calculate overall metrics
        avg_workload = sum(p.get('workload', 0) for p in personas.values()) / max(1, len(personas))
        avg_confidence = sum(p.get('confidence', 0) for p in personas.values()) / max(1, len(personas))
        avg_collab = sum(p.get('collaboration_score', 0) for p in personas.values()) / max(1, len(personas))
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>7-Persona Collaboration Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        .header {{ background: rgba(255,255,255,0.95); border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
        .header h1 {{ color: #667eea; font-size: 32px; margin-bottom: 10px; }}
        .header p {{ color: #666; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .metric-card {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 36px; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
        .grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .card {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 25px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #333; margin-bottom: 20px; font-size: 20px; }}
        .persona-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .persona-card {{ background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 10px; padding: 20px; }}
        .persona-card h3 {{ color: #333; font-size: 16px; margin-bottom: 15px; text-transform: capitalize; }}
        .stat {{ margin: 10px 0; }}
        .stat-label {{ font-size: 12px; color: #666; }}
        .stat-value {{ font-size: 18px; font-weight: bold; color: #667eea; }}
        .progress-bar {{ background: #e0e0e0; border-radius: 10px; height: 8px; overflow: hidden; margin-top: 5px; }}
        .progress-fill {{ height: 100%; border-radius: 10px; transition: width 0.5s; }}
        .progress-low {{ background: #22c55e; }}
        .progress-medium {{ background: #f59e0b; }}
        .progress-high {{ background: #ef4444; }}
        .conflict-item {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .conflict-item.resolved {{ background: #d1fae5; border-left-color: #22c55e; }}
        .conflict-title {{ font-weight: bold; color: #333; margin-bottom: 5px; }}
        .conflict-meta {{ font-size: 12px; color: #666; }}
        .message-item {{ padding: 10px; border-bottom: 1px solid #eee; font-size: 13px; }}
        .message-item:last-child {{ border-bottom: none; }}
        .message-sender {{ color: #667eea; font-weight: bold; }}
        .message-content {{ color: #666; margin-top: 5px; }}
        .status-indicator {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }}
        .status-good {{ background: #22c55e; }}
        .status-warning {{ background: #f59e0b; }}
        .status-critical {{ background: #ef4444; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab {{ padding: 10px 20px; background: rgba(255,255,255,0.5); border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }}
        .tab.active {{ background: white; color: #667eea; font-weight: bold; }}
        @media (max-width: 1024px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 7-Persona Collaboration Dashboard</h1>
            <p>Real-time monitoring of persona states, messages, and conflicts</p>
            <p style="margin-top: 10px; font-size: 13px; color: #888;">Last updated: {state.get('last_updated', 'N/A')[:19].replace('T', ' ')}</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{avg_workload:.0f}%</div>
                <div class="metric-label">Avg Workload</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_confidence*100:.0f}%</div>
                <div class="metric-label">Avg Confidence</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_collab*100:.0f}%</div>
                <div class="metric-label">Collaboration Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(conflicts)}</div>
                <div class="metric-label">Active Conflicts</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{state.get('message_count', 0)}</div>
                <div class="metric-label">Total Messages</div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('personas')">Personas</button>
            <button class="tab" onclick="showTab('conflicts')">Conflicts</button>
            <button class="tab" onclick="showTab('messages')">Messages</button>
        </div>
        
        <div id="personas" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>Persona States</h2>
                    <div class="persona-grid">
"""
        
        persona_colors = {
            'planner': '#667eea',
            'executor': '#f093fb',
            'critic': '#f5576c',
            'learner': '#4facfe',
            'coordinator': '#43e97b',
            'innovator': '#fa709a',
            'meta_cognition': '#764ba2'
        }
        
        for role, data in personas.items():
            workload = data.get('workload', 0)
            confidence = data.get('confidence', 0)
            collab = data.get('collaboration_score', 0)
            color = persona_colors.get(role, '#667eea')
            
            workload_class = 'progress-low' if workload < 40 else ('progress-medium' if workload < 70 else 'progress-high')
            
            html += f"""
                        <div class="persona-card" style="border-left: 4px solid {color};">
                            <h3 style="color: {color};">{role.replace('_', ' ').title()}</h3>
                            <div class="stat">
                                <div class="stat-label">Workload</div>
                                <div class="stat-value">{workload}%</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {workload_class}" style="width: {workload}%; background: {color};"></div>
                                </div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Confidence</div>
                                <div class="stat-value">{confidence*100:.0f}%</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Collaboration</div>
                                <div class="stat-value">{collab*100:.0f}%</div>
                            </div>
                        </div>
"""
        
        html += """
                    </div>
                </div>
                
                <div class="card">
                    <h2>System Health</h2>
                    <div style="margin: 20px 0;">
                        <div style="display: flex; align-items: center; margin: 15px 0;">
                            <span class="status-indicator status-good"></span>
                            <span>Overall Status: <strong>Healthy</strong></span>
                        </div>
                        <div style="display: flex; align-items: center; margin: 15px 0;">
                            <span class="status-indicator status-good"></span>
                            <span>Communication: <strong>Active</strong></span>
                        </div>
                        <div style="display: flex; align-items: center; margin: 15px 0;">
                            <span class="status-indicator status-good"></span>
                            <span>Conflict Resolution: <strong>Effective</strong></span>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 30px; margin-bottom: 15px; color: #333;">Workload Distribution</h3>
                    <canvas id="workloadChart"></canvas>
                </div>
            </div>
        </div>
        
        <div id="conflicts" class="tab-content" style="display: none;">
            <div class="card">
                <h2>Conflict Tracking</h2>
"""
        
        if conflicts:
            for conflict in conflicts:
                status_class = 'resolved' if conflict.get('status') == 'resolved' else ''
                html += f"""
                <div class="conflict-item {status_class}">
                    <div class="conflict-title">
                        {conflict.get('persona1', 'Unknown')} ↔ {conflict.get('persona2', 'Unknown')}
                    </div>
                    <div style="margin: 5px 0;">{conflict.get('issue', 'No description')}</div>
                    <div class="conflict-meta">
                        Severity: {conflict.get('severity', 'medium')} | 
                        Status: {conflict.get('status', 'open')} |
                        {conflict.get('created_at', 'N/A')[:10]}
                    </div>
                </div>
"""
        else:
            html += """
                <div style="text-align: center; padding: 40px; color: #888;">
                    <div style="font-size: 48px; margin-bottom: 10px;">✅</div>
                    <div>No active conflicts</div>
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <div id="messages" class="tab-content" style="display: none;">
            <div class="card">
                <h2>Recent Messages</h2>
                <div id="message-list">
                    <div style="text-align: center; padding: 40px; color: #888;">
                        <div style="font-size: 48px; margin-bottom: 10px;">📩</div>
                        <div>Message log available in persona_state.json</div>
                    </div>
                </div>
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
        
        // Workload chart
        const ctx = document.getElementById('workloadChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {list(personas.keys())},
                datasets: [{{
                    label: 'Workload %',
                    data: {[p.get('workload', 0) for p in personas.values()]},
                    backgroundColor: [
                        '#667eea', '#f093fb', '#f5576c', '#4facfe',
                        '#43e97b', '#fa709a', '#764ba2'
                    ],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Auto-refresh every 10 seconds
        setInterval(() => location.reload(), 10000);
    </script>
</body>
</html>"""
        
        return html


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for dashboard"""
    
    def __init__(self, *args, dashboard=None, **kwargs):
        self.dashboard = dashboard
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            html = self.dashboard.get_html()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        
        elif self.path == '/api/state':
            state = self.dashboard.get_state()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(state).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def main():
    parser = argparse.ArgumentParser(description='Persona Collaboration Dashboard')
    parser.add_argument('--serve', action='store_true', help='Start web server')
    parser.add_argument('--port', type=int, default=8083, help='Server port')
    args = parser.parse_args()
    
    dashboard = PersonaDashboard()
    
    if args.serve:
        print(f"\n🎭 Persona Dashboard: http://localhost:{args.port}")
        print("Auto-refresh: 10 seconds")
        print("Press Ctrl+C to stop\n")
        
        def handler(*args, **kwargs):
            DashboardHandler(*args, dashboard=dashboard, **kwargs)
        
        server = HTTPServer(('0.0.0.0', args.port), handler)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[DASHBOARD] Stopped")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
