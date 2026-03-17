#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Cache Manager
缓存管理器单元测试
"""

import unittest
import sys
from pathlib import Path
import time

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.performance_optimizer import CacheOptimizer, cached

class TestCacheOptimizer(unittest.TestCase):
    """缓存优化器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.cache = CacheOptimizer(max_size=100, ttl_seconds=60)
    
    def test_set_and_get(self):
        """测试设置和获取缓存"""
        self.cache.set('key1', 'value1')
        result = self.cache.get('key1')
        self.assertEqual(result, 'value1')
    
    def test_get_nonexistent(self):
        """测试获取不存在的缓存"""
        result = self.cache.get('nonexistent')
        self.assertIsNone(result)
    
    def test_ttl_expiration(self):
        """测试 TTL 过期"""
        # 设置短 TTL 缓存
        self.cache.set('key2', 'value2', ttl_seconds=1)
        
        # 立即获取应该成功
        result = self.cache.get('key2')
        self.assertEqual(result, 'value2')
        
        # 等待过期
        time.sleep(1.5)
        
        # 获取应该返回 None
        result = self.cache.get('key2')
        self.assertIsNone(result)
    
    def test_max_size(self):
        """测试最大缓存大小"""
        # 填满缓存
        for i in range(100):
            self.cache.set(f'key{i}', f'value{i}')
        
        # 添加新缓存
        self.cache.set('new_key', 'new_value')
        
        # 检查缓存大小
        self.assertLessEqual(len(self.cache.cache), 100)
    
    def test_clear(self):
        """测试清空缓存"""
        # 添加一些缓存
        for i in range(10):
            self.cache.set(f'key{i}', f'value{i}')
        
        # 清空
        self.cache.clear()
        
        # 检查缓存已清空
        self.assertEqual(len(self.cache.cache), 0)
        self.assertEqual(self.cache.hits, 0)
        self.assertEqual(self.cache.misses, 0)
    
    def test_cache_stats(self):
        """测试缓存统计"""
        # 添加缓存
        self.cache.set('key1', 'value1')
        
        # 命中
        self.cache.get('key1')
        self.cache.get('key1')
        
        # 未命中
        self.cache.get('nonexistent')
        
        # 检查统计
        stats = self.cache.get_stats()
        self.assertEqual(stats['hits'], 2)
        self.assertEqual(stats['misses'], 1)
        hit_rate = stats['hit_rate']
        self.assertGreater(hit_rate, 0)

class TestCachedDecorator(unittest.TestCase):
    """缓存装饰器测试"""
    
    def test_cached_function(self):
        """测试缓存函数"""
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
        self.assertEqual(call_count[0], 1)  # 调用次数不变
        
        # 不同参数
        result3 = expensive_function(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count[0], 2)

if __name__ == '__main__':
    unittest.main(verbosity=2)
