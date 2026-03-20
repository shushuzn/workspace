#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BRAINSTORM-SIXHATS-001 Six Thinking Hats Method
【六顶思考帽发散方法】

六顶帽子的定义:
  白帽 - 客观事实与数据
  红帽 - 情感与直觉
  黑帽 - 批判与风险
  黄帽 - 乐观与收益
  绿帽 - 创意与可能
  蓝帽 - 过程控制与总结

使用:
  py brainstorm_sixhats.py <topic>
"""

import json
import sys
from pathlib import Path


# 六顶帽子定义
SIX_HATS = {
    "WHITE": {
        "name": "White Hat (白帽)",
        "emoji": "[W]",
        "focus": "Facts and Information",
        "questions": [
            "What facts do we know?",
            "What information is missing?",
            "What do we need to find out?",
            "What are the key data points?"
        ]
    },
    "RED": {
        "name": "Red Hat (红帽)",
        "emoji": "[R]",
        "focus": "Emotions and Intuition",
        "questions": [
            "What do I feel about this?",
            "What are my gut reactions?",
            "What does my intuition tell me?",
            "What emotions does this topic evoke?"
        ]
    },
    "BLACK": {
        "name": "Black Hat (黑帽)",
        "emoji": "[B]",
        "focus": "Critical Judgment and Risks",
        "questions": [
            "What are the dangers?",
            "What might go wrong?",
            "What are the weaknesses?",
            "Why might this fail?"
        ]
    },
    "YELLOW": {
        "name": "Yellow Hat (黄帽)",
        "emoji": "[Y]",
        "focus": "Optimism and Benefits",
        "questions": [
            "What are the benefits?",
            "What is the best case scenario?",
            "What value does this create?",
            "Why could this work?"
        ]
    },
    "GREEN": {
        "name": "Green Hat (绿帽)",
        "emoji": "[G]",
        "focus": "Creative and Possibilities",
        "questions": [
            "What are new possibilities?",
            "What are alternatives?",
            "What wild ideas emerge?",
            "What if we think outside the box?"
        ]
    },
    "BLUE": {
        "name": "Blue Hat (蓝帽)",
        "emoji": "[L]",
        "focus": "Process Control and Summary",
        "questions": [
            "What is our next step?",
            "What have we achieved?",
            "How should we proceed?",
            "What summary can we make?"
        ]
    }
}


def generate_sixhats_ideas(topic: str) -> dict:
    """使用六顶思考帽方法生成ideas"""
    
    results = {
        "topic": topic,
        "method": "Six Thinking Hats",
        "hats": {}
    }
    
    for hat_key, hat_data in SIX_HATS.items():
        results["hats"][hat_key] = {
            "name": hat_data["name"],
            "emoji": hat_data["emoji"],
            "focus": hat_data["focus"],
            "questions": [q.replace("this", topic) for q in hat_data["questions"]]
        }
    
    return results


def display_sixhats_ideas(results: dict):
    """展示六顶思考帽ideas"""
    
    print("=" * 60)
    print(f"[SIX HATS] Topic: {results['topic']}")
    print("=" * 60)
    
    for hat_key, hat_data in results["hats"].items():
        print(f"\n{hat_data['emoji']} {hat_data['name']}")
        print(f"   Focus: {hat_data['focus']}")
        print("   Questions:")
        for i, q in enumerate(hat_data["questions"], 1):
            print(f"     {i}. {q}")
    
    print("\n" + "=" * 60)


def main():
    """主函数"""
    
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "OpenClaw tools"
    
    results = generate_sixhats_ideas(topic)
    display_sixhats_ideas(results)
    
    # 保存结果
    output_file = Path(f"flow-archive/brainstorm-current/sixhats_ideas.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Saved to] {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
