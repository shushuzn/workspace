import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-STATS-001 Workflow Statistics Analyzer
Analyzes workflow execution patterns and generates reports
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

STATS_FILE = Path("10-MEMORY/00-CORE/.workflow_logs/master.json")

def analyze_stats():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py workflow_stats_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_stats_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

Analyze workflow statistics"""
    if not STATS_FILE.exists():
        return {"error": "No stats file found"}

    data = json.loads(STATS_FILE.read_text(encoding="utf-8", errors="replace"))
    runs = data.get("runs", [])

    if not runs:
        return {"total": 0, "workflows": {}}

    # Count by workflow
    workflows = {}
    for run in runs:
        wf = run.get("workflow", "unknown")
        workflows[wf] = workflows.get(wf, 0) + 1

    # Count by status
    success = sum(1 for r in runs if r.get("status") == "ok")
    failed = len(runs) - success

    # Count by tool
    tools = {}
    for run in runs:
        tool = run.get("step", "unknown")
        tools[tool] = tools.get(tool, 0) + 1

    return {
        "total": len(runs),
        "success": success,
        "failed": failed,
        "rate": f"{success /len(runs) *100:.1f}%",
        "workflows": workflows,
        "top_tools": dict(sorted(tools.items(), key=lambda x: x[1], reverse=True)[:10])
    }

logging.basicConfig(level=logging.INFO)
def main():
    stats = analyze_stats()

    print("\n[WORKFLOW STATISTICS]")
    print("=" * 50)
    print(f"Total Runs: {stats.get('total', 0)}")
    print(f"Success: {stats.get('success', 0)}")
    print(f"Failed: {stats.get('failed', 0)}")
    print(f"Success Rate: {stats.get('rate', 'N/A')}")

    print("\n[TOP WORKFLOWS]")
    for wf, count in sorted(stats.get('workflows', {}).items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {wf}: {count}")

    print("\n[TOP TOOLS]")
    for tool, count in stats.get('top_tools', {}).items():
        print(f"  {tool}: {count}")
    print("=" * 50)

if __name__ == "__main__":
    main()
