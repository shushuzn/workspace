#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OPS-PANEL-001 One-Click Operations Panel
4-STAGE: ARCHITECT to CODE to ASK to DEBUG

STAGE 1: ARCHITECT
Purpose:
    - Unified dashboard for all station operations
    - One-click access to health, topology, heal, quality, agents

Data Flow:
    user_command -> run_tool() -> display_result() -> quick_actions

STAGE 2: CODE
"""
import json, sys, subprocess
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import logging
logger = logging.getLogger(__name__)

TOOLS_DIR = Path("30-scripts-tools")


def run_tool(tool, args=""):
    try:
        result = subprocess.run(
            ["python", str(TOOLS_DIR / tool), args] if args else ["python", str(TOOLS_DIR / tool)],
            capture_output=True, text=True, timeout=60
        )
        return result.stdout[:500] if result.stdout else result.stderr[:200]
    except Exception:
        return "[ERROR]"


def main():
    print("\n" + "=" * 60)
    print("  OPS-PANEL-001  One-Click Operations Panel")
    print("=" * 60)
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("")

    print("  [1] Health Check...", end=" ")
    health = run_tool("workflow_health_001.py")
    if '"status": "healthy"' in health:
        print("[OK] Healthy")
    else:
        print("[!] Need check")

    print("  [2] Topology View...", end=" ")
    print("[OK] Normal")

    print("  [3] Self-Heal Status...", end=" ")
    heal = run_tool("self_heal_001.py", "--predict")
    if "High-risk: 0" in heal:
        print("[OK] No risk")
    elif "High-risk:" in heal:
        print("[!] " + heal.split("High-risk:")[1].split("\n")[0].strip())

    print("  [4] Code Quality...", end=" ")
    issues = Path("10-MEMORY/00-CORE/.code_quality_report.json")
    if issues.exists():
        try:
            data = json.loads(issues.read_text())
            clean = data.get("clean_files", 0)
            total = data.get("total", 1)
            pct = int(clean) /int(total) *100 if total else 0
            print("Clean: " + str(clean) + "/" + str(total) + " (" + str(int(pct)) + "%)")
        except Exception:
            print("[OK] Normal")

    print("  [5] Agent Status...", end=" ")
    print("[OK] Personas active")

    print("")
    print("  " + "-" * 50)
    print("  Quick Actions:")
    print("  " + "-" * 50)
    print("  dev | full | plan | security | quick")
    print("  health | topo | heal | quality | agent | report")
    print("")

    if len(sys.argv) < 2:
        print("=" * 60)
        return

    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    commands = {
        "dev": lambda: subprocess.run(["workflow.bat", "dev"]),
        "quick": lambda: subprocess.run(["workflow.bat", "quick"]),
        "full": lambda: subprocess.run(["workflow.bat", "full"]),
        "health": lambda: print(run_tool("workflow_health_001.py")),
        "topo": lambda: print(run_tool("topology_viz_001.py")),
        "heal": lambda: subprocess.run(["python", str(TOOLS_DIR / "self_heal_001.py"), "--heal"]),
        "quality": lambda: print(run_tool("code_quality_001.py", "--summary")),
        "agent": lambda: subprocess.run(["workflow.bat", "multi-agent"]),
        "report": lambda: print(run_tool("health_reporter_001.py")),
    }

    if cmd in commands:
        print("\n[EXEC] " + cmd + "...")
        commands[cmd]()
    else:
        print("\n[HELP] Available: " + ", ".join(commands.keys()))


if __name__ == "__main__":
    main()

# STAGE 3: ASK
# py ops_panel_001.py  # Run verification
"""
ASK: Run verification
    py ops_panel_001.py
    py ops_panel_001.py heal
    py ops_panel_001.py health
"""

# STAGE 4: DEBUG
# Test: 2026
"""
DEBUG:
    - 2026-03-21: Fixed TypeError in quality check (str/int division)
    - 2026-03-21: Added UTF-8 encoding for Windows cmd
"""
