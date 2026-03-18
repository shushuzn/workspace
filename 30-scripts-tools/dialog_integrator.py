#!/usr/bin/env python3
"""
对话集成器 - 将学习机制集成到实际对话中

在 AI 回复前检查行为配置，自动应用改进
"""

from typing import Dict, Optional
from auto_signal_extractor import extract_signal
from behavior_updater import update_behavior, get_behavior_mode, should_confirm, should_report_progress


class DialogIntegrator:
    """对话集成器"""
    
    def __init__(self):
        self.current_task = None
        self.progress_updates = 0
    
    def preprocess_user_input(self, user_input: str, context: str = '') -> Dict:
        """
        预处理用户输入
        
        1. 提取信号
        2. 更新行为
        3. 返回处理建议
        """
        # 提取信号
        signal = extract_signal(user_input, context)
        
        # 更新行为配置
        if signal.get('signal') or signal.get('action'):
            update_behavior(signal)
        
        # 获取当前行为模式
        mode = get_behavior_mode()
        
        return {
            'user_input': user_input,
            'signal': signal,
            'mode': mode,
            'should_confirm': should_confirm(),
            'should_report_progress': should_report_progress()
        }
    
    def generate_response(self, user_input: str, planned_action: str) -> str:
        """
        生成回复
        
        根据行为配置调整回复方式
        """
        mode = get_behavior_mode()
        
        if mode == 'confirm_first':
            # 确认优先模式
            return self._confirm_then_execute(user_input, planned_action)
        
        elif mode == 'report_progress':
            # 进度报告模式
            return self._report_progress(user_input, planned_action)
        
        else:
            # 正常模式
            return planned_action
    
    def _confirm_then_execute(self, user_input: str, planned_action: str) -> str:
        """确认后再执行"""
        # 提取用户意图
        intent = self._extract_intent(user_input)
        
        # 生成确认问题
        confirm_question = f"我理解你想{intent}，对吗？请确认后再执行。"
        
        return confirm_question
    
    def _report_progress(self, user_input: str, planned_action: str) -> str:
        """报告进度"""
        # 估计任务时长
        estimated_time = self._estimate_time(planned_action)
        
        # 生成进度报告
        progress_report = f"收到，开始处理。预计需要{estimated_time}。"
        progress_report += "\n进度：0% - 准备中..."
        
        return progress_report
    
    def _extract_intent(self, user_input: str) -> str:
        """提取用户意图"""
        # 简单关键词提取 (应使用 LLM)
        if "批判者" in user_input:
            return "启动批判者模式"
        elif "测试" in user_input:
            return "执行测试"
        elif "如何" in user_input or "怎么" in user_input:
            return "获取帮助"
        else:
            return "执行任务"
    
    def _estimate_time(self, action: str) -> str:
        """估计任务时长"""
        if "测试" in action or "简单" in action:
            return "1-2 分钟"
        elif "集成" in action or "改进" in action:
            return "5-10 分钟"
        else:
            return "3-5 分钟"
    
    def update_progress(self, progress: int, message: str = ''):
        """更新进度 (用于长任务)"""
        if should_report_progress():
            self.progress_updates += 1
            print(f"进度：{progress}% - {message}")
    
    def mark_task_complete(self, success: bool, user_feedback: str = ''):
        """标记任务完成"""
        if success:
            # 成功任务，记录正面信号
            if user_feedback:
                extract_signal(user_feedback, '任务完成')
        else:
            # 失败任务，记录负面信号
            extract_signal('任务失败', '执行错误')


# 全局集成器
global_integrator = DialogIntegrator()


def process_dialog(user_input: str, planned_action: str = '') -> Dict:
    """
    便捷函数：处理对话
    
    返回:
    {
        'preprocessed': {...},  # 预处理结果
        'response': '...',      # 生成的回复
        'mode': '...'           # 当前模式
    }
    """
    # 预处理
    preprocessed = global_integrator.preprocess_user_input(user_input)
    
    # 生成回复
    if planned_action:
        response = global_integrator.generate_response(user_input, planned_action)
    else:
        response = None
    
    return {
        'preprocessed': preprocessed,
        'response': response,
        'mode': preprocessed['mode']
    }


# 测试
if __name__ == '__main__':
    integrator = DialogIntegrator()
    
    print("测试对话集成器")
    print("=" * 50)
    
    # 测试 1: 正常对话
    print("\n测试 1: '继续优化'")
    result = process_dialog('继续优化', '开始优化代码')
    print(f"模式：{result['mode']}")
    print(f"回复：{result['response']}")
    
    # 测试 2: 负面信号 (触发确认模式)
    print("\n测试 2: 连续 3 次'你听不懂吗'")
    for i in range(3):
        result = process_dialog('你听不懂吗', '解释')
        print(f"第{i+1}次后模式：{result['mode']}")
    
    # 测试 3: 确认模式下的回复
    print("\n测试 3: 确认模式下的回复")
    result = process_dialog('优化代码', '开始优化')
    print(f"模式：{result['mode']}")
    print(f"回复：{result['response']}")
    
    print("\n测试完成！")
