"""
搜索模块

支持关键词搜索、语义搜索、缓存搜索。
"""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class SearchModule:
    """
    搜索模块
    
    功能:
    - 关键词搜索
    - 语义搜索 (简单实现)
    - 标签搜索
    - 缓存支持
    """

    def __init__(self, config=None, cache=None):
        self.config = config
        self.cache = cache
        self.limit_default = 10

    def search(self, query: str, memories: List[Dict], limit: int = None, **kwargs) -> List[Dict]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            memories: 记忆列表
            limit: 返回数量限制
            **kwargs: 搜索参数
        
        Returns:
            匹配的记忆列表
        """
        limit = limit or self.limit_default

        # 检查缓存
        cache_key = f"search:{hash(query)}:{limit}"
        if self.cache and (cached := self.cache.get(cache_key)):
            return cached

        # 执行搜索
        results = self._search(query, memories, limit, **kwargs)

        # 缓存结果
        if self.cache:
            self.cache.set(cache_key, results)

        return results

    def _search(self, query: str, memories: List[Dict], limit: int, **kwargs) -> List[Dict]:
        """执行搜索"""
        results = []

        for memory in memories:
            score = self._calculate_relevance(query, memory)

            if score > 0:
                memory_copy = memory.copy()
                memory_copy['search_score'] = score
                results.append(memory_copy)

        # 按相关性排序
        results.sort(key=lambda x: x['search_score'], reverse=True)

        return results[:limit]

    def _calculate_relevance(self, query: str, memory: Dict) -> float:
        """计算相关性分数"""
        content = memory.get('content', '').lower()
        tags = memory.get('tags', [])
        title = memory.get('title', '').lower()

        query_lower = query.lower()
        query_words = query_lower.split()

        score = 0.0

        # 完全匹配
        if query_lower in content:
            score += 1.0

        # 标题匹配 (权重更高)
        if query_lower in title:
            score += 2.0

        # 单词匹配
        for word in query_words:
            if len(word) < 2:
                continue

            # 内容中的单词匹配
            if word in content:
                score += 0.3

            # 标签匹配
            if any(word in tag.lower() for tag in tags):
                score += 0.5

            # 标题中的单词匹配
            if word in title:
                score += 0.8

        # 标签完全匹配
        if any(query_lower == tag.lower() for tag in tags):
            score += 1.5

        return score

    def keyword_search(self, keywords: List[str], memories: List[Dict], limit: int = None) -> List[Dict]:
        """关键词搜索"""
        limit = limit or self.limit_default
        results = []

        for memory in memories:
            content = memory.get('content', '').lower()
            tags = memory.get('tags', [])

            match_count = 0
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in content or keyword_lower in ' '.join(tags).lower():
                    match_count += 1

            if match_count > 0:
                memory_copy = memory.copy()
                memory_copy['match_count'] = match_count
                results.append(memory_copy)

        # 按匹配数排序
        results.sort(key=lambda x: x['match_count'], reverse=True)

        return results[:limit]

    def tag_search(self, tags: List[str], memories: List[Dict], limit: int = None) -> List[Dict]:
        """标签搜索"""
        limit = limit or self.limit_default
        results = []

        for memory in memories:
            memory_tags = memory.get('tags', [])

            # 计算标签匹配数
            match_count = sum(1 for tag in tags if tag.lower() in [t.lower() for t in memory_tags])

            if match_count > 0:
                memory_copy = memory.copy()
                memory_copy['tag_match_count'] = match_count
                results.append(memory_copy)

        # 按匹配数排序
        results.sort(key=lambda x: x['tag_match_count'], reverse=True)

        return results[:limit]

    def advanced_search(
        self,
        query: str,
        memories: List[Dict],
        min_score: float = 0.0,
        max_results: int = None,
        tags: List[str] = None,
        date_range: tuple = None
    ) -> List[Dict]:
        """高级搜索"""
        results = self.search(query, memories, limit=max_results)

        # 过滤最低分数
        if min_score > 0:
            results = [r for r in results if r.get('search_score', 0) >= min_score]

        # 过滤标签
        if tags:
            filtered = []
            for r in results:
                memory_tags = r.get('tags', [])
                if any(tag.lower() in [t.lower() for t in memory_tags] for tag in tags):
                    filtered.append(r)
            results = filtered

        # 过滤日期范围
        if date_range:
            start_date, end_date = date_range
            filtered = []
            for r in results:
                timestamp = r.get('timestamp', '')
                if start_date <= timestamp <= end_date:
                    filtered.append(r)
            results = filtered

        return results

    def semantic_search(self, query: str, memories: List[Dict], limit: int = None) -> List[Dict]:
        """
        语义搜索 (简单实现)
        
        TODO: 使用词向量或嵌入模型
        当前实现：基于同义词扩展
        """
        # 同义词扩展
        synonyms = {
            '记忆': ['memory', '记录', '笔记'],
            '学习': ['learn', 'knowledge', '知识'],
            '优化': ['optimize', 'improve', '改进'],
            '系统': ['system', '架构', 'architecture'],
            '质量': ['quality', 'score', '分数'],
        }

        # 扩展查询
        expanded_queries = [query]
        for word in query.split():
            if word in synonyms:
                expanded_queries.extend(synonyms[word])

        # 搜索所有扩展查询
        all_results = []
        for q in expanded_queries:
            results = self.search(q, memories, limit=limit)
            all_results.extend(results)

        # 去重
        seen_ids = set()
        unique_results = []
        for r in all_results:
            if r.get('id') not in seen_ids:
                seen_ids.add(r.get('id'))
                unique_results.append(r)

        return unique_results[:limit]

    def search_stats(self, query: str, memories: List[Dict]) -> Dict:
        """搜索统计"""
        results = self.search(query, memories, limit=None)

        if not results:
            return {
                'total': 0,
                'avg_score': 0,
                'max_score': 0,
                'min_score': 0,
            }

        scores = [r.get('search_score', 0) for r in results]

        return {
            'total': len(results),
            'avg_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
        }
