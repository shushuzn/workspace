#!/usr/bin/env python3
"""
将学习机制应用到自身对话

在每次回复前检查行为配置，自动应用改进
"""

from dialog_integrator import process_dialog, get_behavior_mode
from behavior_updater import get_behavior_mode as get_config
import json
from pathlib import Path

def apply_learning_to_response(user_input: str, planned_response: str) -> str:
    """
    根据学习到的行为模式调整回复
    
    Args:
        user_input: 用户输入
        planned_response: 计划的回复
    
    Returns:
        调整后的回复
    """
    # 预处理用户输入
    preprocessed = process_dialog(user_input, planned_response)
    
    mode = preprocessed['mode']
    
    # 根据模式调整回复
    if mode == 'confirm_first':
        # 确认优先模式
        intent = extract_intent(user_input)
        confirm_msg = f"我理解你想{intent}，对吗？请确认后我再执行。\n\n---\n\n原计划：{planned_response[:100]}..."
        return confirm_msg
    
    elif mode == 'report_progress':
        # 进度报告模式
        progress_msg = f"收到，开始处理。预计需要 3-5 分钟。\n\n进度：0% - 准备中...\n\n---\n\n{planned_response}"
        return progress_msg
    
    else:
        # 正常模式
        return planned_response


def extract_intent(user_input: str) -> str:
    """提取用户意图"""
    if "批判者" in user_input:
        return "启动批判者模式"
    elif "测试" in user_input:
        return "执行测试"
    elif "如何" in user_input or "怎么" in user_input:
        return "获取帮助"
    elif "优化" in user_input or "改进" in user_input:
        return "优化改进"
    else:
        return "执行任务"


def log_dialog(user_input: str, response: str, mode: str):
    """记录对话到日志"""
    log_file = Path("memory/dialog_log.json")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 加载现有日志
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    
    # 添加新记录
    logs.append({
        'user_input': user_input,
        'response': response,
        'mode': mode,
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })
    
    # 只保留最近 100 条
    logs = logs[-100:]
    
    # 保存
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


# 测试
if __name__ == '__main__':
    print("测试自身对话集成")
    print("=" * 60)
    
    # 测试 1: 正常对话
    print("\n测试 1: '继续优化'")
    response = apply_learning_to_response('继续优化', '开始优化代码...')
    print(f"回复：{response[:100]}...")
    
    # 测试 2: 批判者模式
    print("\n测试 2: '批判者上线'")
    response = apply_learning_to_response('批判者上线', '启动批判者 v5.0...')
    print(f"回复：{response[:100]}...")
    
    # 测试 3: 当前行为模式
    print("\n测试 3: 当前行为模式")
    mode = get_behavior_mode()
    print(f"模式：{mode}")
    
    print("\n测试完成！")
