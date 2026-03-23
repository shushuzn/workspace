import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Workflow Master
Main entry point for brainstorm workflow

Usage:
  py brainstorm_workflow.py "Your question/topic"
  py brainstorm_workflow.py --step 1 "topic"
  py brainstorm_workflow.py --step 2
  py brainstorm_workflow.py --step 3
  py brainstorm_workflow.py --step 4
  py brainstorm_workflow.py --status
"""

import json
import sys
from pathlib import Path

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def show_status() -> None:
    """Show current brainstorm status"""
    base = Path("flow-archive/brainstorm-current")

    files = {
        "topic": base / "brainstorm_topic.json",
        "raw": base / "brainstorm_ideas_raw.json",
        "filtered": base / "brainstorm_ideas_filtered.json",
        "prioritized": base / "brainstorm_ideas_prioritized.json"
    }

    print("=" *60)
    print("[BRAINSTORM] Status")
    print("=" *60)

    for name, path in files.items():
        status = "[OK]" if path.exists() else "[MISSING]"
        print(f"  {status} {name}")

    # Show current topic if exists
    if files["topic"].exists():
        with open(files["topic"], encoding="utf-8") as f:
            topic = json.load(f)
        print(f"\nCurrent Topic: {topic.get('topic')}")

def run_full_workflow(topic) -> None:
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
# py brainstorm_workflow_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_workflow_001.py

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

Run the full brainstorm workflow"""
    import subprocess

    print("=" *60)
    print("[BRAINSTORM] Full Workflow")
    print("=" *60)

    # Step 1: Define
    print("\n[Step 1] Defining problem...")
    result = subprocess.run(
        [sys.executable, "30-scripts-tools/brainstorm_001_define.py", topic],
        capture_output=True, text=True
    , timeout=60)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return

    # Step 2: Diverge
    print("\n[Step 2] Generating ideas...")
    result = subprocess.run(
        [sys.executable, "30-scripts-tools/brainstorm_002_diverge.py", "15"],
        capture_output=True, text=True
    , timeout=60)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return

    # Step 3: Filter
    print("\n[Step 3] Filtering ideas...")
    result = subprocess.run(
        [sys.executable, "30-scripts-tools/brainstorm_003_filter.py", "7"],
        capture_output=True, text=True
    , timeout=60)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return

    # Step 4: Prioritize
    print("\n[Step 4] Prioritizing...")
    result = subprocess.run(
        [sys.executable, "30-scripts-tools/brainstorm_004_prioritize.py", "5"],
        capture_output=True, text=True
    , timeout=60)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return

    # Show results
    print("\n" + "=" *60)
    print("[BRAINSTORM] Complete!")
    print("=" *60)

    show_status()

def show_methods() -> None:
    """Show available brainstorm methods"""
    print("\n[Available Methods]")
    print("  --scamper <topic>     SCAMPER method (7 operators)")
    print("  --sixhats <topic>     Six Thinking Hats")
    print("  --reverse <topic>     Reverse Brainstorming")
    print("  --random <topic>      Random Input (triggers unconventional)")
    print("  --analogy <topic>     Analogy (cross-domain solutions)")
    print("  --refine <problem>    Auto-refine problem (AI enhancement)")
    print("\n[NEXT STEP] Run: py brainstorm_next.py for workflow guidance")

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) == 1:
        print(__doc__)
        show_status()
        show_methods()
        return

    if sys.argv[1] == "--status":
        show_status()
        return

    if sys.argv[1] == "--scamper":
        topic = " ".join(sys.argv[2:]) or "OpenClaw tools"
        import subprocess
        subprocess.run([sys.executable, "30-scripts-tools/brainstorm_scamper.py", topic], timeout=60)
        return

    if sys.argv[1] == "--sixhats":
        topic = " ".join(sys.argv[2:]) or "OpenClaw tools"
        import subprocess
        subprocess.run([sys.executable, "30-scripts-tools/brainstorm_sixhats.py", topic], timeout=60)
        return

    if sys.argv[1] == "--reverse":
        topic = " ".join(sys.argv[2:]) or "OpenClaw tools"
        import subprocess
        subprocess.run([sys.executable, "30-scripts-tools/brainstorm_reverse.py", topic], timeout=60)
        return

    if sys.argv[1] == "--random":
        topic = " ".join(sys.argv[2:]) or "OpenClaw tools"
        import subprocess
        subprocess.run([sys.executable, "30-scripts-tools/brainstorm_random.py", topic], timeout=60)
        return

    if sys.argv[1] == "--analogy":
        topic = " ".join(sys.argv[2:]) or "OpenClaw tools"
        import subprocess
        subprocess.run([sys.executable, "30-scripts-tools/brainstorm_analogy.py", topic], timeout=60)
        return

    if sys.argv[1] == "--refine":
        topic = " ".join(sys.argv[2:]) or "优化工作流"
        import subprocess
        subprocess.run([sys.executable, "30-scripts-tools/brainstorm_refine.py", topic], timeout=60)
        return

    if sys.argv[1] == "--next":
        import subprocess
        subprocess.run([sys.executable, "30-scripts-tools/brainstorm_next.py"], timeout=60)
        return

    if sys.argv[1] == "--step":
        step = sys.argv[2] if len(sys.argv) > 2 else "1"
        topic = sys.argv[3] if len(sys.argv) > 3 else None

        steps = {
            "1": "brainstorm_001_define.py",
            "2": "brainstorm_002_diverge.py",
            "3": "brainstorm_003_filter.py",
            "4": "brainstorm_004_prioritize.py"
        }

        script = steps.get(step)
        if not script:
            print(f"Unknown step: {step}")
            return

        cmd = [sys.executable, f"30-scripts-tools/{script}"]
        if topic:
            cmd.append(topic)

        import subprocess
        subprocess.run(cmd, timeout=60)
        return

    # Full workflow with topic
    topic = " ".join(sys.argv[1:])
    run_full_workflow(topic)

if __name__ == "__main__":
    main()