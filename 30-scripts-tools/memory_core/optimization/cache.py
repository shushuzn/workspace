"""
缓存管理器
"""

import time
from typing import Any, Optional, Dict
from collections import OrderedDict


class CacheManager:
    """
    缓存管理器
    
    功能:
    - LRU 缓存
    - TTL 过期
    - 大小限制
    """

    def __init__(self, config):
        self.ttl = config.get('cache_ttl', 300)  # 默认 5 分钟
        self.max_size = config.get('cache_max_size', 1000)
        self.cache: OrderedDict = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]

        # 检查过期
        if time.time() - entry['time'] > self.ttl:
            del self.cache[key]
            self.misses += 1
            return None

        # 移到末尾 (LRU)
        self.cache.move_to_end(key)
        self.hits += 1

        return entry['data']

    def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存"""
        # 检查大小限制
        if len(self.cache) >= self.max_size:
            # 删除最旧的
            self.cache.popitem(last=False)

        self.cache[key] = {
            'data': value,
            'time': time.time(),
            'ttl': ttl or self.ttl
        }

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict:
        """获取统计"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'max_size': self.max_size,
            'ttl': self.ttl,
        }

    def __repr__(self):
        stats = self.get_stats()
        return f"CacheManager(size={stats['size']}, hit_rate={stats['hit_rate']})"
