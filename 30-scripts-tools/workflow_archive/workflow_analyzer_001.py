#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-ANALYZER-001 工作流分析工具 + 复杂度评分

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
# ==============================================================================
Purpose:
    - 分析工作流结构和内容
    - 计算认知复杂度评分 (基于论文 2603.09753 方法)
    - 生成改进建议和行动项

Data Flow:
    workflow.json -> parse() -> complexity_score() -> recommendations

Files:
    - workflow_analyzer_001.py (主工具)
    - flow-archive/*.json (工作流文件)

Edge Cases:
    - 无步骤 -> 返回 0 分
    - 空字段 -> 使用默认值
    - 工具不存在 -> 标记警告

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================
"""

import subprocess
import sys
from pathlib import Path

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ==============================================================================
# 复杂度评分系统 (基于认知科学研究)
# ==============================================================================


def calculate_complexity_score(steps):
    """
    基于论文 2603.09753 的认知复杂度评分系统

    评分维度:
    1. 步骤数量 (基础复杂度)
    2. 决策点数量 (认知负荷)
    3. 工具多样性 (认知灵活性)
    4. 时间压力 (注意力需求)
    5. 错误恢复复杂度 (执行功能)
    """
    if not steps:
        return {"score": 0, "level": "N/A", "factors": {}}

    factors = {}

    # 1. 步骤数量评分 (0-25分)
    step_count = len(steps)
    factors["step_count"] = {
        "value": step_count,
        "max_score": 25,
        "score": min(25, step_count * 2.5),
    }

    # 2. 决策点数量 (0-25分)
    decision_points = sum(
        1
        for s in steps
        if any(
            k in s.get("name", "").lower()
            for k in ["判断", "选择", "decision", "choose", "if", "branch"]
        )
    )
    factors["decision_points"] = {
        "value": decision_points,
        "max_score": 25,
        "score": min(25, decision_points * 8),
    }

    # 3. 工具多样性 (0-25分) - 跨任务学习潜力
    tool_ids = set()
    for s in steps:
        tool = s.get("tool_id", "")
        if tool and tool != "built-in":
            tool_ids.add(tool)
    unique_tools = len(tool_ids)
    factors["tool_diversity"] = {
        "value": unique_tools,
        "max_score": 25,
        "score": min(25, unique_tools * 5),
    }

    # 4. 必需步骤比例 (0-25分) - 训练迁移潜力
    mandatory = sum(1 for s in steps if s.get("mandatory", False))
    mandatory_ratio = mandatory / step_count if step_count > 0 else 0
    factors["mandatory_ratio"] = {
        "value": f"{mandatory_ratio:.0%}",
        "max_score": 25,
        "score": mandatory_ratio * 25,
    }

    # 总分
    total_score = sum(f["score"] for f in factors.values())

    # 复杂度等级
    if total_score < 30:
        level = "简单 (Simple)"
    elif total_score < 60:
        level = "中等 (Moderate)"
    elif total_score < 80:
        level = "复杂 (Complex)"
    else:
        level = "极复杂 (Very Complex)"

    return {
        "score": round(total_score, 1),
        "level": level,
        "max_score": 100,
        "factors": factors,
    }


def analyze_workflow(workflow_path):
    """分析工作流并输出报告"""
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    flow_id = workflow.get("flow_id", "unknown")
    name = workflow.get("name", "Unnamed")
    version = workflow.get("version", "N/A")
    steps = workflow.get("steps", [])

    # 计算复杂度
    complexity = calculate_complexity_score(steps)

    # 打印报告
    print("=" * 70)
    print("工作流分析报告")
    print("=" * 70)
    print(f"ID: {flow_id}")
    print(f"名称: {name}")
    print(f"版本: {version}")
    print("-" * 70)

    # 复杂度评分
    print(f"\n【复杂度评分】 {complexity['score']}/100 ({complexity['level']})")
    print("-" * 70)
    for factor_name, factor_data in complexity["factors"].items():
        bar_len = int(factor_data["score"] / factor_data["max_score"] * 20)
        bar = "#" * bar_len + "-" * (20 - bar_len)
        print(f"  {factor_name:<20} [{bar}] {factor_data['score']:.1f}")

    # 统计
    mandatory_count = sum(1 for s in steps if s.get("mandatory", False))
    total_time = sum(s.get("estimated_time_seconds", 0) for s in steps)

    print(f"\n【基本信息】")
    print(f"  总步骤: {len(steps)}")
    print(f"  必需步骤: {mandatory_count}")
    print(f"  预计时间: {total_time}秒 ({total_time / 60:.1f}分钟)")

    # 检查问题
    issues = []
    tool_ids = set()
    for s in steps:
        tool = s.get("tool_id", "")
        if tool and tool.endswith(".py"):
            tool_ids.add(tool)
            if not Path(f"30-scripts-tools/{tool}").exists():
                issues.append(f"工具不存在: {tool}")

    if issues:
        print(f"\n【警告】 {len(issues)} 个问题")
        for issue in issues:
            print(f"  - {issue}")

    # 训练迁移潜力评估 (基于论文)
    print(f"\n【训练迁移潜力】")
    tool_diversity_score = complexity["factors"]["tool_diversity"]["score"]
    if tool_diversity_score >= 20:
        print("  [HIGH] 高迁移潜力 - 多样化工具组合促进跨任务学习")
    elif tool_diversity_score >= 10:
        print("  [MED] 中等迁移潜力")
    else:
        print("  [LOW] 低迁移潜力 - 建议增加工具多样性")

    print("=" * 70)

    return {
        "flow_id": flow_id,
        "complexity": complexity,
        "stats": {
            "total_steps": len(steps),
            "mandatory_steps": mandatory_count,
            "total_time": total_time,
            "unique_tools": len(tool_ids),
        },
        "issues": issues,
    }


# ==============================================================================
# STAGE 3: ASK 询问确认
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_analyzer_001.py

Expected Output:
    - 显示复杂度评分
    - 列出因素分解
    - 给出改进建议
"""
# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases

Test Cases:
    1. 空工作流 -> score=0
    2. 单步骤 -> 低复杂度
    3. 10步骤 + 多工具 -> 高复杂度

Fixes:
    - (none yet)
"""


if __name__ == "__main__":
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        exit(1)
    print("[OK] Critic Review Passed")

    import sys

    workflow_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "flow-archive/20260318-universal-workflow-001/workflow.json"
    )
    analyze_workflow(workflow_path)
