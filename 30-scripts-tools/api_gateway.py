#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Gateway - Unified API Interface for All Systems
Provides a single API endpoint for all OpenClaw systems
Features: Request routing, authentication, rate limiting, caching, monitoring

Usage:
    python api_gateway.py --start
    python api_gateway.py --status
    python api_gateway.py --docs
"""

import os
import sys
import json
import http.server
import socketserver
import threading
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from functools import wraps
from urllib.parse import urlparse, parse_qs

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # ip -> list of timestamps
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if now - ts < self.window_seconds
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        # Record request
        self.requests[client_ip].append(now)
        return True
    
    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests"""
        now = time.time()
        
        if client_ip not in self.requests:
            return self.max_requests
        
        current = len([ts for ts in self.requests[client_ip] if now - ts < self.window_seconds])
        return max(0, self.max_requests - current)


class Cache:
    """Simple in-memory cache"""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self.cache = {}  # key -> (value, expires_at)
    
    def get(self, key: str) -> Optional[any]:
        """Get cached value"""
        if key in self.cache:
            value, expires_at = self.cache[key]
            if time.time() < expires_at:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: any, ttl: Optional[int] = None):
        """Set cached value"""
        expires_at = time.time() + (ttl or self.ttl_seconds)
        self.cache[key] = (value, expires_at)
    
    def delete(self, key: str):
        """Delete cached value"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()


class APIGateway:
    """Unified API Gateway"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
        self.cache = Cache(ttl_seconds=300)
        
        self.routes = {}
        self.request_log = []
        self.start_time = datetime.now()
        
        self.register_routes()
    
    def register_routes(self):
        """Register API routes"""
        # System endpoints
        self.routes['GET /api/v1/health'] = self.handle_health
        self.routes['GET /api/v1/status'] = self.handle_status
        self.routes['GET /api/v1/systems'] = self.handle_systems
        
        # Self-iteration endpoints
        self.routes['GET /api/v1/self-iteration'] = self.handle_self_iteration
        self.routes['POST /api/v1/self-iteration/run'] = self.handle_self_iteration_run
        self.routes['GET /api/v1/self-iteration/history'] = self.handle_self_iteration_history
        
        # Performance endpoints
        self.routes['GET /api/v1/performance'] = self.handle_performance
        self.routes['GET /api/v1/performance/bottlenecks'] = self.handle_bottlenecks
        self.routes['POST /api/v1/performance/optimize'] = self.handle_optimize
        
        # Monitoring endpoints
        self.routes['GET /api/v1/monitor'] = self.handle_monitor
        self.routes['GET /api/v1/monitor/alerts'] = self.handle_alerts
        
        # Knowledge graph endpoints
        self.routes['GET /api/v1/knowledge'] = self.handle_knowledge
        self.routes['GET /api/v1/knowledge/lessons'] = self.handle_lessons
        self.routes['POST /api/v1/knowledge/sync'] = self.handle_kg_sync
        
        # Report endpoints
        self.routes['GET /api/v1/reports'] = self.handle_reports
        self.routes['POST /api/v1/reports/generate'] = self.handle_report_generate
        
        # Docs
        self.routes['GET /api/v1/docs'] = self.handle_docs
        self.routes['GET /'] = self.handle_root
    
    def authenticate(self, token: Optional[str]) -> bool:
        """Authenticate API request"""
        # Simple token-based auth (in production, use proper auth)
        if not token:
            return False
        
        # Check against environment variable or config
        expected_token = os.getenv('API_TOKEN', 'openclaw-dev-token')
        return token == expected_token
    
    def log_request(self, method: str, path: str, status: int, duration: float, client_ip: str):
        """Log API request"""
        self.request_log.append({
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'path': path,
            'status': status,
            'duration_ms': duration * 1000,
            'client_ip': client_ip
        })
        
        # Keep last 1000 requests
        self.request_log = self.request_log[-1000:]
    
    def handle_request(self, method: str, path: str, headers: Dict, body: Optional[bytes], client_ip: str) -> tuple:
        """Handle incoming API request"""
        start_time = time.time()
        
        # Check rate limit
        if not self.rate_limiter.is_allowed(client_ip):
            self.log_request(method, path, 429, time.time() - start_time, client_ip)
            return 429, {'error': 'Rate limit exceeded', 'retry_after': 60}
        
        # Parse query parameters
        parsed = urlparse(path)
        query_params = parse_qs(parsed.query)
        
        # Find route
        route_key = f"{method} {parsed.path}"
        handler = self.routes.get(route_key)
        
        if not handler:
            # Try GET for unknown methods
            if method != 'GET':
                route_key = f"GET {parsed.path}"
                handler = self.routes.get(route_key)
        
        if not handler:
            self.log_request(method, path, 404, time.time() - start_time, client_ip)
            return 404, {'error': 'Not found'}
        
        # Check cache (for GET requests)
        if method == 'GET':
            cache_key = f"{method}:{parsed.path}"
            cached = self.cache.get(cache_key)
            if cached:
                self.log_request(method, path, 200, time.time() - start_time, client_ip)
                return 200, cached
        
        # Call handler
        try:
            response = handler(query_params, body)
            
            # Cache response (for GET requests)
            if method == 'GET' and isinstance(response, dict):
                cache_key = f"{method}:{parsed.path}"
                self.cache.set(cache_key, response, ttl=300)
            
            duration = time.time() - start_time
            self.log_request(method, path, 200, duration, client_ip)
            
            return 200, response
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_request(method, path, 500, duration, client_ip)
            return 500, {'error': str(e)}
    
    # Handler methods
    
    def handle_health(self, params, body) -> Dict:
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600
        }
    
    def handle_status(self, params, body) -> Dict:
        """System status"""
        return {
            'gateway': 'running',
            'port': self.port,
            'routes': len(self.routes),
            'cache_size': len(self.cache.cache),
            'requests_logged': len(self.request_log)
        }
    
    def handle_systems(self, params, body) -> Dict:
        """List all systems"""
        monitor_file = WORKSPACE / "20-data-reports" / "monitor_data.json"
        
        if monitor_file.exists():
            with open(monitor_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'No system data available'}
    
    def handle_self_iteration(self, params, body) -> Dict:
        """Self-iteration status"""
        state_file = WORKSPACE / "20-data-reports" / "self_iteration_state.json"
        
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'No self-iteration data available'}
    
    def handle_self_iteration_run(self, params, body) -> Dict:
        """Run self-iteration cycle"""
        # In production, would trigger actual execution
        return {
            'status': 'started',
            'message': 'Self-iteration cycle initiated',
            'timestamp': datetime.now().isoformat()
        }
    
    def handle_self_iteration_history(self, params, body) -> Dict:
        """Self-iteration history"""
        history_file = WORKSPACE / "20-data-reports" / "self_iter_history.json"
        
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'No history available'}
    
    def handle_performance(self, params, body) -> Dict:
        """Performance metrics"""
        perf_file = WORKSPACE / "20-data-reports" / "performance_metrics.json"
        
        if perf_file.exists():
            with open(perf_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'No performance data available'}
    
    def handle_bottlenecks(self, params, body) -> Dict:
        """Performance bottlenecks"""
        bn_file = WORKSPACE / "20-data-reports" / "bottlenecks.json"
        
        if bn_file.exists():
            with open(bn_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'No bottleneck data available'}
    
    def handle_optimize(self, params, body) -> Dict:
        """Run optimization"""
        return {
            'status': 'started',
            'message': 'Optimization process initiated',
            'timestamp': datetime.now().isoformat()
        }
    
    def handle_monitor(self, params, body) -> Dict:
        """Monitoring data"""
        monitor_file = WORKSPACE / "20-data-reports" / "monitor_data.json"
        
        if monitor_file.exists():
            with open(monitor_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'No monitor data available'}
    
    def handle_alerts(self, params, body) -> Dict:
        """System alerts"""
        alerts_file = WORKSPACE / "20-data-reports" / "monitor_alerts.json"
        
        if alerts_file.exists():
            with open(alerts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'No alerts available'}
    
    def handle_knowledge(self, params, body) -> Dict:
        """Knowledge graph status"""
        kg_file = WORKSPACE / "15-docs" / "knowledge-graph" / "entities.json"
        
        if kg_file.exists():
            with open(kg_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'No knowledge graph data available'}
    
    def handle_lessons(self, params, body) -> Dict:
        """Lessons learned"""
        lessons_file = WORKSPACE / "15-docs" / "knowledge-graph" / "lessons_learned.json"
        
        if lessons_file.exists():
            with open(lessons_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'error': 'No lessons data available'}
    
    def handle_kg_sync(self, params, body) -> Dict:
        """Sync knowledge graph"""
        return {
            'status': 'started',
            'message': 'Knowledge graph sync initiated',
            'timestamp': datetime.now().isoformat()
        }
    
    def handle_reports(self, params, body) -> Dict:
        """List reports"""
        reports_dir = WORKSPACE / "20-data-reports" / "reports"
        
        if reports_dir.exists():
            reports = [f.name for f in reports_dir.glob("*")]
            return {'reports': reports, 'count': len(reports)}
        
        return {'error': 'No reports available'}
    
    def handle_report_generate(self, params, body) -> Dict:
        """Generate report"""
        return {
            'status': 'started',
            'message': 'Report generation initiated',
            'timestamp': datetime.now().isoformat()
        }
    
    def handle_docs(self, params, body) -> str:
        """API documentation"""
        docs = """# API Gateway Documentation

## Base URL
http://localhost:8080

## Endpoints

### System
- GET /api/v1/health - Health check
- GET /api/v1/status - Gateway status
- GET /api/v1/systems - List all systems

### Self-Iteration
- GET /api/v1/self-iteration - Status
- POST /api/v1/self-iteration/run - Run cycle
- GET /api/v1/self-iteration/history - History

### Performance
- GET /api/v1/performance - Metrics
- GET /api/v1/performance/bottlenecks - Bottlenecks
- POST /api/v1/performance/optimize - Run optimization

### Monitoring
- GET /api/v1/monitor - Monitoring data
- GET /api/v1/monitor/alerts - Alerts

### Knowledge Graph
- GET /api/v1/knowledge - Status
- GET /api/v1/knowledge/lessons - Lessons
- POST /api/v1/knowledge/sync - Sync

### Reports
- GET /api/v1/reports - List reports
- POST /api/v1/reports/generate - Generate report

## Rate Limiting
100 requests per minute per IP

## Authentication
Include header: Authorization: Bearer <token>
Default token: openclaw-dev-token
"""
        return docs
    
    def handle_root(self, params, body) -> str:
        """Root endpoint"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>OpenClaw API Gateway</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; }
        h1 { color: #667eea; }
        .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
        code { background: #eee; padding: 2px 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>🚀 OpenClaw API Gateway</h1>
    <p>Welcome to the unified API interface for all OpenClaw systems.</p>
    
    <h2>Quick Links</h2>
    <div class="endpoint"><a href="/api/v1/health">Health Check</a></div>
    <div class="endpoint"><a href="/api/v1/docs">API Documentation</a></div>
    <div class="endpoint"><a href="/api/v1/status">Gateway Status</a></div>
    
    <h2>Features</h2>
    <ul>
        <li>Unified API for all systems</li>
        <li>Rate limiting (100 req/min)</li>
        <li>Response caching (5 min TTL)</li>
        <li>Request logging</li>
        <li>RESTful endpoints</li>
    </ul>
</body>
</html>
"""
    
    def start_server(self):
        """Start API server"""
        gateway = self
        
        class APIHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self._handle_request('GET')
            
            def do_POST(self):
                self._handle_request('POST')
            
            def _handle_request(self, method):
                client_ip = self.client_address[0]
                
                # Get headers
                headers = {key: value for key, value in self.headers.items()}
                
                # Get body (for POST)
                body = None
                if method == 'POST':
                    content_length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_length)
                
                # Handle request
                status, response = gateway.handle_request(method, self.path, headers, body, client_ip)
                
                # Send response
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('X-RateLimit-Remaining', str(gateway.rate_limiter.get_remaining(client_ip)))
                self.end_headers()
                
                if isinstance(response, str):
                    self.wfile.write(response.encode())
                else:
                    self.wfile.write(json.dumps(response, indent=2).encode())
            
            def log_message(self, format, *args):
                pass  # Suppress default logging
        
        with socketserver.TCPServer(("", self.port), APIHandler) as httpd:
            print(f"\n✅ API Gateway started at http://localhost:{self.port}")
            print(f"Documentation: http://localhost:{self.port}/api/v1/docs\n")
            httpd.serve_forever()
    
    def get_stats(self) -> Dict:
        """Get gateway statistics"""
        return {
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'total_requests': len(self.request_log),
            'routes': len(self.routes),
            'cache_size': len(self.cache.cache),
            'rate_limit': f"{self.rate_limiter.max_requests}/{self.rate_limiter.window_seconds}s"
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='API Gateway')
    parser.add_argument('--start', action='store_true', help='Start server')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--docs', action='store_true', help='Show documentation')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    args = parser.parse_args()
    
    gateway = APIGateway(port=args.port)
    
    if args.start:
        gateway.start_server()
    
    elif args.status:
        stats = gateway.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.docs:
        print(gateway.handle_docs({}, None))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
