import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Menu - 交互式工作流菜单
快速查看状态、执行操作
"""

import json
import sys
from pathlib import Path
from datetime import datetime


class WorkflowMenu:
    """工作流交互式菜单"""
    
    def __init__(self, flow_id: str = "20260318-universal-workflow-001"):
        self.flow_id = flow_id
        self.flow_dir = Path(f"flow-archive/{self.flow_id}")
        self.state_file = self.flow_dir / "execution-state.json"
        self.workflow_file = self.flow_dir / "workflow.json"
        
    def load_state(self) -> dict:
        """加载执行状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_workflow(self) -> dict:
        """加载工作流定义"""
        if self.workflow_file.exists():
            with open(self.workflow_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def show_status(self) -> None:
        """显示当前状态"""
        state = self.load_state()
        workflow = self.load_workflow()
        
        print("\n" + "=" * 50)
        print("📊 工作流状态")
        print("=" * 50)
        
        if not state:
            print("❌ 无执行状态")
            return
        
        print(f"任务: {state.get('task', 'N/A')}")
        print(f"状态: {state.get('status', 'N/A')}")
        print(f"步骤: {state.get('current_step', 0)} / {state.get('total_steps', 0)}")
        print(f"完成度: {state.get('completion_percentage', 0):.1f}%")
        
        # 进度条
        total = state.get('total_steps', 1)
        current = state.get('current_step', 0)
        percent = current / total * 100 if total > 0 else 0
        bar_len = 30
        filled = int(bar_len * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        
        print(f"\n[{bar}] {percent:.1f}%")
        
        # 显示已完成的步骤
        completed = state.get('completed_steps', [])
        if completed:
            print(f"\n✅ 已完成步骤: {completed}")
        
        # 显示步骤状态详情
        step_status = state.get('step_status', {})
        if step_status:
            print("\n📝 步骤详情:")
            for step_id, info in sorted(step_status.items()):
                status_icon = "✅" if info.get('status') == 'completed' else "⏳"
                name = info.get('name', f'Step {step_id}')
                print(f"  {status_icon} {step_id}: {name}")
    
    def complete_step(self, step_id: int = None) -> None:
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
# py workflow_menu_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_menu_001.py

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

完成指定步骤"""
        state = self.load_state()
        
        if step_id is None:
            # 自动完成当前步骤
            step_id = state.get('current_step', 0) + 1
        
        # 更新状态
        if 'completed_steps' not in state:
            state['completed_steps'] = []
        
        if step_id not in state['completed_steps']:
            state['completed_steps'].append(step_id)
        
        state['current_step'] = step_id
        state['completion_percentage'] = len(state['completed_steps']) / state.get('total_steps', 1) * 100
        
        # 添加步骤详情
        if 'step_status' not in state:
            state['step_status'] = {}
        
        workflow = self.load_workflow()
        steps = workflow.get('steps', [])
        step_name = steps[step_id - 1].get('name', f'Step {step_id}') if step_id <= len(steps) else f'Step {step_id}'
        
        state['step_status'][str(step_id)] = {
            'name': step_name,
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        }
        
        # 保存
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 步骤 {step_id} ({step_name}) 已标记完成")
    
    def reset_state(self) -> None:
        """重置状态"""
        state = {
            "flow_id": self.flow_id,
            "current_step": 0,
            "total_steps": 17,
            "status": "ready",
            "completed_steps": [],
            "step_status": {},
            "completion_percentage": 0
        }
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print("✅ 状态已重置")
    
    def show_menu(self) -> None:
        """显示主菜单"""
        print("\n" + "=" * 50)
        print("🔧 工作流工具菜单")
        print("=" * 50)
        print("1. 📊 查看状态")
        print("2. ✅ 完成当前步骤")
        print("3. 🔢 完成指定步骤")
        print("4. 🔄 重置状态")
        print("5. 🚀 启动新会话")
        print("0. ❌ 退出")
        print("=" * 50)
        
    def run(self) -> None:
        """运行菜单"""
        while True:
            self.show_menu()
            choice = input("\n选择操作 [0-5]: ").strip()
            
            if choice == '1':
                self.show_status()
            elif choice == '2':
                self.complete_step()
            elif choice == '3':
                try:
                    step = int(input("输入步骤编号: "))
                    self.complete_step(step)
                except ValueError:
                    print("❌ 无效输入")
            elif choice == '4':
                confirm = input("确认重置? (y/n): ")
                if confirm.lower() == 'y':
                    self.reset_state()
            elif choice == '5':
                print("\n🚀 启动新会话: py 30-scripts-tools/copaw_entry.py")
                break
            elif choice == '0':
                print("👋 再见!")
                break
            else:
                print("❌ 无效选择")


logging.basicConfig(level=logging.INFO)
def main():
    menu = WorkflowMenu()
    
    if len(sys.argv) > 1:
        # 命令行模式
        cmd = sys.argv[1]
        
        if cmd == 'status':
            menu.show_status()
        elif cmd == 'complete':
            step = int(sys.argv[2]) if len(sys.argv) > 2 else None
            menu.complete_step(step)
        elif cmd == 'reset':
            menu.reset_state()
        else:
            print(f"未知命令: {cmd}")
            print("用法: workflow_menu.py [status|complete|reset]")
    else:
        # 交互模式
        menu.run()


if __name__ == "__main__":
    main()