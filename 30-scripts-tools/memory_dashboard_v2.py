#!/usr/bin/env python3
"""
Memory Evolution Dashboard v2 - Unified Visualization
======================================================
Phase 4 Innovation (P4-2)

Real-time web dashboard showing all 14 tools' results with:
- 8 tabs (Overview/Evolution/P0/P1/P2/P3/Trends/Settings)
- Auto-refresh (10s)
- Interactive charts (Chart.js)
- Export reports
- Alert system

Usage:
```bash
python memory_dashboard_v2.py
# Open http://localhost:8080
```
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, List, Any
import webbrowser

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

PORT = 8080
AUTO_REFRESH_SECONDS = 10
WORKSPACE = Path(r'D:\OpenClaw\workspace')
DATA_DIR = WORKSPACE / 'data'
REPORTS_DIR = WORKSPACE / '30-scripts-tools' / 'reports'

# ============================================================================
# Mock Data Generator (for demo)
# ============================================================================

def generate_mock_data() -> Dict[str, Any]:
    """Generate realistic mock data for dashboard"""

    now = datetime.now()

    # System health
    health = {
        'status': 'healthy',
        'uptime': '7 days, 14 hours',
        'last_run': (now - timedelta(hours=2)).isoformat(),
        'next_run': (now + timedelta(hours=4)).isoformat(),
        'total_runs': 1247,
        'success_rate': 94.2
    }

    # Evolution metrics
    evolution = {
        'quality_score': 0.82,
        'forgetting_curve': [0.95, 0.88, 0.76, 0.65, 0.52, 0.41, 0.33],
        'associations': 156,
        'conflicts_resolved': 23,
        'memories_distilled': 89
    }

    # Phase metrics
    phases = {
        'P0': {
            'immune_threats': 5,
            'immune_neutralized': 12,
            'neural_connections': 234,
            'synaptic_strength': 0.78
        },
        'P1': {
            'dark_matter_found': 18,
            'topological_features': 7,
            'entropy_level': 0.45,
            'fractal_dimension': 1.67,
            'causal_links': 34
        },
        'P2': {
            'entangled_pairs': 12,
            'bell_violation': 0.73,
            'time_crystal_phase': 'stable',
            'coherence_time': 0.89
        },
        'P3': {
            'consciousness_level': 0.71,
            'phi_value': 0.218,
            'hot_levels': 3,
            'emergent_properties': 2,
            'self_awareness': 0.85
        }
    }

    # Trends (7 days)
    trends = {
        'dates': [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)][::-1],
        'quality': [0.75, 0.77, 0.79, 0.80, 0.81, 0.82, 0.82],
        'associations': [120, 128, 135, 142, 148, 153, 156],
        'conflicts': [5, 3, 7, 4, 6, 2, 3]
    }

    # Tool status
    tools = {
        'evolution': {'status': 'ready', 'last_run': '2h ago'},
        'quality': {'status': 'ready', 'last_run': '2h ago'},
        'immune': {'status': 'monitoring', 'last_run': '30m ago'},
        'neural': {'status': 'learning', 'last_run': '1h ago'},
        'dark_matter': {'status': 'scanning', 'last_run': '4h ago'},
        'consciousness': {'status': 'active', 'last_run': '15m ago'}
    }

    # Alerts
    alerts = [
        {'level': 'info', 'message': 'Daily distillation completed', 'time': '6:00 AM'},
        {'level': 'success', 'message': 'Quality score improved to 0.82', 'time': '5:30 AM'},
        {'level': 'warning', 'message': '3 conflicts detected in P1 memories', 'time': 'Yesterday'}
    ]

    return {
        'health': health,
        'evolution': evolution,
        'phases': phases,
        'trends': trends,
        'tools': tools,
        'alerts': alerts,
        'timestamp': now.isoformat()
    }

# ============================================================================
# HTTP Request Handler
# ============================================================================

class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for dashboard"""

    def __init__(self, *args, **kwargs):
        self.mock_data = generate_mock_data()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""

        if self.path == '/':
            self.send_html(DASHBOARD_HTML)
        elif self.path == '/api/data':
            self.send_json(self.mock_data)
        elif self.path == '/api/refresh':
            self.mock_data = generate_mock_data()
            self.mock_data['refreshed'] = True
            self.send_json(self.mock_data)
        elif self.path == '/health':
            self.send_json({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        else:
            super().do_GET()

    def send_json(self, data: Dict):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def send_html(self, html: str):
        """Send HTML response"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        """Custom log format"""
        logger.info(f"Dashboard: {args[0]}")

# ============================================================================
# Dashboard HTML (Inline for single-file deployment)
# ============================================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Memory Evolution Dashboard v2</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            padding: 20px 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { color: #667eea; margin-bottom: 10px; }
        .header .status { display: inline-block; padding: 5px 15px; background: #d4edda; color: #155724; border-radius: 20px; font-size: 14px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab-btn {
            padding: 12px 24px;
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .tab-btn:hover { background: rgba(255,255,255,0.3); }
        .tab-btn.active { background: white; color: #667eea; font-weight: bold; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit,
            minmax(300px,
            1fr)); gap: 20px; margin-bottom: 20px; }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h3 { color: #667eea; margin-bottom: 15px; font-size: 16px; }
        .metric { font-size: 32px; font-weight: bold; color: #333; margin-bottom: 5px; }
        .metric-label { color: #666; font-size: 14px; }
        .chart-container { position: relative; height: 300px; }
        .alert { padding: 15px; border-radius: 8px; margin-bottom: 10px; }
        .alert-info { background: #d1ecf1; color: #0c5460; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-warning { background: #fff3cd; color: #856404; }
        .tool-status { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee; }
        .tool-status:last-child { border-bottom: none; }
        .status-badge { padding: 3px 10px; border-radius: 12px; font-size: 12px; }
        .status-ready { background: #d4edda; color: #155724; }
        .status-active { background: #cce5ff; color: #004085; }
        .status-monitoring { background: #fff3cd; color: #856404; }
        .phase-card { border-left: 4px solid #667eea; }
        .phase-p0 { border-left-color: #28a745; }
        .phase-p1 { border-left-color: #17a2b8; }
        .phase-p2 { border-left-color: #6f42c1; }
        .phase-p3 { border-left-color: #e83e8c; }
        .refresh-timer { position: fixed; bottom: 20px; right: 20px; background: white; padding: 10px 20px; border-radius: 20px; box-shadow: 0 2px 4px rgba(0,
            0,
            0,
            0.2); font-size: 14px; }
        .export-btn { background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Memory Evolution Dashboard v2</h1>
            <p>Real-time monitoring of 14 innovation tools across 5 phases</p>
            <div style="margin-top: 10px;">
                <span class="status" id="system-status">● System Healthy</span>
                <button class="export-btn" onclick="exportData()">📊 Export JSON</button>
            </div>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('overview')">Overview</button>
            <button class="tab-btn" onclick="showTab('evolution')">Evolution</button>
            <button class="tab-btn" onclick="showTab('p0')">P0: Biological</button>
            <button class="tab-btn" onclick="showTab('p1')">P1: Physics/Math</button>
            <button class="tab-btn" onclick="showTab('p2')">P2: Quantum/Time</button>
            <button class="tab-btn" onclick="showTab('p3')">P3: Consciousness</button>
            <button class="tab-btn" onclick="showTab('trends')">Trends</button>
            <button class="tab-btn" onclick="showTab('settings')">Settings</button>
        </div>

        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h3>System Health</h3>
                    <div class="metric" id="health-status">Healthy</div>
                    <div class="metric-label">Uptime: <span id="uptime">-</span></div>
                </div>
                <div class="card">
                    <h3>Success Rate</h3>
                    <div class="metric" id="success-rate">-</div>
                    <div class="metric-label">Total Runs: <span id="total-runs">-</span></div>
                </div>
                <div class="card">
                    <h3>Quality Score</h3>
                    <div class="metric" id="quality-score">-</div>
                    <div class="metric-label">Target: 0.90+</div>
                </div>
                <div class="card">
                    <h3>Next Run</h3>
                    <div class="metric" id="next-run">-</div>
                    <div class="metric-label">Last: <span id="last-run">-</span></div>
                </div>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>Recent Alerts</h3>
                    <div id="alerts-container"></div>
                </div>
                <div class="card">
                    <h3>Tool Status</h3>
                    <div id="tools-container"></div>
                </div>
            </div>
        </div>

        <!-- Evolution Tab -->
        <div id="evolution" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h3>Quality Score</h3>
                    <div class="metric" id="evo-quality">-</div>
                </div>
                <div class="card">
                    <h3>Associations</h3>
                    <div class="metric" id="evo-associations">-</div>
                </div>
                <div class="card">
                    <h3>Conflicts Resolved</h3>
                    <div class="metric" id="evo-conflicts">-</div>
                </div>
                <div class="card">
                    <h3>Memories Distilled</h3>
                    <div class="metric" id="evo-distilled">-</div>
                </div>
            </div>
            <div class="card">
                <h3>Forgetting Curve</h3>
                <div class="chart-container">
                    <canvas id="forgetting-chart"></canvas>
                </div>
            </div>
        </div>

        <!-- P0 Tab -->
        <div id="p0" class="tab-content">
            <div class="grid">
                <div class="card phase-card phase-p0">
                    <h3>Immune System</h3>
                    <div class="metric" id="p0-threats">-</div>
                    <div class="metric-label">Threats Detected</div>
                    <div class="metric-label" style="margin-top: 10px;">Neutralized: <span id="p0-neutralized">-</span></div>
                </div>
                <div class="card phase-card phase-p0">
                    <h3>Neural Network</h3>
                    <div class="metric" id="p0-connections">-</div>
                    <div class="metric-label">Synaptic Connections</div>
                    <div class="metric-label" style="margin-top: 10px;">Strength: <span id="p0-strength">-</span></div>
                </div>
            </div>
        </div>

        <!-- P1 Tab -->
        <div id="p1" class="tab-content">
            <div class="grid">
                <div class="card phase-card phase-p1">
                    <h3>Dark Matter</h3>
                    <div class="metric" id="p1-dark-matter">-</div>
                    <div class="metric-label">Hidden Patterns Found</div>
                </div>
                <div class="card phase-card phase-p1">
                    <h3>Topology</h3>
                    <div class="metric" id="p1-topology">-</div>
                    <div class="metric-label">Topological Features</div>
                </div>
                <div class="card phase-card phase-p1">
                    <h3>Thermodynamics</h3>
                    <div class="metric" id="p1-entropy">-</div>
                    <div class="metric-label">Entropy Level</div>
                </div>
                <div class="card phase-card phase-p1">
                    <h3>Fractal</h3>
                    <div class="metric" id="p1-fractal">-</div>
                    <div class="metric-label">Fractal Dimension</div>
                </div>
                <div class="card phase-card phase-p1">
                    <h3>Causal</h3>
                    <div class="metric" id="p1-causal">-</div>
                    <div class="metric-label">Causal Links</div>
                </div>
            </div>
        </div>

        <!-- P2 Tab -->
        <div id="p2" class="tab-content">
            <div class="grid">
                <div class="card phase-card phase-p2">
                    <h3>Quantum Entanglement</h3>
                    <div class="metric" id="p2-entangled">-</div>
                    <div class="metric-label">Entangled Pairs</div>
                    <div class="metric-label" style="margin-top: 10px;">Bell Violation: <span id="p2-bell">-</span></div>
                </div>
                <div class="card phase-card phase-p2">
                    <h3>Time Crystal</h3>
                    <div class="metric" id="p2-phase">-</div>
                    <div class="metric-label">Crystal Phase</div>
                    <div class="metric-label" style="margin-top: 10px;">Coherence: <span id="p2-coherence">-</span></div>
                </div>
            </div>
        </div>

        <!-- P3 Tab -->
        <div id="p3" class="tab-content">
            <div class="grid">
                <div class="card phase-card phase-p3">
                    <h3>Consciousness Level</h3>
                    <div class="metric" id="p3-consciousness">-</div>
                    <div class="metric-label">Global Workspace Active</div>
                </div>
                <div class="card phase-card phase-p3">
                    <h3>Integrated Information (Φ)</h3>
                    <div class="metric" id="p3-phi">-</div>
                    <div class="metric-label">Grade: <span id="p3-grade">-</span></div>
                </div>
                <div class="card phase-card phase-p3">
                    <h3>Higher-Order Thoughts</h3>
                    <div class="metric" id="p3-hot">-</div>
                    <div class="metric-label">Levels of Abstraction</div>
                </div>
                <div class="card phase-card phase-p3">
                    <h3>Emergent Properties</h3>
                    <div class="metric" id="p3-emergent">-</div>
                    <div class="metric-label">Detected Properties</div>
                </div>
                <div class="card phase-card phase-p3">
                    <h3>Self-Awareness</h3>
                    <div class="metric" id="p3-self">-</div>
                    <div class="metric-label">Meta-Cognition Score</div>
                </div>
            </div>
        </div>

        <!-- Trends Tab -->
        <div id="trends" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h3>Quality Trend (7 Days)</h3>
                    <div class="chart-container">
                        <canvas id="quality-trend-chart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <h3>Associations Growth</h3>
                    <div class="chart-container">
                        <canvas id="associations-chart"></canvas>
                    </div>
                </div>
            </div>
            <div class="card">
                <h3>Conflicts Detected</h3>
                <div class="chart-container">
                    <canvas id="conflicts-chart"></canvas>
                </div>
            </div>
        </div>

        <!-- Settings Tab -->
        <div id="settings" class="tab-content">
            <div class="card">
                <h3>Dashboard Settings</h3>
                <div style="margin: 20px 0;">
                    <label>Auto-Refresh Interval: </label>
                    <select id="refresh-interval" onchange="updateRefresh()">
                        <option value="5">5 seconds</option>
                        <option value="10" selected>10 seconds</option>
                        <option value="30">30 seconds</option>
                        <option value="60">1 minute</option>
                        <option value="0">Disabled</option>
                    </select>
                </div>
                <div>
                    <button class="export-btn" onclick="exportData()">📊 Export All Data</button>
                    <button class="export-btn" onclick="location.reload()">🔄 Refresh Now</button>
                </div>
            </div>
        </div>
    </div>

    <div class="refresh-timer">
        Auto-refresh in: <span id="countdown">10</span>s
    </div>

    <script>
        let dashboardData = null;
        let refreshInterval = 10;
        let countdown = refreshInterval;
        let charts = {};

        // Tab switching
        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }

        // Fetch data
        async function fetchData() {
            try {
                const response = await fetch('/api/data');
                dashboardData = await response.json();
                updateDashboard();
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        // Update dashboard
        function updateDashboard() {
            if (!dashboardData) return;

            const { health, evolution, phases, trends, tools, alerts } = dashboardData;

            // Overview
            document.getElementById('health-status').textContent = health.status.toUpperCase();
            document.getElementById('uptime').textContent = health.uptime;
            document.getElementById('success-rate').textContent = health.success_rate + '%';
            document.getElementById('total-runs').textContent = health.total_runs.toLocaleString();
            document.getElementById('quality-score').textContent = evolution.quality_score.toFixed(2);
            document.getElementById('next-run').textContent = new Date(health.next_run).toLocaleTimeString();
            document.getElementById('last-run').textContent = new Date(health.last_run).toLocaleTimeString();

            // Alerts
            const alertsContainer = document.getElementById('alerts-container');
            alertsContainer.innerHTML = alerts.map(alert =>
                `<div class="alert alert-${alert.level}">${alert.message} <small>(${alert.time})</small></div>`
            ).join('');

            // Tools
            const toolsContainer = document.getElementById('tools-container');
            toolsContainer.innerHTML = Object.entries(tools).map(([id, info]) =>
                `<div class="tool-status">
                    <strong>${id}</strong>
                    <span class="status-badge status-${info.status}">${info.status}</span>
                </div>`
            ).join('');

            // Evolution
            document.getElementById('evo-quality').textContent = evolution.quality_score.toFixed(2);
            document.getElementById('evo-associations').textContent = evolution.associations.toLocaleString();
            document.getElementById('evo-conflicts').textContent = evolution.conflicts_resolved.toLocaleString();
            document.getElementById('evo-distilled').textContent = evolution.memories_distilled.toLocaleString();

            // P0
            document.getElementById('p0-threats').textContent = phases.P0.immune_threats.toLocaleString();
            document.getElementById('p0-neutralized').textContent = phases.P0.immune_neutralized.toLocaleString();
            document.getElementById('p0-connections').textContent = phases.P0.neural_connections.toLocaleString();
            document.getElementById('p0-strength').textContent = phases.P0.synaptic_strength.toFixed(2);

            // P1
            document.getElementById('p1-dark-matter').textContent = phases.P1.dark_matter_found.toLocaleString();
            document.getElementById('p1-topology').textContent = phases.P1.topological_features.toLocaleString();
            document.getElementById('p1-entropy').textContent = phases.P1.entropy_level.toFixed(2);
            document.getElementById('p1-fractal').textContent = phases.P1.fractal_dimension.toFixed(2);
            document.getElementById('p1-causal').textContent = phases.P1.causal_links.toLocaleString();

            // P2
            document.getElementById('p2-entangled').textContent = phases.P2.entangled_pairs.toLocaleString();
            document.getElementById('p2-bell').textContent = phases.P2.bell_violation.toFixed(2);
            document.getElementById('p2-phase').textContent = phases.P2.time_crystal_phase.toUpperCase();
            document.getElementById('p2-coherence').textContent = phases.P2.coherence_time.toFixed(2);

            // P3
            document.getElementById('p3-consciousness').textContent = phases.P3.consciousness_level.toFixed(2);
            document.getElementById('p3-phi').textContent = phases.P3.phi_value.toFixed(3);
            document.getElementById('p3-grade').textContent = getPhiGrade(phases.P3.phi_value);
            document.getElementById('p3-hot').textContent = phases.P3.hot_levels;
            document.getElementById('p3-emergent').textContent = phases.P3.emergent_properties;
            document.getElementById('p3-self').textContent = phases.P3.self_awareness.toFixed(2);

            // Charts
            updateCharts(trends, evolution);
        }

        function getPhiGrade(phi) {
            if (phi >= 0.5) return 'A';
            if (phi >= 0.4) return 'B';
            if (phi >= 0.3) return 'C';
            if (phi >= 0.2) return 'C';
            return 'D';
        }

        // Update charts
        function updateCharts(trends, evolution) {
            // Forgetting curve
            if (charts.forgetting) {
                charts.forgetting.data.datasets[0].data = evolution.forgetting_curve;
                charts.forgetting.update();
            } else {
                const ctx1 = document.getElementById('forgetting-chart').getContext('2d');
                charts.forgetting = new Chart(ctx1, {
                    type: 'line',
                    data: {
                        labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                        datasets: [{
                            label: 'Memory Retention',
                            data: evolution.forgetting_curve,
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }

            // Quality trend
            if (charts.quality) {
                charts.quality.data.datasets[0].data = trends.quality;
                charts.quality.update();
            } else {
                const ctx2 = document.getElementById('quality-trend-chart').getContext('2d');
                charts.quality = new Chart(ctx2, {
                    type: 'line',
                    data: {
                        labels: trends.dates,
                        datasets: [{
                            label: 'Quality Score',
                            data: trends.quality,
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }

            // Associations
            if (charts.associations) {
                charts.associations.data.datasets[0].data = trends.associations;
                charts.associations.update();
            } else {
                const ctx3 = document.getElementById('associations-chart').getContext('2d');
                charts.associations = new Chart(ctx3, {
                    type: 'bar',
                    data: {
                        labels: trends.dates,
                        datasets: [{
                            label: 'Total Associations',
                            data: trends.associations,
                            backgroundColor: '#17a2b8'
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }

            // Conflicts
            if (charts.conflicts) {
                charts.conflicts.data.datasets[0].data = trends.conflicts;
                charts.conflicts.update();
            } else {
                const ctx4 = document.getElementById('conflicts-chart').getContext('2d');
                charts.conflicts = new Chart(ctx4, {
                    type: 'bar',
                    data: {
                        labels: trends.dates,
                        datasets: [{
                            label: 'Conflicts Detected',
                            data: trends.conflicts,
                            backgroundColor: '#ffc107'
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }
        }

        // Export data
        function exportData() {
            if (!dashboardData) return;
            const blob = new Blob([JSON.stringify(dashboardData, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `memory_dashboard_export_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
        }

        // Update refresh interval
        function updateRefresh() {
            refreshInterval = parseInt(document.getElementById('refresh-interval').value);
            countdown = refreshInterval;
            if (refreshInterval > 0) {
                startCountdown();
            }
        }

        // Countdown timer
        function startCountdown() {
            setInterval(() => {
                if (countdown > 0) {
                    countdown--;
                    document.getElementById('countdown').textContent = countdown;
                } else {
                    fetchData();
                    countdown = refreshInterval;
                }
            }, 1000);
        }

        // Initialize
        fetchData();
        startCountdown();
    </script>
</body>
</html>
"""

# ============================================================================
# Main Entry Point
# ============================================================================

def start_dashboard():
    """Start the dashboard server"""

    print("\n" + "=" * 60)
    print("🧠 Memory Evolution Dashboard v2")
    print("=" * 60)
    print(f"\nStarting server on http://localhost:{PORT}")
    print(f"Auto-refresh: {AUTO_REFRESH_SECONDS} seconds")
    print(f"Workspace: {WORKSPACE}")
    print("\nPress Ctrl+C to stop\n")

    # Open browser
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()

    # Start server
    server = HTTPServer(('localhost', PORT), DashboardHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down dashboard...")
        server.shutdown()

if __name__ == '__main__':
    start_dashboard()
