#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
头脑风暴 Step 5: 初步筛选工具
从大量想法中选出有潜力的入围想法 (≥5个)
"""

import json
from datetime import datetime
from pathlib import Path

def run():
    """执行初步筛选"""
    
    print("="*60)
    print("🧠 头脑风暴 Step 5: 初步筛选")
    print("="*60)
    
    # 读取想法
    ideas_file = Path("flow-archive/brainstorm-current/ideas_raw.json")
    if not ideas_file.exists():
        print("❌ 请先运行 brainstorm_diverge.py 产生想法")
        return None
    
    with open(ideas_file, encoding="utf-8") as f:
        ideas_data = json.load(f)
    
    ideas = ideas_data.get("ideas", [])
    print(f"\n📌 共 {len(ideas)} 个想法需要筛选")
    
    # 展示想法
    print("\n想法列表:")
    for idea in ideas:
        print(f"  {idea['id']:2d}. {idea['text'][:60]}")
    
    # 选择入围
    print("\n✂️ 初步筛选:")
    print("  输入入围想法的编号 (逗号分隔，如: 1,3,5,8)")
    print("  或输入 'all' 全部入围")
    
    selection = input("\n选择: ").strip()
    
    if selection.lower() == "all":
        shortlisted = ideas
    else:
        try:
            ids = [int(x.strip()) for x in selection.split(",")]
            shortlisted = [i for i in ideas if i["id"] in ids]
        except:
            print("❌ 输入格式错误")
            return None
    
    # 快速评估
    print("\n📊 快速评估 (可选，输入 1-5 分或回车跳过):")
    for idea in shortlisted:
        score = input(f"  {idea['id']}. {idea['text'][:40]}... : ").strip()
        if score.isdigit() and 1 <= int(score) <= 5:
            idea["quick_score"] = int(score)
    
    # 保存结果
    result = {
        "step": "filter",
        "total_candidates": len(ideas),
        "shortlisted": shortlisted,
        "shortlisted_count": len(shortlisted),
        "created_at": datetime.now().isoformat()
    }
    
    output_path = Path("flow-archive/brainstorm-current/ideas_shortlisted.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 入围 {len(shortlisted)} 个想法")
    print(f"📁 已保存到: {output_path}")
    
    return result

if __name__ == "__main__":
    run()