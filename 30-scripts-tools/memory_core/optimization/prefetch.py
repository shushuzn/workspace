"""
预取器
"""

from typing import List, Dict
from collections import defaultdict


class Prefetcher:
    """
    预取器 - 预测性加载
    
    功能:
    - 基于历史预测下一个查询
    - 后台预取数据
    """

    def __init__(self, config):
        self.config = config
        self.query_history: List[str] = []
        self.query_patterns: Dict[str, int] = defaultdict(int)

    def record_query(self, query: str):
        """记录查询"""
        self.query_history.append(query)
        self.query_patterns[query] += 1

        # 限制历史记录
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-500:]

    def predict_next_queries(self, current_query: str, limit: int = 3) -> List[str]:
        """
        预测下一个查询
        
        基于:
        - 历史查询模式
        - 热门查询
        """
        # 简单实现：返回最热门的查询
        sorted_queries = sorted(
            self.query_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 排除当前查询
        predictions = [q for q, _ in sorted_queries if q != current_query]

        return predictions[:limit]

    def get_hot_queries(self, limit: int = 10) -> List[str]:
        """获取热门查询"""
        sorted_queries = sorted(
            self.query_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [q for q, _ in sorted_queries[:limit]]

    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            'total_queries': len(self.query_history),
            'unique_queries': len(self.query_patterns),
            'hot_queries': self.get_hot_queries(5),
        }

    def clear(self):
        """清空历史"""
        self.query_history.clear()
        self.query_patterns.clear()
