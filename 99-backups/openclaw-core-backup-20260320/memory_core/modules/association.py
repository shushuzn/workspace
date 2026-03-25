"""
关联分析模块

查找记忆之间的关联关系。
"""

from typing import Dict, List, Tuple
from pathlib import Path


class AssociationModule:
    """
    关联分析模块
    
    功能:
    - 相似度计算
    - 关联查找
    - 知识图谱构建
    """

    def __init__(self, config=None):
        self.config = config
        self.min_similarity = 0.3
        self.max_associations = 10

    def find(self, memory: Dict, memories: List[Dict], limit: int = None) -> List[Dict]:
        """查找关联记忆"""
        limit = limit or self.max_associations

        associations = []

        for other in memories:
            if other.get('id') == memory.get('id'):
                continue

            similarity = self._calculate_similarity(memory, other)

            if similarity >= self.min_similarity:
                association = other.copy()
                association['similarity'] = similarity
                association['association_type'] = self._get_association_type(memory, other)
                associations.append(association)

        # 按相似度排序
        associations.sort(key=lambda x: x['similarity'], reverse=True)

        return associations[:limit]

    def _calculate_similarity(self, mem1: Dict, mem2: Dict) -> float:
        """计算相似度"""
        content1 = mem1.get('content', '').lower()
        content2 = mem2.get('content', '').lower()

        tags1 = set(mem1.get('tags', []))
        tags2 = set(mem2.get('tags', []))

        # 1. 标签相似度 (Jaccard)
        if tags1 and tags2:
            tag_intersection = len(tags1 & tags2)
            tag_union = len(tags1 | tags2)
            tag_similarity = tag_intersection / tag_union if tag_union > 0 else 0
        else:
            tag_similarity = 0

        # 2. 内容相似度 (简单词重叠)
        words1 = set(content1.split())
        words2 = set(content2.split())

        if words1 and words2:
            word_intersection = len(words1 & words2)
            word_union = len(words1 | words2)
            content_similarity = word_intersection / word_union if word_union > 0 else 0
        else:
            content_similarity = 0

        # 加权平均
        similarity = (tag_similarity * 0.6 + content_similarity * 0.4)

        return similarity

    def _get_association_type(self, mem1: Dict, mem2: Dict) -> str:
        """获取关联类型"""
        tags1 = set(mem1.get('tags', []))
        tags2 = set(mem2.get('tags', []))

        # 标签重叠
        if tags1 & tags2:
            return "tag_match"

        # 时间接近
        if mem1.get('timestamp') and mem2.get('timestamp'):
            # TODO: 检查时间接近度
            return "temporal"

        return "content_similarity"

    def build_graph(self, memories: List[Dict], threshold: float = 0.5) -> Dict:
        """构建知识图谱"""
        nodes = []
        edges = []

        # 添加节点
        for memory in memories:
            nodes.append({
                'id': memory.get('id'),
                'label': memory.get('content', '')[:50],
                'tags': memory.get('tags', []),
                'score': memory.get('score', 0),
            })

        # 添加边
        for i, mem1 in enumerate(memories):
            for mem2 in memories[i +1:]:
                similarity = self._calculate_similarity(mem1, mem2)

                if similarity >= threshold:
                    edges.append({
                        'source': mem1.get('id'),
                        'target': mem2.get('id'),
                        'weight': similarity,
                        'type': self._get_association_type(mem1, mem2),
                    })

        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'node_count': len(nodes),
                'edge_count': len(edges),
                'avg_edges_per_node': len(edges) / len(nodes) if nodes else 0,
            }
        }

    def get_clusters(self, memories: List[Dict]) -> List[List[Dict]]:
        """获取记忆聚类 (简单实现)"""
        if not memories:
            return []

        # 按标签分组
        tag_groups = {}

        for memory in memories:
            tags = memory.get('tags', [])
            if not tags:
                tags = ['untagged']

            for tag in tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(memory)

        # 返回最大的几个组
        sorted_groups = sorted(tag_groups.values(), key=len, reverse=True)

        return sorted_groups[:5]
