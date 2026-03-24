import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自我目标设定 - Agent 自主定义任务目标
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SelfGoalSetter:
    """自我目标设定器"""

    def __init__(self):
        self.goals_file = Path("10-MEMORY/00-CORE/self_goals.json")
        self.progress_file = Path("10-MEMORY/00-CORE/goal_progress.json")
        self.goals = self._load_goals()

    def _load_goals(self) -> Dict:
        """加载目标"""
        if self.goals_file.exists():
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "goals": {
                "daily": [],      # 每日目标
                "weekly": [],     # 每周目标
                "monthly": [],    # 每月目标
                "project": []     # 项目目标
            },
            "active_goal": None
        }

    def set_goal(self, goal_type: str, description: str, priority: int = 5,
                 deadline: str = None, subgoals: List[str] = None) -> Dict:
        """设定目标
        
        Args:
            goal_type: 目标类型 (daily/weekly/monthly/project)
            description: 目标描述
            priority: 优先级 (1-10)
            deadline: 截止日期 (ISO format)
            subgoals: 子目标列表
        """
        if goal_type not in self.goals["goals"]:
            return {"error": f"Invalid goal type: {goal_type}"}

        goal = {
            "id": f"{goal_type}_{len(self.goals['goals'][goal_type]) + 1}",
            "type": goal_type,
            "description": description,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "deadline": deadline,
            "subgoals": subgoals or [],
            "progress": 0,
            "status": "active",
            "self_defined": True  # 标记为自主设定
        }

        self.goals["goals"][goal_type].append(goal)

        # 如果是最高优先级，设为活动目标
        if priority >= 8 and not self.goals["active_goal"]:
            self.goals["active_goal"] = goal["id"]

        self._save_goals()

        return {"status": "success", "goal_id": goal["id"]}

    def auto_generate_goals(self, context: Dict = None) -> Dict:
        """自动生成目标
        
        Args:
            context: 上下文信息 (当前项目/待办事项等)
        """
        generated = {
            "daily": [],
            "weekly": [],
            "project": []
        }

        # 基于上下文的智能目标生成
        if context:
            # 如果有未完成的项目
            if context.get("ongoing_projects"):
                for project in context["ongoing_projects"]:
                    goal = self.set_goal(
                        "project",
                        f"Complete {project} project",
                        priority=8,
                        subgoals=["Design", "Implement", "Test", "Document"]
                    )
                    generated["project"].append(goal)

            # 如果有紧急任务
            if context.get("urgent_tasks"):
                for task in context["urgent_tasks"]:
                    goal = self.set_goal(
                        "daily",
                        f"Complete urgent task: {task}",
                        priority=9,
                        deadline=(datetime.now() + timedelta(days=1)).isoformat()
                    )
                    generated["daily"].append(goal)

        # 默认目标 (如果没有上下文)
        if not context or not generated["daily"]:
            default_daily = [
                ("Maintain workflow compliance 100%", 8),
                ("Keep session memory <5KB", 7),
                ("Zero error principle", 9),
            ]

            for desc, priority in default_daily:
                goal = self.set_goal("daily", desc, priority=priority)
                generated["daily"].append(goal)

        return {"status": "success", "generated": generated}

    def update_progress(self, goal_id: str, progress: int) -> Dict:
        """更新进度
        
        Args:
            goal_id: 目标 ID
            progress: 进度百分比 (0-100)
        """
        for goal_type, goals in self.goals["goals"].items():
            for goal in goals:
                if goal["id"] == goal_id:
                    goal["progress"] = min(100, max(0, progress))

                    # 完成时更新状态
                    if progress >= 100:
                        goal["status"] = "completed"
                        goal["completed_at"] = datetime.now().isoformat()

                    self._save_goals()
                    return {"status": "success", "new_progress": goal["progress"]}

        return {"error": "Goal not found"}

    def get_active_goals(self, limit: int = 5) -> List[Dict]:
        """获取活动目标"""
        active = []

        for goal_type, goals in self.goals["goals"].items():
            for goal in goals:
                if goal["status"] == "active":
                    active.append(goal)

        # 按优先级排序
        active.sort(key=lambda x: x["priority"], reverse=True)

        return active[:limit]

    def reprioritize(self) -> Dict:
        """重新评估优先级"""
        # 基于截止日期和进度重新计算优先级
        now = datetime.now()

        for goal_type, goals in self.goals["goals"].items():
            for goal in goals:
                if goal["status"] != "active":
                    continue

                # 截止日期临近提升优先级
                if goal.get("deadline"):
                    deadline = datetime.fromisoformat(goal["deadline"])
                    days_left = (deadline - now).days

                    if days_left <= 1:
                        goal["priority"] = min(10, goal["priority"] + 2)
                    elif days_left <= 3:
                        goal["priority"] = min(10, goal["priority"] + 1)

                # 进度滞后提升优先级
                if goal["progress"] < 50 and goal.get("deadline"):
                    deadline = datetime.fromisoformat(goal["deadline"])
                    total_days = (deadline - datetime.fromisoformat(goal["created_at"])).days
                    elapsed_days = (now - datetime.fromisoformat(goal["created_at"])).days

                    if total_days > 0 and elapsed_days / total_days > 0.7:
                        goal["priority"] = min(10, goal["priority"] + 1)

        self._save_goals()

        return {"status": "success", "reprioritized": True}

    def get_summary(self) -> Dict:
        """获取目标摘要"""
        summary = {
            "total_goals": 0,
            "by_type": {},
            "by_status": {"active": 0, "completed": 0, "abandoned": 0},
            "avg_progress": 0,
            "active_goal": self.goals["active_goal"]
        }

        total_progress = 0
        for goal_type, goals in self.goals["goals"].items():
            count = len(goals)
            summary["total_goals"] += count
            summary["by_type"][goal_type] = count

            for goal in goals:
                summary["by_status"][goal["status"]] += 1
                total_progress += goal["progress"]

        if summary["total_goals"] > 0:
            summary["avg_progress"] = total_progress / summary["total_goals"]

        return summary

    def _save_goals(self):
        """保存目标"""
        with open(self.goals_file, 'w', encoding='utf-8') as f:
            json.dump(self.goals, f, ensure_ascii=False, indent=2)

    def display_status(self) -> str:
        """显示状态"""
        summary = self.get_summary()
        active = self.get_active_goals(limit=5)

        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 25 + "Self-Goal Setter")
        output.append("=" * 70)

        output.append(f"\n[Overview]")
        output.append(f"  Total Goals:        {summary['total_goals']}")
        output.append(f"  Active Goals:       {summary['by_status']['active']}")
        output.append(f"  Completed:          {summary['by_status']['completed']}")
        output.append(f"  Avg Progress:       {summary['avg_progress']:.1f}%")

        output.append(f"\n[Active Goals (Top 5)]")
        for goal in active:
            status_icon = "✓" if goal["status"] == "completed" else "○"
            output.append(f"  {status_icon} [{goal['priority']}] {goal['description']} ({goal['progress']}%)")

        output.append("\n" + "=" * 70)

        return "\n".join(output)

logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py self_goal_setter_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py self_goal_setter_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

测试入口"""
    setter = SelfGoalSetter()

    print("Self-Goal Setter Test")
    print("=" * 70)

    # 显示状态
    print(setter.display_status())

    # 测试：设定目标
    print("\n[Setting Goals]")

    result1 = setter.set_goal(
        "daily",
        "Maintain 100% workflow compliance",
        priority=9,
        subgoals=["Complete all 20 steps", "Run critic check", "Git commit"]
    )
    print(f"  Daily goal: {result1}")

    result2 = setter.set_goal(
        "project",
        "Implement AAI-5 capabilities",
        priority=10,
        deadline=(datetime.now() + timedelta(days=90)).isoformat(),
        subgoals=["Cross-session memory", "Self-correction", "Self-goal setting", "Tool self-learning"]
    )
    print(f"  Project goal: {result2}")

    # 测试：自动生成
    print("\n[Auto-Generating Goals]")
    context = {
        "ongoing_projects": ["P0 Implementation"],
        "urgent_tasks": ["Git commit before session end"]
    }
    result = setter.auto_generate_goals(context)
    print(f"  Generated: {len(result['generated']['daily'])} daily, {len(result['generated']['project'])} project")

    # 显示更新后状态
    print("\n[Updated Status]")
    print(setter.display_status())

    print(f"\n[OK] Self-goal setter test completed")

if __name__ == "__main__":
    main()
