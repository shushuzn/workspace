#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-MASTER-001 Unified Workflow Executor
"""
import json, sys, subprocess
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

WORKFLOWS = {
    "dev": {"name": "Development Workflow", "category": "dev", "steps": [
        {"tool": "auto_discover_001", "args": ["--scan"]},
        {"tool": "tool_validator_001", "args": ["--check", "30-scripts-tools/workflow_master_001.py"]},
        {"tool": "tool_namer_001", "args": ["--scan"]}
    ]},
    "plan": {"name": "Planning Workflow", "category": "plan", "steps": [
        {"tool": "workflow_diagnosis_001", "args": []},
        {"tool": "workflow_health_001", "args": []},
        {"tool": "workflow_optimizer_001", "args": ["--report"]},
        {"tool": "tool_namer_001", "args": ["--scan"]}
    ]},
    "brainstorm": {"name": "Brainstorm Workflow", "category": "plan", "steps": [
        {"tool": "workflow_diagnosis_001", "args": []},
        {"tool": "brainstorm_workflow_001", "args": ["--step", "1", "NewTopic"]},
        {"tool": "brainstorm_workflow_001", "args": ["--step", "2", "10"]}
    ]},
    "audit": {"name": "Audit Workflow", "category": "plan", "steps": [
        {"tool": "workflow_diagnosis_001", "args": []},
        {"tool": "tool_validator_001", "args": ["--scan"]},
        {"tool": "workflow_security_001", "args": []},
        {"tool": "file_integrity_001", "args": []}
    ]},
    "test": {"name": "Test Workflow", "category": "qa", "steps": [
        {"tool": "tool_validator_001", "args": ["--scan"]},
        {"tool": "tool_namer_001", "args": ["--scan"]},
        {"tool": "workflow_test_001", "args": []}
    ]},
    "security": {"name": "Security Workflow", "category": "qa", "steps": [
        {"tool": "tool_validator_001", "args": ["--scan"]},
        {"tool": "workflow_security_001", "args": []},
        {"tool": "file_integrity_001", "args": []}
    ]},
    "full": {"name": "Full System Check", "category": "qa", "steps": [
        {"tool": "workflow_diagnosis_001", "args": []},
        {"tool": "auto_discover_001", "args": ["--scan"]},
        {"tool": "tool_validator_001", "args": ["--scan"]},
        {"tool": "workflow_health_001", "args": []}
    ]},
    "quick": {"name": "Quick Check", "category": "qa", "steps": [
        {"tool": "tool_validator_001", "args": ["--check", "30-scripts-tools/workflow_master_001.py"]},
        {"tool": "workflow_health_001", "args": []}
    ]},
    "backup": {"name": "Backup Workflow", "category": "ops", "steps": [
        {"tool": "workflow_backup_001", "args": ["--create"]},
        {"tool": "file_integrity_001", "args": []},
        {"tool": "workflow_logger_001", "args": ["--stats"]}
    ]},
    "deploy": {"name": "Deploy Workflow", "category": "ops", "steps": [
        {"tool": "workflow_test_001", "args": []},
        {"tool": "workflow_backup_001", "args": ["--create"]},
        {"tool": "workflow_deploy_001", "args": []},
        {"tool": "workflow_health_001", "args": []}
    ]},
    "monitor": {"name": "Monitor Workflow", "category": "ops", "steps": [
        {"tool": "workflow_monitor_001", "args": []},
        {"tool": "workflow_health_001", "args": []},
        {"tool": "workflow_alert_001", "args": []}
    ]},
    "cleanup": {"name": "Cleanup Workflow", "category": "ops", "steps": [
        {"tool": "workflow_diagnosis_001", "args": []},
        {"tool": "workflow_fix_001", "args": []},
        {"tool": "workflow_optimizer_001", "args": ["--clear-cache"]}
    ]},
    "stock": {"name": "Stock Analysis Workflow", "category": "domain", "steps": [
        {"tool": "sa_signal_generator_001", "args": []},
        {"tool": "sa_backtest_optimizer_001", "args": []}
    ]},
    "stock-full": {"name": "Full Stock Analysis", "category": "domain", "steps": [
        {"tool": "sa_data_optimizer_001", "args": []},
        {"tool": "sa_backtest_optimizer_001", "args": []},
        {"tool": "sa_risk_001", "args": []}
    ]},
    "ci": {"name": "CI/CD Workflow", "category": "ops", "steps": [
        {"tool": "tool_validator_001", "args": ["--scan"]},
        {"tool": "workflow_test_001", "args": []}
    ]}
}

class WorkflowMaster:
    def __init__(self):
        self.logger_path = Path("13-memory/.workflow_logs/master.json")
        self.logger_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _log(self, workflow, step, status):
        log = json.loads(self.logger_path.read_text(encoding="utf-8", errors="replace")) if self.logger_path.exists() else {"runs": []}
        log["runs"].append({"time": datetime.now().isoformat(), "workflow": workflow, "step": step, "status": status})
        if len(log["runs"]) > 100: log["runs"] = log["runs"][-50:]
        self.logger_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def run(self, workflow_id):
        if workflow_id not in WORKFLOWS:
            return {"error": f"Unknown: {workflow_id}", "available": list(WORKFLOWS.keys())}
        wf = WORKFLOWS[workflow_id]
        results = []
        print(f"Running: {wf['name']}")
        print("=" * 50)
        for i, step in enumerate(wf["steps"]):
            tool, args = step["tool"], step["args"]
            cmd = [sys.executable, str(TOOLS_DIR / f"{tool}.py")] + args
            print(f"[{i+1}/{len(wf['steps'])}] {tool}...", end=" ", flush=True)
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace")
                status = "ok" if result.returncode == 0 else "fail"
                print(status.upper())
                results.append({"step": i+1, "tool": tool, "status": status})
            except subprocess.TimeoutExpired:
                print("TIMEOUT")
                results.append({"step": i+1, "tool": tool, "status": "timeout"})
            except Exception:
                print("ERROR")
                results.append({"step": i+1, "tool": tool, "status": "error"})
            self._log(workflow_id, tool, results[-1]["status"])
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"\nComplete: {ok}/{len(results)} OK")
        return {"workflow": workflow_id, "results": results}
    
    def list_workflows(self):
        return [{"id": k, "name": v["name"], "category": v["category"], "steps": len(v["steps"])} for k, v in WORKFLOWS.items()]
    
    def list_categories(self):
        cats = {}
        for k, v in WORKFLOWS.items():
            cat = v["category"]
            if cat not in cats: cats[cat] = []
            cats[cat].append(k)
        return [{"category": k, "workflows": v} for k, v in cats.items()]

if __name__ == "__main__":
    master = WorkflowMaster()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--run" and len(sys.argv) > 2:
            print(json.dumps(master.run(sys.argv[2]), ensure_ascii=False, indent=2))
        elif cmd == "--list":
            print(json.dumps(master.list_workflows(), ensure_ascii=False, indent=2))
        elif cmd == "--categories":
            print(json.dumps(master.list_categories(), ensure_ascii=False, indent=2))
        elif cmd == "--help":
            print("WORKFLOW-MASTER-001 - 15 Workflow Modes")
            print("  --run <wf>      Run workflow")
            print("  --list          List all workflows")
            print("  --categories    List by category")
    else:
        print("WORKFLOW-MASTER-001 - 15 Workflow Modes")
        print("Usage: workflow_master_001.py --run <workflow>")
