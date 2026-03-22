#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TRANSFER-DETECTOR-001 训练迁移检测系统

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
# Purpose:
#     - 检测技能学习在跨任务间的迁移效应
#     - 基于论文 2603.09753 核心发现设计
#     - 量化训练迁移和泛化能力
# Data Flow:
#     task_history -> analyze_patterns() -> transfer_score -> recommendations
# Files:
#     - transfer_detector_001.py (主工具)
#     - .transfer_history.json (迁移历史)
# Edge Cases:
#     - 数据不足 -> 需要至少3个任务
#     - 负迁移 -> 标记问题
#     - 无迁移 -> 返回基线
# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

TRANSFER_FILE = Path(".transfer_history.json")


def load_transfer_data():
    if TRANSFER_FILE.exists():
        try:
            return json.loads(TRANSFER_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"task_attempts": [], "skill_scores": {}, "created_at": datetime.now().isoformat()}


def save_transfer_data(data):
    TRANSFER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def record_attempt(task_id, skill_type, performance_score, time_spent):
    data = load_transfer_data()
    data["task_attempts"].append({
        "task_id": task_id,
        "skill_type": skill_type,
        "performance": performance_score,
        "time_spent": time_spent,
        "timestamp": datetime.now().isoformat(),
    })
    if task_id not in data["skill_scores"]:
        data["skill_scores"][task_id] = {}
    data["skill_scores"][task_id][skill_type] = performance_score
    data["task_attempts"] = data["task_attempts"][-50:]
    save_transfer_data(data)
    return data


def calculate_transfer_score(data):
    attempts = data["task_attempts"]
    if len(attempts) < 3:
        return {"transfer_score": 0, "near_transfer": 0, "far_transfer": 0,
                "generalization": 0, "status": "insufficient_data",
                "message": "Need at least 3 tasks for analysis"}
    
    attempts = sorted(attempts, key=lambda x: x["timestamp"])
    n = len(attempts)
    first_third = attempts[:n//3]
    last_third = attempts[-n//3:]
    
    skill_groups = defaultdict(list)
    for a in attempts:
        skill_groups[a["skill_type"]].append(a)
    
    skill_improvement = {}
    for skill, task_list in skill_groups.items():
        if len(task_list) >= 2:
            first = sum(t["performance"] for t in task_list[:len(task_list)//2]) / (len(task_list)//2)
            last = sum(t["performance"] for t in task_list[-len(task_list)//2:]) / (len(task_list)//2)
            skill_improvement[skill] = (last - first) / max(1, first) * 100
    
    near_transfer = sum(skill_improvement.values()) / max(1, len(skill_improvement))
    improved_skills = sum(1 for v in skill_improvement.values() if v > 0)
    far_transfer = (improved_skills / max(1, len(skill_improvement))) * 50 if len(skill_improvement) > 1 else 0
    
    if first_third and last_third:
        first_avg = sum(a["performance"] for a in first_third) / len(first_third)
        last_avg = sum(a["performance"] for a in last_third) / len(last_third)
        generalization = (last_avg - first_avg) / max(1, first_avg) * 100
    else:
        generalization = 0
    
    transfer_score = near_transfer * 0.4 + far_transfer * 0.3 + generalization * 0.3
    
    return {
        "transfer_score": round(transfer_score, 1),
        "near_transfer": round(near_transfer, 1),
        "far_transfer": round(far_transfer, 1),
        "generalization": round(generalization, 1),
        "status": "analyzed",
        "skill_improvement": skill_improvement,
        "total_tasks": len(attempts),
        "total_skills": len(skill_groups),
    }


def get_recommendations(analysis):
    recs = []
    if analysis["status"] == "insufficient_data":
        recs.append("Complete at least 3 tasks to enable analysis")
        return recs
    score = analysis["transfer_score"]
    if score >= 30:
        recs.append("[HIGH] Strong transfer learning!")
    elif score >= 15:
        recs.append("[MED] Moderate transfer")
    elif score >= 0:
        recs.append("[LOW] Limited transfer")
    else:
        recs.append("[NEGATIVE] Review learning strategy")
    return recs


def analyze_transfer():
    data = load_transfer_data()
    analysis = calculate_transfer_score(data)
    
    print("=" * 60)
    print("TRANSFER OF TRAINING ANALYSIS")
    print("=" * 60)
    print(f"Status: {analysis['status']}")
    print("-" * 60)
    
    if analysis["status"] == "insufficient_data":
        print(f"\n{analysis['message']}")
        print(f"Current attempts: {len(data['task_attempts'])}/3")
    else:
        print(f"\nTotal Tasks: {analysis['total_tasks']}")
        print(f"Total Skills: {analysis['total_skills']}")
        print(f"\n[SCORES]")
        print(f"  Overall Transfer: {analysis['transfer_score']:.1f}/100")
        print(f"  Near Transfer: {analysis['near_transfer']:.1f}%")
        print(f"  Far Transfer: {analysis['far_transfer']:.1f}%")
        print(f"  Generalization: {analysis['generalization']:.1f}%")
        print(f"\n[RECOMMENDATIONS]")
        for r in get_recommendations(analysis):
            print(f"  {r}")
    print("=" * 60)
    return analysis


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  py transfer_detector_001.py --analyze")
        print("  py transfer_detector_001.py --record <task_id> <skill> <score> <time>")
        return
    if sys.argv[1] == "--analyze":
        analyze_transfer()
    elif sys.argv[1] == "--record" and len(sys.argv) >= 6:
        record_attempt(sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5]))
        print(f"[OK] Recorded: {sys.argv[2]}")


# ==============================================================================
# STAGE 3: ASK 询问确认
# py transfer_detector_001.py --analyze
# ==============================================================================

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================

if __name__ == "__main__":
    main()
