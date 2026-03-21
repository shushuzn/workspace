import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
头脑风暴 Step 8: 行动规划工具
将优先级想法转化为可执行的行动计划
"""

import json
from datetime import datetime
from pathlib import Path

def run():
    """执行行动规划"""
    
    print("="*60)
    print("🧠 头脑风暴 Step 8: 行动规划")
    print("="*60)
    
    # 读取排序结果
    ranked_file = Path("flow-archive/brainstorm-current/ideas_ranked.json")
    if not ranked_file.exists():
        print("❌ 请先运行 brainstorm_prioritize.py 排序想法")
        return None
    
    with open(ranked_file, encoding="utf-8") as f:
        ranked_data = json.load(f)
    
    ranked = ranked_data.get("ranked_ideas", [])
    print(f"\n📌 {len(ranked)} 个已排序想法")
    
    # 取前 3 名
    top_ideas = ranked[:3]
    
    actions = []
    print("\n🚀 为每个想法制定行动计划:")
    
    for idea in top_ideas:
        print(f"\n--- #{idea['rank']}: {idea['text'][:50]} ---")
        
        # 分解行动
        print("  分解为具体行动 (每行一个，输入 '完成' 结束):")
        steps = []
        while True:
            step = input("    > ").strip()
            if step in ["完成", "done", "q"]:
                break
            if step:
                steps.append(step)
        
        # 负责人和时间
        owner = input("  负责人: ").strip() or "待定"
        timeline = input("  时间线: ").strip() or "待定"
        
        action = {
            "rank": idea["rank"],
            "idea": idea["text"],
            "steps": steps,
            "owner": owner,
            "timeline": timeline,
            "priority": idea["priority_score"]
        }
        actions.append(action)
    
    # 保存结果
    result = {
        "step": "action_plan",
        "top_ideas_count": len(top_ideas),
        "actions": actions,
        "created_at": datetime.now().isoformat()
    }
    
    output_path = Path("flow-archive/brainstorm-current/action_plan.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 显示摘要
    print("\n" + "="*60)
    print("📋 行动摘要:")
    print("="*60)
    for action in actions:
        print(f"\n#{action['rank']}: {action['idea'][:50]}")
        print(f"  负责人: {action['owner']} | 时间: {action['timeline']}")
        print(f"  行动: {' -> '.join(action['steps'][:3])}")
    
    print(f"\n✅ 行动规划完成")
    print(f"📁 已保存到: {output_path}")
    return result

if __name__ == "__main__":
    run()