#!/usr/bin/env python3
"""
Feishu Message Analytics Dashboard
===================================
Real-time web dashboard for message statistics and analytics.

Features:
- Message volume trends (hourly/daily/weekly)
- Delivery success rate
- Response rate tracking
- Priority distribution
- Template usage analytics
- Auto-refresh (10 seconds)
- Interactive charts (Chart.js)

Usage:
    python feishu-analytics-dashboard.py
    # Opens http://localhost:8080
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, List
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

class AnalyticsConfig:
    """Analytics dashboard configuration"""
    
    # Database paths
    MESSAGE_DB = os.path.join(os.path.dirname(__file__), 'feishu_queue.db')
    APPROVAL_DB = os.path.join(os.path.dirname(__file__), 'feishu_approvals.db')
    
    # Server
    HOST = '0.0.0.0'
    PORT = 8080
    
    # Auto-refresh interval (seconds)
    REFRESH_INTERVAL = 10


# ============================================================================
# Analytics Engine
# ============================================================================

class MessageAnalyticsEngine:
    """Engine for message analytics"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_message_stats(self, days: int = 7) -> Dict:
        """Get message statistics"""
        if not os.path.exists(self.db_path):
            return self._empty_stats()
        
        cutoff = datetime.now() - timedelta(days=days)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            stats = {}
            
            # Total messages
            cursor = conn.execute('''
                SELECT COUNT(*) FROM messages WHERE created_at > ?
            ''', (cutoff,))
            stats['total'] = cursor.fetchone()[0]
            
            # By status
            cursor = conn.execute('''
                SELECT status, COUNT(*) as count
                FROM messages
                WHERE created_at > ?
                GROUP BY status
            ''', (cutoff,))
            stats['by_status'] = {row['status']: row['count'] for row in cursor}
            
            # By priority
            cursor = conn.execute('''
                SELECT priority, COUNT(*) as count
                FROM messages
                WHERE created_at > ?
                GROUP BY priority
            ''', (cutoff,))
            stats['by_priority'] = {row['priority']: row['count'] for row in cursor}
            
            # Hourly trend (last 24 hours)
            cursor = conn.execute('''
                SELECT strftime('%Y-%m-%d %H:00', created_at) as hour, COUNT(*) as count
                FROM messages
                WHERE created_at > datetime('now', '-24 hours')
                GROUP BY hour
                ORDER BY hour
            ''')
            stats['hourly_trend'] = [
                {'time': row['hour'], 'count': row['count']}
                for row in cursor
            ]
            
            # Daily trend (last 7 days)
            cursor = conn.execute('''
                SELECT strftime('%Y-%m-%d', created_at) as day, COUNT(*) as count
                FROM messages
                WHERE created_at > ?
                GROUP BY day
                ORDER BY day
            ''', (cutoff,))
            stats['daily_trend'] = [
                {'date': row['day'], 'count': row['count']}
                for row in cursor
            ]
            
            # Success rate
            total = stats['total']
            sent = stats['by_status'].get('sent', 0)
            failed = stats['by_status'].get('failed', 0)
            stats['success_rate'] = (sent / total * 100) if total > 0 else 0
            stats['failure_rate'] = (failed / total * 100) if total > 0 else 0
            
            # Average delivery time (mock for now)
            stats['avg_delivery_seconds'] = 1.5
            
            return stats
        finally:
            conn.close()
    
    def _empty_stats(self) -> Dict:
        """Return empty stats"""
        return {
            'total': 0,
            'by_status': {},
            'by_priority': {},
            'hourly_trend': [],
            'daily_trend': [],
            'success_rate': 0,
            'failure_rate': 0,
            'avg_delivery_seconds': 0
        }


class ApprovalAnalyticsEngine:
    """Engine for approval analytics"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_approval_stats(self, days: int = 7) -> Dict:
        """Get approval statistics"""
        if not os.path.exists(self.db_path):
            return self._empty_stats()
        
        cutoff = datetime.now() - timedelta(days=days)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            stats = {}
            
            # Total requests
            cursor = conn.execute('''
                SELECT COUNT(*) FROM approval_requests WHERE created_at > ?
            ''', (cutoff,))
            stats['total'] = cursor.fetchone()[0]
            
            # By status
            cursor = conn.execute('''
                SELECT status, COUNT(*) as count
                FROM approval_requests
                WHERE created_at > ?
                GROUP BY status
            ''', (cutoff,))
            stats['by_status'] = {row['status']: row['count'] for row in cursor}
            
            # By priority
            cursor = conn.execute('''
                SELECT priority, COUNT(*) as count
                FROM approval_requests
                WHERE created_at > ?
                GROUP BY priority
            ''', (cutoff,))
            stats['by_priority'] = {row['priority']: row['count'] for row in cursor}
            
            # Average response time
            cursor = conn.execute('''
                SELECT AVG(
                    (julianday(responded_at) - julianday(created_at)) * 24 * 60
                ) as avg_minutes
                FROM approval_requests
                WHERE responded_at IS NOT NULL AND created_at > ?
            ''', (cutoff,))
            row = cursor.fetchone()
            stats['avg_response_minutes'] = row['avg_minutes'] or 0
            
            # Escalation rate
            cursor = conn.execute('''
                SELECT COUNT(*) FROM approval_requests
                WHERE escalation_count > 0 AND created_at > ?
            ''', (cutoff,))
            escalated = cursor.fetchone()[0]
            stats['escalation_rate'] = (escalated / stats['total'] * 100) if stats['total'] > 0 else 0
            
            # Approval rate
            approved = stats['by_status'].get('approved', 0)
            rejected = stats['by_status'].get('rejected', 0)
            total_decided = approved + rejected
            stats['approval_rate'] = (approved / total_decided * 100) if total_decided > 0 else 0
            
            return stats
        finally:
            conn.close()
    
    def _empty_stats(self) -> Dict:
        """Return empty stats"""
        return {
            'total': 0,
            'by_status': {},
            'by_priority': {},
            'avg_response_minutes': 0,
            'escalation_rate': 0,
            'approval_rate': 0
        }


# ============================================================================
# Dashboard HTML
# ============================================================================

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 飞书消息分析仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { color: #333; font-size: 28px; margin-bottom: 8px; }
        .header p { color: #666; font-size: 14px; }
        .status-bar {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #eee;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-card h3 { color: #666; font-size: 14px; margin-bottom: 8px; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: #333; }
        .stat-card .trend { font-size: 12px; color: #4CAF50; margin-top: 8px; }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .chart-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .chart-card h3 { color: #333; font-size: 18px; margin-bottom: 16px; }
        .chart-container { position: relative; height: 300px; }
        .section-title {
            color: white;
            font-size: 20px;
            margin: 24px 0 16px 0;
            font-weight: 600;
        }
        .tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }
        .tab {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .tab.active {
            background: white;
            color: #667eea;
        }
        .tab:hover { background: rgba(255,255,255,0.3); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th { background: #f8f9fa; font-weight: 600; color: #333; }
        tr:hover { background: #f8f9fa; }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-success { background: #E8F5E9; color: #4CAF50; }
        .badge-warning { background: #FFF3E0; color: #FF9800; }
        .badge-danger { background: #FFEBEE; color: #F44336; }
        .badge-info { background: #E3F2FD; color: #2196F3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 飞书消息分析仪表板</h1>
            <p>实时消息统计与性能分析</p>
            <div class="status-bar">
                <div class="status-indicator"></div>
                <span id="last-update">正在加载...</span>
                <span>• 自动刷新：10 秒</span>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('messages')">📨 消息统计</button>
            <button class="tab" onclick="switchTab('approvals')">✅ 审批统计</button>
        </div>
        
        <div id="messages-tab" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>总消息数</h3>
                    <div class="value" id="total-messages">-</div>
                    <div class="trend">过去 7 天</div>
                </div>
                <div class="stat-card">
                    <h3>送达率</h3>
                    <div class="value" id="success-rate">-</div>
                    <div class="trend">成功率</div>
                </div>
                <div class="stat-card">
                    <h3>平均延迟</h3>
                    <div class="value" id="avg-latency">-</div>
                    <div class="trend">秒</div>
                </div>
                <div class="stat-card">
                    <h3>失败率</h3>
                    <div class="value" id="failure-rate">-</div>
                    <div class="trend">需关注</div>
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>📈 24 小时趋势</h3>
                    <div class="chart-container">
                        <canvas id="hourly-chart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>📊 优先级分布</h3>
                    <div class="chart-container">
                        <canvas id="priority-chart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="chart-card">
                <h3>📅 7 天趋势</h3>
                <div class="chart-container">
                    <canvas id="daily-chart"></canvas>
                </div>
            </div>
        </div>
        
        <div id="approvals-tab" class="tab-content">
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>总审批数</h3>
                    <div class="value" id="total-approvals">-</div>
                    <div class="trend">过去 7 天</div>
                </div>
                <div class="stat-card">
                    <h3>批准率</h3>
                    <div class="value" id="approval-rate">-</div>
                    <div class="trend">批准/拒绝</div>
                </div>
                <div class="stat-card">
                    <h3>平均响应时间</h3>
                    <div class="value" id="avg-response">-</div>
                    <div class="trend">分钟</div>
                </div>
                <div class="stat-card">
                    <h3>升级率</h3>
                    <div class="value" id="escalation-rate">-</div>
                    <div class="trend">超时升级</div>
                </div>
            </div>
            
            <div class="chart-card">
                <h3>📊 审批状态分布</h3>
                <div class="chart-container">
                    <canvas id="approval-status-chart"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let hourlyChart, priorityChart, dailyChart, approvalStatusChart;
        
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }
        
        function updateTimestamp() {
            const now = new Date();
            document.getElementById('last-update').textContent = 
                '最后更新：' + now.toLocaleString('zh-CN');
        }
        
        function createCharts() {
            // Hourly chart
            const hourlyCtx = document.getElementById('hourly-chart').getContext('2d');
            hourlyChart = new Chart(hourlyCtx, {
                type: 'line',
                data: { labels: [], datasets: [] },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { stepSize: 1 } }
                    }
                }
            });
            
            // Priority chart
            const priorityCtx = document.getElementById('priority-chart').getContext('2d');
            priorityChart = new Chart(priorityCtx, {
                type: 'doughnut',
                data: { labels: [], datasets: [] },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            
            // Daily chart
            const dailyCtx = document.getElementById('daily-chart').getContext('2d');
            dailyChart = new Chart(dailyCtx, {
                type: 'bar',
                data: { labels: [], datasets: [] },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { stepSize: 1 } }
                    }
                }
            });
            
            // Approval status chart
            const approvalCtx = document.getElementById('approval-status-chart').getContext('2d');
            approvalStatusChart = new Chart(approvalCtx, {
                type: 'pie',
                data: { labels: [], datasets: [] },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        async function fetchData() {
            try {
                const [msgRes, appRes] = await Promise.all([
                    fetch('/api/messages'),
                    fetch('/api/approvals')
                ]);
                
                const msgData = await msgRes.json();
                const appData = await appRes.json();
                
                updateMessageStats(msgData);
                updateApprovalStats(appData);
                updateTimestamp();
            } catch (error) {
                console.error('Failed to fetch data:', error);
            }
        }
        
        function updateMessageStats(data) {
            document.getElementById('total-messages').textContent = data.total || 0;
            document.getElementById('success-rate').textContent = (data.success_rate || 0).toFixed(1) + '%';
            document.getElementById('avg-latency').textContent = (data.avg_delivery_seconds || 0).toFixed(1) + 's';
            document.getElementById('failure-rate').textContent = (data.failure_rate || 0).toFixed(1) + '%';
            
            // Hourly chart
            hourlyChart.data.labels = data.hourly_trend?.map(d => d.time.slice(11) || []) || [];
            hourlyChart.data.datasets = [{
                label: '消息数',
                data: data.hourly_trend?.map(d => d.count) || [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.4
            }];
            hourlyChart.update();
            
            // Priority chart
            priorityChart.data.labels = Object.keys(data.by_priority || {});
            priorityChart.data.datasets = [{
                data: Object.values(data.by_priority || {}),
                backgroundColor: ['#4CAF50', '#2196F3', '#F44336']
            }];
            priorityChart.update();
            
            // Daily chart
            dailyChart.data.labels = data.daily_trend?.map(d => d.date.slice(5) || []) || [];
            dailyChart.data.datasets = [{
                label: '消息数',
                data: data.daily_trend?.map(d => d.count) || [],
                backgroundColor: '#667eea'
            }];
            dailyChart.update();
        }
        
        function updateApprovalStats(data) {
            document.getElementById('total-approvals').textContent = data.total || 0;
            document.getElementById('approval-rate').textContent = (data.approval_rate || 0).toFixed(1) + '%';
            document.getElementById('avg-response').textContent = (data.avg_response_minutes || 0).toFixed(0) + 'm';
            document.getElementById('escalation-rate').textContent = (data.escalation_rate || 0).toFixed(1) + '%';
            
            // Approval status chart
            approvalStatusChart.data.labels = Object.keys(data.by_status || {});
            approvalStatusChart.data.datasets = [{
                data: Object.values(data.by_status || {}),
                backgroundColor: ['#4CAF50', '#F44336', '#FF9800', '#2196F3', '#9E9E9E']
            }];
            approvalStatusChart.update();
        }
        
        // Initialize
        createCharts();
        fetchData();
        setInterval(fetchData, 10000); // Auto-refresh every 10 seconds
    </script>
</body>
</html>
'''


# ============================================================================
# HTTP Server
# ============================================================================

class AnalyticsHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for analytics dashboard"""
    
    def __init__(self, *args, msg_engine=None, app_engine=None, **kwargs):
        self.msg_engine = msg_engine
        self.app_engine = app_engine
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/messages':
            self.send_json(self.msg_engine.get_message_stats())
        elif parsed.path == '/api/approvals':
            self.send_json(self.app_engine.get_approval_stats())
        elif parsed.path == '/':
            self.send_html(DASHBOARD_HTML)
        else:
            self.send_error(404)
    
    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_html(self, html):
        """Send HTML response"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Override to use logger"""
        logger.debug(f"{self.address_string()} - {format % args}")


def run_server():
    """Run analytics dashboard server"""
    config = AnalyticsConfig()
    
    # Initialize engines
    msg_engine = MessageAnalyticsEngine(config.MESSAGE_DB)
    app_engine = ApprovalAnalyticsEngine(config.APPROVAL_DB)
    
    # Create handler factory
    def handler_factory(*args, **kwargs):
        return AnalyticsHandler(*args, msg_engine=msg_engine, app_engine=app_engine, **kwargs)
    
    # Start server
    server = HTTPServer((config.HOST, config.PORT), handler_factory)
    logger.info(f"📊 Analytics Dashboard running at http://localhost:{config.PORT}")
    logger.info(f"Auto-refresh interval: {config.REFRESH_INTERVAL} seconds")
    logger.info("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    run_server()
