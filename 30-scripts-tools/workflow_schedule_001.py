import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-SCHEDULE-001 Scheduled Workflow Runner
"""

import json, sys, time
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SCHEDULE_FILE = Path("13-memory/.workflow_schedule.json")

class WorkflowSchedule:
    def __init__(self):
        if not SCHEDULE_FILE.exists():
            SCHEDULE_FILE.write_text(json.dumps({"schedules": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _load(self):
        return json.loads(SCHEDULE_FILE.read_text(encoding="utf-8", errors="replace"))
    
    def _save(self, data):
        SCHEDULE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def add(self, workflow, interval_minutes=60):
        data = self._load()
        data["schedules"].append({
            "workflow": workflow,
            "interval": interval_minutes,
            "added": datetime.now().isoformat(),
            "last_run": None
        })
        self._save(data)
        return {"status": "added", "workflow": workflow}
    
    def list(self):
        return self._load()["schedules"]

if __name__ == "__main__":
    schedule = WorkflowSchedule()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--add":
            wf = sys.argv[2] if len(sys.argv) > 2 else "dev"
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 60
            print(json.dumps(schedule.add(wf, interval), ensure_ascii=False, indent=2))
        elif cmd == "--list":
            print(json.dumps(schedule.list(), ensure_ascii=False, indent=2))
    else:
        print("Usage: workflow_schedule_001.py --add <workflow> [interval_minutes] | --list")
