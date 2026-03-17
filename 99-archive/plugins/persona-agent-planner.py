#!/usr/bin/env python3
"""
规划者子代理 - 多子代理协同系统

角色：制定计划、分配资源
模型：qwen3.5-plus
权重：1.0
"""

import sys
import json
from datetime import datetime

class PlannerAgent:
    """规划者子代理"""
    
    def __init__(self):
        self.name = "规划者"
        self.role = "制定计划、分配资源"
        self.model = "qwen3.5-plus"
        self.weight = 1.0
        self.agent_id = f"planner-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def process(self, task: str, context: dict) -> dict:
        """
        制定任务计划
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            计划结果
        """
        # 规划逻辑
        plan = self._create_plan(task, context)
        
        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "plan": plan,
            "priority": self._calculate_priority(task, context),
            "estimated_time": self._estimate_time(task, context),
            "confidence": 0.85
        }
        return result
    
    def _create_plan(self, task: str, context: dict) -> dict:
        """创建计划"""
        return {
            "steps": [
                {"step": 1, "action": "分析任务"},
                {"step": 2, "action": "执行任务"},
                {"step": 3, "action": "审查输出"},
                {"step": 4, "action": "总结经验"}
            ],
            "resources_needed": ["执行者", "批判者", "学习者"],
            "dependencies": []
        }
    
    def _calculate_priority(self, task: str, context: dict) -> str:
        """计算优先级"""
        # 简单优先级逻辑
        if "紧急" in task or "critical" in task.lower():
            return "high"
        elif "重要" in task or "important" in task.lower():
            return "medium"
        else:
            return "normal"
    
    def _estimate_time(self, task: str, context: dict) -> int:
        """估计时间 (分钟)"""
        # 简单时间估计
        word_count = len(task.split())
        return max(5, min(60, word_count * 2))


def main():
    """主函数"""
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = json.loads(sys.stdin.read().strip())
    
    agent = PlannerAgent()
    result = agent.process(
        input_data.get("task", ""),
        input_data.get("context", {})
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
