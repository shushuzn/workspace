#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow Dashboard Server

Hosts the workflow dashboard web UI with auto-refresh
and real-time status API.

Usage:
    python workflow_server.py --port 8089

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import json
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class WorkflowHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler with API support"""
    
    def __init__(self, *args, workflow_manager=None, **kwargs):
        self.workflow_manager = workflow_manager
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        
        # API endpoint
        if parsed.path == '/api/status':
            self.send_json_response()
            return
        
        # Dashboard
        if parsed.path == '/' or parsed.path == '/dashboard':
            self.path = '/30-scripts-tools/workflow_dashboard.html'
        
        return super().do_GET()
    
    def send_json_response(self):
        """Send workflow status as JSON"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.workflow_manager and self.workflow_manager.state:
            state = self.workflow_manager.state
            checks = self.workflow_manager.check()
            
            response = {
                'iteration': state.iteration,
                'stage': state.stage,
                'started_at': state.started_at,
                'completed_at': state.completed_at,
                'files': state.files,
                'reports': state.reports,
                'memory_updated': state.memory_updated,
                'tests_passed': state.tests_passed,
                'commit_count': state.commit_count,
                'score': checks.get('score', 0),
                'ready': checks.get('ready', False),
                'has_files': checks.get('has_files', False),
                'has_reports': checks.get('has_reports', False),
            }
        else:
            response = {'error': 'No active iteration'}
        
        self.wfile.write(json.dumps(response, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"🌐 [{self.log_date_time_string()}] {args[0]}")


def open_browser(port):
    """Open browser after delay"""
    import time
    time.sleep(1.5)
    webbrowser.open(f'http://localhost:{port}')
    print(f"🌐 Dashboard opened in browser")


def run_server(port=8089):
    """Start the dashboard server"""
    # Import workflow manager
    sys.path.insert(0, str(Path(__file__).parent))
    from workflow_manager import WorkflowManager
    
    wm = WorkflowManager()
    
    # Create handler with workflow manager
    def handler(*args, **kwargs):
        return WorkflowHandler(*args, workflow_manager=wm, **kwargs)
    
    server = HTTPServer(('0.0.0.0', port), handler)
    
    print(f"\n{'='*70}")
    print(f"🚀 Workflow Dashboard Server")
    print(f"{'='*70}")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"🌐 API: http://localhost:{port}/api/status")
    print(f"📊 Auto-refresh: Every 10 seconds")
    print(f"{'='*70}\n")
    
    # Open browser in background
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    try:
        print(f"📡 Server running on port {port}...")
        print(f"Press Ctrl+C to stop\n")
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Server stopped")
        server.shutdown()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Workflow Dashboard Server')
    parser.add_argument('--port', type=int, default=8089, help='Port to run on')
    parser.add_argument('--no-browser', action='store_true', help="Don't open browser")
    
    args = parser.parse_args()
    
    if args.no_browser:
        # Run without opening browser
        sys.path.insert(0, str(Path(__file__).parent))
        from workflow_manager import WorkflowManager
        
        wm = WorkflowManager()
        
        def handler(*args, **kwargs):
            return WorkflowHandler(*args, workflow_manager=wm, **kwargs)
        
        server = HTTPServer(('0.0.0.0', args.port), handler)
        
        print(f"\n{'='*70}")
        print(f"🚀 Workflow Dashboard Server")
        print(f"{'='*70}")
        print(f"🌐 URL: http://localhost:{args.port}")
        print(f"🌐 API: http://localhost:{args.port}/api/status")
        print(f"{'='*70}\n")
        
        try:
            print(f"📡 Server running on port {args.port}...")
            print(f"Press Ctrl+C to stop\n")
            server.serve_forever()
        except KeyboardInterrupt:
            print(f"\n👋 Server stopped")
            server.shutdown()
    else:
        run_server(args.port)


if __name__ == "__main__":
    main()
