#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-LOGGER-001 Workflow Execution Logger
"""

import json, sys
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LOG_DIR = Path("13-memory/.workflow_logs")
LOG_FILE = LOG_DIR / "executions.json"

class WorkflowLogger:
    def __init__(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if not LOG_FILE.exists():
            self._save({"logs": []})
    
    def _load(self):
        return json.loads(LOG_FILE.read_text(encoding="utf-8", errors="replace"))
    
    def _save(self, data):
        LOG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def log(self, workflow, step, status="start", detail=""):
        data = self._load()
        data["logs"].append({
            "time": datetime.now().isoformat(),
            "workflow": workflow,
            "step": step,
            "status": status,
            "detail": detail
        })
        if len(data["logs"]) > 500:
            data["logs"] = data["logs"][-200:]
        self._save(data)
        return {"ok": True}
    
    def list(self, limit=20):
        logs = self._load()["logs"]
        return logs[-limit:]
    
    def stats(self):
        logs = self._load()["logs"]
        return {
            "total": len(logs),
            "by_status": {s: sum(1 for l in logs if l.get("status") == s) for s in ["start", "ok", "fail"]}
        }

if __name__ == "__main__":
    logger = WorkflowLogger()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--log":
            wf = sys.argv[2] if len(sys.argv) > 2 else "unknown"
            step = sys.argv[3] if len(sys.argv) > 3 else "0"
            status = sys.argv[4] if len(sys.argv) > 4 else "start"
            print(json.dumps(logger.log(wf, step, status), ensure_ascii=False, indent=2))
        elif cmd == "--list":
            print(json.dumps(logger.list(), ensure_ascii=False, indent=2))
        elif cmd == "--stats":
            print(json.dumps(logger.stats(), ensure_ascii=False, indent=2))
    else:
        print("Usage:")
        print("  --log <workflow> <step> [status]")
        print("  --list")
        print("  --stats")
