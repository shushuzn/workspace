#!/usr/bin/env py
# -*- coding: utf-8 -*-
"""
Unit Tests for Data Cache Layer

测试股票数据缓存层

作者：Claw
创建：2026-03-20
版本：v1.0.0
"""

import unittest
import sys
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
WORKSPACE = Path("D:/OpenClaw/workspace")
sys.path.insert(0, str(WORKSPACE / "30-scripts-tools"))

from data_cache import StockDataCache, cache_result


class TestStockDataCache(unittest.TestCase):
    """股票数据缓存测试类"""
    
    def setUp(self) -> None:
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.cache = StockDataCache(
            cache_dir=Path(self.test_dir),
            default_ttl=3600
        )
        self.test_symbol = "TEST"
        self.test_data = {"price": 150.23, "volume": 1000000}
    
    def tearDown(self) -> None:
        """测试后清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self) -> None:
        """测试初始化"""
        self.assertEqual(self.cache.default_ttl, 3600)
        self.assertTrue(self.cache.cache_dir.exists())
        self.assertEqual(len(self.cache.memory_cache), 0)
    
    def test_cache_write_and_read(self) -> None:
        """测试缓存写入和读取"""
        # 写入缓存
        key = self.cache.set(self.test_symbol, "price", self.test_data)
        
        # 验证键格式
        self.assertTrue(key.startswith(f"{self.test_symbol}_price_"))
        
        # 读取缓存
        cached_data = self.cache.get(self.test_symbol, "price")
        
        # 验证数据
        self.assertEqual(cached_data, self.test_data)
    
    def test_cache_hit_miss(self) -> None:
        """测试缓存命中和未命中"""
        # 首次读取 (miss)
        result = self.cache.get(self.test_symbol, "nonexistent")
        self.assertIsNone(result)
        
        # 写入缓存
        self.cache.set(self.test_symbol, "price", self.test_data)
        
        # 再次读取 (hit)
        result = self.cache.get(self.test_symbol, "price")
        self.assertEqual(result, self.test_data)
    
    def test_cache_expiration(self) -> None:
        """测试缓存过期"""
        # 写入短期缓存 (1 秒过期)
        self.cache.set(self.test_symbol, "temp", self.test_data, ttl=1)
        
        # 立即读取 (应该命中)
        result = self.cache.get(self.test_symbol, "temp")
        self.assertEqual(result, self.test_data)
        
        # 等待过期
        time.sleep(1.5)
        
        # 再次读取 (应该过期)
        result = self.cache.get(self.test_symbol, "temp")
        self.assertIsNone(result)
    
    def test_cache_invalidation(self) -> None:
        """测试缓存失效"""
        # 写入多个缓存
        self.cache.set(self.test_symbol, "price", {"price": 100})
        self.cache.set(self.test_symbol, "volume", {"volume": 1000})
        self.cache.set("OTHER", "price", {"price": 200})
        
        # 使 TEST 的 price 缓存失效
        self.cache.invalidate(self.test_symbol, "price")
        
        # 验证 price 缓存已失效
        self.assertIsNone(self.cache.get(self.test_symbol, "price"))
        
        # 验证 volume 缓存仍存在
        self.assertIsNotNone(self.cache.get(self.test_symbol, "volume"))
        
        # 验证 OTHER 缓存仍存在
        self.assertIsNotNone(self.cache.get("OTHER", "price"))
    
    def test_cache_clear_all(self) -> None:
        """测试清除所有缓存"""
        # 写入多个缓存
        self.cache.set("AAPL", "price", {"price": 150})
        self.cache.set("GOOGL", "price", {"price": 2800})
        self.cache.set("TSLA", "price", {"price": 700})
        
        # 清除所有缓存
        self.cache.clear_all()
        
        # 验证所有缓存已清除
        self.assertIsNone(self.cache.get("AAPL", "price"))
        self.assertIsNone(self.cache.get("GOOGL", "price"))
        self.assertIsNone(self.cache.get("TSLA", "price"))
        self.assertEqual(len(self.cache.memory_cache), 0)
    
    def test_cache_stats(self) -> None:
        """测试缓存统计"""
        # 制造一些命中和未命中
        self.cache.get("MISS1", "data")  # miss
        self.cache.get("MISS2", "data")  # miss
        self.cache.set("HIT1", "data", {"value": 1})
        self.cache.get("HIT1", "data")  # hit
        self.cache.set("HIT2", "data", {"value": 2})
        self.cache.get("HIT2", "data")  # hit
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 2)
        self.assertEqual(stats["writes"], 2)
        self.assertEqual(stats["hit_rate"], "50.00%")
    
    def test_memory_cache_lru(self) -> None:
        """测试内存缓存 LRU 淘汰机制"""
        # 设置较小的缓存大小
        self.cache.memory_cache_max_size = 5
        
        # 写入超过限制的缓存
        for i in range(10):
            self.cache.set(f"SYM{i}", "data", {"value": i})
        
        # 验证内存缓存大小不超过限制
        self.assertLessEqual(len(self.cache.memory_cache), 5)
        
        # 验证有淘汰发生
        self.assertGreater(self.cache.stats["evictions"], 0)
    
    def test_disk_cache_persistence(self) -> None:
        """测试磁盘缓存持久化"""
        # 写入缓存
        self.cache.set(self.test_symbol, "persistent", self.test_data)
        
        # 验证磁盘文件存在
        cache_files = list(self.cache.cache_dir.glob("*.json"))
        self.assertGreater(len(cache_files), 0)
        
        # 创建新缓存实例 (模拟重启)
        new_cache = StockDataCache(cache_dir=Path(self.test_dir))
        
        # 验证可以从磁盘读取
        cached_data = new_cache.get(self.test_symbol, "persistent")
        self.assertEqual(cached_data, self.test_data)
    
    def test_cache_with_params(self) -> None:
        """测试带参数的缓存"""
        params1 = {"timeframe": "1d", "adjustment": "forward"}
        params2 = {"timeframe": "1h", "adjustment": "none"}
        
        # 写入不同参数的缓存
        self.cache.set(self.test_symbol, "historical", {"data": "daily"}, params=params1)
        self.cache.set(self.test_symbol, "historical", {"data": "hourly"}, params=params2)
        
        # 验证不同参数返回不同数据
        daily_data = self.cache.get(self.test_symbol, "historical", params=params1)
        hourly_data = self.cache.get(self.test_symbol, "historical", params=params2)
        
        self.assertEqual(daily_data["data"], "daily")
        self.assertEqual(hourly_data["data"], "hourly")
    
    def test_cache_decorator(self) -> None:
        """测试缓存装饰器"""
        call_count = 0
        
        @cache_result(self.cache, "computed", ttl=3600)
        def compute_data(symbol):
            nonlocal call_count
            call_count += 1
            return {"result": symbol * 2}
        
        # 第一次调用 (应该执行函数)
        result1 = compute_data("TEST")
        self.assertEqual(call_count, 1)
        
        # 第二次调用 (应该从缓存读取)
        result2 = compute_data("TEST")
        self.assertEqual(call_count, 1)  # 函数未再次调用
        
        # 验证结果正确
        self.assertEqual(result1, result2)
        self.assertEqual(result1["result"], "TESTTEST")


class TestCacheIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self) -> None:
        """测试完整工作流"""
        test_dir = tempfile.mkdtemp()
        try:
            cache = StockDataCache(cache_dir=Path(test_dir))
            
            # 模拟股票分析工作流
            symbols = ["AAPL", "GOOGL", "TSLA"]
            
            for symbol in symbols:
                # 检查缓存
                data = cache.get(symbol, "analysis")
                if data is None:
                    # 模拟分析
                    data = {"symbol": symbol, "score": 85}
                    cache.set(symbol, "analysis", data)
            
            # 验证所有数据已缓存
            for symbol in symbols:
                cached = cache.get(symbol, "analysis")
                self.assertIsNotNone(cached)
                self.assertEqual(cached["symbol"], symbol)
            
            # 验证统计
            stats = cache.get_stats()
            self.assertEqual(stats["writes"], 3)
            self.assertEqual(stats["hits"], 3)  # 第二次 get 应该命中
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
