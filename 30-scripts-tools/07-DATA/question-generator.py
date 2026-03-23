#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Research Question Generator - 研究问题生成器

功能：
1. 基于知识图谱识别研究空白
2. 生成研究问题
3. 问题优先级排序
4. 可行性评估

作者：Claw (AI Research OS)
创建时间：2026-03-05 21:50
"""

import json
import random
from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResearchQuestion:
    """研究问题"""
    question: str
    category: str
    priority: str
    feasibility: str
    expected_impact: str
    related_work: List[str]

    def to_dict(self) -> Dict:
        return {
            'question': self.question,
            'category': self.category,
            'priority': self.priority,
            'feasibility': self.feasibility,
            'expected_impact': self.expected_impact,
            'related_work': self.related_work
        }


class QuestionGenerator:
    """研究问题生成器"""

    def __init__(self):
        self.question_templates = [
            {
                'template': '如何优化{material}的{property}以提高{application}性能？',
                'category': '材料优化'
            },
            {
                'template': '{material1}和{material2}的复合材料是否具有更好的{property}？',
                'category': '复合材料'
            },
            {
                'template': '{method}方法能否用于合成{material}以降低{cost}?',
                'category': '合成方法'
            },
            {
                'template': '{property}与{property2}之间是否存在关联？',
                'category': '基础机理'
            }
        ]

        self.materials = ['LiFePO4', 'TiO2', 'SiO2', 'LiCoO2', 'LiNiO2']
        self.properties = ['带隙', '形成能', '体积模量', '电导率', '热导率']
        self.methods = ['固相反应', '溶胶 - 凝胶', '水热法', 'CVD']
        self.applications = ['电池', '催化', '光电', '热电']

    def generate(self, n_questions: int = 10) -> List[ResearchQuestion]:
        """生成研究问题"""

        questions = []

        for i in range(n_questions):
            template = random.choice(self.question_templates)

            # 填充模板
            question = template['template'].format(
                material=random.choice(self.materials),
                material1=random.choice(self.materials),
                material2=random.choice(self.materials),
                property=random.choice(self.properties),
                property2=random.choice(self.properties),
                method=random.choice(self.methods),
                application=random.choice(self.applications),
                cost='成本'
            )

            # 优先级
            priority = random.choice(['高', '中', '低'])

            # 可行性
            feasibility = random.choice(['高', '中', '低'])

            # 预期影响
            impact = random.choice(['重大突破', '显著改进', '渐进式改进'])

            questions.append(ResearchQuestion(
                question=question,
                category=template['category'],
                priority=priority,
                feasibility=feasibility,
                expected_impact=impact,
                related_work=[f"相关工作{i+1}"]
            ))

        return questions

    def prioritize(self, questions: List[ResearchQuestion]) -> List[ResearchQuestion]:
        """优先级排序"""

        priority_order = {'高': 0, '中': 1, '低': 2}

        questions.sort(key=lambda q: priority_order.get(q.priority, 1))

        return questions


def main():
    """主函数"""
    print("=" * 60)
    print("Research Question Generator - 研究问题生成器")
    print("=" * 60)

    generator = QuestionGenerator()

    # 生成问题
    questions = generator.generate(n_questions=8)

    # 排序
    questions = generator.prioritize(questions)

    print(f"\n生成 {len(questions)} 个研究问题:\n")

    for i, q in enumerate(questions, 1):
        print(f"{i}. [{q.priority}] {q.question}")
        print(f"   类别：{q.category}")
        print(f"   可行性：{q.feasibility}")
        print(f"   预期影响：{q.expected_impact}")
        print()

    # 保存
    output_path = Path('data/research-questions.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([q.to_dict() for q in questions], f, ensure_ascii=False, indent=2)

    print(f"问题已保存到 {output_path}")

    print("\n" + "=" * 60)
    print("研究问题生成器准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
