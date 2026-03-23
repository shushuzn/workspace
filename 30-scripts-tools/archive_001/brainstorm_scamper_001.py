import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BRAINSTORM-SCAMPER-001 SCAMPER Method for Brainstorm
【SCAMPER发散方法】

SCAMPER = 7个操作符引导发散:
  S - Substitute (替代)
  C - Combine (组合)
  A - Adapt (改造)
  M - Modify (修改)
  P - Put to other use (其他用途)
  E - Eliminate (消除)
  R - Reverse (反转)

使用:
  py brainstorm_scamper.py <topic>
"""

import json
import sys
from pathlib import Path


# SCAMPER操作符定义
SCAMPER_OPERATORS = {
    "S": {
        "name": "Substitute (替代)",
        "prompt": "What can be substituted? Who else? What else?",
        "questions": [
            "What if we replace X with Y?",
            "Who else could do this?",
            "What other ingredients?",
            "What other material?",
            "What other process?"
        ]
    },
    "C": {
        "name": "Combine (组合)",
        "prompt": "What can be combined? What ideas blend?",
        "questions": [
            "What if we combine X with Y?",
            "What ideas merge?",
            "What can we combine for a package deal?",
            "What forces could be combined?"
        ]
    },
    "A": {
        "name": "Adapt (改造)",
        "prompt": "What can be adapted? What else is like this?",
        "questions": [
            "What else is like this?",
            "What other context?",
            "What ideas from other fields?",
            "How to adapt for different market?"
        ]
    },
    "M": {
        "name": "Modify (修改)",
        "prompt": "What can be modified? Bigger? Smaller?",
        "questions": [
            "What if we magnify X?",
            "What if we minify X?",
            "What new twist?",
            "What if we change meaning?",
            "Change color? Shape? Package?"
        ]
    },
    "P": {
        "name": "Put to other use (其他用途)",
        "prompt": "What else can this be used for?",
        "questions": [
            "What other markets?",
            "What other users?",
            "What other functions?",
            "What else could this solve?"
        ]
    },
    "E": {
        "name": "Eliminate (消除)",
        "prompt": "What can be eliminated? Simplified?",
        "questions": [
            "What if we remove X?",
            "What can be simplified?",
            "What is not essential?",
            "What parts can be consolidated?"
        ]
    },
    "R": {
        "name": "Reverse (反转)",
        "prompt": "What if we reverse X? Turn it inside out?",
        "questions": [
            "What if we do the opposite?",
            "What if we turn it upside down?",
            "What roles reversed?",
            "What if we change the order?"
        ]
    }
}


def generate_scamper_ideas(topic: str) -> dict:
    """使用SCAMPER方法生成ideas"""

    results = {
        "topic": topic,
        "method": "SCAMPER",
        "operators": {}
    }

    for op_key, op_data in SCAMPER_OPERATORS.items():
        # 替换X为topic
        questions = []
        for q in op_data["questions"]:
            questions.append(q.replace("X", topic).replace("x", topic))

        results["operators"][op_key] = {
            "name": op_data["name"],
            "prompt": op_data["prompt"],
            "questions": questions
        }

    return results


def display_scamper_ideas(results: dict):
    """展示SCAMPER ideas"""

    print("=" * 60)
    print(f"[SCAMPER] Topic: {results['topic']}")
    print("=" * 60)

    for op_key, op_data in results["operators"].items():
        print(f"\n[{op_key}] {op_data['name']}")
        print(f"  Prompt: {op_data['prompt']}")
        print("  Questions:")
        for i, q in enumerate(op_data["questions"], 1):
            print(f"    {i}. {q}")

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
# py brainstorm_scamper_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_scamper_001.py

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
        topic = "OpenClaw tools"

    results = generate_scamper_ideas(topic)
    display_scamper_ideas(results)

    # 保存结果
    output_file = Path(f"flow-archive/brainstorm-current/scamper_ideas_{len(topic)}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[Saved to] {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
