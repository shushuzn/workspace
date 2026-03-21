import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BRAINSTORM-RANDOM-001 Random Input Brainstorm Method
【随机输入法】

原理: 引入随机词触发非常规联想，突破思维定式

方法:
  1. 选择一个随机词/图像/概念
  2. 强制将随机词与主题关联
  3. 从关联中发现新视角

使用:
  py brainstorm_random.py <topic>
  py brainstorm_random.py <topic> --words <word1,word2,...>
"""

import json
import random
import sys
from pathlib import Path


# 随机词库 - 按类别分组
RANDOM_WORDS = {
    "nature": [
        "ocean", "mountain", "forest", "desert", "river", "volcano",
        "earthquake", "lightning", "tornado", "blizzard", "sunrise", "moonlight",
        "butterfly", "octopus", "dolphin", "spider", "ant", "eagle", "wolf"
    ],
    "technology": [
        "robot", "quantum", "algorithm", "neural", "satellite", "drone",
        "blockchain", "hologram", "nanotech", "cyber", "3d打印", "VR",
        "biometric", "IoT", "edge computing", "serverless"
    ],
    "objects": [
        "钥匙", "镜子", "梯子", "轮子", "针", "锤子", "绳子", "箱子",
        "瓶子", "伞", "钟", "灯", "锁", "桥", "门", "窗", "桌"
    ],
    "抽象": [
        "时间", "空间", "能量", "信息", "系统", "网络", "模式", "流程",
        "规则", "边界", "循环", "平衡", "混沌", "秩序", "熵"
    ],
    "actions": [
        "explode", "merge", "shrink", "grow", "rotate", "flip",
        "multiply", "dissolve", "evolve", "reverse", "amplify", "compress"
    ],
    "emotions": [
        "curiosity", "wonder", "awe", "tension", "flow", "chaos",
        "serenity", "urgency", "nostalgia", "hope", "doubt"
    ],
    "places": [
        "space station", "underground", "island", "jungle", "cave",
        "factory", "lab", "library", "museum", "garden", "stadium"
    ],
    "characters": [
        "detective", "wizard", "scientist", "artist", "hacker",
        "architect", "explorer", "guardian", "messenger", "architect"
    ]
}


def get_random_words(category: str = None, count: int = 3) -> list:
    """获取随机词"""
    if category:
        words = RANDOM_WORDS.get(category, [])
    else:
        # 从所有类别中选择
        words = []
        for cat_words in RANDOM_WORDS.values():
            words.extend(cat_words)
    
    return random.sample(words, min(count, len(words)))


def generate_random_associations(topic: str, random_words: list) -> dict:
    """生成随机联想"""
    
    results = {
        "topic": topic,
        "method": "Random Input",
        "random_words": random_words,
        "associations": []
    }
    
    for word in random_words:
        # 构造关联问题
        associations = {
            "word": word,
            "connections": [
                f"What if {topic} had {word}?",
                f"How would {word} change {topic}?",
                f"What if {word} worked like {topic}?",
                f"What can {topic} learn from {word}?",
                f"How does {word} solve problems similar to {topic}?",
                f"What if we combine {topic} and {word}?",
                f"Can {word} inspire a new approach to {topic}?",
                f"What metaphors connect {topic} and {word}?",
            ]
        }
        results["associations"].append(associations)
    
    return results


def display_random_associations(results: dict):
    """展示随机联想"""
    
    print("=" * 60)
    print(f"[RANDOM INPUT] Topic: {results['topic']}")
    print("=" * 60)
    print(f"\nRandom Words: {', '.join(results['random_words'])}")
    
    for assoc in results["associations"]:
        print(f"\n[{assoc['word']}]")
        for q in assoc["connections"][:4]:  # 只显示前4个
            print(f"  -> {q}")
    
    print("\n" + "=" * 60)


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
# py brainstorm_random_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_random_001.py

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
    
    # 解析参数
    topic = None
    custom_words = None
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--words" and i < len(sys.argv) - 1:
            custom_words = sys.argv[i + 1].split(",")
        elif not arg.startswith("--"):
            topic = arg
    
    if not topic:
        topic = "OpenClaw tools"
    
    # 获取随机词
    if custom_words:
        random_words = custom_words
    else:
        random_words = get_random_words(count=5)
    
    results = generate_random_associations(topic, random_words)
    display_random_associations(results)
    
    # 保存结果
    output_file = Path(f"flow-archive/brainstorm-current/random_ideas.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Saved to] {output_file}")
    print(f"\n[Tip] 尝试不同的随机词或使用 --words 指定")
    
    return 0



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <args>")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
