#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Integration - Agentic BPM 与 Workflow 系统集成
让工作流系统可以使用 Agentic BPM 管理任务
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / '80-PROJECTS/agentic-bpm'))
sys.path.insert(0, str(Path(__file__).parent))

from agentic_bpm import AgenticOrchestrator, Task
from workflow_menu import WorkflowMenu


class WorkflowIntegration:
    """工作流集成器 - 连接 Agentic BPM 和 Workflow 系统"""
    
    def __init__(self):
        self.orchestrator = AgenticOrchestrator()
        self.menu = WorkflowMenu()
        
        # 加载最新工作流
        self._load_workflow()
    
    def _load_workflow(self):
        """加载最新的 Agentic BPM 工作流"""
        wf_dir = self.orchestrator.workflow_dir
        wf_files = list(wf_dir.glob("*.json"))
        if wf_files:
            wf_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            self.orchestrator.load_workflow(wf_files[0].stem)
    
    def sync_from_workflow(self):
        """从现有工作流同步任务到 Agentic BPM"""
        
        # 获取当前工作流状态
        state = self.menu.load_state()
        workflow = self.menu.load_workflow()
        
        if not state:
            print("❌ No workflow state found")
            return False
        
        # 创建新工作流
        wf_name = state.get('task', 'Synced Workflow')
        wf = self.orchestrator.create_workflow(wf_name, "Synced from workflow system")
        
        # 获取步骤定义
        steps = workflow.get('steps', [])
        completed = state.get('completed_steps', [])
        
        # 转换为任务
        for i, step in enumerate(steps, 1):
            step_id = f"s{i}"
            step_name = step.get('name', f'Step {i}')
            step_desc = step.get('description', '')
            
            # 检查是否有依赖
            depends_on = []
            if i > 1:
                # 前一个步骤是依赖
                depends_on = [f"s{i-1}"]
            
            task = Task(
                id=step_id,
                name=step_name,
                description=step_desc,
                priority=10 - i if i <= 10 else 5,
                depends_on=depends_on,
                status="completed" if i in completed else "pending"
            )
            
            self.orchestrator.add_task(task)
        
        # 保存
        self.orchestrator.save_workflow()
        
        print(f"✅ Synced {len(steps)} steps to Agentic BPM")
        return True
    
    def sync_to_workflow(self):
        """从 Agentic BPM 同步状态回工作流"""
        
        # 获取当前任务进度
        status = self.orchestrator.get_status()
        
        if status.get('status') == 'no_workflow':
            print("❌ No Agentic BPM workflow found")
            return False
        
        # 更新工作流状态
        state = self.menu.load_state()
        
        # 统计已完成的任务
        completed_count = status['stats']['completed']
        
        # 更新步骤
        state['current_step'] = completed_count
        state['completion_percentage'] = status['progress']
        
        # 获取已完成的步骤
        if self.orchestrator.current_workflow:
            completed_steps = []
            for task in self.orchestrator.current_workflow.tasks:
                if task.status == 'completed':
                    try:
                        step_num = int(task.id.replace('s', ''))
                        completed_steps.append(step_num)
                    except:
                        pass
            
            state['completed_steps'] = completed_steps
        
        # 保存
        flow_dir = Path(f"flow-archive/{state.get('flow_id', '20260318-universal-workflow-001')}")
        state_file = flow_dir / "execution-state.json"
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Synced progress: {status['progress']:.1f}%")
        return True
    
    def run_integrated(self):
        """运行集成模式"""
        
        print("\n" + "=" * 50)
        print("🔄 Agentic BPM + Workflow 集成模式")
        print("=" * 50)
        
        # Step 1: 同步任务
        print("\n[1/3] Syncing from workflow...")
        if not self.sync_from_workflow():
            return
        
        # Step 2: 执行下一步
        print("\n[2/3] Executing next task...")
        result = self.orchestrator.execute_next()
        
        print(f"   → {result.get('message', result['status'])}")
        
        # Step 3: 同步状态
        print("\n[3/3] Syncing back to workflow...")
        self.sync_to_workflow()
        
        # 显示状态
        status = self.orchestrator.get_status()
        print(f"\n📊 Progress: {status['progress']:.1f}%")
    
    def show_menu(self):
        """显示集成菜单"""
        status = self.orchestrator.get_status()
        
        print("\n" + "=" * 50)
        print("🔧 Agentic BPM + Workflow 集成")
        print("=" * 50)
        print(f"当前工作流: {status.get('workflow_name', 'N/A')}")
        print(f"进度: {status.get('progress', 0):.1f}%")
        print("-" * 50)
        print("1. 同步任务到 Agentic BPM")
        print("2. 执行下一步")
        print("3. 同步状态回工作流")
        print("4. 运行集成模式")
        print("5. 查看 Agentic BPM 状态")
        print("0. 退出")
    
    def run(self):
        """运行交互式菜单"""
        while True:
            self.show_menu()
            choice = input("\n选择 [0-5]: ").strip()
            
            if choice == '1':
                self.sync_from_workflow()
            elif choice == '2':
                result = self.orchestrator.execute_next()
                print(f"→ {result.get('message', result['status'])}")
            elif choice == '3':
                self.sync_to_workflow()
            elif choice == '4':
                self.run_integrated()
            elif choice == '5':
                status = self.orchestrator.get_status()
                print(f"\n📊 {json.dumps(status, indent=2, ensure_ascii=False)}")
            elif choice == '0':
                break


def main():
    integration = WorkflowIntegration()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'sync':
            integration.sync_from_workflow()
        elif cmd == 'next':
            result = integration.orchestrator.execute_next()
            print(result.get('message', result['status']))
        elif cmd == 'push':
            integration.sync_to_workflow()
        elif cmd == 'run':
            integration.run_integrated()
        elif cmd == 'status':
            status = integration.orchestrator.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: workflow_integration.py [sync|next|push|run|status]")
    else:
        integration.run()


if __name__ == "__main__":
    main()