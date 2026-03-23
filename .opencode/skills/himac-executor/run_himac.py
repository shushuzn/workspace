#!/usr/bin/env python
import sys
from pathlib import Path

workspace_root = Path(__file__).resolve().parents[3]
ai_research_path = str(workspace_root / "30-scripts-tools" / "05-AI-RESEARCH")
sys.path.insert(0, ai_research_path)

from himac_executor import HiMACExecutor, GoalStatus

executor = HiMACExecutor()
action = sys.argv[1] if len(sys.argv) > 1 else "status"

if action == "plan":
    task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "general task"
    blueprint = executor.planner.create_blueprint(task)
    print(f"Blueprint created: {blueprint.task}")
    print(f"Subgoals: {len(blueprint.subgoals)}")
    for i, sg in enumerate(blueprint.subgoals, 1):
        print(f"  {i}. [{sg.status.value}] {sg.description}")
    print(f"Progress: {blueprint.progress():.0%}")

elif action == "status":
    bp = executor.current_blueprint
    print(f"HiMAC Executor Status:")
    print(f"  Current blueprint: {bp.task if bp else 'None'}")
    print(f"  Ready for planning")

elif action == "execute":
    print("Execute feature - provide blueprint_id")
    print("Use: py .opencode/skills/himac-executor/run_himac.py plan <task>")

else:
    print(f"Unknown action: {action}")
    print("Available: plan, execute, status")
