from pathlib import Path
#!/usr/bin/env python3
"""
Innovator Dashboard v3.0 - Backend API Server
Provides real-time data for 7-persona system monitoring

Features:
- Session history tracking
- Innovation database
- Memory distillation status
- Git commit tracking
- System health monitoring

Author: Claw 🐾
Version: 3.0
"""

import json
import os
import sys
import subprocess
import datetime
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import psutil

# Configuration
PORT = 8446
DATA_DIR = os.path.join(os.path.dirname(__file__), 'dashboard-data')
WORKSPACE_DIR = str(Path(__file__).parent.parent)

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

class DashboardAPIHandler(SimpleHTTPRequestHandler):
    """HTTP Request Handler for Dashboard API"""

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        # API endpoints
        if path == '/api/sessions':
            self.send_json_response(self.get_sessions())
        elif path == '/api/innovations':
            self.send_json_response(self.get_innovations())
        elif path == '/api/memory':
            self.send_json_response(self.get_memory_status())
        elif path == '/api/git':
            self.send_json_response(self.get_git_stats())
        elif path == '/api/health':
            self.send_json_response(self.get_system_health())
        elif path == '/api/personas':
            self.send_json_response(self.get_persona_history())
        elif path == '/api/dashboard':
            self.send_json_response(self.get_dashboard_summary())
        elif path == '/' or path == '/index.html':
            self.serve_dashboard()
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/innovations':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                result = self.add_innovation(data)
                self.send_json_response(result)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 400)
        else:
            self.send_error(404, 'Not Found')

    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

    def send_json_file(self, filepath):
        """Serve JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.send_json_response(data)
        except FileNotFoundError:
            self.send_json_response({'error': 'File not found'}, 404)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def serve_dashboard(self):
        """Serve dashboard HTML"""
        dashboard_path = os.path.join(os.path.dirname(__file__), 'innovator-dashboard-v3.html')
        if os.path.exists(dashboard_path):
            self.path = dashboard_path
            return SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_error(404, 'Dashboard HTML not found')

    def get_sessions(self):
        """Get recent session history"""
        sessions_dir = os.path.join(WORKSPACE_DIR, 'sessions')
        sessions = []

        try:
            if os.path.exists(sessions_dir):
                files = sorted(os.listdir(sessions_dir), reverse=True)[:10]
                for filename in files:
                    if filename.endswith('.json'):
                        filepath = os.path.join(sessions_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                session = json.load(f)
                                sessions.append({
                                    'id': filename.replace('.json', ''),
                                    'timestamp': session.get('timestamp', 'Unknown'),
                                    'duration': session.get('duration', 'Unknown'),
                                    'tasks_completed': len(session.get('tasks', [])),
                                    'innovations': session.get('innovations_count', 0),
                                    'persona_scores': session.get('persona_scores', {})
                                })
                        except:
                            pass
        except Exception as e:
            return {'error': str(e)}

        return {'sessions': sessions, 'total': len(sessions)}

    def get_innovations(self):
        """Get innovation database"""
        innovations_file = os.path.join(DATA_DIR, 'innovations.json')

        # Load existing innovations
        if os.path.exists(innovations_file):
            with open(innovations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return sample data
            sample = {
                'innovations': [
                    {
                        'id': 'INNOVATOR-055',
                        'title': '快速操作按钮',
                        'description': '表格内一键设置预警',
                        'impact': 'high',
                        'feasibility': 'high',
                        'status': 'implemented',
                        'created_at': '2026-03-15T21:30:00Z',
                        'implemented_at': '2026-03-15T22:00:00Z'
                    },
                    {
                        'id': 'INNOVATOR-054',
                        'title': '价格预警系统',
                        'description': '阈值通知机制',
                        'impact': 'high',
                        'feasibility': 'medium',
                        'status': 'implemented',
                        'created_at': '2026-03-15T20:00:00Z',
                        'implemented_at': '2026-03-15T21:00:00Z'
                    }
                ],
                'total': 2,
                'by_status': {'implemented': 2, 'in_progress': 0, 'pending': 0}
            }
            return sample

    def add_innovation(self, data):
        """Add new innovation"""
        innovations_file = os.path.join(DATA_DIR, 'innovations.json')

        # Load existing
        if os.path.exists(innovations_file):
            with open(innovations_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
        else:
            db = {'innovations': [], 'total': 0}

        # Add new
        new_innovation = {
            'id': f"INNOVATOR-{len(db['innovations']) + 1:03d}",
            'title': data.get('title', 'Untitled'),
            'description': data.get('description', ''),
            'impact': data.get('impact', 'medium'),
            'feasibility': data.get('feasibility', 'medium'),
            'status': 'pending',
            'created_at': datetime.datetime.now().isoformat()
        }

        db['innovations'].append(new_innovation)
        db['total'] = len(db['innovations'])

        # Save
        with open(innovations_file, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

        return {'success': True, 'innovation': new_innovation}

    def get_memory_status(self):
        """Get memory distillation status"""
        memory_dir = os.path.join(WORKSPACE_DIR, '13-memory-记忆系统')
        result = {
            'daily_notes': 0,
            'memory_file_size': 0,
            'last_distillation': 'Unknown',
            'recent_insights': [],
            'weekly_progress': 0
        }

        try:
            if os.path.exists(memory_dir):
                # Count daily notes
                files = [f for f in os.listdir(memory_dir) if f.endswith('.md') and f[0].isdigit()]
                result['daily_notes'] = len(files)

                # Get MEMORY.md size
                memory_file = os.path.join(WORKSPACE_DIR, 'MEMORY.md')
                if os.path.exists(memory_file):
                    result['memory_file_size'] = os.path.getsize(memory_file) // 1024  # KB

                # Get recent files
                recent_files = sorted(files, reverse=True)[:5]
                result['recent_insights'] = [
                    {'file': f, 'date': f.replace('.md', '')}
                    for f in recent_files
                ]

                # Calculate weekly progress (simple heuristic)
                today = datetime.datetime.now()
                week_ago = today - datetime.timedelta(days=7)
                week_files = [f for f in files if f.replace('.md', '') >= week_ago.strftime('%Y-%m-%d')]
                result['weekly_progress'] = min(100, len(week_files) * 20)  # Cap at 100%
        except Exception as e:
            result['error'] = str(e)

        return result

    def get_git_stats(self):
        """Get Git commit statistics"""
        result = {
            'today_commits': 0,
            'week_commits': 0,
            'total_commits': 0,
            'recent_commits': [],
            'files_changed': {'created': 0, 'modified': 0, 'deleted': 0}
        }

        try:
            os.chdir(WORKSPACE_DIR)

            # Total commits
            total = subprocess.run(['git', 'rev-list', '--count', 'HEAD'],
                                   capture_output=True, text=True, timeout=10)
            if total.returncode == 0:
                result['total_commits'] = int(total.stdout.strip())

            # Recent commits
            log = subprocess.run(['git', 'log', '--oneline', '-10'],
                                 capture_output=True, text=True, timeout=10)
            if log.returncode == 0:
                result['recent_commits'] = [
                    {'hash': line.split()[0], 'message': ' '.join(line.split()[1:])}
                    for line in log.stdout.strip().split('\n') if line
                ]

            # Today's commits
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            log_today = subprocess.run(['git', 'log', '--since=today', '--oneline'],
                                       capture_output=True, text=True, timeout=10)
            if log_today.returncode == 0:
                commits = [l for l in log_today.stdout.strip().split('\n') if l]
                result['today_commits'] = len(commits)

            # Week's commits
            week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            log_week = subprocess.run(['git', 'log', f'--since={week_ago}', '--oneline'],
                                      capture_output=True, text=True, timeout=10)
            if log_week.returncode == 0:
                commits = [l for l in log_week.stdout.strip().split('\n') if l]
                result['week_commits'] = len(commits)

            # Files changed (last commit)
            diff = subprocess.run(['git', 'diff-tree', '--no-commit-id', '--name-status', '-r', 'HEAD'],
                                  capture_output=True, text=True, timeout=10)
            if diff.returncode == 0:
                for line in diff.stdout.strip().split('\n'):
                    if line.startswith('A'):
                        result['files_changed']['created'] += 1
                    elif line.startswith('M'):
                        result['files_changed']['modified'] += 1
                    elif line.startswith('D'):
                        result['files_changed']['deleted'] += 1
        except Exception as e:
            result['error'] = str(e)

        return result

    def get_system_health(self):
        """Get system health metrics"""
        result = {
            'local': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent if sys.platform != 'win32' else psutil.disk_usage('C:\\').percent,
                'status': 'healthy'
            },
            'cloud': {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'status': 'unknown',
                'services': []
            },
            'services': [
                {'name': 'Innovator Dashboard', 'port': 8444, 'status': 'unknown'},
                {'name': 'Workflow Visualizer', 'port': 8445, 'status': 'unknown'},
                {'name': 'Stock Analyzer', 'port': 8500, 'status': 'unknown'}
            ]
        }

        # Try to check cloud server via SSH (simplified - just mark as unknown)
        # In production, you'd use paramiko to connect and check

        # Determine overall status
        if result['local']['cpu_percent'] < 80 and result['local']['memory_percent'] < 80:
            result['local']['status'] = 'healthy'
        elif result['local']['cpu_percent'] < 90 or result['local']['memory_percent'] < 90:
            result['local']['status'] = 'warning'
        else:
            result['local']['status'] = 'critical'

        return result

    def get_persona_history(self):
        """Get 7-persona score history"""
        # Load from data file or generate sample
        history_file = os.path.join(DATA_DIR, 'persona-history.json')

        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Generate sample data for last 7 days
            today = datetime.datetime.now()
            personas = ['planner', 'executor', 'critic', 'learner', 'coordinator', 'innovator', 'metacognition']
            history = []

            for i in range(7):
                date = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                scores = {p: 85 + (hash(date + p) % 15) for p in personas}
                history.append({
                    'date': date,
                    'scores': scores,
                    'average': sum(scores.values()) / len(scores)
                })

            sample = {
                'history': history,
                'averages': {p: sum(h['scores'][p] for h in history) / len(history) for p in personas}
            }

            # Save for future use
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(sample, f, ensure_ascii=False, indent=2)

            return sample

    def get_dashboard_summary(self):
        """Get dashboard summary with all key metrics"""
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'sessions': self.get_sessions(),
            'innovations': self.get_innovations(),
            'memory': self.get_memory_status(),
            'git': self.get_git_stats(),
            'health': self.get_system_health(),
            'personas': self.get_persona_history()
        }

    def log_message(self, format, *args):
        """Override to suppress default logging"""
        pass


def run_server():
    """Start the API server"""
    # Fix Windows console encoding for emoji support
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, DashboardAPIHandler)
    print("[INNOVATOR] Dashboard API v3.0")
    print(f"[SERVER] Running on http://0.0.0.0:{PORT}")
    print(f"[DATA] Directory: {DATA_DIR}")
    print(f"[WORKSPACE] {WORKSPACE_DIR}")
    print("\n[API] Endpoints:")
    print("  GET  /api/sessions    - Session history")
    print("  GET  /api/innovations - Innovation database")
    print("  GET  /api/memory      - Memory status")
    print("  GET  /api/git         - Git statistics")
    print("  GET  /api/health      - System health")
    print("  GET  /api/personas    - Persona history")
    print("  GET  /api/dashboard   - Full summary")
    print("  POST /api/innovations - Add innovation")
    print("\n[INFO] Press Ctrl+C to stop\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
