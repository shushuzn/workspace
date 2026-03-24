#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Research Workflow CLI - AI Agent 研究工作流 v2.0

基于 FLARE + MEMORA + HiMAC 的智能研究系统

Commands:
    python research_workflow_cli.py run "<task>"    - 运行研究任务
    python research_workflow_cli.py status          - 查看研究状态
    python research_workflow_cli.py memory "<query>" - 搜索记忆
    python research_workflow_cli.py add "<finding>"  - 添加研究发现
    python research_workflow_cli.py demo            - 运行演示

Based on:
    - FLARE (arXiv:2601.22311) - Future-aware planning
    - MEMORA (arXiv:2602.03315) - Dual-layer memory (98% token savings)
    - HiMAC (arXiv:2603.00977) - Hierarchical macro-micro execution
    - ABC (arXiv:2602.22302) - Behavioral contracts
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent


def load_research_state():
    """Load research state"""
    state_file = WORKSPACE / "data" / "research_state.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except:
            pass
    return {"sessions": [], "memories": []}


def save_research_state(state):
    """Save research state"""
    state_file = WORKSPACE / "data" / "research_state.json"
    state_file.parent.mkdir(exist_ok=True)
    state_file.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def cmd_run(task: str):
    """Run a research task"""
    print(f"\n{'=' * 60}")
    print(f"  [*] Research Workflow v2.0")
    print(f"{'=' * 60}")
    print(f"\nTask: {task}")

    sys.path.insert(0, str(SCRIPT_DIR))
    from research_workflow_v2 import create_research_workflow

    wf = create_research_workflow()

    if not wf.initialize():
        print("[X] Failed to initialize components")
        return

    print("\n> Executing research workflow...\n")
    result = wf.run(task)

    print(f"Success: {result['success']}")
    print(f"\nSteps:")
    for step in result.get("steps", []):
        icon = "[OK]" if step["status"] == "completed" else "[X]"
        print(f"  {icon} {step['name']}: {step['status']}")

    if "plan" in result:
        plan = result["plan"]
        meta = plan.get("metadata", {})
        print(f"\n[*] Plan:")
        print(f"  Iterations: {meta.get('iterations', 'N/A')}")
        print(f"  Committed actions: {meta.get('committed_count', 0)}")

    if "blueprint" in result:
        bp = result["blueprint"]
        print(f"\n[*] Blueprint:")
        print(f"  Subgoals: {len(bp.get('subgoals', []))}")

    state = load_research_state()
    state["sessions"].append(
        {"task": task, "result": result, "timestamp": datetime.now().isoformat()}
    )
    save_research_state(state)

    print(f"\n[OK] Research task completed")


def cmd_status():
    """Show research status"""
    state = load_research_state()

    print(f"\n{'=' * 60}")
    print(f"  [S] Research Status")
    print(f"{'=' * 60}")

    sessions = state.get("sessions", [])
    print(f"\nTotal sessions: {len(sessions)}")

    if sessions:
        last = sessions[-1]
        print(f"Last session:")
        print(f"  Task: {last.get('task', 'N/A')}")
        print(f"  Time: {last.get('timestamp', 'N/A')}")
        print(f"  Success: {last.get('result', {}).get('success', 'N/A')}")


def cmd_memory(query: str):
    """Search research memories"""
    print(f"\n[*] Searching memories for: {query}")

    sys.path.insert(0, str(SCRIPT_DIR))
    from research_workflow_v2 import create_research_workflow

    wf = create_research_workflow()

    if not wf.initialize():
        print("❌ Failed to initialize")
        return

    results = wf.get_memory(query, limit=5)

    if results:
        print(f"\nFound {len(results)} memories:")
        for i, m in enumerate(results, 1):
            print(f"  {i}. {m[:80]}...")
    else:
        print("No relevant memories found")


def cmd_add(finding: str):
    """Add a research finding"""
    print(f"\n[+] Adding finding: {finding[:50]}...")

    sys.path.insert(0, str(SCRIPT_DIR))
    from research_workflow_v2 import create_research_workflow

    wf = create_research_workflow()

    if not wf.initialize():
        print("[X] Failed to initialize")
        return

    entities = [w for w in finding.split() if len(w) > 3][:5]
    wf.add_research_findings(finding, entities=entities)

    print("[OK] Finding added to memory")


def cmd_demo():
    """Run demo"""
    sys.path.insert(0, str(SCRIPT_DIR))
    from research_workflow_v2 import demo as workflow_demo

    print("\n" + "=" * 60)
    print("  [*] Research Workflow v2.0 Demo")
    print("=" * 60 + "\n")

    workflow_demo()


def main():
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        return

    print("[OK] Critic Review Passed")

    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCommands:")
        print("  run <task>      - Run research task")
        print("  status          - Show research status")
        print("  memory <query>  - Search memories")
        print("  add <finding>   - Add research finding")
        print("  demo            - Run demo")
        return

    command = sys.argv[1].lower()

    if command == "run" and len(sys.argv) > 2:
        cmd_run(" ".join(sys.argv[2:]))
    elif command == "status":
        cmd_status()
    elif command == "memory" and len(sys.argv) > 2:
        cmd_memory(" ".join(sys.argv[2:]))
    elif command == "add" and len(sys.argv) > 2:
        cmd_add(" ".join(sys.argv[2:]))
    elif command == "demo":
        cmd_demo()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python research_workflow_cli.py' for help")


if __name__ == "__main__":
    main()
