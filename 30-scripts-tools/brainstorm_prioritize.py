#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
头脑风暴 Step 7: 优先级排序工具
使用 ICE 或 RICE 方法对想法进行优先级排序
"""

import json
from datetime import datetime
from pathlib import Path

def ice_score(impact, confidence, ease):
    """计算 ICE 分数"""
    return impact * confidence * ease

def run():
    """执行优先级排序"""
    
    print("="*60)
    print("🧠 头脑风暴 Step 7: 优先级排序")
    print("="*60)
    
    # 读取入围想法
    shortlisted_file = Path("flow-archive/brainstorm-current/ideas_shortlisted.json")
    if not shortlisted_file.exists():
        print("❌ 请先运行 brainstorm_filter.py 筛选想法")
        return None
    
    with open(shortlisted_file, encoding="utf-8") as f:
        filter_data = json.load(f)
    
    shortlisted = filter_data.get("shortlisted", [])
    print(f"\n📌 {len(shortlisted)} 个入围想法待排序")
    
    # 选择方法
    print("\n🛠️ 排序方法:")
    print("  1. ICE (Impact, Confidence, Ease)")
    print("  2. RICE (Reach, Impact, Confidence, Effort)")
    method = input("选择方法 (1/2, 默认1): ").strip() or "1"
    
    scored = []
    print("\n📊 评分 (1-10 分):")
    
    for idea in shortlisted:
        text = idea["text"]
        print(f"\n{idea['id']}. {text[:50]}...")
        
        if method == "1":
            impact = int(input("  Impact (影响力): ").strip() or "5")
            confidence = int(input("  Confidence (信心): ").strip() or "5")
            ease = int(input("  Ease (易度): ").strip() or "5")
            score = ice_score(impact, confidence, ease)
        else:
            reach = int(input("  Reach (触达): ").strip() or "5")
            impact = int(input("  Impact (影响): ").strip() or "5")
            confidence = int(input("  Confidence (信心): ").strip() or "5")
            effort = int(input("  Effort (努力): ").strip() or "5")
            score = (reach * impact * confidence) / effort
        
        idea["priority_score"] = score
        idea["method"] = "ICE" if method == "1" else "RICE"
        scored.append(idea)
    
    # 排序
    scored.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # 添加排名
    for i, idea in enumerate(scored, 1):
        idea["rank"] = i
    
    # 保存结果
    result = {
        "step": "prioritize",
        "method": "ICE" if method == "1" else "RICE",
        "ranked_ideas": scored,
        "created_at": datetime.now().isoformat()
    }
    
    output_path = Path("flow-archive/brainstorm-current/ideas_ranked.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 显示结果
    print("\n" + "="*60)
    print("🏆 优先级排名:")
    print("="*60)
    for idea in scored:
        print(f"  #{idea['rank']:2d} (分数:{idea['priority_score']:5.1f}) {idea['text'][:45]}")
    
    print(f"\n📁 已保存到: {output_path}")
    return result

if __name__ == "__main__":
    run()