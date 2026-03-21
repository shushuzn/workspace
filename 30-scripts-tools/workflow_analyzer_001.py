import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""工作流分析工具"""

import json
from pathlib import Path

def analyze_workflow(workflow_path):
    """分析工作流"""
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    print("=" * 70)
    print(f"工作流: {workflow['flow_id']}")
    print(f"名称: {workflow['name']}")
    print(f"版本: {workflow.get('version', 'N/A')}")
    print(f"总步骤: {workflow.get('total_steps', 0)}")
    print("=" * 70)
    
    print("\n步骤列表:")
    print("-" * 70)
    
    steps = workflow.get('steps', [])
    
    # 按步骤编号排序
    def get_step_num(step):
        step_id = step.get('step_id', 0)
        if isinstance(step_id, (int, float)):
            return float(step_id)
        return float(step_id)
    
    steps_sorted = sorted(steps, key=get_step_num)
    
    issues = []
    prev_step = 0
    
    for step in steps_sorted:
        step_id = step.get('step_id', 0)
        name = step.get('name', 'Unknown')
        mandatory = step.get('mandatory', False)
        tool_id = step.get('tool_id', 'N/A')
        estimated_time = step.get('estimated_time_seconds', 0)
        
        # 检查问题
        step_num = float(step_id) if isinstance(step_id, (int, float)) else float(step_id)
        
        # 检查步骤编号是否连续
        if step_num != prev_step + 1 and prev_step != 0:
            if step_num != int(step_num):  # 小数步骤
                issues.append(f"步骤 {step_id}: 非整数编号")
            else:
                issues.append(f"步骤 {step_id}: 编号不连续 (期望 {prev_step + 1})")
        
        prev_step = int(step_num) if step_num == int(step_num) else prev_step
        
        # 检查工具是否存在
        if tool_id and tool_id != 'N/A' and tool_id.endswith('.py'):
            tool_path = Path(f"30-scripts-tools/{tool_id}")
            if not tool_path.exists():
                issues.append(f"步骤 {step_id}: 工具不存在 {tool_id}")
        
        status = "[M]" if mandatory else "[ ]"
        tool_display = tool_id if tool_id else "(built-in)"
        print(f"{status} {step_id:>5} {name:<35} {tool_display:<25} {estimated_time}s")
    
    print("-" * 70)
    
    # 统计
    mandatory_count = sum(1 for s in steps if s.get('mandatory', False))
    total_time = sum(s.get('estimated_time_seconds', 0) for s in steps)
    
    print(f"\n统计:")
    print(f"  必要步骤: {mandatory_count}/{len(steps)}")
    print(f"  预计时间: {total_time}秒 ({total_time/60:.1f}分钟)")
    
    if issues:
        print(f"\n发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"\n状态: 无问题")
    
    return {
        'total_steps': len(steps),
        'mandatory_steps': mandatory_count,
        'total_time': total_time,
        'issues': issues
    }


if __name__ == "__main__":
    import sys
    workflow_path = sys.argv[1] if len(sys.argv) > 1 else "flow-archive/20260318-universal-workflow-001/workflow.json"
    analyze_workflow(workflow_path)