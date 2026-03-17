#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流质量评估器 (PRM) - 基于 OpenClaw-RL 启发

从工作流结果和用户反馈自动提取质量信号
"""

from typing import Dict, Any, Optional
from datetime import datetime


class WorkflowPRM:
    """工作流质量评估器"""
    
    def __init__(self):
        self.criteria = {
            'completeness': 0.3,  # 完整性
            'accuracy': 0.3,       # 准确性
            'efficiency': 0.2,     # 效率
            'user_satisfaction': 0.2  # 用户满意度
        }
    
    def evaluate(self, workflow_result: Dict[str, Any], user_feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        评估工作流质量
        
        Args:
            workflow_result: 工作流执行结果
            user_feedback: 用户反馈 (可选)
        
        Returns:
            评估结果 {total, level, scores}
        """
        scores = {}
        
        # 完整性评分 (30%)
        scores['completeness'] = self._score_completeness(workflow_result)
        
        # 准确性评分 (30%)
        scores['accuracy'] = self._score_accuracy(workflow_result)
        
        # 效率评分 (20%)
        scores['efficiency'] = self._score_efficiency(workflow_result)
        
        # 用户满意度评分 (20%)
        if user_feedback:
            scores['user_satisfaction'] = self._parse_feedback(user_feedback)
        else:
            scores['user_satisfaction'] = 0.5  # 默认中性
        
        # 加权总分
        total = sum(scores[k] * self.criteria[k] for k in scores)
        
        return {
            'total': round(total, 3),
            'level': 'good' if total > 0.7 else 'neutral' if total > 0.4 else 'bad',
            'scores': scores,
            'timestamp': datetime.now().isoformat()
        }
    
    def _score_completeness(self, result: Dict[str, Any]) -> float:
        """完整性评分"""
        # 检查必要字段
        required_fields = ['status', 'result']
        present = sum(1 for f in required_fields if f in result)
        return present / len(required_fields)
    
    def _score_accuracy(self, result: Dict[str, Any]) -> float:
        """准确性评分"""
        # 检查错误
        if 'error' in result:
            return 0.2
        if result.get('status') == 'success':
            return 0.9
        return 0.5
    
    def _score_efficiency(self, result: Dict[str, Any]) -> float:
        """效率评分"""
        # 基于执行时间
        duration = result.get('duration', 0)
        if duration < 5:
            return 1.0
        elif duration < 30:
            return 0.7
        else:
            return 0.4
    
    def _parse_feedback(self, feedback: str) -> float:
        """解析用户反馈"""
        if not feedback:
            return 0.5
        
        text = feedback.lower()
        
        # 正面词汇
        positive_words = ['好', '不错', '满意', '棒', 'perfect', 'good', 'excellent', 'great']
        # 负面词汇
        negative_words = ['差', '不好', '失望', 'bad', 'poor', 'terrible', 'awful']
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            return 0.9
        elif neg_count > pos_count:
            return 0.2
        return 0.5
    
    def evaluate_from_user_action(self, action: str) -> Dict[str, Any]:
        """
        从用户行为提取质量信号
        
        Args:
            action: 用户行为类型
        
        Returns:
            评估结果
        """
        # 用户行为 → 质量信号映射
        action_signals = {
            'continue': 1.0,    # 继续使用
            'retry': -1.0,      # 重新执行
            'modify': -0.5,     # 修改参数
            'abandon': -1.0,    # 放弃离开
            'praise': 1.0,      # 明确好评
            'complain': -1.0,   # 明确差评
            'share': 0.8,       # 分享给他人
            'bookmark': 0.7,    # 收藏
            'export': 0.6       # 导出结果
        }
        
        signal = action_signals.get(action, 0.0)
        
        # 转换为 0-1 评分
        score = (signal + 1) / 2  # -1~1 → 0~1
        
        return {
            'total': round(score, 3),
            'level': 'good' if score > 0.7 else 'neutral' if score > 0.4 else 'bad',
            'action': action,
            'signal': signal,
            'timestamp': datetime.now().isoformat()
        }


# 全局 PRM 实例
global_prm = WorkflowPRM()


def evaluate_workflow(result: Dict[str, Any], feedback: Optional[str] = None) -> Dict[str, Any]:
    """便捷函数：评估工作流"""
    return global_prm.evaluate(result, feedback)


def evaluate_action(action: str) -> Dict[str, Any]:
    """便捷函数：评估用户行为"""
    return global_prm.evaluate_from_user_action(action)


# 测试
if __name__ == '__main__':
    prm = WorkflowPRM()
    
    # 测试 1: 成功的工作流
    result1 = {
        'status': 'success',
        'result': {'data': 'test'},
        'duration': 3
    }
    print("测试 1 (成功):", prm.evaluate(result1))
    
    # 测试 2: 失败的工作流
    result2 = {
        'status': 'failed',
        'error': 'test error',
        'duration': 60
    }
    print("测试 2 (失败):", prm.evaluate(result2))
    
    # 测试 3: 用户反馈
    print("测试 3 (好评):", prm.evaluate(result1, "很好，很满意"))
    print("测试 4 (差评):", prm.evaluate(result1, "太差了，失望"))
    
    # 测试 5: 用户行为
    print("测试 5 (继续):", prm.evaluate_from_user_action('continue'))
    print("测试 6 (重试):", prm.evaluate_from_user_action('retry'))
    print("测试 7 (分享):", prm.evaluate_from_user_action('share'))
