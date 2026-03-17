#!/usr/bin/env python3
"""
Next-state 信号学习器 - 基于 OpenClaw-RL 启发

从对话自动提取改进信号，更新行为模式
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


class NextStateLearner:
    """Next-state 信号学习器"""
    
    def __init__(self):
        # 用户回复 → 信号映射
        self.signal_patterns = {
            # 负面信号 (需要改进)
            '好了吗': 'wait_too_long',
            '等一下': 'wait_too_long',
            '还没好': 'wait_too_long',
            '不对': 'understand_wrong',
            '错了': 'understand_wrong',
            '听不懂': 'understand_wrong',
            '重新': 'need_retry',
            '重试': 'need_retry',
            
            # 正面信号 (保持方式)
            '好的': 'satisfied',
            '对的': 'satisfied',
            '继续': 'satisfied',
            '很好': 'satisfied',
            '不错': 'satisfied',
            
            # 中性信号
            '批判者': 'need_review',
            '测试': 'need_test',
            '如何使用': 'need_help',
        }
        
        # 信号 → 改进行动
        self.improvement_actions = {
            'wait_too_long': 'report_progress_for_long_tasks',
            'understand_wrong': 'confirm_before_execute',
            'need_retry': 'add_retry_mechanism',
            'satisfied': 'keep_current_approach',
            'need_review': 'start_critic_mode',
            'need_test': 'add_test_code',
            'need_help': 'provide_detailed_guide',
        }
        
        # 行为模式计数
        self.pattern_counts = {
            'confirm_before_execute': 0,
            'report_progress_for_long_tasks': 0,
            'add_retry_mechanism': 0,
        }
        
        # 自动改进阈值
        self.auto_improve_threshold = 3  # 同一信号出现 3 次自动改进
    
    def extract_signal(self, user_reply: str) -> Optional[str]:
        """从用户回复提取信号"""
        reply_lower = user_reply.lower()
        
        for pattern, signal in self.signal_patterns.items():
            if pattern in reply_lower:
                return signal
        
        return None
    
    def record_signal(self, signal: str, context: str = '') -> Dict:
        """记录信号并生成改进行动"""
        action = self.improvement_actions.get(signal, 'no_action')
        
        # 记录到计数
        if action in self.pattern_counts:
            self.pattern_counts[action] += 1
        
        # 检查是否需要自动改进
        auto_improve = self.pattern_counts.get(action, 0) >= self.auto_improve_threshold
        
        return {
            'signal': signal,
            'action': action,
            'auto_improve': auto_improve,
            'count': self.pattern_counts.get(action, 0),
            'timestamp': datetime.now().isoformat(),
            'context': context
        }
    
    def get_current_behavior_mode(self) -> Dict[str, bool]:
        """获取当前行为模式"""
        return {
            'confirm_before_execute': self.pattern_counts['confirm_before_execute'] >= self.auto_improve_threshold,
            'report_progress_for_long_tasks': self.pattern_counts['report_progress_for_long_tasks'] >= self.auto_improve_threshold,
            'add_retry_mechanism': self.pattern_counts['add_retry_mechanism'] >= self.auto_improve_threshold,
        }
    
    def save_to_memory(self, record: Dict, memory_file: str = 'memory/next_state_log.json'):
        """保存到记忆文件"""
        memory_path = Path(memory_file)
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取现有记录
        if memory_path.exists():
            with open(memory_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
        else:
            records = []
        
        # 添加新记录
        records.append(record)
        
        # 只保留最近 100 条
        records = records[-100:]
        
        # 保存
        with open(memory_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    def analyze_trend(self) -> Dict:
        """分析改进趋势"""
        total_signals = sum(self.pattern_counts.values())
        
        if total_signals == 0:
            return {'trend': 'no_data'}
        
        # 计算各行为模式的比例
        return {
            'confirm_rate': self.pattern_counts['confirm_before_execute'] / total_signals,
            'progress_report_rate': self.pattern_counts['report_progress_for_long_tasks'] / total_signals,
            'retry_rate': self.pattern_counts['add_retry_mechanism'] / total_signals,
            'auto_improved_modes': sum(1 for v in self.get_current_behavior_mode().values() if v),
        }


# 全局学习器实例
global_learner = NextStateLearner()


def learn_from_reply(user_reply: str, context: str = '') -> Dict:
    """便捷函数：从回复学习"""
    signal = global_learner.extract_signal(user_reply)
    if signal:
        record = global_learner.record_signal(signal, context)
        global_learner.save_to_memory(record)
        return record
    return {'signal': None, 'action': 'no_action'}


def get_behavior_mode() -> Dict[str, bool]:
    """便捷函数：获取当前行为模式"""
    return global_learner.get_current_behavior_mode()


# 测试
if __name__ == '__main__':
    learner = NextStateLearner()
    
    print("测试 Next-state 信号提取")
    print("=" * 50)
    
    # 测试 1: 负面信号
    print("\n测试 1: '好了吗'")
    record = learner.record_signal(learner.extract_signal('好了吗'), '等待太久')
    print(f"信号：{record['signal']}")
    print(f"改进行动：{record['action']}")
    
    # 测试 2: 正面信号
    print("\n测试 2: '继续'")
    record = learner.record_signal(learner.extract_signal('继续'), '方向正确')
    print(f"信号：{record['signal']}")
    print(f"改进行动：{record['action']}")
    
    # 测试 3: 理解错误
    print("\n测试 3: '你听不懂吗'")
    signal = learner.extract_signal('你听不懂吗')
    record = learner.record_signal(signal, '理解错误')
    print(f"信号：{record['signal']}")
    print(f"改进行动：{record['action']}")
    
    # 测试 4: 自动改进
    print("\n测试 4: 自动改进测试")
    for i in range(3):
        learner.record_signal('understand_wrong', f'测试{i}')
    
    mode = learner.get_current_behavior_mode()
    print(f"当前行为模式：{mode}")
    
    # 测试 5: 趋势分析
    print("\n测试 5: 趋势分析")
    trend = learner.analyze_trend()
    print(f"趋势：{trend}")
    
    print("\n所有测试完成！")
