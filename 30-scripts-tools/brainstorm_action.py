#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Action - 行动规划工具

目标：将想法转化为可执行任务
输出：action_plan.md
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 配置 UTF-8 输出
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = Path("30-scripts-tools")
MATRIX_FILE = OUTPUT_DIR / "priority_matrix.json"
ACTION_FILE = OUTPUT_DIR / "action_plan.md"

def load_matrix():
    if not MATRIX_FILE.exists():
        print("⚠️  未找到优先级矩阵，请先运行排序工具")
        return None
    
    with open(MATRIX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_action_plan(matrix_data):
    """创建行动计划"""
    print(f"\n{'='*60}")
    print("📋 创建行动计划")
    print(f"{'='*60}\n")
    
    p0_ideas = matrix_data["matrix"].get("P0", [])
    p1_ideas = matrix_data["matrix"].get("P1", [])
    
    # 选择 Top 3
    top_ideas = []
    if p0_ideas:
        top_ideas.extend(sorted(p0_ideas, key=lambda x: x['total'], reverse=True)[:2])
    if p1_ideas and len(top_ideas) < 3:
        top_ideas.extend(sorted(p1_ideas, key=lambda x: x['total'], reverse=True)[:1])
    
    if not top_ideas:
        print("⚠️  没有高优先级想法，请重新头脑风暴")
        return None
    
    print(f"选择 Top {len(top_ideas)} 想法进行规划:\n")
    for i, idea in enumerate(top_ideas, 1):
        print(f"  {i}. {idea['name']} (总分:{idea['total']})")
    
    # 为每个想法创建行动计划
    actions = []
    for idea in top_ideas:
        print(f"\n--- 规划：{idea['name']} ---")
        next_step = input("下一步行动 (具体可执行): ").strip() or "待定"
        resources = input("所需资源: ").strip() or "待定"
        time_estimate = input("时间估算 (小时/天): ").strip() or "待定"
        
        actions.append({
            "idea": idea['name'],
            "priority": "P0" if idea in p0_ideas else "P1",
            "next_step": next_step,
            "resources": resources,
            "time_estimate": time_estimate,
            "status": "planned"
        })
    
    return actions

def save_action_plan(actions, matrix_data):
    """保存行动计划"""
    content = f"""# 头脑风暴行动计划

**主题:** 头脑风暴  
**日期:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**状态:** 规划完成

---

## 🎯 Top 优先级想法

"""
    
    for i, action in enumerate(actions, 1):
        priority_icon = "🔴" if action['priority'] == "P0" else "🟡"
        content += f"### {i}. {priority_icon} {action['idea']}\n\n"
        content += f"- **下一步:** {action['next_step']}\n"
        content += f"- **资源:** {action['resources']}\n"
        content += f"- **时间:** {action['time_estimate']}\n"
        content += f"- **状态:** {action['status']}\n\n"
    
    content += f"""---

## 📊 优先级矩阵摘要

- P0 (立即执行): {matrix_data['summary']['P0_count']} 个
- P1 (规划执行): {matrix_data['summary']['P1_count']} 个
- P2 (可选执行): {matrix_data['summary']['P2_count']} 个
- P3 (暂不执行): {matrix_data['summary']['P3_count']} 个

---

## ✅ 验收标准

- [ ] Top 想法已明确下一步行动
- [ ] 资源需求已识别
- [ ] 时间估算合理
- [ ] 责任人已指定 (如适用)

---

*生成工具：brainstorm_action.py*
"""
    
    with open(ACTION_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 行动计划已保存：{ACTION_FILE}")

def main():
    print(f"{'='*60}")
    print("📋 行动规划")
    print(f"{'='*60}\n")
    
    matrix_data = load_matrix()
    if not matrix_data:
        return
    
    actions = create_action_plan(matrix_data)
    if not actions:
        return
    
    save_action_plan(actions, matrix_data)
    
    print(f"\n{'='*60}")
    print("✅ 行动规划完成")
    print(f"{'='*60}")
    print(f"\n💡 下一步:")
    print(f"  1. 执行 Top 想法的下一步行动")
    print(f"  2. 使用通用工作流跟踪进度")
    print(f"  3. 定期回顾和更新")

if __name__ == "__main__":
    main()
