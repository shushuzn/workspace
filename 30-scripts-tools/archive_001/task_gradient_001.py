#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TASK-GRADIENT-001 渐进式任务难度系统

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
# Purpose:
#     - 基于用户表现动态调整任务难度
#     - 实现"最佳挑战区" (Optimal Challenge Zone)
#     - 促进技能迁移和泛化 (论文 2603.09753 核心发现)
# Data Flow:
#     user_metrics -> calculate_difficulty() -> next_task -> evaluate -> update_metrics
# Files:
#     - task_gradient_001.py (主工具)
#     - .task_progress.json (进度存储)
# Edge Cases:
#     - 新用户 -> 从简单任务开始
#     - 连续失败 -> 降低难度
#     - 连续成功 -> 提高难度
# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from enum import IntEnum

logger = logging.getLogger(__name__)

PROGRESS_FILE = Path(".task_progress.json")


class DifficultyLevel(IntEnum):
    """难度等级 (基于游戏化设计参考论文)"""
    BEGINNER = 1      # 初学者
    EASY = 2          # 简单
    MEDIUM = 3        # 中等
    HARD = 4          # 困难
    EXPERT = 5        # 专家
    MASTER = 6        # 大师


DIFFICULTY_CONFIG = {
    DifficultyLevel.BEGINNER: {
        "name": "Beginner",
        "steps_min": 1,
        "steps_max": 3,
        "required_tools": 1,
        "time_estimate": 30,      # 秒
        "error_tolerance": 2,
        "description": "Simple single-step tasks"
    },
    DifficultyLevel.EASY: {
        "name": "Easy",
        "steps_min": 2,
        "steps_max": 5,
        "required_tools": 2,
        "time_estimate": 60,
        "error_tolerance": 1,
        "description": "Basic workflow tasks"
    },
    DifficultyLevel.MEDIUM: {
        "name": "Medium",
        "steps_min": 4,
        "steps_max": 8,
        "required_tools": 3,
        "time_estimate": 120,
        "error_tolerance": 0,
        "description": "Multi-step workflows"
    },
    DifficultyLevel.HARD: {
        "name": "Hard",
        "steps_min": 7,
        "steps_max": 12,
        "required_tools": 5,
        "time_estimate": 240,
        "error_tolerance": 0,
        "description": "Complex workflows with branching"
    },
    DifficultyLevel.EXPERT: {
        "name": "Expert",
        "steps_min": 10,
        "steps_max": 18,
        "required_tools": 7,
        "time_estimate": 400,
        "error_tolerance": 0,
        "description": "Expert-level multi-tool workflows"
    },
    DifficultyLevel.MASTER: {
        "name": "Master",
        "steps_min": 15,
        "steps_max": 25,
        "required_tools": 10,
        "time_estimate": 600,
        "error_tolerance": 0,
        "description": "Master-level challenges"
    },
}


def load_progress():
    """加载进度"""
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    
    return {
        "user_id": "default",
        "current_level": DifficultyLevel.BEGINNER,
        "consecutive_success": 0,
        "consecutive_failure": 0,
        "total_tasks_completed": 0,
        "level_history": [],
        "created_at": datetime.now().isoformat(),
    }


def save_progress(data):
    """保存进度"""
    PROGRESS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def calculate_optimal_difficulty(progress):
    """
    基于论文 2603.09753 的"最佳挑战区"理论
    计算最优难度等级
    
    理论依据:
    - 难度过低: 无聊 (boredom)
    - 难度过高: 焦虑 (anxiety)  
    - 最佳区: 心流 (flow state)
    """
    current = progress["current_level"]
    consecutive_success = progress["consecutive_success"]
    consecutive_failure = progress["consecutive_failure"]
    
    # 连续成功 -> 提高难度
    if consecutive_success >= 3:
        new_level = min(DifficultyLevel.MASTER, current + 1)
    # 连续失败 -> 降低难度
    elif consecutive_failure >= 2:
        new_level = max(DifficultyLevel.BEGINNER, current - 1)
    else:
        new_level = current
    
    return new_level


def evaluate_task_result(progress, task_result):
    """
    评估任务结果并更新进度
    
    Args:
        task_result: {
            "completed": bool,
            "errors": int,
            "time_spent": int,
            "steps_completed": int
        }
    """
    progress["total_tasks_completed"] += 1
    success = task_result.get("completed", False)
    errors = task_result.get("errors", 0)
    
    if success:
        progress["consecutive_success"] += 1
        progress["consecutive_failure"] = 0
    else:
        progress["consecutive_failure"] += 1
        progress["consecutive_success"] = 0
    
    # 记录历史
    progress["level_history"].append({
        "level": int(progress["current_level"]),
        "success": success,
        "errors": errors,
        "timestamp": datetime.now().isoformat(),
    })
    
    # 只保留最近20条记录
    progress["level_history"] = progress["level_history"][-20:]
    
    # 计算新难度
    new_level = calculate_optimal_difficulty(progress)
    progress["current_level"] = new_level
    
    save_progress(progress)
    return progress


def get_next_task():
    """获取下一个推荐任务"""
    progress = load_progress()
    level = progress["current_level"]
    config = DIFFICULTY_CONFIG[level]
    
    return {
        "difficulty": level,
        "level_name": config["name"],
        "description": config["description"],
        "steps_range": f"{config['steps_min']}-{config['steps_max']}",
        "recommended_tools": config["required_tools"],
        "time_estimate": config["time_estimate"],
        "consecutive_success": progress["consecutive_success"],
        "consecutive_failure": progress["consecutive_failure"],
    }


def show_progress():
    """显示进度报告"""
    progress = load_progress()
    level = progress["current_level"]
    config = DIFFICULTY_CONFIG[level]
    
    # 计算成功率
    history = progress["level_history"]
    if history:
        success_rate = sum(1 for h in history if h["success"]) / len(history) * 100
    else:
        success_rate = 0
    
    # 计算平均难度
    if history:
        avg_level = sum(h["level"] for h in history) / len(history)
    else:
        avg_level = level
    
    print("=" * 70)
    print("TASK GRADIENT PROGRESS REPORT")
    print("=" * 70)
    print(f"Current Level: [{level}] {config['name']}")
    print(f"Description: {config['description']}")
    print("-" * 70)
    
    print("\n[STATS]")
    print(f"  Total Tasks: {progress['total_tasks_completed']}")
    print(f"  Success Rate: {success_rate:.1f}%")
    print(f"  Avg Difficulty: {avg_level:.1f}/6")
    
    print("\n[PROGRESSION]")
    print(f"  Consecutive Success: {progress['consecutive_success']}/3 (need 3 to level up)")
    print(f"  Consecutive Failure: {progress['consecutive_failure']}/2 (need 2 to level down)")
    
    print("\n[DIFFICULTY LADDER]")
    for lvl in DifficultyLevel:
        marker = ">>>" if lvl == level else "   "
        name = DIFFICULTY_CONFIG[lvl]["name"]
        desc = DIFFICULTY_CONFIG[lvl]["description"]
        print(f"  {marker} [{lvl}] {name:<10} - {desc}")
    
    print("\n[OPTIMAL CHALLENGE ZONE]")
    if 2 <= progress["consecutive_success"] <= 4:
        print("  [FLOW STATE] You are in the optimal challenge zone!")
    elif progress["consecutive_failure"] >= 2:
        print("  [ANXIETY] Difficulty too high - reducing...")
    elif progress["consecutive_success"] == 0 and progress["total_tasks_completed"] == 0:
        print("  [NEW USER] Starting at beginner level")
    else:
        print("  [READY] Get ready for your next task")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("TASK-GRADIENT-001 Usage:")
        print("  py task_gradient_001.py --show")
        print("  py task_gradient_001.py --next")
        print("  py task_gradient_001.py --complete")
        print("  py task_gradient_001.py --fail")
        return
    
    if sys.argv[1] == "--show":
        show_progress()
    elif sys.argv[1] == "--next":
        task = get_next_task()
        print("=" * 60)
        print("NEXT RECOMMENDED TASK")
        print("=" * 60)
        print(f"Difficulty: [{task['difficulty']}] {task['level_name']}")
        print(f"Description: {task['description']}")
        print(f"Steps: {task['steps_range']}")
        print(f"Tools: {task['recommended_tools']}")
        print(f"Time Est: {task['time_estimate']}s")
        print("=" * 60)
    elif sys.argv[1] == "--complete":
        progress = load_progress()
        progress = evaluate_task_result(progress, {"completed": True, "errors": 0})
        print(f"[OK] Task completed! Level: {progress['current_level']}")
        print(f"     Consecutive success: {progress['consecutive_success']}/3")
    elif sys.argv[1] == "--fail":
        progress = load_progress()
        progress = evaluate_task_result(progress, {"completed": False, "errors": 1})
        print(f"[INFO] Task failed. Level: {progress['current_level']}")
        print(f"       Consecutive failure: {progress['consecutive_failure']}/2")


# ==============================================================================
# STAGE 3: ASK 询问确认
# py task_gradient_001.py --show
# ==============================================================================

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases
    1. First run -> Beginner level
    2. 3x complete -> Level up
    3. 2x fail -> Level down
"""


if __name__ == "__main__":
    main()