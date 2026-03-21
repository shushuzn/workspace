#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MULTI-AGENT-VIZ-001 Collaboration Visualizer
Visualize multi-agent collaboration status
"""
import json, sys
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

PERSONAS = ["planner", "executor", "critic", "learner", "coordinator", "innovator", "metacognition"]
STATS_FILE = Path("13-memory/.workflow_logs/master.json")

def load_stats():
    """Load workflow execution stats"""
    if not STATS_FILE.exists():
        return {}
    return json.loads(STATS_FILE.read_text(encoding="utf-8", errors="replace"))

def generate_ascii():
    """Generate ASCII art visualization"""
    stats = load_stats()
    runs = stats.get("runs", [])
    
    # Count persona usage
    usage = {p: 0 for p in PERSONAS}
    for run in runs:
        tool = run.get("tool", "")
        for p in PERSONAS:
            if p in tool.lower():
                usage[p] += 1
    
    output = []
    output.append("\n" + "="*60)
    output.append("  MULTI-AGENT COLLABORATION STATUS")
    output.append("="*60)
    output.append(f"\n  Updated: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # ASCII persona diagram
    output.append("         [PLANNER]")
    output.append("              ↑↓")
    output.append("    [CRITIC] ← → [EXECUTOR]")
    output.append("              ↑↓")
    output.append("      [COORDINATOR]")
    output.append("         ↕     ↕")
    output.append("   [LEARNER] [INNOVATOR]")
    output.append("              ↑")
    output.append("      [METACOGNITION]")
    
    # Usage stats
    output.append("\n" + "-"*60)
    output.append("  PERSONA USAGE STATS")
    output.append("-"*60)
    
    max_usage = max(usage.values()) if usage.values() else 1
    for p in PERSONAS:
        bar_len = int(usage[p] / max_usage * 30) if max_usage > 0 else 0
        bar = "█" * bar_len
        pct = (usage[p] / len(runs) * 100) if runs else 0
        output.append(f"  {p.upper():15} {bar:30} {usage[p]:3} ({pct:.1f}%)")
    
    output.append("-"*60)
    output.append(f"  Total Executions: {len(runs)}")
    output.append("="*60 + "\n")
    
    return "\n".join(output)

def generate_json():
    """Generate JSON status"""
    stats = load_stats()
    runs = stats.get("runs", [])
    
    return json.dumps({
        "status": "active",
        "personas": PERSONAS,
        "total_executions": len(runs),
        "timestamp": datetime.now().isoformat()
    }, indent=2)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(generate_json())
    else:
        print(generate_ascii())
