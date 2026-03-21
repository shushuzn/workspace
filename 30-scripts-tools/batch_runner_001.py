#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BATCH-RUNNER-001 Batch Workflow Executor
Runs multiple workflows in sequence with reporting
"""
import json, subprocess, sys, time
from pathlib import Path
from datetime import datetime

WORKFLOWS = ["dev", "quick", "plan", "security", "full"]

def run_workflow(name):
    """Run single workflow"""
    start = time.time()
    try:
        result = subprocess.run(
            ["workflow.bat", name],
            capture_output=True, text=True, timeout=120
        )
        elapsed = time.time() - start
        return {
            "name": name,
            "status": "OK" if result.returncode == 0 else "FAIL",
            "time": f"{elapsed:.1f}s"
        }
    except Exception as e:
        return {
            "name": name,
            "status": "ERROR",
            "time": f"{time.time()-start:.1f}s",
            "error": str(e)
        }

def batch_run(workflows=None):
    """Run batch workflows"""
    if workflows is None:
        workflows = WORKFLOWS
    
    print(f"\n[BATCH-RUNNER-001] Running {len(workflows)} workflows")
    print("=" * 50)
    
    results = []
    for wf in workflows:
        print(f"-> {wf}...", end=" ", flush=True)
        result = run_workflow(wf)
        results.append(result)
        print(result["status"])
    
    # Summary
    ok = sum(1 for r in results if r["status"] == "OK")
    total_time = sum(float(r["time"].rstrip("s")) for r in results)
    
    print("\n[SUMMARY]")
    print(f"  Passed: {ok}/{len(results)}")
    print(f"  Total: {total_time:.1f}s")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "workflows": workflows,
        "results": results,
        "summary": {"passed": ok, "total": len(results), "time": total_time}
    }
    
    report_file = Path("13-memory/.batch_report.json")
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"  Report: {report_file}")
    
    return report

def main():
    if len(sys.argv) > 1:
        workflows = sys.argv[1:]
    else:
        workflows = ["dev", "quick"]  # Default: quick batch
    
    batch_run(workflows)

if __name__ == "__main__":
    main()
