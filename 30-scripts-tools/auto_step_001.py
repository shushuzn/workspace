import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Auto-Step - 自动步骤追踪
工具执行后自动完成对应步骤
"""

import json
import sys
from pathlib import Path
from datetime import datetime


class AutoStepTracker:
    """自动步骤追踪器"""
    
    def __init__(self, flow_id: str = "20260318-universal-workflow-001"):
        self.flow_id = flow_id
        self.flow_dir = Path(f"flow-archive/{flow_id}")
        self.state_file = self.flow_dir / "execution-state.json"
        
    def load_state(self) -> dict:
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_state(self, state: dict):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def auto_complete(self, tool_name: str = None) -> None:
        """
        根据工具调用自动完成步骤
        
        映射规则：
        - read_file/grep_search → Step 2 (上下文加载)
        - write_file/edit_file → Step 3 (任务规划)
        - browser_use → Step 4 (工具执行)
        - execute_shell_command → Step 4 (工具执行)
        """
        state = self.load_state()
        
        # 工具到步骤的映射
        tool_step_map = {
            # Step 1: 上下文加载
            'read_file': 1,
            'grep_search': 1,
            'glob_search': 1,
            'memory_search': 1,
            
            # Step 2: 任务解析
            'get_current_time': 2,
            'get_token_usage': 2,
            
            # Step 3: 任务规划/工具选择
            'write_file': 3,
            'edit_file': 3,
            
            # Step 4: 工具执行
            'browser_use': 4,
            'execute_shell_command': 4,
            'send_file_to_user': 4,
        }
        
        # 如果没有指定工具名，根据当前步骤自动+1
        if tool_name is None:
            next_step = state.get('current_step', 0) + 1
        else:
            next_step = tool_step_map.get(tool_name, state.get('current_step', 0) + 1)
        
        # 完成该步骤
        if 'completed_steps' not in state:
            state['completed_steps'] = []
        
        if next_step not in state['completed_steps']:
            state['completed_steps'].append(next_step)
        
        state['current_step'] = next_step
        state['completion_percentage'] = len(state['completed_steps']) / state.get('total_steps', 1) * 100
        state['last_updated'] = datetime.now().isoformat()
        
        self.save_state(state)
        
        print(f"✅ 自动完成步骤 {next_step}")
        print(f"   当前进度: {state['completion_percentage']:.1f}%")
        
        return state


logging.basicConfig(level=logging.INFO)
def main():
    tracker = AutoStepTracker()
    
    tool = sys.argv[1] if len(sys.argv) > 1 else None
    tracker.auto_complete(tool)


if __name__ == "__main__":
    main()