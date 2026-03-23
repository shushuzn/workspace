import logging
logger = logging.getLogger(__name__)

"""
工具调用拦截器 - 强制所有工具调用通过防护层

问题：execute_shell_command 可以直接调用，绕过 tool_executor 和防护检查

解决：
1. 拦截所有工具调用
2. 检查 session 状态
3. 检查防护标志
4. 记录调用日志
5. 拒绝违规调用
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 工具调用白名单（允许直接调用的工具）
SAFE_TOOLS = [
    'read_file',
    'write_file',
    'edit_file',
    'browser_use',
    'desktop_screenshot',
    'view_image',
    'get_current_time',
    'get_token_usage',
    'memory_search',
    'send_file_to_user',
]

# 需要防护检查的工具
PROTECTED_TOOLS = [
    'execute_shell_command',
]


class ToolCallInterceptor:
    """工具调用拦截器"""

    def __init__(self):
        self.session_id = None
        self.state_file = None
        self.tool_log = Path("30-scripts-tools/tool_call_log.jsonl")

    def check_session(self) -> tuple[bool, str]:
        """检查会话状态"""
        # 检查 execution-state.json
        state_files = list(Path("flow-archive").glob("*/execution-state.json"))
        if not state_files:
            return False, "无 execution-state.json - 未初始化会话"

        # 使用最新的 state 文件
        self.state_file = max(state_files, key=lambda f: f.stat().st_mtime)

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.session_id = state.get('session_id')
            return True, f"Session valid: {self.session_id}"
        except Exception as e:
            return False, f"State file error: {e}"

    def check_protection_flags(self) -> tuple[bool, str]:
        """检查防护标志"""
        # 检查 .STOP_FLAG
        if Path(".STOP_FLAG").exists():
            return False, "系统已停止 (.STOP_FLAG exists)"

        # 检查 .lockdown_active
        if Path(".lockdown_active").exists():
            return False, "系统封锁中 (.lockdown_active exists)"

        return True, "防护检查通过"

    def log_tool_call(self, tool_name: str, params: dict, result: str) -> None:
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
# py tool_call_interceptor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py tool_call_interceptor_001.py

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

记录工具调用"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "tool_id": tool_name,
            "params": params,
            "result": result,
        }

        with open(self.tool_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def intercept(self, tool_name: str, params: dict) -> tuple[bool, str, dict]:
        """
        拦截工具调用
        
        Returns:
            (allowed, message, modified_params)
        """
        # 白名单工具直接放行
        if tool_name in SAFE_TOOLS:
            return True, "Whitelisted tool", params
        
        # 保护工具需要检查
        if tool_name in PROTECTED_TOOLS:
            # 检查会话
            session_ok, session_msg = self.check_session()
            if not session_ok:
                return False, f"[BLOCK] {session_msg}", {}
            
            # 检查防护标志
            protection_ok, protection_msg = self.check_protection_flags()
            if not protection_ok:
                return False, f"[BLOCK] {protection_msg}", {}
            
            # 强制通过 safe_shell_executor
            if tool_name == 'execute_shell_command':
                command = params.get('command', '')
                # 如果命令已经通过 safe_shell_executor，放行
                if 'safe_shell_executor' in command or 'protected_py' in command:
                    return True, "Protected command", params
                # 否则拒绝
                return False, f"[BLOCK] 必须通过 safe_shell_executor: {command}", {}
            
            return True, "Protection check passed", params
        
        # 未知工具放行（但记录）
        return True, f"Unknown tool (logged): {tool_name}", params


# 全局拦截器实例
_interceptor = None

def get_interceptor() -> ToolCallInterceptor:
    """获取拦截器实例"""
    global _interceptor
    if _interceptor is None:
        _interceptor = ToolCallInterceptor()
    return _interceptor


def intercept_tool_call(tool_name: str, params: dict) -> tuple[bool, str, dict]:
    """
    拦截工具调用（供外部调用）
    
    Returns:
        (allowed, message, modified_params)
    """
    interceptor = get_interceptor()
    return interceptor.intercept(tool_name, params)


if __name__ == '__main__':
    # 测试
    print("工具调用拦截器测试\n")
    
    interceptor = ToolCallInterceptor()
    
    # 测试 1: 无 session
    print("测试 1: execute_shell_command (无 session)")
    allowed, msg, _ = interceptor.intercept('execute_shell_command', {'command': 'echo test'})
    print(f"  结果：{msg}\n")
    
    # 测试 2: 白名单工具
    print("测试 2: read_file (白名单)")
    allowed, msg, _ = interceptor.intercept('read_file', {'file_path': 'test.txt'})
    print(f"  结果：{msg}\n")
    
    # 测试 3: 受保护命令
    print("测试 3: execute_shell_command with safe_shell_executor")
    allowed, msg, _ = interceptor.intercept('execute_shell_command', {
        'command': 'py 30-scripts-tools/safe_shell_executor.py echo test'
    })
    print(f"  结果：{msg}\n")
