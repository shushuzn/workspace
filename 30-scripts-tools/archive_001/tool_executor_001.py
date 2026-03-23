import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具执行器 - 所有工具调用的唯一入口

用途：
1. 拦截所有工具调用
2. 检查防护层
3. 记录调用日志
4. 拒绝违规调用

使用方式：
    py 30-scripts-tools/tool_executor.py execute_shell_command "echo test"
    py 30-scripts-tools/tool_executor.py read_file "file_path=test.txt"
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

# 导入防护层
try:
    from auto_protection_layer import get_protection_layer
    PROTECTION_ENABLED = True
except ImportError:
    PROTECTION_ENABLED = False

# 导入工具包装器（强制工作流检查）
try:
    from tool_wrapper import before_tool_call, after_tool_call
    TOOL_WRAPPER_ENABLED = True
except ImportError:
    TOOL_WRAPPER_ENABLED = False

# 导入工作流强制执行器（步骤验证）
try:
    from workflow_enforcer import WorkflowEnforcer
    WORKFLOW_ENFORCER_ENABLED = True
except ImportError:
    WORKFLOW_ENFORCER_ENABLED = False


def parse_args(args):
    """解析命令行参数"""
    if len(args) < 2:
        print("用法：py tool_executor.py <tool_name> [params...]")
        print("示例:")
        print("  py tool_executor.py execute_shell_command \"echo test\"")
        print("  py tool_executor.py read_file \"file_path=test.txt\"")
        sys.exit(1)

    tool_name = args[0]
    params_str = args[1] if len(args) > 1 else ""

    # 解析参数字符串为字典
    params = {}
    if params_str:
        # 简单解析：key=value 格式
        for item in params_str.split(','):
            if '=' in item:
                key, value = item.split('=', 1)
                params[key.strip()] = value.strip()
        # 如果是 execute_shell_command，command 参数是完整的剩余部分
        if tool_name == 'execute_shell_command' and 'command' not in params:
            params['command'] = params_str

    return tool_name, params


def execute_tool(tool_name: str, params: dict) -> tuple[int, str, str]:
    """
    执行工具调用 - 增强版（集成工作流强制执行）
    
    Returns:
        (returncode, stdout, stderr)
    """
    # 步骤 0: 工具包装器检查（强制工作流）
    if TOOL_WRAPPER_ENABLED:
        if not before_tool_call(tool_name, params):
            return 1, "", "未初始化会话 - 请先运行 copaw_entry.py"

    # 步骤 0.5: 工作流强制执行检查（新增）
    if WORKFLOW_ENFORCER_ENABLED:
        enforcer = WorkflowEnforcer()
        # 工具调用视为 Step 6（工具执行阶段）
        if not enforcer.verify_step_execution(6):
            return 1, "", "工作流步骤未完成 - 请先完成前面步骤"

    # 防护检查
    if PROTECTION_ENABLED:
        layer = get_protection_layer()
        allowed, msg = layer.before_tool_call(tool_name, params)
        if not allowed:
            print(f"[BLOCK] {msg}", file=sys.stderr)
            return 1, "", msg

    # 执行工具
    if tool_name == 'execute_shell_command':
        command = params.get('command', '')
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            # 步骤 6.x: 更新步骤状态（新增）
            if WORKFLOW_ENFORCER_ENABLED:
                enforcer = WorkflowEnforcer()
                enforcer.update_step_status(6, 'completed', f'Executed: {command[:50]}')
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timeout (60s)"
        except Exception as e:
            return 1, "", str(e)

    elif tool_name == 'read_file':
        file_path = params.get('file_path', '')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return 0, content, ""
        except Exception as e:
            return 1, "", str(e)

    elif tool_name == 'write_file':
        file_path = params.get('file_path', '')
        content = params.get('content', '')
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return 0, f"Written to {file_path}", ""
        except Exception as e:
            return 1, "", str(e)

    else:
        return 1, "", f"Unknown tool: {tool_name}"


def log_call(tool_name: str, params: dict, result: str, returncode: int):
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
# py tool_executor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py tool_executor_001.py

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
        "tool_id": tool_name,
        "params": params,
        "result": result,
        "returncode": returncode,
    }

    # 尝试获取 session_id
    session_id = "unknown"
    state_files = list(Path("flow-archive").glob("*/execution-state.json"))
    if state_files:
        try:
            with open(max(state_files, key=lambda f: f.stat().st_mtime), 'r', encoding='utf-8') as f:
                state = json.load(f)
            session_id = state.get('session_id', 'unknown')
        except (Exception,):
            pass

    log_entry["session_id"] = session_id

    # 写入日志
    log_file = Path("30-scripts-tools/tool_call_log.jsonl")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


logging.basicConfig(level=logging.INFO)
def main():
    tool_name, params = parse_args(sys.argv[1:])

    # 执行工具
    returncode, stdout, stderr = execute_tool(tool_name, params)

    # 记录调用
    result = "success" if returncode == 0 else "error"
    log_call(tool_name, params, result, returncode)

    # 工具包装器记录
    if TOOL_WRAPPER_ENABLED:
        after_tool_call(tool_name, params, result)

    # 【新增】自动完成工作流步骤
    try:
        from auto_step import AutoStepTracker
        tracker = AutoStepTracker()
        tracker.auto_complete(tool_name)
    except Exception as e:
        pass  # 静默失败，不影响工具执行

    # 输出结果
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    sys.exit(returncode)


if __name__ == '__main__':
    main()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <args>")
        sys.exit(1)
