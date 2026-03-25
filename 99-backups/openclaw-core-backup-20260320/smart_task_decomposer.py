#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能任务拆解工具 - 基于 arXiv 2603.01234
使用 LLM 自动分解复杂任务为可执行子任务
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class SmartTaskDecomposer:
    """智能任务拆解器"""

    # 任务复杂度评估标准
    COMPLEXITY_CRITERIA = {
        "low": {"max_subtasks": 3, "estimated_time_minutes": 15},
        "medium": {"max_subtasks": 5, "estimated_time_minutes": 30},
        "high": {"max_subtasks": 8, "estimated_time_minutes": 60},
        "very_high": {"max_subtasks": 12, "estimated_time_minutes": 120}
    }

    def __init__(self):
        self.decomposition_history = []

    def assess_complexity(self, task_description: str) -> str:
        """评估任务复杂度"""

        # 简单启发式规则 (实际应使用 LLM)
        word_count = len(task_description.split())
        has_multiple_goals = any(kw in task_description for kw in ["并且", "同时", "还有", "and", "also"])
        requires_research = any(kw in task_description for kw in ["研究", "调研", "research"])
        requires_coding = any(kw in task_description for kw in ["代码", "编程", "code", "create"])

        score = 0
        if word_count > 20:
            score += 1
        if word_count > 50:
            score += 1
        if has_multiple_goals:
            score += 1
        if requires_research:
            score += 1
        if requires_coding:
            score += 1

        if score <= 1:
            return "low"
        elif score <= 2:
            return "medium"
        elif score <= 3:
            return "high"
        else:
            return "very_high"

    def decompose(self, task_description: str, complexity: str) -> List[Dict]:
        """分解任务为子任务"""

        criteria = self.COMPLEXITY_CRITERIA[complexity]
        max_subtasks = criteria["max_subtasks"]

        # 启发式分解 (实际应使用 LLM)
        subtasks = []

        # 通用分解模式
        if "研究" in task_description or "research" in task_description.lower():
            subtasks = [
                {"name": "文献调研", "description": "收集相关研究和资料", "estimated_minutes": 15},
                {"name": "数据收集", "description": "整理所需数据和信息", "estimated_minutes": 10},
                {"name": "分析总结", "description": "分析数据并总结发现", "estimated_minutes": 10},
                {"name": "报告撰写", "description": "撰写研究报告", "estimated_minutes": 15}
            ]
        elif "代码" in task_description or "create" in task_description.lower():
            subtasks = [
                {"name": "需求分析", "description": "明确功能需求", "estimated_minutes": 10},
                {"name": "设计架构", "description": "设计代码架构", "estimated_minutes": 15},
                {"name": "实现功能", "description": "编写代码实现", "estimated_minutes": 30},
                {"name": "测试验证", "description": "测试功能正确性", "estimated_minutes": 15},
                {"name": "文档编写", "description": "编写使用文档", "estimated_minutes": 10}
            ]
        elif "头脑风暴" in task_description or "brainstorm" in task_description.lower():
            subtasks = [
                {"name": "主题定义", "description": "明确头脑风暴主题", "estimated_minutes": 5},
                {"name": "发散环", "description": "产生尽可能多的想法", "estimated_minutes": 30},
                {"name": "收敛环", "description": "筛选和优先级排序", "estimated_minutes": 25},
                {"name": "实施计划", "description": "制定实施计划", "estimated_minutes": 15}
            ]
        else:
            # 通用分解
            subtasks = [
                {"name": "任务理解", "description": "理解任务要求", "estimated_minutes": 5},
                {"name": "计划制定", "description": "制定执行计划", "estimated_minutes": 10},
                {"name": "执行任务", "description": "执行主要任务", "estimated_minutes": 20},
                {"name": "结果验证", "description": "验证结果正确性", "estimated_minutes": 10}
            ]

        # 限制子任务数量
        subtasks = subtasks[:max_subtasks]

        # 添加元数据
        for i, subtask in enumerate(subtasks, 1):
            subtask["id"] = i
            subtask["priority"] = "high" if i <= 2 else "medium"
            subtask["dependencies"] = [i -1] if i > 1 else []

        return subtasks

    def generate_decomposition_plan(self, task_description: str) -> Dict:
        """生成完整的任务分解计划"""

        # 评估复杂度
        complexity = self.assess_complexity(task_description)

        # 分解任务
        subtasks = self.decompose(task_description, complexity)

        # 计算总时间
        total_time = sum(st["estimated_minutes"] for st in subtasks)

        plan = {
            "original_task": task_description,
            "complexity": complexity,
            "complexity_criteria": self.COMPLEXITY_CRITERIA[complexity],
            "subtasks": subtasks,
            "total_subtasks": len(subtasks),
            "total_estimated_minutes": total_time,
            "created_at": datetime.now().isoformat()
        }

        self.decomposition_history.append(plan)

        return plan

    def print_plan(self, plan: Dict):
        """打印分解计划"""

        print(f"\n{'=' *60}")
        print(f"任务分解计划")
        print(f"{'=' *60}")
        print(f"原任务：{plan['original_task'][:50]}...")
        print(f"复杂度：{plan['complexity']}")
        print(f"子任务数：{plan['total_subtasks']}")
        print(f"预计时间：{plan['total_estimated_minutes']} 分钟")
        print(f"\n子任务列表:")

        for st in plan["subtasks"]:
            deps = f" (依赖：{st['dependencies']})" if st['dependencies'] else ""
            print(f"  [{st['id']}] {st['name']} - {st['estimated_minutes']} 分钟{deps}")
            print(f"      {st['description']}")

        print(f"{'=' *60}")

    def run(self, task_description: str) -> Dict:
        """完整流程：评估 -> 分解 -> 输出"""

        plan = self.generate_decomposition_plan(task_description)
        self.print_plan(plan)

        return plan

def main():
    """测试入口"""
    decomposer = SmartTaskDecomposer()

    # 测试不同任务
    test_tasks = [
        "简单查询：今天天气如何？",
        "研究任务：CNT 导电性预测研究，需要文献调研和数据分析",
        "代码开发：创建一个 Python 工具脚本，实现自动化文件整理功能",
        "头脑风暴：AI Agent 优化想法，需要发散和收敛思维"
    ]

    for task in test_tasks:
        decomposer.run(task)

if __name__ == "__main__":
    main()
