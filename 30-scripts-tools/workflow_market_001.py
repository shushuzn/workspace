#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-MARKET-001 Workflow Template Market
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


MARKET_DIR = Path("13-memory/.workflow_market")
TEMPLATES_FILE = MARKET_DIR / "templates.json"
MY_TEMPLATES_FILE = MARKET_DIR / "my_templates.json"


class WorkflowMarket:
    """Workflow Template Market"""
    
    BUILTIN_TEMPLATES = {
        "quick-brainstorm": {
            "id": "quick-brainstorm",
            "name": "Quick Brainstorm",
            "description": "5-min quick brainstorm flow",
            "category": "brainstorm",
            "steps": [
                {"tool": "brainstorm_001_define", "args": []},
                {"tool": "brainstorm_002_diverge", "args": [10]},
                {"tool": "brainstorm_003_filter", "args": [5]},
                {"tool": "brainstorm_004_prioritize", "args": [3]}
            ],
            "tags": ["quick", "brainstorm", "5min"],
            "rating": 5
        },
        "discover-sync": {
            "id": "discover-sync",
            "name": "Tool Discovery & Sync",
            "description": "Scan and sync tool registry",
            "category": "tooling",
            "steps": [
                {"tool": "auto_discover_001", "args": ["--sync"]}
            ],
            "tags": ["tool", "discover", "sync"],
            "rating": 5
        },
        "full-optimize": {
            "id": "full-optimize",
            "name": "Full Optimize Cycle",
            "description": "Discover -> Optimize -> Report",
            "category": "optimization",
            "steps": [
                {"tool": "auto_discover_001", "args": ["--scan"]},
                {"tool": "chain_runner_001", "args": ["--run", "optimize-cycle"]}
            ],
            "tags": ["optimize", "automation"],
            "rating": 4
        },
        "daily-review": {
            "id": "daily-review",
            "name": "Daily Review",
            "description": "Review daily work, update notes",
            "category": "routine",
            "steps": [
                {"tool": "version_ctrl_001", "args": ["--snapshot", "daily"]}
            ],
            "tags": ["daily", "review"],
            "rating": 4
        }
    }
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.tools_dir = self.workspace / "30-scripts-tools"
        MARKET_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_files()
    
    def _ensure_files(self):
        if not TEMPLATES_FILE.exists():
            TEMPLATES_FILE.write_text(json.dumps({"templates": self.BUILTIN_TEMPLATES}, ensure_ascii=False, indent=2))
        if not MY_TEMPLATES_FILE.exists():
            MY_TEMPLATES_FILE.write_text(json.dumps({"templates": {}}, ensure_ascii=False, indent=2))
    
    def _load_templates(self) -> dict:
        return json.loads(TEMPLATES_FILE.read_text(encoding="utf-8"))
    
    def _save_templates(self, data: dict):
        TEMPLATES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def _load_my_templates(self) -> dict:
        return json.loads(MY_TEMPLATES_FILE.read_text(encoding="utf-8"))
    
    def _save_my_templates(self, data: dict):
        MY_TEMPLATES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def list_templates(self, category: str = None) -> List:
        templates = self._load_templates()["templates"]
        if category:
            templates = {k: v for k, v in templates.items() if v.get("category") == category}
        return [{"id": k, "name": v["name"], "description": v["description"], "category": v.get("category"), "steps": len(v.get("steps", [])), "rating": v.get("rating", 3)} for k, v in templates.items()]
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        templates = self._load_templates()["templates"]
        return templates.get(template_id)
    
    def import_template(self, template_id: str) -> Dict:
        template = self.get_template(template_id)
        if not template:
            return {"status": "error", "reason": "Template not found"}
        my_templates = self._load_my_templates()
        if template_id in my_templates["templates"]:
            return {"status": "exists", "reason": "Already imported"}
        my_templates["templates"][template_id] = {**template, "imported_at": datetime.now().isoformat()}
        self._save_my_templates(my_templates)
        return {"status": "success", "template_id": template_id}
    
    def search(self, keyword: str) -> List:
        templates = self._load_templates()["templates"]
        results = []
        for tid, t in templates.items():
            if keyword.lower() in t.get("name", "").lower():
                results.append({"id": tid, "name": t["name"], "match": "name"})
            elif any(keyword.lower() in tag.lower() for tag in t.get("tags", [])):
                results.append({"id": tid, "name": t["name"], "match": "tag"})
        return results
    
    def run_template(self, template_id: str) -> Dict:
        template = self.get_template(template_id)
        if not template:
            return {"status": "error", "reason": "Template not found"}
        return {"status": "ready", "template": template_id, "steps": len(template.get("steps", []))}


def main():
    market = WorkflowMarket()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--list":
            templates = market.list_templates()
            print(json.dumps(templates, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--import":
            tid = sys.argv[2] if len(sys.argv) > 2 else None
            if not tid:
                print("Error: Specify template id")
                return 1
            result = market.import_template(tid)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--search":
            keyword = sys.argv[2] if len(sys.argv) > 2 else ""
            results = market.search(keyword)
            print(json.dumps(results, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--run":
            tid = sys.argv[2] if len(sys.argv) > 2 else None
            if not tid:
                print("Error: Specify template id")
                return 1
            result = market.run_template(tid)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("WORKFLOW-MARKET-001 Workflow Template Market")
    print("Usage:")
    print("  py workflow_market_001.py --list                  # List all")
    print("  py workflow_market_001.py --import <id>          # Import")
    print("  py workflow_market_001.py --search <keyword>     # Search")
    print("  py workflow_market_001.py --run <id>              # Run template")
    return 0


if __name__ == "__main__":
    sys.exit(main())
