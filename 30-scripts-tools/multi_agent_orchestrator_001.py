#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MULTI-AGENT-ORCHESTRATOR-001 Unified Multi-Agent Orchestrator
Integrates all multi-agent capabilities with workflow system
"""
import json, sys, subprocess
from pathlib import Path
from datetime import datetime

PERSONAS = ["planner", "executor", "critic", "learner", "coordinator", "innovator", "metacognition"]
WORKFLOWS_FILE = Path("30-scripts-tools/workflows.json")

ROUTING = {
    "planner": ["plan", "analyze", "strategy", "roadmap", "设计", "规划", "分析"],
    "executor": ["implement", "code", "build", "create", "run", "执行", "写代码", "实现"],
    "critic": ["review", "check", "validate", "test", "审查", "检查", "测试", "验证"],
    "learner": ["learn", "research", "study", "discover", "研究", "学习", "发现"],
    "coordinator": ["orchestrate", "coordinate", "manage", "schedule", "协调", "管理", "调度"],
    "innovator": ["innovate", "creative", "improve", "optimize", "创新", "改进", "优化"],
    "metacognition": ["reflect", "think", "improve", "evaluate", "思考", "反思", "评估"]
}

STATS_FILE = Path("13-memory/.workflow_logs/master.json")
LEARN_FILE = Path("13-memory/.multi_agent_learn/collaboration_history.json")

def ensure_dir(p):
    p.mkdir(parents=True, exist_ok=True)

def analyze_intent(text):
    text_lower = text.lower()
    scores = {p: 0 for p in ROUTING}
    for persona, keywords in ROUTING.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[persona] += 1
    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "coordinator"

def load_learn_history():
    if LEARN_FILE.exists():
        return json.loads(LEARN_FILE.read_text(encoding="utf-8", errors="replace"))
    return {"persona_scores": {}}

def save_learn_history(history):
    ensure_dir(LEARN_FILE.parent)
    LEARN_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

def get_best_persona(task_text):
    history = load_learn_history()
    scores = {}
    keywords = task_text.lower().split()
    for keyword in keywords:
        for persona, pscores in history.get("persona_scores", {}).items():
            if keyword in pscores:
                scores[persona] = scores.get(persona, 0) + pscores[keyword]
    if not scores:
        return analyze_intent(task_text)
    return max(scores.items(), key=lambda x: x[1])[0]

def record_outcome(task, persona, success, keywords):
    history = load_learn_history()
    if "persona_scores" not in history:
        history["persona_scores"] = {}
    for kw in keywords:
        if persona not in history["persona_scores"]:
            history["persona_scores"][persona] = {}
        if kw not in history["persona_scores"][persona]:
            history["persona_scores"][persona][kw] = 0
        if success:
            history["persona_scores"][persona][kw] += 1
        else:
            history["persona_scores"][persona][kw] -= 0.5
    save_learn_history(history)

def orchestrate_task(task_text):
    print("\n[MULTI-AGENT ORCHESTRATOR]")
    print("=" * 50)
    
    print("\n[1] Intent Analysis...")
    intent = analyze_intent(task_text)
    print(f"    Detected: {intent.upper()}")
    
    print("\n[2] Smart Routing...")
    best_persona = get_best_persona(task_text)
    print(f"    Best Persona: {best_persona.upper()} (learned)")
    
    print("\n[3] Execution Plan:")
    steps = [
        {"persona": "planner", "action": "plan"},
        {"persona": best_persona, "action": "execute"},
        {"persona": "critic", "action": "review"},
        {"persona": "metacognition", "action": "reflect"}
    ]
    for i, step in enumerate(steps, 1):
        print(f"    {i}. {step['persona'].upper()} -> {step['action']}")
    
    print("\n[4] Executing via Workflow...")
    wf_map = {
        "planner": "plan", "executor": "dev", "critic": "security",
        "learner": "research", "coordinator": "full", "innovator": "quick",
        "metacognition": "plan"
    }
    wf_id = wf_map.get(best_persona, "quick")
    
    try:
        result = subprocess.run(
            ["python", "30-scripts-tools/workflow_master_001.py", "--run", wf_id],
            capture_output=True, text=True, timeout=60
        )
        success = result.returncode == 0
        print(f"    Workflow '{wf_id}': {'OK' if success else 'FAIL'}")
    except Exception as e:
        success = False
        print(f"    Error: {e}")
    
    print("\n[5] Recording Outcome...")
    keywords = task_text.lower().split()[:5]
    record_outcome(task_text, best_persona, success, keywords)
    
    print("\n" + "=" * 50)
    print("[COMPLETE] Orchestration done")
    return {"intent": intent, "persona": best_persona, "success": success}

def run_visualization():
    stats = {}
    if STATS_FILE.exists():
        stats = json.loads(STATS_FILE.read_text(encoding="utf-8", errors="replace"))
    runs = stats.get("runs", [])
    
    print("\n[MULTI-AGENT COLLABORATION STATUS]")
    print("=" * 50)
    print(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    print("""
         [PLANNER]
              |
    [CRITIC]--+--[EXECUTOR]
              |
      [COORDINATOR]
         |     |
   [LEARNER] [INNOVATOR]
              |
      [METACOGNITION]
    """)
    print(f"Total Executions: {len(runs)}")
    print("=" * 50)

def generate_report():
    history = load_learn_history()
    print("\n[MULTI-AGENT LEARNING REPORT]")
    print("=" * 50)
    print(f"Patterns Learned: {len(history.get('persona_scores', {}))}")
    print("\nTop Combinations:")
    
    combos = []
    for persona, task_scores in history.get("persona_scores", {}).items():
        for task, score in task_scores.items():
            if score > 0:
                combos.append((persona, task, score))
    
    combos.sort(key=lambda x: x[2], reverse=True)
    for persona, task, score in combos[:5]:
        print(f"  {persona.upper():12} + {task:15} = {score:.1f}")
    print("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[MULTI-AGENT ORCHESTRATOR v1.0]")
        print("Usage: python multi_agent_orchestrator_001.py <task>")
        print("       python multi_agent_orchestrator_001.py --viz")
        print("       python multi_agent_orchestrator_001.py --report")
        print("\nExamples:")
        print('  python multi_agent_orchestrator_001.py "优化代码性能"')
        print('  python multi_agent_orchestrator_001.py --viz')
    else:
        cmd = sys.argv[1]
        if cmd == "--viz":
            run_visualization()
        elif cmd == "--report":
            generate_report()
        else:
            task = " ".join(sys.argv[1:])
            orchestrate_task(task)
