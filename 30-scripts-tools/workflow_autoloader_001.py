#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流自动加载器 - 每次任务开始自动显示完整 20 步
强制读取 workflow.json，显示所有步骤，不允许跳过
"""

import json
from pathlib import Path
from datetime import datetime

class WorkflowAutoLoader:
    """工作流自动加载器 - 强制显示所有步骤"""
    
    def __init__(self):
        self.workflow_file = Path("flow-archive/20260318-universal-workflow-001/workflow.json")
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        
        if not self.workflow_file.exists():
            raise FileNotFoundError("主工作流配置文件不存在！")
        
        with open(self.workflow_file, 'r', encoding='utf-8') as f:
            self.workflow = json.load(f)
    
    def load_and_display(self, task_description: str) -> dict:
        """加载并显示完整工作流"""
        
        print("\n" + "=" * 80)
        print(" " * 20 + "主工作流自动加载")
        print("=" * 80)
        print(f"\n任务：{task_description}")
        print(f"Flow ID: {self.workflow.get('flow_id', '20260318-universal-workflow-001')}")
        print(f"版本：{self.workflow.get('version', 'unknown')}")
        print(f"时间：{datetime.now().isoformat()}")
        
        # 显示所有步骤
        steps = self.workflow.get('steps', [])
        print(f"\n完整步骤：{len(steps)} 步")
        print("-" * 80)
        
        for i, step in enumerate(steps, 1):
            step_id = str(step.get('step_id', i))
            step_name = step.get('name', f'Step {i}')
            required = step.get('required', True)
            tool = step.get('tool', 'N/A')
            
            req_mark = "[必需]" if required else "[可选]"
            print(f"  {i:2d}. {step_id:6s} {step_name:30s} {req_mark:6s} (工具：{tool})")
        
        print("-" * 80)
        print(f"\n总计：{len(steps)} 步 (必需：{sum(1 for s in steps if s.get('required', True))} 步)")
        
        # 初始化执行状态
        state = {
            "flow_id": self.workflow.get('flow_id'),
            "task": task_description,
            "started_at": datetime.now().isoformat(),
            "total_steps": len(steps),
            "completed_steps": [],
            "current_step": None,
            "status": "started"
        }
        
        # 保存状态
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"\n执行状态已保存：{self.state_file}")
        print("=" * 80)
        
        return state
    
    def mark_step_complete(self, step_id: str) -> dict:
        """标记步骤完成"""
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        if step_id not in state['completed_steps']:
            state['completed_steps'].append(step_id)
            state['current_step'] = step_id
            state['updated_at'] = datetime.now().isoformat()
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        return state
    
    def check_completion(self) -> dict:
        """检查完成度"""
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        steps = self.workflow.get('steps', [])
        required_steps = [s['step_id'] for s in steps if s.get('required', True)]
        completed = state['completed_steps']
        
        missing = [s for s in required_steps if s not in completed]
        completion_rate = len(completed) / len(required_steps) * 100 if required_steps else 0
        
        print("\n" + "=" * 80)
        print(" " * 25 + "工作流完成度检查")
        print("=" * 80)
        print(f"\n必需步骤：{len(required_steps)} 步")
        print(f"已完成：{len(completed)} 步")
        print(f"完成率：{completion_rate:.1f}%")
        
        if missing:
            print(f"\n缺失步骤：{len(missing)}")
            for step_id in missing:
                print(f"  - {step_id}")
        else:
            print("\n所有必需步骤已完成！")
        
        print("=" * 80)
        
        return {
            "total_required": len(required_steps),
            "completed": len(completed),
            "missing": len(missing),
            "missing_steps": missing,
            "completion_rate": completion_rate,
            "can_commit": len(missing) == 0
        }

def main():
    """测试入口"""
    loader = WorkflowAutoLoader()
    
    # 测试：加载并显示工作流
    print("测试：加载并显示主工作流")
    loader.load_and_display("P1 优化实施")
    
    # 测试：检查完成度
    print("\n测试：检查完成度")
    loader.check_completion()

if __name__ == "__main__":
    main()
