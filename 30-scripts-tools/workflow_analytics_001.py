#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-ANALYTICS-001 Usage Analytics
"""

import json, sys
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LOGS_DIR = Path("13-memory/.workflow_logs")

class WorkflowAnalytics:
    def analyze(self):
        log_file = LOGS_DIR / "master.json"
        if not log_file.exists():
            return {"error": "No logs found"}
        
        log = json.loads(log_file.read_text(encoding="utf-8", errors="replace"))
        runs = log.get("runs", [])
        
        # Tool usage frequency
        tool_usage = {}
        for run in runs:
            tool = run.get("workflow", "unknown")
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        # Success rate by tool
        tool_success = {}
        for run in runs:
            tool = run.get("workflow", "unknown")
            if tool not in tool_success:
                tool_success[tool] = {"ok": 0, "fail": 0}
            tool_success[tool][run.get("status", "ok")] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_runs": len(runs),
                "tools_used": len(tool_usage),
                "avg_per_tool": len(runs) / len(tool_usage) if tool_usage else 0
            },
            "tool_usage": tool_usage,
            "success_rate": {k: f"{(v['ok']/(v['ok']+v['fail'])*100):.0f}%" for k, v in tool_success.items()}
        }

if __name__ == "__main__":
    analytics = WorkflowAnalytics()
    print(json.dumps(analytics.analyze(), ensure_ascii=False, indent=2))
