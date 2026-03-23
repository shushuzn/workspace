#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Diverge - 自由联想工具

目标：产生尽可能多的想法 (不评判)
输出：ideas_raw.md
"""

import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("30-scripts-tools")
TOPIC_FILE = OUTPUT_DIR / "brainstorm_topic.json"
IDEAS_FILE = OUTPUT_DIR / "ideas_raw.md"

def load_topic():
    if not TOPIC_FILE.exists():
        print("❌ 请先定义主题 (运行 brainstorm_define.py)")
        return None

    with open(TOPIC_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def diverge_thinking(topic):
    """自由联想生成想法"""
    print(f"\n{'='*60}")
    print(f"🧠 自由联想 - 主题：{topic['topic']}")
    print(f"{'='*60}\n")

    print("💡 提示：不要评判，追求数量，越疯狂越好！\n")
    print("方法建议:")
    print("  - 头脑书写：快速写下所有想法")
    print("  - SCAMPER: 替代/合并/调整/修改/他用/消除/重组")
    print("  - 逆向思维：反过来想会怎样？")
    print("  - 类比思维：其他领域怎么解决？\n")

    ideas = []
    print("请输入想法 (每行一个，输入空行结束):\n")

    while True:
        idea = input(f"想法 #{len(ideas)+1}: ").strip()
        if not idea:
            if len(ideas) < 5:
                print("⚠️  至少输入 5 个想法！")
                continue
            break
        ideas.append(idea)

    print(f"\n✅ 生成 {len(ideas)} 个想法")
    return ideas

def save_ideas(ideas, topic):
    """保存想法到文件"""
    content = f"""# 原始想法清单

**主题:** {topic['topic']}  
**日期:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**数量:** {len(ideas)} 个

---

## 💡 想法列表

"""

    for i, idea in enumerate(ideas, 1):
        content += f"{i}. {idea}\n"

    content += f"""
---

*生成工具：brainstorm_diverge.py*
"""

    with open(IDEAS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 想法已保存：{IDEAS_FILE}")

def main():
    topic = load_topic()
    if not topic:
        return

    ideas = diverge_thinking(topic)
    save_ideas(ideas, topic)

    # 验证
    print(f"\n{'='*60}")
    print("📊 验证")
    print(f"{'='*60}")

    if len(ideas) >= 20:
        print("✅ 想法数量 ≥20 (优秀)")
    elif len(ideas) >= 10:
        print("✅ 想法数量 ≥10 (合格)")
    else:
        print("⚠️  想法数量 <10 (建议继续发散)")

if __name__ == "__main__":
    main()
