#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流步骤优化器 v1.0

功能：
1. 合并执行步骤 5-6: 工具选择与调度
2. 合并执行步骤 8-10: 验证、备份、检查点
3. 智能跳过优化条件

使用：
  py workflow_optimizer.py --combine-5-6
  py workflow_optimizer.py --combine-8-10
  py workflow_optimizer.py --all
  py workflow_optimizer.py --check
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class WorkflowOptimizer:
    """工作流优化器"""

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.workflow_path = self.workspace / "flow-archive/20260318-universal-workflow-001/workflow.json"

    def load_workflow(self) -> Dict:
        """加载工作流"""
        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_workflow(self, workflow: Dict):
        """保存工作流"""
        with open(self.workflow_path, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)

    def combine_steps_5_6(self, workflow: Dict) -> Dict:
        """合并步骤 5 和 6: 工具选择 + 子工作流调度"""

        # 找到步骤 5 和 6
        steps = workflow.get('steps', [])
        step_5 = None
        step_6 = None

        for step in steps:
            if step.get('step_id') == 5:
                step_5 = step
            elif step.get('step_id') == 6:
                step_6 = step

        if not step_5 or not step_6:
            return {'status': 'skipped', 'reason': 'Steps 5 or 6 not found'}

        # 创建合并步骤
        combined_step = {
            "step_id": 5,
            "name": "工具选择与调度",
            "description": "根据任务选择工具并调度子工作流",
            "tool_id": "workflow_optimizer.py",
            "mandatory": False,
            "estimated_time_seconds": 15,  # 5 + 10 的组合
            "skip_condition": "if tool_already_selected and no_subworkflow_needed",
            "outputs": ["selected_tools", "tool_order", "scheduled_tasks"],
            "error_handling": {
                "on_fail": "continue",
                "max_retries": 1
            },
            "combined_from": [5, 6],
            "sub_steps": [
                {
                    "sub_id": "5a",
                    "name": "工具选择",
                    "original_tool": step_5.get('tool_id'),
                    "function": "select_tools"
                },
                {
                    "sub_id": "6a",
                    "name": "子工作流调度",
                    "original_tool": step_6.get('tool_id'),
                    "function": "schedule_workflow"
                }
            ]
        }

        # 移除步骤 6，其他步骤编号不变（因为我们用工具选择作为主步骤）
        new_steps = []
        for step in steps:
            if step.get('step_id') == 5:
                new_steps.append(combined_step)
            elif step.get('step_id') == 6:
                continue  # 跳过步骤 6
            else:
                new_steps.append(step)

        workflow['steps'] = new_steps

        return {
            'status': 'success',
            'action': 'combine_steps_5_6',
            'old_steps': [5, 6],
            'new_step': 5,
            'time_saved': 0  # 10s (原来 10+5=15s, 现在 15s, 节省 0s 但减少开销)
        }

    def combine_steps_8_10(self, workflow: Dict) -> Dict:
        """合并步骤 8, 9, 10: 内容验证 + 自动备份 + 检查点保存"""

        # 找到步骤 8, 9, 10
        steps = workflow.get('steps', [])
        step_8 = None
        step_9 = None
        step_10 = None

        for step in steps:
            if step.get('step_id') == 8:
                step_8 = step
            elif step.get('step_id') == 9:
                step_9 = step
            elif step.get('step_id') == 10:
                step_10 = step

        if not step_8 or not step_9 or not step_10:
            return {'status': 'skipped', 'reason': 'Steps 8, 9, or 10 not found'}

        # 创建合并步骤
        combined_step = {
            "step_id": 8,
            "name": "验证与保障",
            "description": "验证执行结果、备份配置、保存检查点",
            "tool_id": "workflow_optimizer.py",
            "mandatory": False,
            "estimated_time_seconds": 20,  # 10+5+5 = 20s
            "skip_condition": "if_no_output_generated and if_backup_recent",
            "outputs": ["validation_result", "backup_path", "checkpoint_id"],
            "error_handling": {
                "on_fail": "warn",
                "max_retries": 1
            },
            "combined_from": [8, 9, 10],
            "sub_steps": [
                {
                    "sub_id": "8a",
                    "name": "内容验证",
                    "original_tool": step_8.get('tool_id'),
                    "function": "validate_content"
                },
                {
                    "sub_id": "9a",
                    "name": "自动备份",
                    "original_tool": step_9.get('tool_id'),
                    "function": "auto_backup"
                },
                {
                    "sub_id": "10a",
                    "name": "检查点保存",
                    "original_tool": step_10.get('tool_id'),
                    "function": "save_checkpoint"
                }
            ],
            "parallel_enabled": True,
            "parallel_config": {
                "9a": {"after": "8a", "dependency": "validation_passed"},
                "10a": {"after": "8a", "dependency": "none"}
            }
        }

        # 移除步骤 9 和 10
        new_steps = []
        for step in steps:
            if step.get('step_id') == 8:
                new_steps.append(combined_step)
            elif step.get('step_id') in [9, 10]:
                continue  # 跳过步骤 9 和 10
            else:
                new_steps.append(step)

        workflow['steps'] = new_steps

        return {
            'status': 'success',
            'action': 'combine_steps_8_10',
            'old_steps': [8, 9, 10],
            'new_step': 8,
            'time_saved': 0
        }

    def optimize_all(self) -> Dict:
        """执行所有优化"""
        workflow = self.load_workflow()

        results = []

        # 合并 5 和 6
        result1 = self.combine_steps_5_6(workflow)
        results.append(result1)

        # 合并 8, 9, 10
        result2 = self.combine_steps_8_10(workflow)
        results.append(result2)

        # 保存
        self.save_workflow(workflow)

        return {
            'timestamp': datetime.now().isoformat(),
            'optimizations': results,
            'total_time_saved': sum(r.get('time_saved', 0) for r in results)
        }

    def check_optimization(self) -> Dict:
        """检查优化可行性"""
        workflow = self.load_workflow()
        steps = workflow.get('steps', [])

        # 找到可合并的步骤
        combinable = []

        # 检查 5 和 6
        step_5 = next((s for s in steps if s.get('step_id') == 5), None)
        step_6 = next((s for s in steps if s.get('step_id') == 6), None)

        if step_5 and step_6:
            if not step_5.get('mandatory') and not step_6.get('mandatory'):
                combinable.append({
                    'steps': [5, 6],
                    'name': '工具选择 + 子工作流调度',
                    'time': (step_5.get('estimated_time_seconds', 10) +
                            step_6.get('estimated_time_seconds', 5)),
                    'savings': 0
                })

        # 检查 8, 9, 10
        step_8 = next((s for s in steps if s.get('step_id') == 8), None)
        step_9 = next((s for s in steps if s.get('step_id') == 9), None)
        step_10 = next((s for s in steps if s.get('step_id') == 10), None)

        if step_8 and step_9 and step_10:
            total_time = (step_8.get('estimated_time_seconds', 10) +
                        step_9.get('estimated_time_seconds', 5) +
                        step_10.get('estimated_time_seconds', 5))
            if not step_8.get('mandatory') and not step_9.get('mandatory'):
                combinable.append({
                    'steps': [8, 9, 10],
                    'name': '内容验证 + 自动备份 + 检查点保存',
                    'time': total_time,
                    'savings': 0
                })

        return {
            'timestamp': datetime.now().isoformat(),
            'combinable_steps': combinable,
            'total_optimizations': len(combinable)
        }

    def generate_report(self) -> str:
        """生成优化报告"""
        check_result = self.check_optimization()

        report = []
        report.append("=" * 70)
        report.append("工作流步骤合并优化报告")
        report.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")

        if check_result['combinable_steps']:
            report.append(f"发现 {len(check_result['combinable_steps'])} 个可合并的步骤组:")
            report.append("-" * 70)

            for i, combo in enumerate(check_result['combinable_steps'], 1):
                report.append(f"  {i}. 步骤 {combo['steps']}: {combo['name']}")
                report.append(f"     时间: {combo['time']}s")

            report.append("")
            report.append("执行: py workflow_optimizer.py --all")
        else:
            report.append("[OK] 无需优化")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


def main():
    """主函数"""
    optimizer = WorkflowOptimizer()

    if len(sys.argv) < 2:
        print(optimizer.generate_report())
        return

    command = sys.argv[1]

    if command == '--check':
        result = optimizer.check_optimization()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--combine-5-6':
        workflow = optimizer.load_workflow()
        result = optimizer.combine_steps_5_6(workflow)
        optimizer.save_workflow(workflow)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--combine-8-10':
        workflow = optimizer.load_workflow()
        result = optimizer.combine_steps_8_10(workflow)
        optimizer.save_workflow(workflow)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--all':
        result = optimizer.optimize_all()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--report':
        print(optimizer.generate_report())

    else:
        print(f"未知命令: {command}")
        print("用法:")
        print("  py workflow_optimizer.py --check          检查优化可行性")
        print("  py workflow_optimizer.py --combine-5-6   合并步骤 5 和 6")
        print("  py workflow_optimizer.py --combine-8-10 合并步骤 8, 9, 10")
        print("  py workflow_optimizer.py --all          执行所有优化")


if __name__ == "__main__":
    main()