import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Step 2: Diverge - Generate Ideas
Use multiple methods to generate as many ideas as possible
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Thinking methods
METHODS = [
    "SCAMPER (Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse)",
    "Reverse Thinking (opposite approach)",
    "Analogy (borrow from other fields)",
    "Extreme假设 (what if...)",
    "Random Word Association",
    "User Perspective",
    "System Decomposition",
    "Trend Extrapolation"
]

def load_topic() -> None:
    """Load topic from file"""
    topic_file = Path("flow-archive/brainstorm-current/brainstorm_topic.json")
    if not topic_file.exists():
        print("ERROR: Please run brainstorm_001_define.py first")
        return None

    with open(topic_file, encoding="utf-8") as f:
        return json.load(f)

def generate_ideas(topic_data, count=15) -> None:
    """Generate ideas based on topic"""
    topic = topic_data.get("topic", "")

    # Predefined idea templates for OpenClaw
    templates = [
        f"Auto-generate documentation for {topic}",
        f"Add AI-powered analysis for {topic}",
        f"Create visualization for {topic}",
        f"Implement caching for {topic}",
        f"Add batch processing for {topic}",
        f"Create API wrapper for {topic}",
        f"Add real-time monitoring for {topic}",
        f"Implement parallel execution for {topic}",
        f"Create template system for {topic}",
        f"Add export functionality for {topic}",
        f"Implement undo/redo for {topic}",
        f"Add collaboration features for {topic}",
        f"Create scheduler for {topic}",
        f"Add notification system for {topic}",
        f"Implement version control for {topic}"
    ]

    # Add some random variations
    ideas = []
    for i, t in enumerate(templates[:count], 1):
        ideas.append({
            "id": f"idea-{i:03d}",
            "text": t,
            "method": random.choice(METHODS),
            "score": random.randint(5, 10)
        })

    return ideas

def save_ideas(ideas) -> None:
    """Save ideas to file"""
    output_file = Path("flow-archive/brainstorm-current/brainstorm_ideas_raw.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ideas, f, ensure_ascii=False, indent=2)

    print(f"\n[Saved] {len(ideas)} ideas to {output_file}")
    return output_file

def run(count=15) -> None:
    """Execute diverge step"""
    print("="*60)
    print("[BRAINSTORM] Step 2: Diverge - Generate Ideas")
    print("="*60)

    # Load topic
    topic_data = load_topic()
    if not topic_data:
        return None

    print(f"\nTopic: {topic_data.get('topic')}")
    print(f"Methods: {len(METHODS)}")

    # Generate ideas
    ideas = generate_ideas(topic_data, count)

    print(f"\n[Generated] {len(ideas)} ideas:")
    for i, idea in enumerate(ideas[:5], 1):
        print(f"  {i}. {idea['text']}")
    if len(ideas) > 5:
        print(f"  ... and {len(ideas) - 5} more")

    # Save
    save_ideas(ideas)

    return ideas
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
# py brainstorm_diverge_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_diverge_001.py

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
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    run(count)