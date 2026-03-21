import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-VERSION-001 Version Manager
"""

import json, sys, subprocess
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

VERSION_FILE = Path("13-memory/.workflow_version.json")

class WorkflowVersion:
    def __init__(self):
        if not VERSION_FILE.exists():
            VERSION_FILE.write_text(json.dumps({"version": "1.0.0", "history": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _load(self):
        return json.loads(VERSION_FILE.read_text(encoding="utf-8", errors="replace"))
    
    def _save(self, data):
        VERSION_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def bump(self, part="patch"):
        data = self._load()
        parts = data["version"].split(".")
        
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        else:
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        data["version"] = new_version
        data["history"].append({
            "version": new_version,
            "time": datetime.now().isoformat()
        })
        
        self._save(data)
        return {"status": "bumped", "old": data["version"], "new": new_version}
    
    def current(self):
        data = self._load()
        return {"version": data["version"]}

if __name__ == "__main__":
    version = WorkflowVersion()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--bump":
            part = sys.argv[2] if len(sys.argv) > 2 else "patch"
            print(json.dumps(version.bump(part), ensure_ascii=False, indent=2))
        elif cmd == "--current":
            print(json.dumps(version.current(), ensure_ascii=False, indent=2))
    else:
        print("Usage: workflow_version_001.py --bump [major|minor|patch] | --current")
