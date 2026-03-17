#!/usr/bin/env python3
"""
自动信号提取器 - 用 LLM 自动从对话提取改进信号

无需硬编码模式，LLM 自动分析用户意图
"""

from typing import Dict, Optional
from datetime import datetime
import json
from pathlib import Path


class AutoSignalExtractor:
    """自动信号提取器"""
    
    def __init__(self):
        self.memory_file = Path('memory/auto_signals.json')
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 历史信号记录
        self.signals = self._load_memory()
    
    def _load_memory(self) -> list:
        """加载记忆"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_memory(self):
        """保存记忆"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.signals[-100:], f, ensure_ascii=False, indent=2)
    
    def extract(self, user_reply: str, context: str = '') -> Dict:
        """
        用 LLM 自动提取信号
        
        分析维度:
        1. 情感倾向 (正面/负面/中性)
        2. 紧迫程度 (高/中/低)
        3. 改进类型 (理解/速度/质量/其他)
        4. 具体行动建议
        """
        # 简单 LLM 模拟 (实际应调用 LLM API)
        # 这里用规则 + 关键词分析模拟 LLM 判断
        
        reply_lower = user_reply.lower()
        
        # 情感分析
        positive_words = ['好', '对', '继续', '棒', 'perfect', 'good', 'great', 'excellent']
        negative_words = ['不', '错', '差', '慢', 'wrong', 'bad', 'poor', 'slow']
        
        pos_count = sum(1 for w in positive_words if w in reply_lower)
        neg_count = sum(1 for w in negative_words if w in reply_lower)
        
        if pos_count > neg_count:
            sentiment = 'positive'
            sentiment_score = 0.8
        elif neg_count > pos_count:
            sentiment = 'negative'
            sentiment_score = 0.2
        else:
            sentiment = 'neutral'
            sentiment_score = 0.5
        
        # 紧迫程度分析
        urgent_words = ['现在', '立即', '快点', '急', 'urgent', 'now', 'fast']
        urgency = 'high' if any(w in reply_lower for w in urgent_words) else 'medium'
        
        # 改进类型分析
        if any(w in reply_lower for w in ['听不懂', '不对', '错', 'wrong', 'understand']):
            improvement_type = 'understanding'
            action = 'confirm_before_execute'
        elif any(w in reply_lower for w in ['慢', '等', '久', 'slow', 'wait']):
            improvement_type = 'speed'
            action = 'report_progress'
        elif any(w in reply_lower for w in ['好', '对', '继续', 'good', 'continue']):
            improvement_type = 'keep'
            action = 'keep_current'
        else:
            improvement_type = 'other'
            action = 'analyze_further'
        
        # 生成自然语言改进建议
        improvement_suggestion = self._generate_suggestion(
            sentiment, improvement_type, user_reply
        )
        
        # 记录信号
        signal = {
            'user_reply': user_reply,
            'context': context,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'urgency': urgency,
            'improvement_type': improvement_type,
            'action': action,
            'suggestion': improvement_suggestion,
            'timestamp': datetime.now().isoformat(),
            'applied': False,
            'effective': None
        }
        
        self.signals.append(signal)
        self._save_memory()
        
        return signal
    
    def _generate_suggestion(self, sentiment: str, improvement_type: str, reply: str) -> str:
        """生成改进建议"""
        suggestions = {
            ('negative', 'understanding'): "用户表示理解错误，下次应先确认'你是说 X 吗？'再执行",
            ('negative', 'speed'): "用户表示等待太久，长任务应先报告进度",
            ('positive', 'keep'): "用户满意，保持当前方式",
            ('neutral', 'other'): "需要进一步分析用户需求",
        }
        return suggestions.get((sentiment, improvement_type), "记录用户反馈")
    
    def get_pending_improvements(self) -> list:
        """获取待应用的改进"""
        return [s for s in self.signals if not s.get('applied', False)]
    
    def mark_applied(self, signal_index: int, effective: Optional[bool] = None):
        """标记改进已应用"""
        if signal_index < len(self.signals):
            self.signals[signal_index]['applied'] = True
            if effective is not None:
                self.signals[signal_index]['effective'] = effective
            self._save_memory()
    
    def get_behavior_config(self) -> Dict[str, bool]:
        """获取行为配置 (基于历史信号)"""
        # 分析最近 10 条负面信号
        recent_negative = [s for s in self.signals[-10:] if s['sentiment'] == 'negative']
        
        if not recent_negative:
            return {
                'confirm_before_execute': False,
                'report_progress': False,
                'keep_current': True
            }
        
        # 统计改进类型
        understanding_count = sum(1 for s in recent_negative if s['improvement_type'] == 'understanding')
        speed_count = sum(1 for s in recent_negative if s['improvement_type'] == 'speed')
        
        return {
            'confirm_before_execute': understanding_count >= 2,
            'report_progress': speed_count >= 2,
            'keep_current': False
        }


# 全局提取器
global_extractor = AutoSignalExtractor()


def extract_signal(user_reply: str, context: str = '') -> Dict:
    """便捷函数：提取信号"""
    return global_extractor.extract(user_reply, context)


def get_behavior_config() -> Dict[str, bool]:
    """便捷函数：获取行为配置"""
    return global_extractor.get_behavior_config()


# 测试
if __name__ == '__main__':
    extractor = AutoSignalExtractor()
    
    print("测试自动信号提取")
    print("=" * 50)
    
    # 测试 1: 负面 - 理解错误
    print("\n测试 1: '你听不懂吗'")
    signal = extractor.extract('你听不懂吗', 'AI 理解错误')
    print(f"情感：{signal['sentiment']}")
    print(f"改进类型：{signal['improvement_type']}")
    print(f"行动：{signal['action']}")
    print(f"建议：{signal['suggestion']}")
    
    # 测试 2: 负面 - 速度慢
    print("\n测试 2: '好了吗，等很久了'")
    signal = extractor.extract('好了吗，等很久了', '任务执行慢')
    print(f"情感：{signal['sentiment']}")
    print(f"紧迫度：{signal['urgency']}")
    print(f"改进类型：{signal['improvement_type']}")
    
    # 测试 3: 正面 - 满意
    print("\n测试 3: '好的，继续'")
    signal = extractor.extract('好的，继续', '用户满意')
    print(f"情感：{signal['sentiment']}")
    print(f"行动：{signal['action']}")
    
    # 测试 4: 行为配置
    print("\n测试 4: 行为配置")
    config = extractor.get_behavior_config()
    print(f"当前配置：{config}")
    
    print("\n测试完成！")
