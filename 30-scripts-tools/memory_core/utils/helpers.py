"""
记忆辅助工具
"""

import hashlib
import time
from typing import Dict, List, Any
from datetime import datetime


class MemoryHelper:
    """记忆辅助工具"""

    @staticmethod
    def generate_id(content: str) -> str:
        """生成记忆 ID"""
        timestamp = str(int(time.time() * 1000))
        hash_input = f"{content}{timestamp}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        return f"mem_{hash_value}"

    @staticmethod
    def clean_text(text: str) -> str:
        """清洗文本"""
        # 移除多余空格
        text = ' '.join(text.split())

        # 移除特殊字符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        return text.strip()

    @staticmethod
    def extract_tags(content: str, max_tags: int = 5) -> List[str]:
        """从内容中提取标签 (简单实现)"""
        # TODO: 使用 NLP 提取关键词
        # 临时实现：返回空列表
        return []

    @staticmethod
    def summarize(content: str, max_length: int = 200) -> str:
        """生成摘要"""
        if len(content) <= max_length:
            return content

        # 简单截断
        return content[:max_length - 3] + "..."

    @staticmethod
    def format_memory(memory: Dict) -> str:
        """格式化记忆用于显示"""
        lines = [
            f"ID: {memory.get('id', 'N/A')}",
            f"Score: {memory.get('score', 0.0):.2f}",
            f"Created: {memory.get('created_at', 'N/A')}",
            f"Content: {memory.get('content', '')[:200]}",
        ]

        if memory.get('tags'):
            lines.append(f"Tags: {', '.join(memory['tags'])}")

        return "\n".join(lines)

    @staticmethod
    def merge_memories(memories: List[Dict]) -> Dict:
        """合并多个记忆"""
        if not memories:
            return {}

        merged_content = "\n\n".join(m.get('content', '') for m in memories)
        merged_tags = []

        for m in memories:
            merged_tags.extend(m.get('tags', []))

        return {
            'content': merged_content,
            'tags': list(set(merged_tags)),
            'source_count': len(memories),
            'merged_at': str(datetime.now()),
        }

    @staticmethod
    def compare_memories(mem1: Dict, mem2: Dict) -> float:
        """比较两个记忆的相似度 (简单实现)"""
        # TODO: 使用余弦相似度或 Jaccard 相似度
        # 临时实现：基于内容重叠
        content1 = set(mem1.get('content', '').lower().split())
        content2 = set(mem2.get('content', '').lower().split())

        if not content1 or not content2:
            return 0.0

        intersection = len(content1 & content2)
        union = len(content1 | content2)

        return intersection / union if union > 0 else 0.0
