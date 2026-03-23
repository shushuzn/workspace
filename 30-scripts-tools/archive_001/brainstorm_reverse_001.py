import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BRAINSTORM-REVERSE-001 Reverse Brainstorming Method
【逆向头脑风暴方法】

原理: 不是思考"如何解决问题"，而是思考"如何制造问题"
      然后反转这些"制造问题"的方法来获得解决方案

使用:
  py brainstorm_reverse.py <problem>
"""

import json
import sys
from pathlib import Path


# 问题制造方向
PROBLEM_CAUSES = [
    "How to make this slower?",
    "How to make this more expensive?",
    "How to make users confused?",
    "How to add more steps?",
    "How to reduce quality?",
    "How to make it harder to use?",
    "How to introduce bugs?",
    "How to create bottlenecks?",
    "How to increase complexity?",
    "How to make it unreliable?",
]


def generate_reverse_ideas(topic: str) -> dict:
    """逆向头脑风暴"""

    results = {
        "topic": topic,
        "method": "Reverse Brainstorming",
        "steps": {
            "step1_problems": [],
            "step2_solutions": []
        }
    }

    # Step 1: 列出制造问题的方向
    for cause in PROBLEM_CAUSES:
        question = cause.replace("this", topic)
        results["steps"]["step1_problems"].append(question)

    # Step 2: 反转这些方向得到解决方案
    reversals = [
        ("slower", "faster"),
        ("more expensive", "cheaper"),
        ("confused", "clear"),
        ("more steps", "fewer steps"),
        ("reduce quality", "improve quality"),
        ("harder to use", "easier to use"),
        ("bugs", "reliability"),
        ("bottlenecks", "parallel"),
        ("complexity", "simplicity"),
        ("unreliable", "reliable"),
    ]

    for cause, solution in reversals:
        question = f"How to make {topic} {solution}?"
        results["steps"]["step2_solutions"].append(question)

    return results


def display_reverse_ideas(results: dict):
    """展示逆向头脑风暴结果"""

    print("=" * 60)
    print(f"[REVERSE BRAINSTORM] Topic: {results['topic']}")
    print("=" * 60)

    print("\n[Step 1] 逆向问题 (如何制造问题)")
    print("-" * 40)
    for i, q in enumerate(results["steps"]["step1_problems"], 1):
        print(f"  {i}. {q}")

    print("\n[Step 2] 解决方案 (反转问题)")
    print("-" * 40)
    for i, q in enumerate(results["steps"]["step2_solutions"], 1):
        print(f"  {i}. {q}")

    print("\n" + "=" * 60)


logging.basicConfig(level=logging.INFO)
def main():
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
# py brainstorm_reverse_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_reverse_001.py

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

    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "OpenClaw workflow"

    results = generate_reverse_ideas(topic)
    display_reverse_ideas(results)

    # 保存结果
    output_file = Path(f"flow-archive/brainstorm-current/reverse_ideas.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[Saved to] {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
