#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
头脑风暴 Step 3: 自由联想工具
使用多种方法产生尽可能多的想法 (≥20个)
"""

import json
import random
from datetime import datetime
from pathlib import Path

# 思维方法
METHODS = [
    "SCAMPER法 (替代、组合、改造、改变用途、去除、逆转)",
    "逆向思维 (反其道而行之)",
    "类比思维 (借鉴其他领域)",
    "极端假设 (如果...会怎样)",
    "随机词联想 (随机触发灵感)",
    "用户视角 (从用户角度看问题)",
    "系统拆解 (把问题分解为部件)",
    "趋势外推 (未来可能的发展)"
]

def run():
    """执行自由联想"""
    
    print("="*60)
    print("🧠 头脑风暴 Step 3: 自由联想")
    print("="*60)
    
    # 读取主题
    topic_file = Path("flow-archive/brainstorm-current/brainstorm_topic.json")
    if not topic_file.exists():
        print("❌ 请先运行 brainstorm_define.py 定义问题")
        return None
    
    with open(topic_file, encoding="utf-8") as f:
        topic_data = json.load(f)
    
    print(f"\n📌 主题: {topic_data['topic']}")
    
    # 选择方法
    print("\n🛠️ 思维方法:")
    for i, m in enumerate(METHODS, 1):
        print(f"  {i}. {m}")
    
    selected = input("\n选择方法 (1-8, 逗号分隔, 回车随机): ").strip()
    
    ideas = []
    print("\n💡 请输入想法 (每行一个，输入 '完成' 结束):")
    print("   (目标是 ≥20 个想法)")
    
    count = 0
    while True:
        idea = input(f"  [{count+1}] ").strip()
        if idea in ["完成", "done", "q"]:
            break
        if idea:
            ideas.append(idea)
            count += 1
    
    # 如果不够20个，生成建议
    if len(ideas) < 20:
        print(f"\n⚠️ 当前 {len(ideas)} 个想法，建议继续补充...")
        more = input("继续输入 (y/n)? ").strip().lower()
        if more == "y":
            while True:
                idea = input(f"  [{count+1}] ").strip()
                if idea in ["完成", "done", "q"]:
                    break
                if idea:
                    ideas.append(idea)
                    count += 1
    
    # 保存结果
    result = {
        "step": "divergence",
        "method": selected or "mixed",
        "total_ideas": len(ideas),
        "ideas": [{"id": i+1, "text": t} for i, t in enumerate(ideas)],
        "created_at": datetime.now().isoformat()
    }
    
    output_path = Path("flow-archive/brainstorm-current/ideas_raw.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 产生 {len(ideas)} 个想法")
    print(f"📁 已保存到: {output_path}")
    
    return result

if __name__ == "__main__":
    run()