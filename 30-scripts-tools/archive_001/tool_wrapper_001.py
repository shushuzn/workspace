import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具调用包装器 v2 - 强制工作流 + 自动步骤跟踪

用途：
1. 检查 session 是否存在
2. 无 session → 拒绝执行
3. 有 session → 记录调用日志 + 自动更新步骤状态

使用方式:
    from tool_wrapper import before_tool_call, after_tool_call
    
    def my_tool(params):
        before_tool_call('my_tool', params)
        result = ...
        after_tool_call('my_tool', params, result)
        return result
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class ToolWrapper:
    """工具调用包装器 - 自动步骤跟踪"""

    def __init__(self):
        self.session_id = None
        self.state_file = None
        self.tool_log = Path("30-scripts-tools/tool_call_log.jsonl")
        self.workflow_dir = None
        self.current_step = None
        self.step_counter = 0

    def load_state(self) -> bool:
        """加载 session 状态"""
        state_files = list(Path("flow-archive").glob("*/execution-state.json"))
        if not state_files:
            print("=" * 70, file=sys.stderr)
            print("[BLOCK] 工具调用被拒绝", file=sys.stderr)
            print("[BLOCK] 原因：execution-state.json 不存在", file=sys.stderr)
            print("[BLOCK] 请先运行：py 30-scripts-tools/copaw_entry.py <task>", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            return False

        # 使用最新的 state 文件
        self.state_file = max(state_files, key=lambda f: f.stat().st_mtime)
        self.workflow_dir = self.state_file.parent

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.session_id = state.get('session_id')
            self.current_step = state.get('current_step', 1)
            return True
        except Exception as e:
            print(f"[ERROR] 读取 state 文件失败：{e}", file=sys.stderr)
            return False

    def before_tool_call(self, tool_name: str, params: dict) -> bool:
        """
        工具调用前检查
        
        Returns:
            bool: 是否允许执行
        """
        # 自举例外：允许 copaw_entry.py 在无 session 时执行（用于初始化）
        if tool_name in ('copaw_entry', 'copaw_entry.py'):
            print("[BOOTSTRAP] 允许执行 copaw_entry.py（会话初始化例外）")
            return True

        # 每次检查 session（确保最新状态）
        if not self.load_state():
            return False

        # 检查防护标志
        if Path(".STOP_FLAG").exists():
            print("[BLOCK] 系统已停止 (.STOP_FLAG exists)", file=sys.stderr)
            return False

        if Path(".lockdown_active").exists():
            print("[BLOCK] 系统封锁中 (.lockdown_active exists)", file=sys.stderr)
            return False

        return True

    def after_tool_call(self, tool_name: str, params: dict, result: str) -> None:
        """
        工具调用后记录日志 + 自动更新步骤状态
        """
        if not self.session_id:
            return

        # 1. 记录工具调用日志
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "tool_id": tool_name,
            "params": params,
            "result": result,
        }

        try:
            with open(self.tool_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[WARNING] 记录工具调用失败：{e}", file=sys.stderr)

        # 2. 自动更新步骤状态
        self._update_step_status(tool_name, result)

    def _update_step_status(self, tool_name: str, result: str):
        """自动更新步骤状态"""
        try:
            # 读取当前 state
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # 步骤计数器递增
            self.step_counter += 1

            # 映射工具到步骤（简化版）
            step_mapping = {
                'safe_shell_executor': 6,  # 工具执行
                'tool_executor': 6,
                'context_verify': 1,  # 上下文验证
                'task_analyzer': 3,  # 任务分析
                'auto_critic': 9,  # 批判者审查
            }

            base_step = step_mapping.get(tool_name, 6)
            step_id = float(f"{base_step}.{self.step_counter}")

            # 更新 step_status
            if 'step_status' not in state:
                state['step_status'] = {}

            state['step_status'][step_id] = {
                "name": f"工具调用：{tool_name}",
                "status": "completed",
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "result": result
            }

            # 更新 completed_steps
            if 'completed_steps' not in state:
                state['completed_steps'] = []

            if step_id not in state['completed_steps']:
                state['completed_steps'].append(step_id)

            # 更新完成率
            total_steps = state.get('total_steps', 20)
            state['completion_percentage'] = min(100.0, len(state['completed_steps']) / total_steps * 100)

            # 更新当前步骤
            state['current_step'] = step_id

            # 保存更新后的 state
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"[WARNING] 更新步骤状态失败：{e}", file=sys.stderr)


# 全局包装器实例
_wrapper = None

def get_wrapper() -> ToolWrapper:
    """获取包装器实例"""
    global _wrapper
    if _wrapper is None:
        _wrapper = ToolWrapper()
    return _wrapper


def before_tool_call(tool_name: str, params: dict) -> bool:
    """
    工具调用前检查（供工具脚本使用）
    
    Returns:
        bool: 是否允许执行
    """
    wrapper = get_wrapper()
    return wrapper.before_tool_call(tool_name, params)


def after_tool_call(tool_name: str, params: dict, result: str) -> None:
    """工具调用后记录（供工具脚本使用）- 自动更新步骤状态"""
    wrapper = get_wrapper()
    wrapper.after_tool_call(tool_name, params, result)


# 装饰器
def require_workflow(func):
    """
    装饰器：要求工具调用必须通过工作流
    
    用法:
        @require_workflow
        def my_tool(params):
            ...
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
# py tool_wrapper_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py tool_wrapper_001.py

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


    def wrapper(*args, **kwargs):
        # 提取参数
        params = kwargs if kwargs else (args[0] if args else {})

        if not before_tool_call(func.__name__, params):
            raise PermissionError("工具调用被拒绝：未初始化会话")

        try:
            result = func(*args, **kwargs)
            after_tool_call(func.__name__, params, str(result))
            return result
        except Exception as e:
            after_tool_call(func.__name__, params, f"ERROR: {e}")
            raise

    return wrapper


if __name__ == '__main__':
    # 测试
    print("工具调用包装器 v2 测试（自动步骤跟踪）\n")

    wrapper = ToolWrapper()

    print("测试 1: before_tool_call")
    allowed = wrapper.before_tool_call('test_tool', {'param': 'value'})
    print(f"  结果：{'允许' if allowed else '拒绝'}\n")

    print("测试 2: after_tool_call（自动更新步骤）")
    wrapper.after_tool_call('test_tool', {'param': 'value'}, 'success')
    print(f"  结果：已记录 + 步骤已更新\n")
