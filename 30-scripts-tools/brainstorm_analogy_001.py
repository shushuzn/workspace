import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BRAINSTORM-ANALOGY-001 Analogy Brainstorm Method
【类比思维法】

原理: 从其他领域借用解决方案，通过类比找到新思路

类比类型:
  1. 直接类比 - 类似领域中找相似解决方案
  2. 符号类比 - 用符号或图像触发联想
  3. 幻想类比 - 想象完美解决方案，反向推导

使用:
  py brainstorm_analogy.py <topic>
  py brainstorm_analogy.py <topic> --domain <领域>
"""

import json
import sys
from pathlib import Path


# 领域类比库
DOMAIN_ANALOGIES = {
    "nature": {
        "name": "自然界",
        "examples": [
            {"concept": "蜂巢", "lesson": "高效协作、分工明确" },
            {"concept": "神经网络", "lesson": "分布式处理、自学习" },
            {"concept": "生态系统", "lesson": "循环利用、平衡共生" },
            {"concept": "进化", "lesson": "适者生存、持续迭代" },
            {"concept": "光合作用", "lesson": "低成本能量转换" },
            {"concept": "免疫系统", "lesson": "识别异常、自动响应" },
        ]
    },
    "business": {
        "name": "商业世界",
        "examples": [
            {"concept": "精益创业", "lesson": "快速验证、最小可行产品" },
            {"concept": "长尾理论", "lesson": "小众市场汇聚大价值" },
            {"concept": "平台效应", "lesson": "网络效应、赢家通吃" },
            {"concept": "敏捷开发", "lesson": "迭代交付、响应变化" },
            {"concept": "蓝海战略", "lesson": "避开竞争、创造新市场" },
        ]
    },
    "science": {
        "name": "科学方法",
        "examples": [
            {"concept": "假设验证", "lesson": "大胆假设、小心求证" },
            {"concept": "第一性原理", "lesson": "从本质出发" },
            {"concept": "还原论", "lesson": "分解问题、逐个解决" },
            {"concept": "涌现", "lesson": "整体大于部分之和" },
        ]
    },
    "arts": {
        "name": "艺术创作",
        "examples": [
            {"concept": "爵士乐即兴", "lesson": "在约束中创新" },
            {"concept": "蒙太奇", "lesson": "重新组合、创造新意" },
            {"concept": "极简主义", "lesson": "Less is More" },
            {"concept": "解构主义", "lesson": "打破常规、重构意义" },
        ]
    },
    "history": {
        "name": "历史经验",
        "examples": [
            {"concept": "工业革命", "lesson": "自动化替代重复劳动" },
            {"concept": "印刷术", "lesson": "知识复制与传播" },
            {"concept": "互联网", "lesson": "连接一切、降低门槛" },
        ]
    },
    "engineering": {
        "name": "工程方法",
        "examples": [
            {"concept": "模块化设计", "lesson": "独立组件、易于替换" },
            {"concept": "容错设计", "lesson": "接受失败、快速恢复" },
            {"concept": "冗余备份", "lesson": "多份保障、降低风险" },
            {"concept": "接口标准化", "lesson": "统一协议、易于集成" },
        ]
    }
}


def generate_domain_analogies(topic: str, domain: str = None) -> dict:
    """生成领域类比"""
    
    results = {
        "topic": topic,
        "method": "Analogy",
        "analogies": []
    }
    
    # 选择领域
    if domain and domain in DOMAIN_ANALOGIES:
        domains = [domain]
    else:
        domains = list(DOMAIN_ANALOGIES.keys())
    
    # 生成类比
    for d in domains:
        domain_data = DOMAIN_ANALOGIES[d]
        for example in domain_data["examples"]:
            analogy = {
                "domain": domain_data["name"],
                "concept": example["concept"],
                "lesson": example["lesson"],
                "questions": [
                    f"How can {topic} apply the lesson of {example['concept']}?",
                    f"What if {topic} worked like {example['concept']}?",
                    f"How does {example['concept']} solve similar problems to {topic}?",
                ]
            }
            results["analogies"].append(analogy)
    
    return results


def display_analogies(results: dict):
    """展示类比结果"""
    
    print("=" * 60)
    print(f"[ANALOGY] Topic: {results['topic']}")
    print("=" * 60)
    
    # 按领域分组显示
    current_domain = None
    for analogy in results["analogies"]:
        if analogy["domain"] != current_domain:
            current_domain = analogy["domain"]
            print(f"\n【{current_domain}】")
        
        print(f"\n  [{analogy['concept']}]")
        print(f"  Lesson: {analogy['lesson']}")
        print(f"  -> {analogy['questions'][0]}")
    
    print("\n" + "=" * 60)


logging.basicConfig(level=logging.INFO)
def main():
    """主函数"""
    
    topic = None
    domain = None
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--domain" and i < len(sys.argv) - 1:
            domain = sys.argv[i + 1]
        elif not arg.startswith("--"):
            topic = arg
    
    if not topic:
        topic = "OpenClaw tools"
    
    results = generate_domain_analogies(topic, domain)
    display_analogies(results)
    
    # 保存结果
    output_file = Path(f"flow-archive/brainstorm-current/analogy_ideas.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Saved to] {output_file}")
    print(f"\n[Tip] 使用 --domain <领域> 指定领域: {', '.join(DOMAIN_ANALOGIES.keys())}")
    
    return 0



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <args>")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
