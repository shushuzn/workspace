#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""步骤重新编号工具"""

import json
from pathlib import Path
from workflow_optimizer import WorkflowOptimizer


def renumber_workflow():
    """重新编号工作流步骤"""
    optimizer = WorkflowOptimizer()
    workflow = optimizer.load_workflow()

    steps = workflow.get('steps', [])

    # 新的步骤 ID 映射
    old_to_new = {}
    new_id = 1

    # 按原顺序重新编号
    for step in sorted(steps, key=lambda x: x.get('step_id', 0)):
        old_id = step.get('step_id')
        old_to_new[old_id] = new_id
        step['step_id'] = new_id
        new_id += 1

    # 更新步骤数量
    workflow['total_steps'] = new_id - 1

    # 更新步骤分组
    if 'step_groups' in workflow:
        groups = workflow['step_groups']
        new_groups = {}

        for group_name, group_info in groups.items():
            old_steps = group_info.get('steps', [])
            new_steps = [old_to_new.get(s, s) for s in old_steps]
            new_groups[group_name] = {**group_info, 'steps': new_steps}

        workflow['step_groups'] = new_groups

    # 更新跳过条件
    if 'skip_conditions' in workflow:
        new_skip = {}
        for step_id, condition in workflow['skip_conditions'].items():
            new_id = old_to_new.get(int(step_id), int(step_id))
            new_skip[str(new_id)] = condition
        workflow['skip_conditions'] = new_skip

    # 更新并行组
    if 'parallel_groups' in workflow:
        new_parallel = []
        for group in workflow['parallel_groups']:
            new_group = [old_to_new.get(s, s) for s in group]
            new_parallel.append(new_group)
        workflow['parallel_groups'] = new_parallel

    # 保存
    optimizer.save_workflow(workflow)

    return {
        'old_to_new': old_to_new,
        'total_steps': workflow['total_steps']
    }


if __name__ == "__main__":
    result = renumber_workflow()
    print(f"重新编号完成: {result['total_steps']} 步骤")
    print(f"映射: {result['old_to_new']}")