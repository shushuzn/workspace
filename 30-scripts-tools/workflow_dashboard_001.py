#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-DASHBOARD-001 Workflow Visual Dashboard
"""

import json, sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS = {
    "workflow_market": {"name": "Template Market", "steps": 4, "status": "ok"},
    "nl_workflow": {"name": "NL Generator", "steps": 3, "status": "ok"},
    "workflow_scheduler": {"name": "Scheduler", "steps": 2, "status": "ok"}
}

class Dashboard:
    def __init__(self):
        self.tools = TOOLS
    
    def status(self):
        total = len(self.tools)
        ok = sum(1 for t in self.tools.values() if t["status"] == "ok")
        return {"total": total, "ok": ok, "failed": total - ok}
    
    def render(self):
        s = self.status()
        print("=" * 50)
        print("WORKFLOW DASHBOARD")
        print("=" * 50)
        print(f"Status: {s['ok']}/{s['total']} tools OK")
        print()
        for id, tool in self.tools.items():
            icon = "OK" if tool["status"] == "ok" else "FAIL"
            print(f"[{icon}] {tool['name']} ({tool['steps']} steps)")
        print("=" * 50)

if __name__ == "__main__":
    d = Dashboard()
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(d.status(), ensure_ascii=False, indent=2))
    else:
        d.render()
