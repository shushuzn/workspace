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

TOOLS_DIR = Path("30-scripts-tools")

WORKFLOWS = {
    "dev": {
        "name": "Development Workflow",
        "steps": [
            {"tool": "auto_discover_001", "args": ["--scan"]},
            {"tool": "tool_validator_001", "args": ["--check", "30-scripts-tools/workflow_master_001.py"]},
            {"tool": "tool_namer_001", "args": ["--scan"]}
        ]
    },
    "brainstorm": {
        "name": "Brainstorm Workflow",
        "steps": [
            {"tool": "workflow_diagnosis_001", "args": []},
            {"tool": "brainstorm_workflow_001", "args": ["--step", "1", "NewTopic"]},
            {"tool": "brainstorm_workflow_001", "args": ["--step", "2", "10"]}
        ]
    },
    "full": {
        "name": "Full System Check",
        "steps": [
            {"tool": "workflow_diagnosis_001", "args": []},
            {"tool": "auto_discover_001", "args": ["--scan"]},
            {"tool": "tool_validator_001", "args": ["--check", "30-scripts-tools/safe_coder_001.py"]},
            {"tool": "workflow_logger_001", "args": ["--stats"]}
        ]
    }
}

class WorkflowMaster:
    def __init__(self):
        self.logger_path = Path("13-memory/.workflow_logs/master.json")
        self.logger_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _log(self, workflow, step, status, output=""):
        log = json.loads(self.logger_path.read_text(encoding="utf-8", errors="replace")) if self.logger_path.exists() else {"runs": []}
        log["runs"].append({
            "time": datetime.now().isoformat(),
            "workflow": workflow,
            "step": step,
            "status": status,
            "output": str(output)[:100]
        })
        if len(log["runs"]) > 100:
            log["runs"] = log["runs"][-50:]
        self.logger_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def run(self, workflow_id):
        if workflow_id not in WORKFLOWS:
            return {"error": f"Unknown workflow: {workflow_id}", "available": list(WORKFLOWS.keys())}
        
        workflow = WORKFLOWS[workflow_id]
        results = []
        
        print(f"Running: {workflow['name']}")
        print("=" * 50)
        
        for i, step in enumerate(workflow["steps"]):
            tool = step["tool"]
            args = step["args"]
            cmd = [sys.executable, str(TOOLS_DIR / f"{tool}.py")] + args
            
            print(f"[{i+1}/{len(workflow['steps'])}] {tool}...", end=" ", flush=True)
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace")
                status = "ok" if result.returncode == 0 else "fail"
                output = result.stdout[:50] if result.stdout else result.stderr[:50]
                print(status.upper())
                self._log(workflow_id, i+1, status, output)
                results.append({"step": i+1, "tool": tool, "status": status})
            except subprocess.TimeoutExpired:
                print("TIMEOUT")
                self._log(workflow_id, i+1, "timeout")
                results.append({"step": i+1, "tool": tool, "status": "timeout"})
            except Exception as e:
                print(f"ERROR: {e}")
                self._log(workflow_id, i+1, "error", str(e))
                results.append({"step": i+1, "tool": tool, "status": "error"})
        
        success = sum(1 for r in results if r["status"] == "ok")
        print("=" * 50)
        print(f"Complete: {success}/{len(results)} steps OK")
        
        return {"workflow": workflow_id, "results": results}
    
    def list_workflows(self):
        return [{"id": k, "name": v["name"], "steps": len(v["steps"])} for k, v in WORKFLOWS.items()]
    
    def stats(self):
        if not self.logger_path.exists():
            return {"total_runs": 0}
        log = json.loads(self.logger_path.read_text(encoding="utf-8", errors="replace"))
        runs = log.get("runs", [])
        return {
            "total_runs": len(runs),
            "by_status": {s: sum(1 for r in runs if r.get("status") == s) for s in ["ok", "fail", "timeout", "error"]}
        }

if __name__ == "__main__":
    master = WorkflowMaster()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--run":
            wid = sys.argv[2] if len(sys.argv) > 2 else "dev"
            print(json.dumps(master.run(wid), ensure_ascii=False, indent=2))
        elif cmd == "--list":
            print(json.dumps(master.list_workflows(), ensure_ascii=False, indent=2))
        elif cmd == "--stats":
            print(json.dumps(master.stats(), ensure_ascii=False, indent=2))
    else:
        print("WORKFLOW-MASTER-001")
        print("Commands:")
        print("  --list              Show workflows")
        print("  --run <workflow>    Run workflow")
        print("  --stats             Show stats")
