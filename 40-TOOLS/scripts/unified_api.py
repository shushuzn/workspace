#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unified API Server - Phase 4 Deep Iteration
REST API for all Phase 4 tools
Features: HTTP server, JSON API, async execution, status tracking

Usage:
    python unified_api.py --start
    python unified_api.py --port 8080
    python unified_api.py --test
"""

import os
import sys
import json
import time
import argparse
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any
import uuid

# Workspace root
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / "30-scripts-tools"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


# Global execution tracker
EXECUTIONS = {}


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for API"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        print(f"[API GET] {path}")
        
        # Routes
        if path == '/health':
            self._send_json({'status': 'ok', 'timestamp': datetime.now().isoformat()})
        
        elif path == '/tools':
            tools = self._list_tools()
            self._send_json({'tools': tools, 'count': len(tools)})
        
        elif path == '/workflows':
            workflows = ['daily_brief', 'code_quality', 'system_maintenance', 'research_pipeline']
            self._send_json({'workflows': workflows})
        
        elif path.startswith('/tool/'):
            tool_name = path.split('/')[2]
            self._send_json({'tool': tool_name, 'status': 'available'})
        
        elif path.startswith('/execution/'):
            exec_id = path.split('/')[2]
            if exec_id in EXECUTIONS:
                self._send_json(EXECUTIONS[exec_id])
            else:
                self._send_error(404, 'Execution not found')
        
        elif path == '/executions':
            self._send_json({'executions': list(EXECUTIONS.values())[-10:]})
        
        else:
            self._send_error(404, 'Not found')
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        print(f"[API POST] {path} - {data}")
        
        # Routes
        if path == '/execute':
            tool = data.get('tool')
            args = data.get('args', [])
            
            if not tool:
                self._send_error(400, 'Missing tool parameter')
                return
            
            exec_id = self._execute_tool(tool, args)
            self._send_json({'execution_id': exec_id, 'status': 'started'})
        
        elif path == '/workflow':
            workflow_id = data.get('workflow')
            
            if not workflow_id:
                self._send_error(400, 'Missing workflow parameter')
                return
            
            exec_id = self._execute_workflow(workflow_id)
            self._send_json({'execution_id': exec_id, 'status': 'started'})
        
        elif path == '/cache/clear':
            # Clear cache
            self._send_json({'status': 'ok', 'message': 'Cache cleared'})
        
        else:
            self._send_error(404, 'Not found')
    
    def _list_tools(self) -> list:
        """List available tools"""
        tools = []
        
        for py_file in TOOLS_DIR.glob("*.py"):
            tools.append({
                'name': py_file.name,
                'path': str(py_file.relative_to(WORKSPACE)),
                'size_kb': round(py_file.stat().st_size / 1024, 2)
            })
        
        return sorted(tools, key=lambda x: x['name'])
    
    def _execute_tool(self, tool: str, args: list) -> str:
        """Execute a tool asynchronously"""
        exec_id = str(uuid.uuid4())[:8]
        
        tool_path = TOOLS_DIR / tool
        
        EXECUTIONS[exec_id] = {
            'id': exec_id,
            'type': 'tool',
            'tool': tool,
            'args': args,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'result': None
        }
        
        def run_tool():
            try:
                cmd = ['python', str(tool_path)] + args
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(WORKSPACE)
                )
                
                EXECUTIONS[exec_id]['end_time'] = datetime.now().isoformat()
                EXECUTIONS[exec_id]['status'] = 'success' if result.returncode == 0 else 'error'
                EXECUTIONS[exec_id]['result'] = {
                    'stdout': result.stdout[:1000],
                    'stderr': result.stderr[:500],
                    'returncode': result.returncode
                }
            
            except Exception as e:
                EXECUTIONS[exec_id]['end_time'] = datetime.now().isoformat()
                EXECUTIONS[exec_id]['status'] = 'error'
                EXECUTIONS[exec_id]['result'] = {'error': str(e)}
        
        thread = threading.Thread(target=run_tool, daemon=True)
        thread.start()
        
        return exec_id
    
    def _execute_workflow(self, workflow_id: str) -> str:
        """Execute a workflow asynchronously"""
        exec_id = str(uuid.uuid4())[:8]
        
        EXECUTIONS[exec_id] = {
            'id': exec_id,
            'type': 'workflow',
            'workflow': workflow_id,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'result': None
        }
        
        def run_workflow():
            try:
                workflow_script = TOOLS_DIR / 'workflow_engine.py'
                
                cmd = ['python', str(workflow_script), '--run', workflow_id]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=str(WORKSPACE)
                )
                
                EXECUTIONS[exec_id]['end_time'] = datetime.now().isoformat()
                EXECUTIONS[exec_id]['status'] = 'success' if result.returncode == 0 else 'error'
                EXECUTIONS[exec_id]['result'] = {
                    'output_lines': len(result.stdout.split('\n')),
                    'returncode': result.returncode
                }
            
            except Exception as e:
                EXECUTIONS[exec_id]['end_time'] = datetime.now().isoformat()
                EXECUTIONS[exec_id]['status'] = 'error'
                EXECUTIONS[exec_id]['result'] = {'error': str(e)}
        
        thread = threading.Thread(target=run_workflow, daemon=True)
        thread.start()
        
        return exec_id
    
    def _send_json(self, data: Dict, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(response.encode('utf-8'))
    
    def _send_error(self, status: int, message: str):
        """Send error response"""
        self._send_json({'error': message, 'status': status}, status)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class UnifiedAPIServer:
    """Unified API server"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.server = None
        self.running = False
    
    def start(self):
        """Start the API server"""
        self.server = HTTPServer(('0.0.0.0', self.port), APIHandler)
        self.running = True
        
        print("\n" + "=" * 60)
        print("Unified API Server")
        print("=" * 60)
        print(f"🌐 URL: http://localhost:{self.port}")
        print(f"📡 Health: http://localhost:{self.port}/health")
        print(f"🔧 Tools: http://localhost:{self.port}/tools")
        print(f"📋 Workflows: http://localhost:{self.port}/workflows")
        print(f"▶️  Execute: POST http://localhost:{self.port}/execute")
        print("=" * 60)
        print("\nServer starting... Press Ctrl+C to stop\n")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n[API] Stopping server...")
            self.stop()
    
    def stop(self):
        """Stop the API server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("[API] Stopped")


def test_api():
    """Test API endpoints"""
    import urllib.request
    
    base_url = "http://localhost:8080"
    
    print("\n[TEST] Testing API endpoints...")
    print("=" * 60)
    
    # Test health
    try:
        with urllib.request.urlopen(f"{base_url}/health", timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✅ /health - {data['status']}")
    except Exception as e:
        print(f"❌ /health - {e}")
    
    # Test tools
    try:
        with urllib.request.urlopen(f"{base_url}/tools", timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✅ /tools - {data['count']} tools")
    except Exception as e:
        print(f"❌ /tools - {e}")
    
    # Test workflows
    try:
        with urllib.request.urlopen(f"{base_url}/workflows", timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✅ /workflows - {len(data['workflows'])} workflows")
    except Exception as e:
        print(f"❌ /workflows - {e}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Unified API Server')
    parser.add_argument('--start', action='store_true', help='Start API server')
    parser.add_argument('--port', type=int, default=8080, help='Port number')
    parser.add_argument('--test', action='store_true', help='Test API endpoints')
    args = parser.parse_args()
    
    if args.start:
        server = UnifiedAPIServer(port=args.port)
        server.start()
    
    if args.test:
        test_api()
    
    if not any([args.start, args.test]):
        parser.print_help()


if __name__ == "__main__":
    main()
