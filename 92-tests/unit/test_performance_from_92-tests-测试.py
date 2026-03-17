#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Performance Optimizer
性能优化器单元测试
"""

import unittest
import sys
from pathlib import Path
import time

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.performance_optimizer import (
    PerformanceProfiler,
    CacheOptimizer,
    PerformanceOptimizer,
    cached,
    timed
)

class TestPerformanceProfiler(unittest.TestCase):
    """性能分析器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.profiler = PerformanceProfiler()
    
    def test_profile_context(self):
        """测试分析上下文"""
        with self.profiler.profile('test_operation'):
            time.sleep(0.1)
        
        stats = self.profiler.get_stats()
        
        self.assertIn('test_operation', stats)
        self.assertEqual(stats['test_operation']['count'], 1)
        self.assertGreater(stats['test_operation']['total'], 0.1)
    
    def test_multiple_profiles(self):
        """测试多次分析"""
        for i in range(3):
            with self.profiler.profile('repeated_operation'):
                time.sleep(0.05)
        
        stats = self.profiler.get_stats()
        
        self.assertEqual(stats['repeated_operation']['count'], 3)
    
    def test_reset(self):
        """测试重置"""
        with self.profiler.profile('test'):
            pass
        
        self.profiler.reset()
        
        stats = self.profiler.get_stats()
        self.assertEqual(len(stats), 0)

class TestCacheOptimizer(unittest.TestCase):
    """缓存优化器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.cache = CacheOptimizer(max_size=100, ttl_seconds=60)
    
    def test_set_and_get(self):
        """测试设置和获取"""
        self.cache.set('key1', 'value1')
        result = self.cache.get('key1')
        
        self.assertEqual(result, 'value1')
    
    def test_get_nonexistent(self):
        """测试获取不存在的缓存"""
        result = self.cache.get('nonexistent')
        self.assertIsNone(result)
    
    def test_ttl_expiration(self):
        """测试 TTL 过期"""
        self.cache.set('key2', 'value2', ttl_seconds=1)
        
        # 立即获取
        result = self.cache.get('key2')
        self.assertEqual(result, 'value2')
        
        # 等待过期
        time.sleep(1.5)
        
        # 获取应该返回 None
        result = self.cache.get('key2')
        self.assertIsNone(result)
    
    def test_max_size(self):
        """测试最大缓存大小"""
        for i in range(100):
            self.cache.set(f'key{i}', f'value{i}')
        
        # 添加新缓存
        self.cache.set('new_key', 'new_value')
        
        # 检查缓存大小
        self.assertLessEqual(len(self.cache.cache), 100)
    
    def test_clear(self):
        """测试清空缓存"""
        for i in range(10):
            self.cache.set(f'key{i}', f'value{i}')
        
        self.cache.clear()
        
        self.assertEqual(len(self.cache.cache), 0)
        self.assertEqual(self.cache.hits, 0)
        self.assertEqual(self.cache.misses, 0)
    
    def test_get_stats(self):
        """测试获取统计"""
        self.cache.set('key1', 'value1')
        
        # 命中
        self.cache.get('key1')
        self.cache.get('key1')
        
        # 未命中
        self.cache.get('nonexistent')
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['hits'], 2)
        self.assertEqual(stats['misses'], 1)
        self.assertGreater(stats['hit_rate'], 0)

class TestPerformanceOptimizer(unittest.TestCase):
    """性能优化器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.optimizer = PerformanceOptimizer()
    
    def test_optimize_data_loading_cache_miss(self):
        """测试优化数据加载 (缓存未命中)"""
        call_count = [0]
        
        def load_data():
            call_count[0] += 1
            return {'data': 'test'}
        
        result = self.optimizer.optimize_data_loading(load_data, 'test_key', ttl=60)
        
        self.assertEqual(result, {'data': 'test'})
        self.assertEqual(call_count[0], 1)
    
    def test_optimize_data_loading_cache_hit(self):
        """测试优化数据加载 (缓存命中)"""
        call_count = [0]
        
        def load_data():
            call_count[0] += 1
            return {'data': 'test'}
        
        # 第一次加载
        self.optimizer.optimize_data_loading(load_data, 'test_key', ttl=60)
        
        # 第二次加载 (应该命中缓存)
        result = self.optimizer.optimize_data_loading(load_data, 'test_key', ttl=60)
        
        self.assertEqual(result, {'data': 'test'})
        self.assertEqual(call_count[0], 1)  # 只调用了一次
    
    def test_optimize_batch_processing(self):
        """测试优化批量处理"""
        def process_item(item):
            return item * 2
        
        items = list(range(100))
        results = self.optimizer.optimize_batch_processing(items, process_item, batch_size=10)
        
        expected = [i * 2 for i in range(100)]
        self.assertEqual(results, expected)
    
    def test_get_optimization_report(self):
        """测试获取优化报告"""
        report = self.optimizer.get_optimization_report()
        
        self.assertIn('profiler', report)
        self.assertIn('cache', report)

class TestDecorators(unittest.TestCase):
    """装饰器测试"""
    
    def test_cached_decorator(self):
        """测试缓存装饰器"""
        call_count = [0]
        
        @cached(ttl_seconds=60)
        def expensive_function(x, y):
            call_count[0] += 1
            return x + y
        
        # 第一次调用
        result1 = expensive_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count[0], 1)
        
        # 第二次调用 (应该命中缓存)
        result2 = expensive_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count[0], 1)
    
    def test_timed_decorator(self):
        """测试计时装饰器"""
        @timed
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result = slow_function()
        self.assertEqual(result, "done")

if __name__ == '__main__':
    unittest.main(verbosity=2)
