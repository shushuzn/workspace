#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BATCH-RUNNER-001 Batch Workflow Executor
4-STAGE: ARCHITECT to CODE to ASK to DEBUG

STAGE 1: ARCHITECT
Purpose:
    - Run multiple workflows in sequence
    - Report pass/fail for each workflow
    - Summary statistics

Data Flow:
    parse_args() -> run_workflow() -> collect_results() -> print_summary()

STAGE 2: CODE
"""
import json, subprocess, sys, time
from pathlib import Path
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

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
        success = result.returncode == 0
        return {"name": name, "success": success, "elapsed": elapsed}
    except Exception as e:
        logger.error("Failed to run " + name + ": " + str(e))
        return {"name": name, "success": False, "elapsed": 0}


def main():
    print("\n[BATCH-RUNNER-001] Running workflows")
    print("=" * 50)

    if len(sys.argv) < 2:
        workflows_to_run = WORKFLOWS[:3]  # Default: dev, quick, plan
    else:
        workflows_to_run = sys.argv[1:]

    results = []
    for wf in workflows_to_run:
        print("-> " + wf + "...", end=" ", flush=True)
        result = run_workflow(wf)
        results.append(result)
        status = "OK" if result["success"] else "FAIL"
        print(status)

    # Summary
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    total_time = sum(r["elapsed"] for r in results)

    print("")
    print("[SUMMARY]")
    print("  Passed: " + str(passed) + "/" + str(total))
    print("  Total: " + str(int(total_time)) + "s")

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "passed": passed,
        "total": total
    }
    Path("13-memory/.batch_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print("  Report: 13-memory/.batch_report.json")


if __name__ == "__main__":
    main()

# STAGE 3: ASK
# py batch_runner_001.py  # Run verification
"""
ASK: Run verification
    py batch_runner_001.py
    py batch_runner_001.py dev quick
    py batch_runner_001.py full
"""

# STAGE 4: DEBUG
# Test: 2026
"""
DEBUG:
    - 2026-03-21: 3/3 workflows pass
    - 2026-03-21: Report saved to JSON
"""
