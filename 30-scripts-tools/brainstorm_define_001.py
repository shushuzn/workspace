#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Step 1: Problem Definition
Define the topic, context, constraints and expected output
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Disable Unicode buffering issues on Windows
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def run(topic_arg=None):
    """Execute problem definition"""
    
    print("="*60)
    print("[BRAINSTORM] Step 1: Problem Definition")
    print("="*60)
    
    # Use argument or default
    if topic_arg:
        topic = topic_arg
    else:
        topic = "New tools for OpenClaw"
    
    background = ""
    constraints = ""
    expected = ""
    
    # Build result
    result = {
        "step": "problem_definition",
        "topic": topic,
        "background": background or "Not provided",
        "constraints": constraints or "None",
        "expected_output": expected or "Idea list",
        "created_at": datetime.now().isoformat()
    }
    
    # Save file
    output_path = Path("flow-archive/brainstorm-current/brainstorm_topic.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Saved] {output_path}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

if __name__ == "__main__":
    # Get topic from command line or input
    topic = None
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    run(topic)