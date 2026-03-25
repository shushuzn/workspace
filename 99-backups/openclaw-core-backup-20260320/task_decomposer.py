#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能任务分解器 - 自动将大任务拆分为≤10 分钟子任务
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class TaskDecomposer:
    """智能任务分解器"""

    def __init__(self):
        self.max_subtask_time = 10  # minutes
        self.output_dir = Path("flow-archive/task-decompositions")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def decompose(self, task: str, estimated_time: int = None) -> Dict:
        """分解任务
        
        Args:
            task: 任务描述
            estimated_time: 预估总用时 (分钟)
        """
        # 估算总用时
        if estimated_time is None:
            estimated_time = self._estimate_time(task)

        # 计算需要的子任务数
        num_subtasks = max(1, (estimated_time + self.max_subtask_time - 1) // self.max_subtask_time)

        # 生成子任务
        subtasks = self._generate_subtasks(task, num_subtasks)

        # 创建分解方案
        decomposition = {
            "task_id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "original_task": task,
            "estimated_total_time": estimated_time,
            "num_subtasks": len(subtasks),
            "max_subtask_time": self.max_subtask_time,
            "subtasks": subtasks,
            "created_at": datetime.now().isoformat(),
            "status": "ready"
        }

        # 保存分解方案
        output_file = self.output_dir / f"{decomposition['task_id']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(decomposition, f, ensure_ascii=False, indent=2)

        return decomposition

    def _estimate_time(self, task: str) -> int:
        """估算任务用时"""
        # 基于关键词简单估算
        time_keywords = {
            "create": 15,
            "implement": 30,
            "fix": 10,
            "test": 15,
            "review": 10,
            "document": 20,
            "optimize": 25,
            "debug": 20,
            "deploy": 15,
            "research": 30
        }

        task_lower = task.lower()
        total_time = 20  # 默认 20 分钟

        for keyword, time in time_keywords.items():
            if keyword in task_lower:
                total_time = time
                break

        return total_time

    def _generate_subtasks(self, task: str, num_subtasks: int) -> List[Dict]:
        """生成子任务列表"""
        subtasks = []

        # 标准分解模式
        patterns = {
            "create": ["设计", "实现", "测试", "文档"],
            "implement": ["分析需求", "设计方案", "编码实现", "单元测试", "代码审查"],
            "fix": ["复现问题", "定位原因", "实施修复", "验证修复", "回归测试"],
            "test": ["准备测试数据", "编写测试用例", "执行测试", "记录结果", "提交报告"],
            "research": ["定义问题", "收集资料", "分析对比", "总结结论", "输出报告"]
        }

        # 匹配模式
        task_lower = task.lower()
        pattern = None
        for keyword, steps in patterns.items():
            if keyword in task_lower:
                pattern = steps
                break

        if pattern is None:
            pattern = ["准备", "执行", "验证", "总结"]

        # 生成子任务
        for i, step in enumerate(pattern[:num_subtasks], 1):
            subtask = {
                "subtask_id": i,
                "description": f"{step}: {task}",
                "estimated_time": min(self.max_subtask_time, 10),
                "status": "pending",
                "dependencies": [i -1] if i > 1 else []
            }
            subtasks.append(subtask)

        return subtasks

    def get_progress(self, task_id: str) -> Dict:
        """获取任务进度"""
        task_file = self.output_dir / f"{task_id}.json"

        if not task_file.exists():
            return {"error": "Task not found"}

        with open(task_file, 'r', encoding='utf-8') as f:
            decomposition = json.load(f)

        completed = sum(1 for s in decomposition['subtasks'] if s['status'] == 'completed')
        total = len(decomposition['subtasks'])

        return {
            "task_id": task_id,
            "original_task": decomposition['original_task'],
            "progress": f"{completed}/{total}",
            "progress_percent": (completed / total) * 100 if total > 0 else 0,
            "status": decomposition['status']
        }

    def mark_subtask_complete(self, task_id: str, subtask_id: int) -> Dict:
        """标记子任务完成"""
        task_file = self.output_dir / f"{task_id}.json"

        if not task_file.exists():
            return {"error": "Task not found"}

        with open(task_file, 'r', encoding='utf-8') as f:
            decomposition = json.load(f)

        # 更新状态
        for subtask in decomposition['subtasks']:
            if subtask['subtask_id'] == subtask_id:
                subtask['status'] = 'completed'
                subtask['completed_at'] = datetime.now().isoformat()
                break

        # 检查是否全部完成
        all_completed = all(s['status'] == 'completed' for s in decomposition['subtasks'])
        if all_completed:
            decomposition['status'] = 'completed'

        # 保存更新
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(decomposition, f, ensure_ascii=False, indent=2)

        return {"status": "updated", "all_completed": all_completed}

    def display_status(self) -> str:
        """显示状态"""
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 25 + "Task Decomposer")
        output.append("=" * 70)

        output.append(f"\n[Settings]")
        output.append(f"  Max Subtask Time:   {self.max_subtask_time} minutes")
        output.append(f"  Output Directory:   {self.output_dir}")

        # 统计已有分解
        decompositions = list(self.output_dir.glob("*.json"))
        output.append(f"\n[Decompositions]")
        output.append(f"  Total Tasks:        {len(decompositions)}")

        output.append("\n" + "=" * 70)

        return "\n".join(output)

def main():
    """测试入口"""
    decomposer = TaskDecomposer()

    print("Task Decomposer Test")
    print("=" * 70)

    # 显示状态
    print(decomposer.display_status())

    # 测试：分解任务
    test_task = "Create intelligent task decomposer tool"
    print(f"\n[Decomposing Task]: {test_task}")

    result = decomposer.decompose(test_task, estimated_time=30)

    print(f"\n[OK] Decomposed into {result['num_subtasks']} subtasks:")
    for subtask in result['subtasks']:
        status_icon = "✓" if subtask['status'] == 'completed' else "○"
        print(f"  {status_icon} Subtask {subtask['subtask_id']}: {subtask['description']} ({subtask['estimated_time']}min)")

    print(f"\n[OK] Task decomposer test completed")

if __name__ == "__main__":
    main()
