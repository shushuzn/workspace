#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对话入口 - 所有对话必须通过此入口

功能：
1. 检查工作流状态
2. 无 session 时自动启动简化工作流
3. 记录所有对话到工作流日志
4. 强制对话关联到 session

使用方式：
    py dialog_entry.py "用户问题"
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 导入工作流强制器
sys.path.insert(0, str(Path("30-scripts-tools").resolve()))
from dialog_workflow_enforcer import enforce_workflow, log_dialog_response, is_simple_question

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
SIMPLIFIED_STATE_FILE = Path("flow-archive/20260318-universal-workflow-001-simplified/execution-state.json")


def auto_start_simplified_session(question: str):
    """自动启动简化会话"""
    from copaw_entry import CoPawEntry
    
    print("[INFO] 检测到无 session，自动启动简化会话...")
    
    entry = CoPawEntry("简单问答")
    entry.initialize()
    
    print(f"[OK] 简化会话已启动：{entry.session_id}")
    return entry


def main():
    if len(sys.argv) < 2:
        print("用法：py dialog_entry.py \"用户问题\"")
        print("")
        print("此脚本确保所有对话都通过工作流")
        sys.exit(1)
    
    user_input = sys.argv[1]
    
    # 步骤 1: 检查工作流状态
    result = enforce_workflow(user_input)
    
    print("="*70)
    print("对话工作流检查")
    print("="*70)
    print(f"用户输入：{user_input[:100]}")
    print(f"检查结果：{result['action']}")
    print(f"原因：{result['reason']}")
    
    # 步骤 2: 根据检查结果处理
    if result['action'] == 'require_session':
        # 需要启动 session
        print("\n" + result['message'])
        
        # 询问是否自动启动
        if is_simple_question(user_input):
            print("[ACTION] 自动启动简化会话...")
            entry = auto_start_simplified_session(user_input)
        else:
            print("[ACTION] 请手动运行：py 30-scripts-tools/copaw_entry.py \"任务\"")
            sys.exit(1)
    
    elif result['action'] == 'allow_with_warning':
        # 简单问题，允许但警告
        print(f"\n[WARNING] {result.get('warning', '')}")
        print("[INFO] 建议启动 session：py 30-scripts-tools/copaw_entry.py \"任务\"")
    
    # 步骤 3: 记录对话
    log_dialog_response(user_input, "allowed", result.get('workflow_type', 'none'))
    
    print("\n[OK] 对话已记录")
    print("="*70)
    
    # 继续处理对话（这里应该调用 LLM）
    # 实际使用时，这里会调用 LLM 并返回响应
    print("[INFO] 现在可以处理对话...")


if __name__ == '__main__':
    main()
