#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Persona Collaboration API Service
RESTful API for persona collaboration system
Features: HTTP server, REST endpoints, async execution, JSON responses

Usage:
    python persona_api.py --serve
    python persona_api.py --serve --port 8084
"""

import os
import sys
import json
import argparse
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

# Workspace root
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / "00-人格系统"))

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


class PersonaAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Persona API"""

    def __init__(self, *args, engine=None, orchestrator=None, analyzer=None, **kwargs):
        self.engine = engine
        self.orchestrator = orchestrator
        self.analyzer = analyzer
        super().__init__(*args, **kwargs)

    def _send_json(self, data: Dict, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, message: str, status: int = 400):
        """Send error response"""
        self._send_json({"error": message}, status)

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Health check
        if path == "/health":
            self._send_json(
                {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "service": "persona-api",
                }
            )

        # Get persona state
        elif path == "/api/v1/personas":
            state = self.engine.get_state() if self.engine else {}
            self._send_json(state)

        # Get specific persona
        elif path.startswith("/api/v1/personas/"):
            persona_name = path.split("/")[-1]
            state = self.engine.get_state() if self.engine else {}
            personas = state.get("personas", {})
            if persona_name in personas:
                self._send_json(personas[persona_name])
            else:
                self._send_error(f"Persona not found: {persona_name}", 404)

        # Get collaboration scores
        elif path == "/api/v1/scores":
            scores = self.engine.get_collaboration_score() if self.engine else {}
            self._send_json(scores)

        # Get conflicts
        elif path == "/api/v1/conflicts":
            state = self.engine.get_state() if self.engine else {}
            conflicts = state.get("conflicts", [])
            self._send_json({"conflicts": conflicts})

        # Get messages
        elif path == "/api/v1/messages":
            state = self.engine.get_state() if self.engine else {}
            messages = state.get("messages", [])
            self._send_json({"messages": messages})

        # Get orchestrator status
        elif path == "/api/v1/orchestrator":
            if self.orchestrator:
                status = self.orchestrator.get_status()
                self._send_json(status)
            else:
                self._send_error("Orchestrator not available", 503)

        # Get analysis
        elif path == "/api/v1/analysis":
            if self.analyzer:
                patterns = self.analyzer.analyze_patterns()
                self._send_json(patterns)
            else:
                self._send_error("Analyzer not available", 503)

        # Get bottlenecks
        elif path == "/api/v1/bottlenecks":
            if self.analyzer:
                bottlenecks = self.analyzer.detect_bottlenecks()
                self._send_json({"bottlenecks": bottlenecks})
            else:
                self._send_error("Analyzer not available", 503)

        # Get recommendations
        elif path == "/api/v1/recommendations":
            if self.analyzer:
                recs = self.analyzer.generate_recommendations()
                self._send_json({"recommendations": recs})
            else:
                self._send_error("Analyzer not available", 503)

        # Get health report
        elif path == "/api/v1/report":
            if self.analyzer:
                report = self.analyzer.generate_report(save=False)
                self._send_json({"report": report})
            else:
                self._send_error("Analyzer not available", 503)

        # API documentation
        elif path == "/api" or path == "/":
            docs = {
                "service": "Persona Collaboration API",
                "version": "1.0",
                "endpoints": {
                    "GET /health": "Health check",
                    "GET /api/v1/personas": "Get all persona states",
                    "GET /api/v1/personas/<name>": "Get specific persona state",
                    "GET /api/v1/scores": "Get collaboration scores",
                    "GET /api/v1/conflicts": "Get all conflicts",
                    "GET /api/v1/messages": "Get message history",
                    "GET /api/v1/orchestrator": "Get orchestrator status",
                    "GET /api/v1/analysis": "Get pattern analysis",
                    "GET /api/v1/bottlenecks": "Get detected bottlenecks",
                    "GET /api/v1/recommendations": "Get optimization recommendations",
                    "GET /api/v1/report": "Get full analysis report",
                    "POST /api/v1/run": "Run collaboration workflow",
                    "POST /api/v1/schedule": "Schedule task",
                    "POST /api/v1/message": "Send inter-persona message",
                },
            }
            self._send_json(docs)

        else:
            self._send_error("Not found", 404)

    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = {}
        if content_length > 0:
            try:
                body = json.loads(self.rfile.read(content_length).decode("utf-8"))
            except:
                pass

        # Run collaboration workflow
        if path == "/api/v1/run":
            if not self.engine:
                self._send_error("Engine not available", 503)
                return

            task = body.get("task", "Default task")

            try:
                result = self.engine.run_collaboration_workflow(task)
                self._send_json(result)
            except Exception as e:
                self._send_error(str(e), 500)

        # Schedule task
        elif path == "/api/v1/schedule":
            if not self.orchestrator:
                self._send_error("Orchestrator not available", 503)
                return

            description = body.get("description", "Scheduled task")
            priority = body.get("priority", 2)
            delay = body.get("delay_minutes", 0)

            try:
                task_id = self.orchestrator.schedule_task(description, priority, delay)
                self._send_json({"task_id": task_id, "scheduled": True})
            except Exception as e:
                self._send_error(str(e), 500)

        # Send message
        elif path == "/api/v1/message":
            if not self.engine:
                self._send_error("Engine not available", 503)
                return

            from persona_collaboration import PersonaRole, MessagePriority

            sender = body.get("sender")
            receiver = body.get("receiver")
            content = body.get("content")
            priority = body.get("priority", "NORMAL")

            if not all([sender, receiver, content]):
                self._send_error(
                    "Missing required fields: sender, receiver, content", 400
                )
                return

            try:
                sender_role = PersonaRole[sender.upper()]
                receiver_role = PersonaRole[receiver.upper()]
                priority_level = MessagePriority[priority.upper()]

                msg = self.engine.send_message(
                    sender_role, receiver_role, content, priority_level
                )
                self._send_json({"message_id": msg.id, "sent": True})
            except Exception as e:
                self._send_error(str(e), 400)

        else:
            self._send_error("Not found", 404)

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class PersonaAPIServer:
    """API Server wrapper"""

    def __init__(self, port: int = 8084):
        self.port = port
        self.engine = None
        self.orchestrator = None
        self.analyzer = None
        self.server = None

    def initialize(self):
        """Initialize components"""
        print("[API] Initializing components...")

        try:
            from persona_collaboration import PersonaCollaborationEngine

            self.engine = PersonaCollaborationEngine()
            print("  ✅ Engine loaded")
        except Exception as e:
            print(f"  ⚠️  Engine failed: {e}")

        try:
            from persona_orchestrator import PersonaOrchestrator

            self.orchestrator = PersonaOrchestrator()
            print("  ✅ Orchestrator loaded")
        except Exception as e:
            print(f"  ⚠️  Orchestrator failed: {e}")

        try:
            from persona_analyzer import PersonaAnalyzer

            self.analyzer = PersonaAnalyzer()
            print("  ✅ Analyzer loaded")
        except Exception as e:
            print(f"  ⚠️  Analyzer failed: {e}")

    def start(self):
        """Start API server"""
        self.initialize()

        def handler(*args, **kwargs):
            PersonaAPIHandler(
                *args,
                engine=self.engine,
                orchestrator=self.orchestrator,
                analyzer=self.analyzer,
                **kwargs,
            )

        self.server = HTTPServer(("0.0.0.0", self.port), handler)

        print(f"\n{'=' * 60}")
        print(f"Persona Collaboration API Server")
        print(f"{'=' * 60}")
        print(f"URL: http://localhost:{self.port}")
        print(f"Docs: http://localhost:{self.port}/api")
        print(f"Health: http://localhost:{self.port}/health")
        print(f"Press Ctrl+C to stop\n")

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n[API] Stopped")
            self.server.shutdown()


def main():
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        return
    print("[OK] Critic Review Passed")

    parser = argparse.ArgumentParser(description="Persona Collaboration API")
    parser.add_argument("--serve", action="store_true", help="Start API server")
    parser.add_argument("--port", type=int, default=8084, help="Server port")
    args = parser.parse_args()

    if args.serve:
        server = PersonaAPIServer(args.port)
        server.start()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
