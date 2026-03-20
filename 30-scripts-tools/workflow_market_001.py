#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-MARKET-001 Template Market
=====================================
Browse, install, and manage workflow templates
"""

import json, sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MARKET_DIR = Path("13-memory/.workflow_market")
MARKET_DIR.mkdir(parents=True, exist_ok=True)

MARKETPLACE_TEMPLATES = {
    # Stock Analysis Templates
    "stock-quick": {
        "id": "stock-quick",
        "name": "Stock Quick Analysis",
        "description": "Quick stock analysis in under 1 minute",
        "category": "stock",
        "steps": [
            {"tool": "sa_signal_generator_001", "args": []},
            {"tool": "sa_analyzer_001", "args": ["--quick"]}
        ],
        "rating": 5,
        "installs": 0
    },
    "stock-full": {
        "id": "stock-full",
        "name": "Stock Full Analysis",
        "description": "Comprehensive stock analysis with backtest",
        "category": "stock",
        "steps": [
            {"tool": "sa_historical_downloader_001", "args": []},
            {"tool": "sa_analyzer_001", "args": []},
            {"tool": "sa_signal_generator_001", "args": []},
            {"tool": "sa_backtesting_001", "args": []},
            {"tool": "sa_risk_001", "args": []}
        ],
        "rating": 5,
        "installs": 0
    },
    "stock-research": {
        "id": "stock-research",
        "name": "Stock Research Mode",
        "description": "Deep dive research with all metrics",
        "category": "stock",
        "steps": [
            {"tool": "sa_financial_collector_001", "args": []},
            {"tool": "sa_indicator_calculator_001", "args": []},
            {"tool": "sa_trend_analysis_001", "args": []},
            {"tool": "sa_valuation_model_001", "args": []},
            {"tool": "sa_report_generator_001", "args": []}
        ],
        "rating": 5,
        "installs": 0
    },
    "stock-monitor": {
        "id": "stock-monitor",
        "name": "Stock Monitor",
        "description": "Real-time stock monitoring",
        "category": "stock",
        "steps": [
            {"tool": "sa_realtime_001", "args": []},
            {"tool": "sa_sentiment_monitor_001", "args": []},
            {"tool": "sa_alert_system_001", "args": []}
        ],
        "rating": 4,
        "installs": 0
    },
    
    # Development Templates
    "dev-cycle": {
        "id": "dev-cycle",
        "name": "Development Cycle",
        "description": "Discover -> Validate -> Test -> Commit",
        "category": "development",
        "steps": [
            {"tool": "auto_discover_001", "args": ["--scan"]},
            {"tool": "tool_validator_001", "args": []},
            {"tool": "tool_namer_001", "args": ["--scan"]},
            {"tool": "workflow_test_001", "args": []}
        ],
        "rating": 5,
        "installs": 0
    },
    "safe-code": {
        "id": "safe-code",
        "name": "Safe Code Generation",
        "description": "Generate code with safety checks",
        "category": "development",
        "steps": [
            {"tool": "safe_coder_001", "args": []},
            {"tool": "tool_validator_001", "args": []},
            {"tool": "file_integrity_001", "args": []}
        ],
        "rating": 5,
        "installs": 0
    },
    "code-review": {
        "id": "code-review",
        "name": "Code Review",
        "description": "Full code quality review",
        "category": "development",
        "steps": [
            {"tool": "tool_validator_001", "args": []},
            {"tool": "workflow_security_001", "args": []},
            {"tool": "file_integrity_001", "args": []}
        ],
        "rating": 4,
        "installs": 0
    },
    
    # Brainstorm Templates
    "brainstorm-quick": {
        "id": "brainstorm-quick",
        "name": "Quick Brainstorm",
        "description": "5-minute brainstorm",
        "category": "brainstorm",
        "steps": [
            {"tool": "brainstorm_workflow_001", "args": ["--step", "1"]},
            {"tool": "brainstorm_workflow_001", "args": ["--step", "2"]}
        ],
        "rating": 5,
        "installs": 0
    },
    "brainstorm-scamp": {
        "id": "brainstorm-scamp",
        "name": "SCAMPER Analysis",
        "description": "SCAMPER creative method",
        "category": "brainstorm",
        "steps": [
            {"tool": "brainstorm_scamper_001", "args": []}
        ],
        "rating": 4,
        "installs": 0
    },
    
    # System Templates
    "health-check": {
        "id": "health-check",
        "name": "System Health Check",
        "description": "Check overall system health",
        "category": "system",
        "steps": [
            {"tool": "workflow_diagnosis_001", "args": []},
            {"tool": "workflow_health_001", "args": []},
            {"tool": "workflow_monitor_001", "args": []}
        ],
        "rating": 5,
        "installs": 0
    },
    "daily-standup": {
        "id": "daily-standup",
        "name": "Daily Standup",
        "description": "Daily workflow check",
        "category": "routine",
        "steps": [
            {"tool": "workflow_master_001", "args": ["--run", "dev"]},
            {"tool": "workflow_analytics_001", "args": []}
        ],
        "rating": 4,
        "installs": 0
    },
    "weekly-review": {
        "id": "weekly-review",
        "name": "Weekly Review",
        "description": "Comprehensive weekly review",
        "category": "routine",
        "steps": [
            {"tool": "workflow_master_001", "args": ["--run", "full"]},
            {"tool": "workflow_analytics_001", "args": []},
            {"tool": "workflow_backup_001", "args": ["--create", "weekly"]},
            {"tool": "workflow_report_001", "args": []}
        ],
        "rating": 5,
        "installs": 0
    }
}

class WorkflowMarket:
    def __init__(self):
        self.installed_file = MARKET_DIR / "installed.json"
        if not self.installed_file.exists():
            self._save_installed({})
    
    def _load_installed(self):
        return json.loads(self.installed_file.read_text(encoding="utf-8", errors="replace"))
    
    def _save_installed(self, data):
        self.installed_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def list(self, category=None):
        templates = list(MARKETPLACE_TEMPLATES.values())
        if category:
            templates = [t for t in templates if t.get("category") == category]
        
        installed = self._load_installed()
        
        for t in templates:
            t["installed"] = t["id"] in installed
        
        return {
            "templates": templates,
            "count": len(templates),
            "categories": list(set(t.get("category") for t in templates))
        }
    
    def install(self, template_id):
        if template_id not in MARKETPLACE_TEMPLATES:
            return {"error": f"Template not found: {template_id}"}
        
        installed = self._load_installed()
        installed[template_id] = MARKETPLACE_TEMPLATES[template_id]
        installed[template_id]["installed_at"] = str(Path().resolve())
        
        self._save_installed(installed)
        MARKETPLACE_TEMPLATES[template_id]["installs"] += 1
        
        return {"status": "installed", "template": template_id}
    
    def uninstall(self, template_id):
        installed = self._load_installed()
        if template_id not in installed:
            return {"error": f"Template not installed: {template_id}"}
        
        del installed[template_id]
        self._save_installed(installed)
        
        return {"status": "uninstalled", "template": template_id}
    
    def run(self, template_id):
        """Run an installed template"""
        installed = self._load_installed()
        if template_id not in installed:
            return {"error": f"Template not installed: {template_id}"}
        
        template = installed[template_id]
        return {
            "template": template_id,
            "name": template["name"],
            "steps": len(template["steps"]),
            "workflow": template["steps"]
        }
    
    def categories(self):
        """List all categories"""
        cats = {}
        for t in MARKETPLACE_TEMPLATES.values():
            cat = t.get("category", "other")
            if cat not in cats:
                cats[cat] = {"count": 0, "templates": []}
            cats[cat]["count"] += 1
            cats[cat]["templates"].append(t["id"])
        
        return {"categories": cats}

if __name__ == "__main__":
    market = WorkflowMarket()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--list":
            cat = sys.argv[2] if len(sys.argv) > 2 else None
            print(json.dumps(market.list(cat), ensure_ascii=False, indent=2))
        elif cmd == "--install":
            tid = sys.argv[2] if len(sys.argv) > 2 else ""
            print(json.dumps(market.install(tid), ensure_ascii=False, indent=2))
        elif cmd == "--uninstall":
            tid = sys.argv[2] if len(sys.argv) > 2 else ""
            print(json.dumps(market.uninstall(tid), ensure_ascii=False, indent=2))
        elif cmd == "--run":
            tid = sys.argv[2] if len(sys.argv) > 2 else ""
            print(json.dumps(market.run(tid), ensure_ascii=False, indent=2))
        elif cmd == "--categories":
            print(json.dumps(market.categories(), ensure_ascii=False, indent=2))
    else:
        print("WORKFLOW-MARKET-001")
        print("Commands:")
        print("  --list [category]     List templates")
        print("  --install <id>       Install template")
        print("  --uninstall <id>    Uninstall template")
        print("  --run <id>           Run template")
        print("  --categories         List categories")
        print()
        print("Categories: stock, development, brainstorm, system, routine")

    
   