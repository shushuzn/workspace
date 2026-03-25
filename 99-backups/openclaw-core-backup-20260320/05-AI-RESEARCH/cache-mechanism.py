#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Mechanism v1
缓存机制实现
"""

import time
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

class Cache:
    """缓存系统"""

    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl  # 默认 TTL (秒)
        self.hits = 0
        self.misses = 0

    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_key = self._generate_key(key)

        if cache_key not in self.cache:
            self.misses += 1
            return None

        item = self.cache[cache_key]

        # 检查是否过期
        if datetime.now() > item["expires_at"]:
            del self.cache[cache_key]
            self.misses += 1
            return None

        self.hits += 1
        return item["value"]

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存"""
        cache_key = self._generate_key(key)
        ttl = ttl or self.default_ttl

        self.cache[cache_key] = {
            "value": value,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=ttl)
        }

        return True

    def delete(self, key: str) -> bool:
        """删除缓存"""
        cache_key = self._generate_key(key)

        if cache_key in self.cache:
            del self.cache[cache_key]
            return True
        return False

    def clear(self) -> int:
        """清空缓存"""
        count = len(self.cache)
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        return count

    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "total_keys": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }

    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        expired_keys = [
            key for key, item in self.cache.items()
            if datetime.now() > item["expires_at"]
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

def demo():
    """演示使用"""
    print("=" * 60)
    print("Cache Mechanism v1 Demo")
    print("=" * 60)

    cache = Cache(default_ttl=10)  # 10 秒 TTL

    # 设置缓存
    print("\n💾 设置缓存:")
    cache.set("user:1", {"name": "Alice", "age": 30})
    cache.set("user:2", {"name": "Bob", "age": 25})
    print("  已设置 2 个缓存项")

    # 获取缓存
    print("\n🔍 获取缓存:")
    user1 = cache.get("user:1")
    print(f"  user:1 = {user1}")

    user2 = cache.get("user:2")
    print(f"  user:2 = {user2}")

    # 获取不存在的缓存
    print("\n❓ 获取不存在的缓存:")
    user3 = cache.get("user:3")
    print(f"  user:3 = {user3}")

    # 缓存统计
    print("\n📊 缓存统计:")
    stats = cache.get_stats()
    print(f"  总键数：{stats['total_keys']}")
    print(f"  命中：{stats['hits']}")
    print(f"  未命中：{stats['misses']}")
    print(f"  命中率：{stats['hit_rate']}")

    # 等待缓存过期
    print("\n⏳ 等待缓存过期 (11 秒)...")
    time.sleep(11)

    # 获取过期缓存
    print("\n🕐 获取过期缓存:")
    user1 = cache.get("user:1")
    print(f"  user:1 = {user1} (已过期)")

    # 清理过期缓存
    print("\n🧹 清理过期缓存:")
    cleaned = cache.cleanup_expired()
    print(f"  清理了 {cleaned} 个过期项")

    # 最终统计
    print("\n📊 最终统计:")
    stats = cache.get_stats()
    print(f"  总键数：{stats['total_keys']}")
    print(f"  命中率：{stats['hit_rate']}")

    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    demo()
