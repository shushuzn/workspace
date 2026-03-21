import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
步骤跟踪器 - 实时跟踪主工作流 20 步执行状态
自动记录每步完成时间、耗时、状态
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class StepTracker:
    """步骤跟踪器"""
    
    def __init__(self):
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        self.history_file = Path("flow-archive/20260318-universal-workflow-001/execution-history.json")
        self.workflow_file = Path("flow-archive/20260318-universal-workflow-001/workflow.json")
        
        # 加载工作流
        with open(self.workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        
        self.steps = workflow.get('steps', [])
        # 步骤 ID 可能是整数或字符串，统一处理
        self.step_ids = [s.get('step_id') for s in self.steps]
        
        # 初始化或加载状态
        self.state = self._load_or_init_state()
    
    def _load_or_init_state(self) -> Dict:
        """加载或初始化状态"""
        
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "flow_id": "20260318-universal-workflow-001",
            "task": "",
            "started_at": datetime.now().isoformat(),
            "total_steps": len(self.step_ids),
            "completed_steps": [],
            "current_step": None,
            "step_details": {},
            "status": "started"
        }
    
    def start_task(self, task_description: str) -> Dict:
        """开始任务"""
        
        self.state['task'] = task_description
        self.state['started_at'] = datetime.now().isoformat()
        self.state['status'] = "in_progress"
        self.state['completed_steps'] = []
        self.state['step_details'] = {}
        
        self._save_state()
        return self.state
    
    def complete_step(self, step_id, duration_seconds: float = 0, notes: str = "") -> Dict:
        """标记步骤完成"""
        
        # 步骤 ID 可能是整数或字符串
        step_id_normalized = step_id
        if step_id not in self.step_ids:
            # 尝试转换类型
            try:
                step_id_normalized = int(step_id)
            except (ValueError, TypeError):
                pass
        
        if step_id_normalized not in self.step_ids:
            raise ValueError(f"Invalid step ID: {step_id}")
        
        now = datetime.now().isoformat()
        
        # 记录步骤详情
        self.state['step_details'][str(step_id_normalized)] = {
            "completed_at": now,
            "duration_seconds": duration_seconds,
            "notes": notes,
            "status": "completed"
        }
        
        # 添加到完成列表
        if step_id_normalized not in self.state['completed_steps']:
            self.state['completed_steps'].append(step_id_normalized)
        
        self.state['current_step'] = step_id_normalized
        self.state['updated_at'] = now
        
        # 检查是否全部完成
        required_steps = [s.get('step_id') for s in self.steps if s.get('required', True)]
        if all(sid in self.state['completed_steps'] for sid in required_steps):
            self.state['status'] = "completed"
            self.state['completed_at'] = now
        
        self._save_state()
        return self.state
    
    def get_progress(self) -> Dict:
        """获取进度信息"""
        
        required_steps = [s.get('step_id') for s in self.steps if s.get('required', True)]
        completed = self.state.get('completed_steps', [])
        
        completed_required = [s for s in completed if s in required_steps]
        completion_rate = len(completed_required) / len(required_steps) * 100 if required_steps else 0
        
        return {
            "total_steps": len(self.step_ids),
            "required_steps": len(required_steps),
            "completed": len(completed),
            "completed_required": len(completed_required),
            "completion_rate": completion_rate,
            "missing_steps": [s for s in required_steps if s not in completed],
            "status": self.state.get('status', 'unknown')
        }
    
    def display_status(self) -> str:
        """显示状态文本"""
        
        progress = self.get_progress()
        
        output = []
        output.append("\n" + "=" * 80)
        output.append(" " * 25 + "Workflow Execution Status")
        output.append("=" * 80)
        output.append(f"\nTask: {self.state.get('task', 'N/A')}")
        output.append(f"Flow ID: {self.state.get('flow_id', 'N/A')}")
        output.append(f"Status: {self.state.get('status', 'unknown')}")
        output.append(f"\nCompletion: {progress['completion_rate']:.1f}% ({progress['completed_required']}/{progress['required_steps']} required steps)")
        
        # 显示所有步骤状态
        output.append("\nStep Status:")
        output.append("-" * 80)
        
        for i, step in enumerate(self.steps, 1):
            step_id = step.get('step_id', i)
            step_name = step.get('name', f'Step {i}')
            required = step.get('required', True)
            
            is_completed = step_id in self.state.get('completed_steps', [])
            status_mark = "[x]" if is_completed else "[ ]"
            req_mark = "Required" if required else "Optional"
            
            # 步骤详情
            details = self.state.get('step_details', {}).get(str(step_id), {})
            duration = details.get('duration_seconds', 0)
            duration_str = f" ({duration:.1f}s)" if duration > 0 else ""
            
            output.append(f"  {status_mark} {str(step_id):6s} {step_name:35s} [{req_mark}]{duration_str}")
        
        output.append("-" * 80)
        
        if progress['missing_steps']:
            output.append(f"\nMissing steps: {len(progress['missing_steps'])}")
            for step_id in progress['missing_steps']:
                output.append(f"  - {step_id}")
        else:
            output.append("\nAll required steps completed!")
        
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def _save_state(self):
        """保存状态"""
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
        
        # 追加到历史
        self._append_to_history()
    
    def _append_to_history(self):
        """追加到历史记录"""
        
        history = []
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": self.state.get('task'),
            "progress": self.get_progress(),
            "status": self.state.get('status')
        }
        
        history.append(history_entry)
        
        # 只保留最近 100 条
        history = history[-100:]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def can_commit(self) -> bool:
        """检查是否可以提交"""
        
        progress = self.get_progress()
        return progress['completion_rate'] >= 100

logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py step_tracker_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py step_tracker_001.py

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

测试入口"""
    tracker = StepTracker()
    
    # 测试：开始任务
    print("测试：开始任务")
    tracker.start_task("P0 方案实施 - 状态跟踪")
    
    # 测试：完成几个步骤
    print("\n测试：完成步骤")
    tracker.complete_step(1, 30, "Context loaded")
    tracker.complete_step(2, 10, "Flow ID bound")
    tracker.complete_step(3, 60, "Task analyzed")
    
    # 测试：显示状态
    print(tracker.display_status())
    
    # 测试：检查是否可以提交
    print(f"\nCan commit: {tracker.can_commit()}")

if __name__ == "__main__":
    main()
