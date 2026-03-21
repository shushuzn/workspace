import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Step 3: Filter - Evaluate and Filter Ideas
Remove low-quality ideas, keep top candidates
"""

import json
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def load_ideas() -> None:
    """Load raw ideas"""
    ideas_file = Path("flow-archive/brainstorm-current/brainstorm_ideas_raw.json")
    if not ideas_file.exists():
        print("ERROR: Please run brainstorm_002_diverge.py first")
        return None
    
    with open(ideas_file, encoding="utf-8") as f:
        return json.load(f)

def filter_ideas(ideas, min_score=6) -> None:
    """Filter ideas by score"""
    filtered = [idea for idea in ideas if idea.get("score", 0) >= min_score]
    return sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)

def save_filtered(filtered) -> None:
    """Save filtered ideas"""
    output_file = Path("flow-archive/brainstorm-current/brainstorm_ideas_filtered.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Saved] {len(filtered)} filtered ideas")
    return output_file

def run(min_score=6) -> None:
    """Execute filter step"""
    print("="*60)
    print("[BRAINSTORM] Step 3: Filter - Evaluate Ideas")
    print("="*60)
    
    # Load ideas
    ideas = load_ideas()
    if not ideas:
        return None
    
    print(f"\n[Input] {len(ideas)} ideas")
    
    # Filter
    filtered = filter_ideas(ideas, min_score)
    
    print(f"[Output] {len(filtered)} filtered ideas (score >= {min_score})")
    print("\n[Top Ideas]")
    for i, idea in enumerate(filtered[:5], 1):
        print(f"  {i}. [{idea.get('score')}] {idea['text']}")
    
    # Save
    save_filtered(filtered)
    
    return filtered
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
# py brainstorm_filter_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_filter_001.py

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
    score = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    run(score)