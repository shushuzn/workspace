# -*- coding: utf-8 -*-
"""
Working Memory - 短期工作记忆
管理当前会话的活跃上下文
"""

import re
from typing import List, Dict, Optional
from collections import deque
from datetime import datetime, timedelta

from .models import MemoryItem


class WorkingMemory:
    """
    短期工作记忆
    
    特性:
    - Token 预算限制
    - LRU 淘汰策略
    - 自动压缩阈值
    """

    def __init__(self, token_budget: int = 5000, max_items: int = 100):
        self.token_budget = token_budget
        self.max_items = max_items
        self._items: deque = deque(maxlen=max_items)
        self._id_index: Dict[str, int] = {}

    def add(self, item: MemoryItem) -> None:
        """添加记忆单元"""
        # 检查是否已存在
        if item.id in self._id_index:
            # 更新访问时间
            idx = self._id_index[item.id]
            self._items[idx] = item
        else:
            # 添加新项
            self._items.append(item)
            self._id_index[item.id] = len(self._items) - 1

        # 超过预算时自动淘汰
        self._enforce_budget()

    def remove(self, item_id: str) -> bool:
        """移除指定记忆"""
        if item_id not in self._id_index:
            return False

        idx = self._id_index[item_id]
        del self._items[idx]

        # 重建索引
        self._rebuild_index()
        return True

    def get_all(self) -> List[MemoryItem]:
        """获取所有记忆（保持顺序）"""
        return list(self._items)

    def get_recent(self, n: int = 10) -> List[MemoryItem]:
        """获取最近N条"""
        return list(self._items)[-n:]

    def get_low_priority(self, threshold: float = 0.3) -> List[MemoryItem]:
        """获取低优先级项（可归档）"""
        return [item for item in self._items if item.importance < threshold]

    def count(self) -> int:
        """记忆数量"""
        return len(self._items)

    def estimate_tokens(self, items: List[MemoryItem] = None) -> int:
        """估算token数量（简单：4字符=1token）"""
        items = items or self._items
        total_chars = sum(len(item.content) for item in items)
        return total_chars // 4

    def compress(self) -> int:
        """
        压缩工作记忆
        - 合并相似内容
        - 摘要化旧对话
        返回压缩掉的项数
        """
        if len(self._items) < 5:
            return 0

        compressed_count = 0

        # 策略1: 合并连续相似对话
        merged = []
        prev_item = None

        for item in self._items:
            if prev_item and item.type == 'conversation' and prev_item.type == 'conversation':
                # 合并为摘要
                combined = f"{prev_item.content[:100]}... {item.content[:100]}"
                prev_item = MemoryItem(
                    id=f"merged_{prev_item.id}",
                    content=combined,
                    type='summary',
                    importance=max(prev_item.importance, item.importance),
                    created_at=prev_item.created_at,
                    metadata={"merged_from": [prev_item.id, item.id]}
                )
                compressed_count += 1
            else:
                if prev_item:
                    merged.append(prev_item)
                prev_item = item

        if prev_item:
            merged.append(prev_item)

        # 重建
        self._items = deque(merged, maxlen=self.max_items)
        self._rebuild_index()

        return compressed_count

    def _enforce_budget(self) -> None:
        """强制执行token预算"""
        while self.estimate_tokens() > self.token_budget and len(self._items) > 1:
            # 移除最老的低优先级项
            oldest = self._items[0]
            if oldest.importance < 0.5:
                self.remove(oldest.id)
            else:
                # 尝试压缩
                self.compress()
                if self.estimate_tokens() > self.token_budget:
                    # 强制移除最老的
                    self.remove(oldest.id)

    def _rebuild_index(self) -> None:
        """重建ID索引"""
        self._id_index = {
            item.id: idx
            for idx, item in enumerate(self._items)
        }

    def search(self, keyword: str) -> List[MemoryItem]:
        """关键词搜索"""
        keyword = keyword.lower()
        return [
            item for item in self._items
            if keyword in item.content.lower()
        ]

    def get_by_type(self, memory_type: str) -> List[MemoryItem]:
        """按类型获取"""
        return [item for item in self._items if item.type == memory_type]


# 导出兼容接口
__all__ = ['WorkingMemory']