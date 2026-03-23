# -*- coding: utf-8 -*-
"""
Memory Models - 数据模型定义
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


@dataclass
class MemoryItem:
    """记忆单元"""
    id: str
    content: str
    type: str  # 'conversation', 'decision', 'preference', 'fact'
    importance: float  # 0.0 - 1.0
    created_at: str
    access_count: int = 0
    last_accessed: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryStats:
    """记忆系统统计"""
    working_count: int
    working_tokens: int
    archive_count: int
    session_id: str
    token_budget: int


# 导出
__all__ = ['MemoryItem', 'MemoryStats']