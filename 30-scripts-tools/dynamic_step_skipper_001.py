import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
动态步骤跳过工具 - 基于上下文智能跳过非必要步骤
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class DynamicStepSkipper:
    """动态步骤跳过器"""
    
    # 跳过规则
    SKIP_RULES = {
        "time_pressure": {
            "condition": "time_remaining_minutes < 10",
            "skip_steps": [2, 6.6, 8.5, 13],
            "reason": "时间不足，跳过非必要步骤"
        },
        "simple_task": {
            "condition": "task_complexity == 'low'",
            "skip_steps": [2, 8.5, 9, 13],
            "reason": "简单任务，跳过研究/记忆/文档步骤"
        },
        "no_new_tools": {
            "condition": "new_tools_created == false",
            "skip_steps": [6.5, 6.6],
            "reason": "无新工具创建，跳过验证/测试"
        },
        "low_risk": {
            "condition": "risk_score < 0.3",
            "skip_steps": [10],
            "reason": "低风险任务，简化质量门禁"
        },
        "human_approved": {
            "condition": "human_approval_obtained == true",
            "skip_steps": [9, 10],
            "reason": "已获人工批准，跳过自动审查"
        }
    }
    
    def __init__(self, workflow_file: str):
        self.workflow_file = Path(workflow_file)
        with open(self.workflow_file, 'r', encoding='utf-8') as f:
            self.workflow = json.load(f)
    
    def evaluate_context(self, context: Dict) -> List[str]:
        """评估当前上下文，确定适用哪些跳过规则"""
        
        applicable_rules = []
        
        # 时间压力检查
        time_remaining = context.get("time_remaining_minutes", 60)
        if time_remaining < 10:
            applicable_rules.append("time_pressure")
        
        # 任务复杂度检查
        complexity = context.get("task_complexity", "medium")
        if complexity == "low":
            applicable_rules.append("simple_task")
        
        # 新工具创建检查
        if not context.get("new_tools_created", False):
            applicable_rules.append("no_new_tools")
        
        # 风险评分检查
        risk_score = context.get("risk_score", 0.5)
        if risk_score < 0.3:
            applicable_rules.append("low_risk")
        
        # 人工批准检查
        if context.get("human_approval_obtained", False):
            applicable_rules.append("human_approved")
        
        return applicable_rules
    
    def get_steps_to_skip(self, applicable_rules: List[str]) -> Dict[int, List[str]]:
        """获取需要跳过的步骤及原因"""
        
        steps_to_skip = {}
        
        for rule in applicable_rules:
            if rule not in self.SKIP_RULES:
                continue
            
            rule_config = self.SKIP_RULES[rule]
            for step_id in rule_config["skip_steps"]:
                if step_id not in steps_to_skip:
                    steps_to_skip[step_id] = []
                steps_to_skip[step_id].append(rule_config["reason"])
        
        return steps_to_skip
    
    def apply_skip_logic(self, steps_to_skip: Dict[int, List[str]]) -> Dict:
        """应用跳过逻辑到工作流"""
        
        adapted_workflow = self.workflow.copy()
        
        for step in adapted_workflow["steps"]:
            step_id = step["step_id"]
            
            if step_id in steps_to_skip:
                reasons = steps_to_skip[step_id]
                
                # 设置条件跳过
                step["conditional"] = {
                    "run_if": "false",
                    "skip_message": f"动态跳过：{', '.join(reasons)}"
                }
                
                print(f"  [Skip] Step {step_id}: {step['name']}")
                print(f"         原因：{', '.join(reasons)}")
        
        return adapted_workflow
    
    def run(self, context: Dict) -> Dict:
        """完整流程：评估 -> 决策 -> 应用"""
        
        print(f"\n{'='*60}")
        print(f"动态步骤跳过决策")
        print(f"{'='*60}")
        print(f"上下文:")
        print(f"  剩余时间：{context.get('time_remaining_minutes', 'N/A')} 分钟")
        print(f"  任务复杂度：{context.get('task_complexity', 'N/A')}")
        print(f"  新工具创建：{context.get('new_tools_created', False)}")
        print(f"  风险评分：{context.get('risk_score', 'N/A')}")
        print(f"  人工批准：{context.get('human_approval_obtained', False)}")
        
        # 评估上下文
        applicable_rules = self.evaluate_context(context)
        print(f"\n适用规则：{applicable_rules}")
        
        # 获取跳过步骤
        steps_to_skip = self.get_steps_to_skip(applicable_rules)
        print(f"\n跳过步骤：{list(steps_to_skip.keys())}")
        
        # 应用跳过逻辑
        adapted = self.apply_skip_logic(steps_to_skip)
        
        print(f"\n{'='*60}")
        
        return {
            "applicable_rules": applicable_rules,
            "steps_to_skip": list(steps_to_skip.keys()),
            "skip_reasons": steps_to_skip,
            "adapted_workflow": adapted,
            "success": True
        }

logging.basicConfig(level=logging.INFO)
def main():
    """测试入口"""
    skipper = DynamicStepSkipper(
        "flow-archive/20260318-universal-workflow-001/workflow.json"
    )
    
    # 测试场景 1: 时间压力
    print("\n[场景 1] 时间压力")
    skipper.run({
        "time_remaining_minutes": 8,
        "task_complexity": "medium",
        "new_tools_created": True,
        "risk_score": 0.5,
        "human_approval_obtained": False
    })
    
    # 测试场景 2: 简单任务
    print("\n[场景 2] 简单任务")
    skipper.run({
        "time_remaining_minutes": 30,
        "task_complexity": "low",
        "new_tools_created": False,
        "risk_score": 0.2,
        "human_approval_obtained": False
    })

if __name__ == "__main__":
    main()
