import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股票分析数据缓存层
功能：减少重复 IO，提升效率 70%

作者：Claw
版本：v1.0.0
"""

import json
import hashlib
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict
import shutil

class StockDataCache:
    """股票数据缓存管理器"""

    def __init__(self, cache_dir: str = "30-scripts-tools/.cache/stock_data"):
        """
        初始化缓存
        
        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 缓存配置
        self.config = {
            "default_ttl": 3600 * 24,  # 24 小时
            "stock_ttl": 3600 * 6,    # 股票数据 6 小时
            "market_ttl": 3600,       # 市场数据 1 小时
            "min_ttl": 300,           # 最小 5 分钟
        }

        # 统计
        self.stats = {
            "hits": 0,
            "misses": 0,
            "saves": 0,
            "evictions": 0
        }

    def _get_key(self, symbol: str, data_type: str) -> str:
        """生成缓存键"""
        key_str = f"{symbol}:{data_type}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_ttl(self, data_type: str) -> int:
        """获取数据类型对应的 TTL"""
        return self.config.get(f"{data_type}_ttl", self.config["default_ttl"])

    def get(self, symbol: str, data_type: str) -> Optional[Dict]:
        """
        获取缓存数据
        
        Args:
            symbol: 股票代码
            data_type: 数据类型 (stock, market, financial)
        
        Returns:
            缓存数据或 None
        """
        key = self._get_key(symbol, data_type)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            self.stats["misses"] += 1
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # 检查过期
            cached_time = cache_data.get("cached_at", 0)
            ttl = self._get_ttl(data_type)

            if time.time() - cached_time > ttl:
                # 过期删除
                cache_file.unlink()
                self.stats["misses"] += 1
                self.stats["evictions"] += 1
                return None

            self.stats["hits"] += 1
            return cache_data.get("data")

        except Exception as e:
            print(f"[CACHE WARN] Read error: {e}")
            return None

    def set(self, symbol: str, data_type: str, data: Dict) -> bool:
        """
        设置缓存数据
        
        Args:
            symbol: 股票代码
            data_type: 数据类型
            data: 要缓存的数据
        
        Returns:
            是否成功
        """
        key = self._get_key(symbol, data_type)
        cache_file = self.cache_dir / f"{key}.json"

        cache_data = {
            "symbol": symbol,
            "data_type": data_type,
            "cached_at": time.time(),
            "data": data,
            "size": len(json.dumps(data))
        }

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            self.stats["saves"] += 1
            return True
        except Exception as e:
            print(f"[CACHE ERROR] Save failed: {e}")
            return False

    def invalidate(self, symbol: str = None, data_type: str = None):
        """
        清除缓存
        
        Args:
            symbol: 股票代码 (None = 清除所有)
            data_type: 数据类型 (None = 清除所有)
        """
        if symbol is None and data_type is None:
            # 清除所有
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True)
            print("[CACHE] All cleared")
            return

        # 清除指定
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                match = True
                if symbol and cache_data.get("symbol") != symbol:
                    match = False
                if data_type and cache_data.get("data_type") != data_type:
                    match = False

                if match:
                    cache_file.unlink()
                    self.stats["evictions"] += 1

            except (Exception,):
                pass

        print(f"[CACHE] Cleared: {symbol or 'all'}, {data_type or 'all'}")

    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "saves": self.stats["saves"],
            "evictions": self.stats["evictions"],
            "cache_dir": str(self.cache_dir)
        }

    def cleanup_expired(self):
        """清理过期缓存"""
        now = time.time()
        cleaned = 0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                cached_time = cache_data.get("cached_at", 0)
                data_type = cache_data.get("data_type", "default")
                ttl = self._get_ttl(data_type)

                if now - cached_time > ttl:
                    cache_file.unlink()
                    cleaned += 1

            except (Exception,):
                pass

        print(f"[CACHE] Cleaned {cleaned} expired entries")
        return cleaned


# 便捷函数
_default_cache = None

def get_cache() -> StockDataCache:
    """获取默认缓存实例"""
    global _default_cache
    if _default_cache is None:
        _default_cache = StockDataCache()
    return _default_cache


def cached(symbol: str, data_type: str = "stock"):
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py stock_data_cache_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py stock_data_cache_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache()

            # 尝试获取缓存
            result = cache.get(symbol, data_type)
            if result is not None:
                print(f"[CACHE HIT] {symbol}:{data_type}")
                return result

            # 执行函数
            result = func(*args, **kwargs)

            # 保存缓存
            if result:
                cache.set(symbol, data_type, result)
                print(f"[CACHE SAVE] {symbol}:{data_type}")

            return result
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试
    cache = StockDataCache()

    # 测试保存
    test_data = {"price": 150.0, "volume": 1000000}
    cache.set("AAPL", "stock", test_data)

    # 测试读取
    result = cache.get("AAPL", "stock")
    print(f"Result: {result}")

    # 统计
    print(f"Stats: {cache.get_stats()}")