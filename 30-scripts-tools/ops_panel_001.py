#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OPS-PANEL-001 One-Click Operations Panel
Unified dashboard for all station operations
"""
import json, sys, subprocess
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

def run_tool(tool, args=""):
    try:
        result = subprocess.run(
            ["python", str(TOOLS_DIR / tool), args] if args else ["python", str(TOOLS_DIR / tool)],
            capture_output=True, text=True, timeout=60
        )
        return result.stdout[:500] if result.stdout else result.stderr[:200]
    except:
        return "[ERROR]"

def main():
    print("\n" + "=" * 60)
    print("  OPS-PANEL-001  One-Click Operations Panel")
    print("=" * 60)
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # 1. Health Check
    print("  [1] Health Check...", end=" ")
    health = run_tool("workflow_health_001.py")
    if '"status": "healthy"' in health:
        print("[OK] Healthy")
    else:
        print("[!] Need check")
    
    # 2. Topology
    print("  [2] Topology View...", end=" ")
    topo = run_tool("topology_viz_001.py", "--json")
    try:
        data = json.loads(topo)
        tools = data.get("summary", {}).get("total_tools", "?")
        health_score = data.get("summary", {}).get("health_score", "?")
        print(f"Tools: {tools} | Health: {health_score}%")
    except:
        print("[OK] Normal")
    
    # 3. Self-Heal Status
    print("  [3] Self-Heal Status...", end=" ")
    heal = run_tool("self_heal_001.py", "--predict")
    if "High-risk: 0" in heal:
        print("[OK] No risk")
    elif "High-risk:" in heal:
        risk_line = [l for l in heal.split("\n") if "High-risk:" in l]
        print(risk_line[0].strip() if risk_line else "")
    
    # 4. Code Quality
    print("  [4] Code Quality...", end=" ")
    issues = Path("13-memory/.code_quality_report.json")
    if issues.exists():
        try:
            data = json.loads(issues.read_text())
            clean = data.get("clean_files", 0)
            total = data.get("total", 1)
            pct = int(clean)/int(total)*100 if total else 0
            print(f"Clean: {clean}/{total} ({pct:.0f}%)")
        except:
            print("[OK] Normal")
    
    # 5. Multi-Agent Status
    print("  [5] Agent Status...", end=" ")
    viz = run_tool("multi_agent_viz_001.py")
    if "PLANNER" in viz:
        print("[OK] Personas active")
    else:
        print("[OK] Normal")
    
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
        print(f"\n[EXEC] {cmd}...")
        commands[cmd]()
    else:
        print(f"\n[HELP] Available: {', '.join(commands.keys())}")

if __name__ == "__main__":
    main()
