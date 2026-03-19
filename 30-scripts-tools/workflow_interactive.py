#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interactive Menu for Workflow Execution
交互式菜单 - 降低工作流使用门槛 (方案 B)
"""

import json
import subprocess
import sys
import os
import io
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
FLOW_ARCHIVE = WORKSPACE / "flow-archive"

class WorkflowInteractive:
    def __init__(self, flow_id="20260318-universal-workflow-001"):
        self.flow_id = flow_id
        self.checkpoint_file = FLOW_ARCHIVE / flow_id / "checkpoint.json"
        self.workflow_file = FLOW_ARCHIVE / flow_id / "workflow.json"
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def load_state(self):
        if not self.checkpoint_file.exists():
            return None
        with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_workflow(self):
        if not self.workflow_file.exists():
            return None
        with open(self.workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def show_header(self, state, workflow):
        print("=" * 60)
        print(f"工作流执行器 - {workflow.get('name', 'Unknown')} (v{workflow.get('version', '?')})")
        print("=" * 60)
        
        if state:
            total = state.get('total_steps', 0)
            completed = len(state.get('completed_steps', []))
            progress = int(completed / total * 10) if total > 0 else 0
            progress_bar = "█" * progress + "░" * (10 - progress)
            percentage = int(completed / total * 100) if total > 0 else 0
            
            print(f"\n进度：[{progress_bar}] {completed}/{total} 步骤完成 ({percentage}%)")
            print(f"状态：{state.get('status', 'unknown')}")
            print(f"违规：{len(state.get('violations', []))} 次")
    
    def show_current_step(self, state, workflow):
        if not state or not workflow:
            return
        
        completed = state.get('completed_steps', [])
        current_step_num = len(completed) + 1
        
        steps = workflow.get('steps', [])
        if current_step_num > len(steps):
            print("\n[OK] 所有步骤已完成!")
            return
        
        current_step = steps[current_step_num - 1]
        step_name = current_step.get('name', 'Unknown')
        blocking = current_step.get('blocking', False)
        blocking_tag = "[阻塞]" if blocking else "[非阻塞]"
        
        print(f"\n{'=' * 60}")
        print(f"当前步骤：{current_step_num}. {step_name} {blocking_tag}")
        print(f"{'=' * 60}")
        print(f"\n描述：{current_step.get('description', 'N/A')}")
        print(f"工具：{current_step.get('tool_id', 'N/A')}")
    
    def show_menu(self):
        print("\n可用操作:")
        print("  1. 执行当前步骤")
        print("  2. 查看步骤详情")
        print("  3. 查看工作流完整状态")
        print("  4. 查看执行历史")
        print("  5. 跳过当前步骤 (需要确认)")
        print("  6. 暂停工作流")
        print("  7. 退出（保持工作流状态）")
        print("  8. 刷新状态")
        print("  9. 帮助")
    
    def execute_current_step(self, state, workflow):
        if not state or not workflow:
            print("[ERROR] 工作流未启动")
            return
        
        completed = state.get('completed_steps', [])
        current_step_num = len(completed) + 1
        
        steps = workflow.get('steps', [])
        if current_step_num > len(steps):
            print("[OK] 所有步骤已完成!")
            return
        
        current_step = steps[current_step_num - 1]
        tool_id = current_step.get('tool_id')
        
        if not tool_id:
            print(f"[INFO] 步骤 {current_step_num} 无关联工具")
            return
        
        registry_file = WORKSPACE / "30-scripts-tools" / "tools_registry.json"
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        tool_config = registry.get('tools', {}).get(tool_id)
        if not tool_config:
            print(f"[ERROR] 工具未找到：{tool_id}")
            return
        
        command = tool_config.get('command')
        print(f"\n[执行] {command}")
        print("-" * 60)
        
        result = subprocess.run(command, shell=True, encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            print("\n[OK] 工具执行成功，自动完成步骤...")
            subprocess.run([
                sys.executable,
                str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
                "--complete-step",
                str(current_step_num)
            ])
        else:
            print("\n[ERROR] 工具执行失败")
    
    def show_step_details(self, state, workflow):
        if not workflow:
            return
        
        steps = workflow.get('steps', [])
        print("\n步骤详情:")
        print("-" * 60)
        
        for i, step in enumerate(steps, 1):
            status = "[✓]" if i in state.get('completed_steps', []) else "[ ]"
            blocking = "[阻塞]" if step.get('blocking', False) else "[非阻塞]"
            print(f"{status} {i}. {step.get('name')} {blocking}")
    
    def show_full_status(self, state):
        if not state:
            print("[INFO] 工作流未启动")
            return
        
        print("\n完整状态:")
        print("-" * 60)
        for key, value in state.items():
            if isinstance(value, list):
                print(f"{key}: {value}")
            else:
                print(f"{key}: {value}")
    
    def show_history(self):
        log_file = FLOW_ARCHIVE / self.flow_id / "execution-log.json"
        
        if not log_file.exists():
            print("[INFO] 无执行历史")
            return
        
        with open(log_file, 'r', encoding='utf-8') as f:
            log = json.load(f)
        
        print("\n执行历史:")
        print("-" * 60)
        
        executions = log.get('executions', [])
        for exec_item in executions[-10:]:
            print(f"  步骤 {exec_item.get('step')}: {exec_item.get('tool_id')}")
            print(f"    时间：{exec_item.get('timestamp', 'N/A')}")
            print(f"    结果：{'✓' if exec_item.get('success') else '✗'}")
    
    def skip_step(self, state):
        confirm = input("\n确认跳过当前步骤？(y/N): ")
        if confirm.lower() != 'y':
            print("[取消] 跳过操作已取消")
            return
        
        print("[WARN] 步骤已跳过，违规已记录")
    
    def run(self):
        print("\n[启动] 加载工作流...")
        
        state = self.load_state()
        workflow = self.load_workflow()
        
        if not workflow:
            print("[ERROR] 工作流配置未找到!")
            return
        
        if not state:
            print("[INFO] 工作流未启动，是否现在启动？")
            confirm = input("启动工作流？(y/N): ")
            if confirm.lower() == 'y':
                subprocess.run([
                    sys.executable,
                    str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
                    "--start"
                ])
                state = self.load_state()
            else:
                return
        
        while True:
            self.clear_screen()
            self.show_header(state, workflow)
            self.show_current_step(state, workflow)
            self.show_menu()
            
            choice = input("\n选择操作 [1-9]: ").strip()
            
            if choice == '1':
                self.execute_current_step(state, workflow)
            elif choice == '2':
                self.show_step_details(state, workflow)
            elif choice == '3':
                self.show_full_status(state)
            elif choice == '4':
                self.show_history()
            elif choice == '5':
                self.skip_step(state)
            elif choice == '6':
                print("[暂停] 工作流已暂停")
                input("按 Enter 继续...")
            elif choice == '7':
                print("[退出] 保持工作流状态")
                break
            elif choice == '8':
                state = self.load_state()
                print("[刷新] 状态已更新")
                input("按 Enter 继续...")
            elif choice == '9':
                print("\n帮助:")
                print("  - 数字 1-9 选择对应操作")
                print("  - 步骤分阻塞/非阻塞两种")
                print("  - 阻塞步骤必须完成才能继续")
                input("\n按 Enter 继续...")
            
            state = self.load_state()


if __name__ == '__main__':
    ui = WorkflowInteractive()
    ui.run()
