#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自适应工作流编排工具 - 基于 arXiv 2512.04521
根据任务类型/复杂度/上下文动态调整工作流步骤
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class AdaptiveWorkflowOrchestrator:
    """自适应工作流编排器"""
    
    # 任务类型到工作流配置的映射
    WORKFLOW_PROFILES = {
        "simple_query": {
            "name": "简单查询",
            "steps_to_skip": [2, 6.6, 8.5, 13],
            "parallel_enabled": False,
            "timeout_multiplier": 0.5
        },
        "research_task": {
            "name": "研究任务",
            "steps_to_enhance": [2, 6, 9, 10],
            "additional_steps": ["literature_review", "citation_check"],
            "timeout_multiplier": 2.0
        },
        "code_development": {
            "name": "代码开发",
            "steps_to_enhance": [6, 6.5, 6.6, 10],
            "additional_steps": ["code_review", "security_scan"],
            "timeout_multiplier": 1.5
        },
        "brainstorm": {
            "name": "头脑风暴",
            "steps_to_skip": [6.5, 6.6, 8.5],
            "divergent_phase": True,
            "convergent_phase": True,
            "timeout_multiplier": 1.2
        },
        "data_analysis": {
            "name": "数据分析",
            "steps_to_enhance": [6, 6.6, 9, 10],
            "additional_steps": ["data_validation", "statistical_test"],
            "timeout_multiplier": 1.8
        }
    }
    
    def __init__(self, workflow_file: str):
        self.workflow_file = Path(workflow_file)
        with open(self.workflow_file, 'r', encoding='utf-8') as f:
            self.workflow = json.load(f)
    
    def detect_task_type(self, task_description: str) -> str:
        """检测任务类型"""
        
        task_lower = task_description.lower()
        
        if any(kw in task_lower for kw in ["查询", "query", "简单", "simple"]):
            return "simple_query"
        elif any(kw in task_lower for kw in ["研究", "research", "论文", "paper"]):
            return "research_task"
        elif any(kw in task_lower for kw in ["代码", "code", "开发", "development", "编程"]):
            return "code_development"
        elif any(kw in task_lower for kw in ["头脑风暴", "brainstorm", "创意", "ideas"]):
            return "brainstorm"
        elif any(kw in task_lower for kw in ["数据", "data", "分析", "analysis", "统计"]):
            return "data_analysis"
        else:
            return "general"
    
    def adapt_workflow(self, task_type: str) -> Dict:
        """根据任务类型自适应调整工作流"""
        
        if task_type not in self.WORKFLOW_PROFILES:
            print(f"[Adaptive] 使用通用工作流 (未识别任务类型：{task_type})")
            return self.workflow
        
        profile = self.WORKFLOW_PROFILES[task_type]
        adapted = self.workflow.copy()
        
        print(f"\n[Adaptive] 任务类型：{task_type} - {profile['name']}")
        
        # 调整步骤
        steps_to_skip = profile.get("steps_to_skip", [])
        adapted_steps = []
        
        for step in adapted["steps"]:
            step_id = step["step_id"]
            
            # 跳过指定步骤
            if step_id in steps_to_skip:
                step["conditional"] = {
                    "run_if": "false",
                    "skip_message": f"自适应跳过：{task_type} 不需要此步骤"
                }
                print(f"  [Skip] Step {step_id}: {step['name']}")
            
            # 增强指定步骤
            if step_id in profile.get("steps_to_enhance", []):
                step["enhanced"] = True
                step["timeout_seconds"] = int(step.get("timeout_seconds", 60) * 1.5)
                print(f"  [Enhance] Step {step_id}: {step['name']} (timeout x1.5)")
            
            adapted_steps.append(step)
        
        adapted["steps"] = adapted_steps
        
        # 应用超时乘数
        timeout_mult = profile.get("timeout_multiplier", 1.0)
        adapted["timeout_multiplier"] = timeout_mult
        print(f"  [Timeout] 全局超时乘数：x{timeout_mult}")
        
        return adapted
    
    def save_adapted_workflow(self, adapted: Dict, output_file: str):
        """保存自适应工作流"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(adapted, f, ensure_ascii=False, indent=2)
        
        print(f"\n[OK] 自适应工作流已保存到：{output_file}")
    
    def run(self, task_description: str, output_file: Optional[str] = None) -> Dict:
        """完整流程：检测 -> 适配 -> 保存"""
        
        # 检测任务类型
        task_type = self.detect_task_type(task_description)
        
        # 自适应调整
        adapted = self.adapt_workflow(task_type)
        
        # 保存
        if output_file:
            self.save_adapted_workflow(adapted, output_file)
        
        return {
            "task_type": task_type,
            "adapted_workflow": adapted,
            "success": True
        }

def main():
    """测试入口"""
    orchestrator = AdaptiveWorkflowOrchestrator(
        "flow-archive/20260318-universal-workflow-001/workflow.json"
    )
    
    # 测试不同任务类型
    test_tasks = [
        "简单查询：今天天气如何？",
        "研究任务：CNT 导电性预测研究",
        "代码开发：创建 Python 工具脚本",
        "头脑风暴：AI Agent 优化想法",
        "数据分析：实验数据统计分析"
    ]
    
    for task in test_tasks:
        print("\n" + "=" * 60)
        result = orchestrator.run(task, output_file=None)
        print(f"任务：{task[:30]}...")
        print(f"类型：{result['task_type']}")

if __name__ == "__main__":
    main()
