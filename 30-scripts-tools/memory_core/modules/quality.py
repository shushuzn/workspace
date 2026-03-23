"""
质量评估模块

评估记忆的质量分数 (0-1)。
"""

from typing import Dict, List, Tuple
from pathlib import Path


class QualityModule:
    """
    质量评估器
    
    评估维度:
    - 内容完整性
    - 信息密度
    - 清晰度
    - 可操作性
    - 时效性
    """

    def __init__(self, config=None):
        self.config = config
        self.weights = {
            'completeness': 0.25,
            'density': 0.25,
            'clarity': 0.20,
            'actionability': 0.15,
            'recency': 0.15,
        }

    def evaluate(self, memory: Dict) -> float:
        """
        评估记忆质量
        
        Args:
            memory: 记忆字典
        
        Returns:
            质量分数 (0-1)
        """
        scores = {
            'completeness': self._evaluate_completeness(memory),
            'density': self._evaluate_density(memory),
            'clarity': self._evaluate_clarity(memory),
            'actionability': self._evaluate_actionability(memory),
            'recency': self._evaluate_recency(memory),
        }

        # 加权平均
        total_score = sum(
            scores[dim] * self.weights[dim]
            for dim in self.weights
        )

        # 存储详细评分
        memory['quality_details'] = scores

        return min(max(total_score, 0.0), 1.0)

    def _evaluate_completeness(self, memory: Dict) -> float:
        """评估完整性"""
        content = memory.get('content', '')

        # 检查必需字段
        required_fields = ['content']
        optional_fields = ['tags', 'source', 'timestamp', 'category']

        field_score = len(required_fields) / len(required_fields)  # 1.0

        # 可选字段加分
        optional_count = sum(1 for f in optional_fields if memory.get(f))
        field_score += (optional_count / len(optional_fields)) * 0.5

        # 内容长度评分
        length = len(content)
        if length >= 200:
            length_score = 1.0
        elif length >= 100:
            length_score = 0.8
        elif length >= 50:
            length_score = 0.6
        elif length >= 20:
            length_score = 0.4
        else:
            length_score = 0.2

        return (field_score * 0.6 + length_score * 0.4)

    def _evaluate_density(self, memory: Dict) -> float:
        """评估信息密度"""
        content = memory.get('content', '')

        if not content:
            return 0.0

        # 计算关键词密度
        keywords = [
            '重要', '关键', '核心', '目标', '结果', '方法',
            '发现', '结论', '建议', '必须', '应该', '需要',
            '优化', '改进', '提升', '增强', '解决', '问题'
        ]

        keyword_count = sum(content.count(kw) for kw in keywords)
        word_count = len(content.split())

        if word_count == 0:
            return 0.0

        density = keyword_count / word_count

        # 密度评分
        if density >= 0.05:
            return 1.0
        elif density >= 0.03:
            return 0.8
        elif density >= 0.02:
            return 0.6
        elif density >= 0.01:
            return 0.4
        else:
            return 0.2

    def _evaluate_clarity(self, memory: Dict) -> float:
        """评估清晰度"""
        content = memory.get('content', '')

        if not content:
            return 0.0

        # 检查句子结构
        sentences = content.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        # 平均句子长度
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # 理想句子长度：15-25 词
        if 15 <= avg_length <= 25:
            length_score = 1.0
        elif 10 <= avg_length <= 30:
            length_score = 0.8
        elif 5 <= avg_length <= 40:
            length_score = 0.6
        else:
            length_score = 0.4

        # 检查是否有明确的主题
        has_topic = bool(memory.get('title') or memory.get('category'))
        topic_score = 1.0 if has_topic else 0.5

        # 检查标签
        tags = memory.get('tags', [])
        tag_score = min(len(tags) / 3, 1.0)

        return (length_score * 0.5 + topic_score * 0.3 + tag_score * 0.2)

    def _evaluate_actionability(self, memory: Dict) -> float:
        """评估可操作性"""
        content = memory.get('content', '').lower()

        # 检查行动导向词汇
        action_words = [
            '执行', '实施', '完成', '开始', '结束',
            '下一步', '计划', '任务', '行动', '做'
        ]

        action_count = sum(content.count(word) for word in action_words)

        if action_count >= 3:
            return 1.0
        elif action_count >= 2:
            return 0.8
        elif action_count >= 1:
            return 0.6
        else:
            # 检查是否有下一步
            if 'next' in content or '下一步' in content:
                return 0.7
            return 0.3

    def _evaluate_recency(self, memory: Dict) -> float:
        """评估时效性"""
        from datetime import datetime, timedelta

        timestamp = memory.get('timestamp')

        if not timestamp:
            return 0.5  # 没有时间戳，给中等分数

        try:
            # 解析时间
            if isinstance(timestamp, str):
                # 尝试常见格式
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d']:
                    try:
                        date = datetime.strptime(timestamp, fmt)
                        break
                    except:
                        continue
                else:
                    return 0.5
            else:
                return 0.5

            # 计算天数
            days_old = (datetime.now() - date).days

            # 时效性评分
            if days_old <= 1:
                return 1.0
            elif days_old <= 3:
                return 0.9
            elif days_old <= 7:
                return 0.8
            elif days_old <= 14:
                return 0.7
            elif days_old <= 30:
                return 0.6
            elif days_old <= 60:
                return 0.5
            elif days_old <= 90:
                return 0.4
            else:
                return 0.3

        except:
            return 0.5

    def get_quality_label(self, score: float) -> str:
        """获取质量标签"""
        if score >= 0.85:
            return "优秀"
        elif score >= 0.70:
            return "良好"
        elif score >= 0.50:
            return "中等"
        elif score >= 0.30:
            return "待改进"
        else:
            return "低质量"

    def get_distribution(self, memories: List[Dict]) -> Dict:
        """获取质量分布"""
        scores = [self.evaluate(m) for m in memories]

        if not scores:
            return {}

        return {
            'excellent': len([s for s in scores if s >= 0.85]),
            'good': len([s for s in scores if 0.70 <= s < 0.85]),
            'average': len([s for s in scores if 0.50 <= s < 0.70]),
            'needs_improvement': len([s for s in scores if 0.30 <= s < 0.50]),
            'low': len([s for s in scores if s < 0.30]),
            'avg_score': sum(scores) / len(scores),
        }
