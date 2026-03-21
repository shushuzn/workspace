#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MULTI-AGENT-ROUTER-001 Smart Task Router
Automatically routes tasks to appropriate personas
"""
import json, sys, re
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

# Persona routing rules
ROUTING = {
    "planner": ["plan", "analyze", "strategy", "roadmap", "设计", "规划", "分析"],
    "executor": ["implement", "code", "build", "create", "run", "执行", "写代码", "实现"],
    "critic": ["review", "check", "validate", "test", "criticize", "审查", "检查", "测试", "验证"],
    "learner": ["learn", "research", "study", "discover", "研究", "学习", "发现"],
    "coordinator": ["orchestrate", "coordinate", "manage", "schedule", "协调", "管理", "调度"],
    "innovator": ["innovate", "creative", "improve", "optimize", "创新", "改进", "优化"],
    "metacognition": ["reflect", "think", "improve", "evaluate", "思考", "反思", "评估"]
}

def analyze_intent(text):
    """Analyze user intent and return best persona match"""
    text_lower = text.lower()
    scores = {p: 0 for p in ROUTING}
    
    for persona, keywords in ROUTING.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[persona] += 1
    
    # Return highest scoring persona
    best = max(scores.items(), key=lambda x: x[1])
    if best[1] == 0:
        return "coordinator"  # Default
    return best[0]

def route_task(task_text, options=None):
    """Route a task and return execution plan"""
    persona = analyze_intent(task_text)
    
    # Build execution plan
    plan = {
        "task": task_text,
        "primary_persona": persona,
        "timestamp": datetime.now().isoformat(),
        "steps": [
            {"persona": "planner", "action": "plan"},
            {"persona": persona, "action": "execute"},
            {"persona": "critic", "action": "review"},
            {"persona": "metacognition", "action": "reflect"}
        ],
        "confidence": 0.8
    }
    
    return plan

def run_cli():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python multi_agent_router_001.py <task>")
        print("\nExamples:")
        print('  python multi_agent_router_001.py "优化代码性能"')
        print('  python multi_agent_router_001.py "分析股票趋势"')
        print('  python multi_agent_router_001.py "设计新功能"')
        return
    
    task = " ".join(sys.argv[1:])
    result = route_task(task)
    
    print(f"\n🔀 Task Router Result")
    print(f"{'='*50}")
    print(f"Task: {result['task']}")
    print(f"Primary Persona: {result['primary_persona'].upper()}")
    print(f"\nExecution Plan:")
    for i, step in enumerate(result['steps'], 1):
        print(f"  {i}. {step['persona'].upper()} → {step['action']}")
    print(f"\nConfidence: {result['confidence']*100}%")

if __name__ == "__main__":
    run_cli()
