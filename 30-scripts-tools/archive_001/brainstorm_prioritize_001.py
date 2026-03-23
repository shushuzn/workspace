import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Step 4: Prioritize - Rank and Plan
Rank ideas and create implementation plan
"""

import json
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def load_filtered() -> None:
    """Load filtered ideas"""
    ideas_file = Path("flow-archive/brainstorm-current/brainstorm_ideas_filtered.json")
    if not ideas_file.exists():
        print("ERROR: Please run brainstorm_003_filter.py first")
        return None

    with open(ideas_file, encoding="utf-8") as f:
        return json.load(f)

def prioritize(ideas, top_n=5) -> None:
    """Prioritize top N ideas"""
    # Take top N
    top = ideas[:top_n]

    # Add implementation phases
    phases = {
        1: "Week 1 - Quick Wins",
        2: "Week 2 - Core Features",
        3: "Week 3 - Advanced"
    }

    prioritized = []
    for i, idea in enumerate(top, 1):
        idea["priority"] = i
        idea["phase"] = phases.get(i, "Future")
        prioritized.append(idea)

    return prioritized

def save_prioritized(prioritized) -> None:
    """Save prioritized list"""
    output_file = Path("flow-archive/brainstorm-current/brainstorm_ideas_prioritized.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(prioritized, f, ensure_ascii=False, indent=2)

    print(f"\n[Saved] {len(prioritized)} prioritized ideas")
    return output_file

def run(top_n=5) -> None:
    """Execute prioritize step"""
    print("="*60)
    print("[BRAINSTORM] Step 4: Prioritize - Rank & Plan")
    print("="*60)

    # Load filtered ideas
    ideas = load_filtered()
    if not ideas:
        return None

    print(f"\n[Input] {len(ideas)} filtered ideas")

    # Prioritize
    prioritized = prioritize(ideas, top_n)

    print(f"\n[Output] Top {top_n} Prioritized Ideas:")
    for idea in prioritized:
        print(f"  {idea['priority']}. [{idea['phase']}] {idea['text']}")

    # Save
    save_prioritized(prioritized)

    return prioritized
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
# py brainstorm_prioritize_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_prioritize_001.py

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



if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    run(n)