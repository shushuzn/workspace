import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-MONITOR-001 Real-time Workflow Monitor
"""

import json, sys, time, re
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class WorkflowMonitor:
    def __init__(self):
        self.tools_dir = Path("30-scripts-tools")
        self.log_dir = Path("13-memory/.workflow_logs")
    
    def health_check(self):
        checks = []
        
        # Check tools directory
        tools = list(self.tools_dir.glob("*_001.py"))
        checks.append({"check": "tools_dir", "status": "ok" if len(tools) > 100 else "warning", "value": len(tools)})
        
        # Check naming convention
        naming_violations = sum(1 for f in tools if not re.match(r'^[a-z][a-z0-9_]*_\d+\.py$', str(f.name)))
        checks.append({"check": "naming_convention", "status": "ok" if naming_violations == 0 else "warning", "violations": naming_violations})
        
        # Check logs
        log_file = self.log_dir / "master.json"
        if log_file.exists():
            log = json.loads(log_file.read_text(encoding="utf-8", errors="replace"))
            runs = log.get("runs", [])
            recent = [r for r in runs if "T" in str(r.get("time", ""))]
            checks.append({"check": "execution_log", "status": "ok", "recent_runs": len(recent)})
        else:
            checks.append({"check": "execution_log", "status": "warning", "value": "no logs"})
        
        # Overall status
        warnings = sum(1 for c in checks if c.get("status") == "warning")
        overall = "healthy" if warnings == 0 else "degraded"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall": overall,
            "checks": checks
        }
    
    def dashboard(self):
        health = self.health_check()
        
        print("=" * 50)
        print("WORKFLOW MONITOR")
        print("=" * 50)
        print(f"Status: {health['overall'].upper()}")
        print(f"Time: {health['timestamp']}")
        print()
        
        for check in health["checks"]:
            icon = "OK" if check["status"] == "ok" else "!"
            value = check.get("value", check.get("violations", check.get("recent_runs", "")))
            print(f"[{icon}] {check['check']}: {value}")
        
        print("=" * 50)

if __name__ == "__main__":
    monitor = WorkflowMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(monitor.health_check(), ensure_ascii=False, indent=2))
    else:
        monitor.dashboard()
