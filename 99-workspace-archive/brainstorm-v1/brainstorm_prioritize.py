#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Prioritize - 优先级排序工具

目标：生成优先级矩阵
输出：priority_matrix.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 配置 UTF-8 输出
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = Path("30-scripts-tools")
SHORTLIST_FILE = OUTPUT_DIR / "ideas_shortlist.md"
MATRIX_FILE = OUTPUT_DIR / "priority_matrix.json"

def load_shortlist():
    """加载入围想法"""
    if not SHORTLIST_FILE.exists():
        print("⚠️  未找到入围清单，请先运行筛选工具")
        return []

    ideas = []
    with open(SHORTLIST_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('- ['):
                # 解析：- [想法名称] (可行性:X, 影响力:Y, 新颖性:Z)
                try:
                    name = line.split(']')[0].split('[')[1]
                    scores = line.split('(')[1].split(')')[0]
                    feasibility = int(scores.split(',')[0].split(':')[1])
                    impact = int(scores.split(',')[1].split(':')[1])
                    novelty = int(scores.split(',')[2].split(':')[1])
                    ideas.append({
                        "name": name.strip(),
                        "feasibility": feasibility,
                        "impact": impact,
                        "novelty": novelty,
                        "total": feasibility + impact + novelty
                    })
                except Exception:
                    continue
    return ideas

def prioritize(ideas):
    """生成优先级矩阵"""
    matrix = {
        "P0": [],  # 高价值 + 低难度
        "P1": [],  # 高价值 + 高难度
        "P2": [],  # 低价值 + 低难度
        "P3": []   # 低价值 + 高难度
    }

    for idea in ideas:
        value = idea['impact'] + idea['novelty']  # 价值 = 影响力 + 新颖性
        difficulty = 6 - idea['feasibility']  # 难度 = 6 - 可行性

        if value >= 7 and difficulty <= 3:
            matrix["P0"].append(idea)
        elif value >= 7 and difficulty > 3:
            matrix["P1"].append(idea)
        elif value < 7 and difficulty <= 3:
            matrix["P2"].append(idea)
        else:
            matrix["P3"].append(idea)

    return matrix

def save_matrix(matrix):
    """保存优先级矩阵"""
    result = {
        "matrix": matrix,
        "summary": {
            "P0_count": len(matrix["P0"]),
            "P1_count": len(matrix["P1"]),
            "P2_count": len(matrix["P2"]),
            "P3_count": len(matrix["P3"]),
            "total": sum(len(v) for v in matrix.values())
        },
        "recommendations": [],
        "created_at": datetime.now().isoformat()
    }

    # 生成建议
    if matrix["P0"]:
        result["recommendations"].append(f"立即执行：{len(matrix['P0'])} 个高价值低难度想法")
    if matrix["P1"]:
        result["recommendations"].append(f"规划执行：{len(matrix['P1'])} 个高价值高难度想法")
    if matrix["P2"]:
        result["recommendations"].append(f"可选执行：{len(matrix['P2'])} 个低价值低难度想法")
    if not matrix["P0"] and not matrix["P1"]:
        result["recommendations"].append("⚠️  建议重新头脑风暴，缺乏高价值想法")

    with open(MATRIX_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 优先级矩阵已保存：{MATRIX_FILE}")
    return result

def print_matrix(matrix):
    """打印优先级矩阵"""
    print(f"\n{'='*60}")
    print("📊 优先级矩阵")
    print(f"{'='*60}\n")

    priorities = [
        ("P0", "🔴 高价值 + 低难度", "立即执行"),
        ("P1", "🟡 高价值 + 高难度", "规划执行"),
        ("P2", "🟢 低价值 + 低难度", "可选执行"),
        ("P3", "⚪ 低价值 + 高难度", "暂不执行")
    ]

    for key, label, action in priorities:
        ideas = matrix[key]
        print(f"{key}: {label} - {action}")
        print(f"   数量：{len(ideas)}")
        if ideas:
            for idea in ideas[:3]:  # 显示前 3 个
                print(f"   - {idea['name']} (总分:{idea['total']})")
        print()

def main():
    print(f"{'='*60}")
    print("🎯 优先级排序")
    print(f"{'='*60}\n")

    ideas = load_shortlist()

    if not ideas:
        print("❌ 没有入围想法，请先运行筛选工具")
        return

    print(f"加载 {len(ideas)} 个入围想法\n")

    matrix = prioritize(ideas)
    result = save_matrix(matrix)
    print_matrix(matrix)

    print("💡 建议:")
    for rec in result["recommendations"]:
        print(f"  - {rec}")

if __name__ == "__main__":
    main()
