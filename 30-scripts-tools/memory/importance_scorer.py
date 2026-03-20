# -*- coding: utf-8 -*-
"""
Importance Scorer - 重要性评分器
双层记忆架构的核心差异化模块

评分维度:
1. 操作频率权重 (0.3) - 用户反复提及的内容
2. 用户反馈权重 (0.4) - 明确表示重要的内容
3. 独特性权重 (0.3) - 稀缺/唯一的信息
"""

import re
from typing import Dict, Any, List
from datetime import datetime


class ImportanceScorer:
    """
    多维度重要性评分器
    
    输出: 0.0 - 1.0 重要性分数
    """
    
    def __init__(self):
        # 权重配置
        self.weights = {
            'frequency': 0.3,    # 操作频率
            'feedback': 0.4,     # 用户反馈
            'uniqueness': 0.3    # 独特性
        }
        
        # 高重要性关键词
        self.high_importance_keywords = {
            'preference': ['我喜欢', '我想要', 'prefer', 'always', 'never'],
            'decision': ['决定', '选择', 'decided', 'chosen', 'final'],
            'critical': ['必须', '绝对', 'critical', 'important', '必须不能'],
            'personal': ['我的', '我是', 'i am', 'my name'],
        }
        
        # 唯一性检测词
        self.uniqueness_indicators = [
            '第一次', '首次', '唯一', 'only', 'unique', 
            '第一次出现', 'never before'
        ]
    
    def calculate(self, content: str, memory_type: str, 
                  metadata: Dict[str, Any] = None) -> float:
        """
        计算重要性分数
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型 ('conversation', 'decision', 'preference', 'fact')
            metadata: 额外元数据
            
        Returns:
            float: 0.0 - 1.0 重要性分数
        """
        metadata = metadata or {}
        
        # 1. 基础分数（基于类型）
        base_score = self._type_base_score(memory_type)
        
        # 2. 关键词匹配分数
        keyword_score = self._keyword_score(content)
        
        # 3. 上下文增强（从metadata）
        context_boost = self._context_boost(metadata)
        
        # 4. 长度惩罚/奖励
        length_score = self._length_score(content)
        
        # 加权计算
        final_score = (
            base_score * 0.3 +
            keyword_score * 0.4 +
            context_boost * 0.2 +
            length_score * 0.1
        )
        
        # 边界限制
        return min(1.0, max(0.0, final_score))
    
    def _type_base_score(self, memory_type: str) -> float:
        """记忆类型基础分数"""
        type_scores = {
            'preference': 0.7,   # 用户偏好 - 最重要
            'decision': 0.8,     # 决策 - 非常重要
            'fact': 0.5,         # 事实 - 中等
            'conversation': 0.3, # 普通对话 - 较低
            'summary': 0.4,      # 摘要 - 中低
            'system': 0.2,       # 系统信息 - 最低
        }
        return type_scores.get(memory_type, 0.3)
    
    def _keyword_score(self, content: str) -> float:
        """关键词匹配分数"""
        content_lower = content.lower()
        score = 0.0
        
        for category, keywords in self.high_importance_keywords.items():
            for kw in keywords:
                if kw in content or kw in content_lower:
                    if category == 'critical':
                        score += 0.3
                    elif category == 'preference':
                        score += 0.25
                    elif category == 'decision':
                        score += 0.25
                    elif category == 'personal':
                        score += 0.2
        
        # 唯一性检测
        for indicator in self.uniqueness_indicators:
            if indicator in content or indicator in content_lower:
                score += 0.15
        
        return min(1.0, score)
    
    def _context_boost(self, metadata: Dict) -> float:
        """上下文增强"""
        boost = 0.0
        
        # 用户反馈
        if metadata.get('user_feedback') == 'positive':
            boost += 0.5
        elif metadata.get('user_feedback') == 'important':
            boost += 0.4
        
        # 明确标记
        if metadata.get('explicit_important'):
            boost += 0.3
        
        # 引用次数
        ref_count = metadata.get('reference_count', 0)
        if ref_count > 5:
            boost += 0.3
        elif ref_count > 2:
            boost += 0.15
        
        # 来源
        source = metadata.get('source', '')
        if 'memory' in source.lower():  # 来自长期记忆
            boost += 0.1
        
        return min(1.0, boost)
    
    def _length_score(self, content: str) -> float:
        """长度分数 - 适中的长度更有价值"""
        length = len(content)
        
        # 理想长度: 50-500 字符
        if 50 <= length <= 500:
            return 0.8
        elif length < 50:
            # 太短，可能信息不足
            return 0.3 + (length / 50) * 0.3
        elif length > 2000:
            # 太长，可能需要摘要
            return max(0.2, 0.8 - (length - 2000) / 5000)
        else:
            # 500-2000
            return 0.7
    
    def batch_score(self, items: List[Dict]) -> List[float]:
        """批量评分"""
        return [
            self.calculate(
                item.get('content', ''),
                item.get('type', 'conversation'),
                item.get('metadata', {})
            )
            for item in items
        ]
    
    def rank_items(self, items: List[Dict], 
                   top_k: int = 10) -> List[Dict]:
        """排序并返回top-k"""
        scored = [
            {**item, 'importance_score': self.calculate(
                item.get('content', ''),
                item.get('type', 'conversation'),
                item.get('metadata', {})
            )}
            for item in items
        ]
        
        scored.sort(key=lambda x: x['importance_score'], reverse=True)
        return scored[:top_k]
    
    def get_importance_level(self, score: float) -> str:
        """获取重要性等级"""
        if score >= 0.8:
            return 'CRITICAL'
        elif score >= 0.6:
            return 'HIGH'
        elif score >= 0.4:
            return 'MEDIUM'
        elif score >= 0.2:
            return 'LOW'
        else:
            return 'MINIMAL'


# 导出
__all__ = ['ImportanceScorer']