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
WORKFLOWS_FILE = TOOLS_DIR / "workflows.json"

def load_workflows():
    if WORKFLOWS_FILE.exists():
        return json.loads(WORKFLOWS_FILE.read_text(encoding="utf-8", errors="replace"))
    return {}

WORKFLOWS = load_workflows()

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
        global WORKFLOWS
        WORKFLOWS = load_workflows()
        
        if workflow_id not in WORKFLOWS:
            return {"error": f"Unknown: {workflow_id}", "available": list(WORKFLOWS.keys())}
        
        wf = WORKFLOWS[workflow_id]
        
        # Check if it's a directory workflow
        if "workflow_dir" in wf:
            return self._run_dir_workflow(workflow_id, wf)
        
        # Standard step-based workflow
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
    
    def _run_dir_workflow(self, workflow_id, wf):
        """Run a directory-based workflow"""
        wf_dir = Path(wf["workflow_dir"])
        
        if not wf_dir.exists():
            return {"error": f"Workflow directory not found: {wf_dir}"}
        
        print(f"Running: {wf['name']}")
        print(f"Directory: {wf_dir}")
        print("=" * 50)
        
        # Look for workflow.json or main script
        workflow_json = wf_dir / "workflow.json"
        main_script = wf_dir / "run.py"
        
        if workflow_json.exists():
            # Run from workflow.json config
            config = json.loads(workflow_json.read_text(encoding="utf-8", errors="replace"))
            return self._run_from_config(workflow_id, wf, config)
        elif main_script.exists():
            # Run main script directly
            print(f"Executing: {main_script}")
            try:
                result = subprocess.run(
                    [sys.executable, str(main_script)],
                    capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace"
                )
                status = "ok" if result.returncode == 0 else "fail"
                print(f"\nComplete: {status}")
                return {"workflow": workflow_id, "status": status, "output": result.stdout[:500]}
            except subprocess.TimeoutExpired:
                return {"workflow": workflow_id, "status": "timeout"}
        else:
            return {"error": f"No workflow.json or run.py found in {wf_dir}"}
    
    def _run_from_config(self, workflow_id, wf, config):
        """Run workflow from config file"""
        results = []
        steps = config.get("steps", [])
        
        for i, step in enumerate(steps):
            tool = step.get("tool", step.get("script", ""))
            args = step.get("args", [])
            cmd = [sys.executable, str(tool)] + args if tool.endswith(".py") else [tool] + args
            
            print(f"[{i+1}/{len(steps)}] {Path(tool).name}...", end=" ", flush=True)
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace")
                status = "ok" if result.returncode == 0 else "fail"
                print(status.upper())
                results.append({"step": i+1, "tool": tool, "status": status})
            except Exception:
                print("ERROR")
                results.append({"step": i+1, "tool": tool, "status": "error"})
        
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"\nComplete: {ok}/{len(results)} OK")
        return {"workflow": workflow_id, "results": results}
    
    def list_workflows(self):
        global WORKFLOWS
        WORKFLOWS = load_workflows()
        return [{"id": k, "name": v["name"], "category": v.get("category", "other"), "steps": len(v.get("steps", [])), "type": "dir" if "workflow_dir" in v else "steps"} for k, v in WORKFLOWS.items()]
    
    def list_categories(self):
        global WORKFLOWS
        WORKFLOWS = load_workflows()
        cats = {}
        for k, v in WORKFLOWS.items():
            cat = v.get("category", "other")
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
            print("WORKFLOW-MASTER-001 - Workflow Manager")
            print("  --run <wf>       Run workflow")
            print("  --list           List all workflows")
            print("  --categories     List by category")
    else:
        print("WORKFLOW-MASTER-001 - Workflow Manager")
        print("Usage: workflow_master_001.py --run <workflow>")
