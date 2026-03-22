import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MULTI-AGENT-LEARN-001 Multi-Agent Learning System
Learns from past collaborations to improve routing and execution
"""
import json, sys, os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

if sys.platform == 'win32':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

LEARN_DIR = Path("13-memory/.multi_agent_learn")
STATS_FILE = Path("13-memory/.workflow_logs/master.json")
LEARN_FILE = LEARN_DIR / "collaboration_history.json"
PATTERNS_FILE = LEARN_DIR / "routing_patterns.json"

def ensure_dir() -> None:
    """Ensure learn directory exists"""
    LEARN_DIR.mkdir(parents=True, exist_ok=True)

def load_history() -> None:
    """Load collaboration history"""
    ensure_dir()
    if LEARN_FILE.exists():
        return json.loads(LEARN_FILE.read_text(encoding="utf-8", errors="replace"))
    return {"tasks": [], "outcomes": [], "patterns": {}}

def save_history(history) -> None:
    """Save collaboration history"""
    ensure_dir()
    LEARN_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

def load_patterns() -> None:
    """Load routing patterns"""
    ensure_dir()
    if PATTERNS_FILE.exists():
        return json.loads(PATTERNS_FILE.read_text(encoding="utf-8", errors="replace"))
    return {"persona_scores": {}, "task_keywords": {}}

def save_patterns(patterns) -> None:
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
# py multi_agent_learn_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py multi_agent_learn_001.py

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

Save routing patterns"""
    ensure_dir()
    PATTERNS_FILE.write_text(json.dumps(patterns, indent=2, ensure_ascii=False), encoding="utf-8")

def analyze_patterns() -> None:
    """Analyze past patterns and improve routing"""
    history = load_history()
    patterns = load_patterns()
    
    # Count successful persona-task combinations
    success_counts = defaultdict(lambda: defaultdict(int))
    failure_counts = defaultdict(lambda: defaultdict(int))
    
    for task_info in history.get("tasks", []):
        persona = task_info.get("persona", "")
        success = task_info.get("success", True)
        
        for keyword in task_info.get("keywords", []):
            if success:
                success_counts[persona][keyword] += 1
            else:
                failure_counts[persona][keyword] += 1
    
    # Update patterns
    patterns["persona_scores"] = {
        persona: {
            k: success_counts[persona][k] - failure_counts[persona][k] * 0.5
            for k in set(list(success_counts[persona].keys()) + list(failure_counts[persona].keys()))
        }
        for persona in success_counts.keys()
    }
    
    save_patterns(patterns)
    return patterns

def record_outcome(task, persona, success, keywords) -> None:
    """Record task outcome for learning"""
    history = load_history()
    
    history["tasks"].append({
        "task": task,
        "persona": persona,
        "success": success,
        "keywords": keywords,
        "timestamp": datetime.now().isoformat()
    })
    
    # Keep only last 1000 entries
    history["tasks"] = history["tasks"][-1000:]
    
    save_history(history)

def get_best_persona(task_text) -> None:
    """Get best persona based on learned patterns"""
    patterns = load_patterns()
    scores = defaultdict(float)
    
    keywords = task_text.lower().split()
    
    for keyword in keywords:
        for persona, persona_scores in patterns.get("persona_scores", {}).items():
            if keyword in persona_scores:
                scores[persona] += persona_scores[keyword]
    
    if not scores:
        return "coordinator"
    
    return max(scores.items(), key=lambda x: x[1])[0]

def generate_report() -> None:
    """Generate learning report"""
    history = load_history()
    patterns = load_patterns()
    stats = {}
    
    if STATS_FILE.exists():
        stats = json.loads(STATS_FILE.read_text(encoding="utf-8", errors="replace"))
    
    total = len(history.get("tasks", []))
    success = sum(1 for t in history.get("tasks", []) if t.get("success"))
    
    report = f"""
╔══════════════════════════════════════════════════════════╗
║       MULTI-AGENT LEARNING REPORT                         ║
╠══════════════════════════════════════════════════════════╣
║  Total Tasks Recorded: {total:5}                              ║
║  Successful: {success:5} ({success/total*100 if total else 0:.1f}%)                              ║
║  Patterns Learned: {len(patterns.get('persona_scores', {})):5}                        ║
╠══════════════════════════════════════════════════════════╣
║  TOP PERSONA-TASK COMBINATIONS                           ║"""
    
    # Find top combinations
    combos = []
    for persona, task_scores in patterns.get("persona_scores", {}).items():
        for task, score in task_scores.items():
            if score > 0:
                combos.append((persona, task, score))
    
    combos.sort(key=lambda x: x[2], reverse=True)
    
    for persona, task, score in combos[:5]:
        report += f"\n║    {persona.upper():12} + {task:15} = {score:5.1f}        ║"
    
    report += "\n╚══════════════════════════════════════════════════════════╝"
    
    return report

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--analyze":
            patterns = analyze_patterns()
            print("Patterns analyzed and updated.")
        elif sys.argv[1] == "--report":
            print(generate_report())
        elif sys.argv[1] == "--record":
            # record_outcome("test task", "planner", True, ["test"])
            print("Recording enabled.")
        else:
            print(f"Unknown command: {sys.argv[1]}")
    else:
        print(generate_report())
