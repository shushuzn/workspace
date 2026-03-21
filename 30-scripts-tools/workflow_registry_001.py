import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-REGISTRY-001 Tool Registry
"""

import json, sys
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REGISTRY_FILE = Path("13-memory/.workflow_registry.json")

class WorkflowRegistry:
    def __init__(self):
        if not REGISTRY_FILE.exists():
            REGISTRY_FILE.write_text(json.dumps({"tools": {}}, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _load(self):
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8", errors="replace"))
    
    def _save(self, data):
        REGISTRY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def register(self, tool_name, category="general", description=""):
        data = self._load()
        data["tools"][tool_name] = {
            "registered": datetime.now().isoformat(),
            "category": category,
            "description": description
        }
        self._save(data)
        return {"status": "registered", "tool": tool_name}
    
    def list(self, category=None):
        data = self._load()
        tools = data.get("tools", {})
        if category:
            tools = {k: v for k, v in tools.items() if v.get("category") == category}
        return {"count": len(tools), "tools": tools}

if __name__ == "__main__":
    registry = WorkflowRegistry()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--register":
            name = sys.argv[2] if len(sys.argv) > 2 else "tool"
            cat = sys.argv[3] if len(sys.argv) > 3 else "general"
            print(json.dumps(registry.register(name, cat), ensure_ascii=False, indent=2))
        elif cmd == "--list":
            print(json.dumps(registry.list(), ensure_ascii=False, indent=2))
    else:
        print("Usage: workflow_registry_001.py --register <name> [category] | --list")
