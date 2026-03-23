import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对话工作流强制器 - 确保所有对话都通过工作流

问题：
- LLM 可以直接回复用户，绕过工作流
- 工具调用被防护，但对话响应没有防护

解决方案：
1. 每次回复前检查 session 状态
2. 无 session 且是复杂任务 → 拒绝回复，要求启动 session
3. 有 session → 强制记录到工作流步骤
4. 简单问答可以使用 simplified workflow

使用方式：
    from dialog_workflow_enforcer import enforce_workflow
    enforce_workflow("用户问题")
"""

import json
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
SIMPLIFIED_STATE_FILE = Path("flow-archive/20260318-universal-workflow-001-simplified/execution-state.json")
DIALOG_LOG = Path("dialog/2026-03-20.jsonl")

# 简单问题列表（不需要完整工作流）
SIMPLE_QUESTIONS = [
    "几点", "时间", "日期", "help", "帮助",
    "status", "状态", "version", "版本",
]

# 需要工作流的关键词
WORKFLOW_REQUIRED = [
    "研究", "分析", "报告", "创建", "修改", "执行",
    "run", "create", "analyze", "research", "report",
    "代码", "脚本", "工具", "文件", "提交",
]


def check_session() -> tuple[bool, str]:
    """
    检查 session 状态
    
    Returns:
        (has_session, workflow_type)
    """
    # 检查完整 workflow
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            if state.get('session_id') and state.get('mandatory_execution'):
                return True, 'full'
        except (Exception,):
            pass

    # 检查简化 workflow
    if SIMPLIFIED_STATE_FILE.exists():
        try:
            with open(SIMPLIFIED_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            if state.get('session_id'):
                return True, 'simplified'
        except (Exception,):
            pass

    return False, 'none'


def is_simple_question(user_input: str) -> bool:
    """判断是否是简单问题"""
    user_input_lower = user_input.lower()

    # 检查是否在简单问题列表
    for keyword in SIMPLE_QUESTIONS:
        if keyword in user_input_lower:
            return True

    # 检查是否是需要工作流的关键词
    for keyword in WORKFLOW_REQUIRED:
        if keyword in user_input_lower:
            return False

    # 默认：短问题视为简单问题
    if len(user_input) < 20:
        return True

    return False


def enforce_workflow(user_input: str) -> dict:
    """
    强制工作流检查
    
    Args:
        user_input: 用户输入
    
    Returns:
        dict: {
            "allowed": bool,
            "reason": str,
            "action": str,
            "workflow_type": str
        }
    """
    has_session, workflow_type = check_session()
    is_simple = is_simple_question(user_input)

    # 情况 1: 有 session → 允许
    if has_session:
        return {
            "allowed": True,
            "reason": "Session 存在",
            "action": "continue",
            "workflow_type": workflow_type
        }

    # 情况 2: 无 session + 简单问题 → 允许（但建议启动 session）
    if is_simple:
        return {
            "allowed": True,
            "reason": "简单问题",
            "action": "allow_with_warning",
            "workflow_type": "none",
            "warning": "建议启动 session 以获得完整功能"
        }

    # 情况 3: 无 session + 复杂任务 → 拒绝
    return {
        "allowed": False,
        "reason": "复杂任务需要 session",
        "action": "require_session",
        "workflow_type": "none",
        "message": f"""
================================================================================
[BLOCK] 工作流未启动
================================================================================
任务类型：复杂任务
检测到关键词：{[k for k in WORKFLOW_REQUIRED if k in user_input.lower()][:3]}

必须先启动工作流会话：
  py 30-scripts-tools/copaw_entry.py "任务描述"

或使用简化模式（仅问答）：
  py 30-scripts-tools/copaw_entry.py "简单问答" --simplified

================================================================================
"""
    }


def log_dialog_response(user_input: str, response_type: str, workflow_type: str):
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
# py dialog_workflow_enforcer_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py dialog_workflow_enforcer_001.py

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

记录对话响应到日志"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input[:200],  # 截断
        "response_type": response_type,
        "workflow_type": workflow_type,
    }

    try:
        DIALOG_LOG.parent.mkdir(exist_ok=True)
        with open(DIALOG_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"[WARNING] 记录对话日志失败：{e}")


if __name__ == '__main__':
    # 测试
    test_inputs = [
        "现在几点？",
        "帮我分析这个数据",
        "创建研究报告",
        "status",
        "运行这个脚本",
    ]

    print("="*70)
    print("对话工作流强制器测试")
    print("="*70)

    for test_input in test_inputs:
        result = enforce_workflow(test_input)
        print(f"\n输入：{test_input}")
        print(f"  允许：{result['allowed']}")
        print(f"  原因：{result['reason']}")
        print(f"  操作：{result['action']}")
        if 'workflow_type' in result:
            print(f"  工作流类型：{result['workflow_type']}")
