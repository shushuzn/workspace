import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BRAINSTORM-NEXT-001 Next Step Advisor
【下一步建议器】

根据当前头脑风暴状态，推荐下一步该做什么

使用:
  py brainstorm_next.py
  py brainstorm_next.py --status
"""

import json
import sys
from pathlib import Path
from datetime import datetime


# 工作流步骤定义
WORKFLOW_STEPS = {
    "define": {
        "step": 1,
        "name": "问题定义",
        "file": "brainstorm_001_define.py",
        "next": "diverge",
        "tip": "清晰的问题定义是成功头脑风暴的一半"
    },
    "diverge": {
        "step": 2,
        "name": "发散思维",
        "file": "brainstorm_002_diverge.py",
        "next": "filter",
        "tip": "数量胜于质量，先发散再收敛"
    },
    "filter": {
        "step": 3,
        "name": "过滤筛选",
        "file": "brainstorm_003_filter.py",
        "next": "prioritize",
        "tip": "选择最有潜力的想法继续"
    },
    "prioritize": {
        "step": 4,
        "name": "排序规划",
        "file": "brainstorm_004_prioritize.py",
        "next": "implement",
        "tip": "确定优先级，开始执行第一个想法"
    },
    "implement": {
        "step": 5,
        "name": "执行落地",
        "file": None,
        "next": "review",
        "tip": "动手实现，迭代改进"
    },
    "review": {
        "step": 6,
        "name": "复盘总结",
        "file": None,
        "next": "define",
        "tip": "总结经验教训，为下一轮做准备"
    }
}


# 方法推荐矩阵
METHOD_RECOMMENDATIONS = {
    "define": ["--refine", "--scamper"],
    "diverge": ["--scamper", "--sixhats", "--random", "--analogy", "--reverse"],
    "filter": [],
    "prioritize": [],
    "implement": [],
    "review": []
}


def get_current_status() -> dict:
    """获取当前状态"""
    base = Path("flow-archive/brainstorm-current")
    
    status = {
        "topic": None,
        "steps_completed": [],
        "next_step": "define",
        "current_phase": None
    }
    
    # 检查各步骤文件
    if (base / "brainstorm_topic.json").exists():
        status["steps_completed"].append("define")
        with open(base / "brainstorm_topic.json", encoding="utf-8") as f:
            data = json.load(f)
            status["topic"] = data.get("topic")
    
    if (base / "brainstorm_ideas_raw.json").exists():
        status["steps_completed"].append("diverge")
    
    if (base / "brainstorm_ideas_filtered.json").exists():
        status["steps_completed"].append("filter")
    
    if (base / "brainstorm_ideas_prioritized.json").exists():
        status["steps_completed"].append("prioritize")
    
    # 确定下一步
    for step in ["define", "diverge", "filter", "prioritize", "implement", "review"]:
        if step not in status["steps_completed"]:
            status["next_step"] = step
            status["current_phase"] = step
            break
    
    return status


def generate_recommendations(status: dict) -> dict:
    """生成建议"""
    
    recommendations = {
        "status": status,
        "suggestions": [],
        "methods": [],
        "command": None
    }
    
    next_step = status["next_step"]
    
    # 主流程建议
    if next_step in WORKFLOW_STEPS:
        step_info = WORKFLOW_STEPS[next_step]
        recommendations["suggestions"].append({
            "type": "main",
            "priority": 1,
            "message": f"[主流程] 下一步: {step_info['name']}",
            "tip": step_info['tip'],
            "command": f"py brainstorm_workflow.py --step {step_info['step']}"
        })
        
        # 方法推荐
        if next_step in METHOD_RECOMMENDATIONS:
            methods = METHOD_RECOMMENDATIONS[next_step]
            for method in methods:
                recommendations["methods"].append(method)
    
    # 如果已完成基本流程，推荐高级方法
    if next_step == "implement":
        recommendations["suggestions"].append({
            "type": "enhancement",
            "priority": 2,
            "message": "[建议] 完成后可用以下方法继续发散",
            "methods": ["--scamper", "--sixhats", "--random", "--analogy", "--reverse"]
        })
    
    # 如果有topic但还在早期，推荐多种方法
    if status["topic"] and next_step in ["define", "diverge"]:
        recommendations["suggestions"].append({
            "type": "method",
            "priority": 3,
            "message": "[可选] 使用不同方法探索同一topic",
            "methods": ["--scamper", "--sixhats", "--random", "--analogy"]
        })
    
    return recommendations


def display_next_step(recommendations: dict):
    """显示下一步"""
    
    status = recommendations["status"]
    
    print("=" * 60)
    print("[NEXT STEP] Brainstorm Workflow Advisor")
    print("=" * 60)
    
    # 当前状态
    print(f"\n[Status]")
    print(f"  Topic: {status['topic'] or 'Not set'}")
    print(f"  Completed: {', '.join(status['steps_completed']) or 'None'}")
    print(f"  Next: {status['next_step']}")
    
    # 建议
    print(f"\n[Recommendations]")
    for suggestion in recommendations["suggestions"]:
        print(f"\n  [{suggestion['priority']}] {suggestion['message']}")
        if suggestion.get("tip"):
            print(f"      Tip: {suggestion['tip']}")
        if suggestion.get("command"):
            print(f"      Command: {suggestion['command']}")
        if suggestion.get("methods"):
            print(f"      Methods: {', '.join(suggestion['methods'])}")
    
    # 快速执行命令
    if status["next_step"] in WORKFLOW_STEPS:
        step_info = WORKFLOW_STEPS[status["next_step"]]
        if step_info["step"] <= 4:
            recommendations["command"] = f"py brainstorm_workflow.py --step {step_info['step']}"
    
    print("\n" + "=" * 60)
    
    # 快速命令
    if recommendations.get("command"):
        print(f"\n[Quick Command]")
        print(f"  {recommendations['command']}")
    
    # 完整方法列表
    print(f"\n[All Methods]")
    print("  --step N       Continue workflow step N")
    print("  --scamper      SCAMPER method")
    print("  --sixhats      Six Thinking Hats")
    print("  --reverse      Reverse Brainstorming")
    print("  --random       Random Input")
    print("  --analogy      Analogy Thinking")
    print("  --refine       Auto-refine Problem")


logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py brainstorm_next_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_next_001.py

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

主函数"""
    
    status = get_current_status()
    recommendations = generate_recommendations(status)
    display_next_step(recommendations)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
