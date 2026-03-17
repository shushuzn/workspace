#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Optimizer
性能优化器
"""

import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Callable
from functools import wraps
from contextlib import contextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.profiles = {}
    
    @contextmanager
    def profile(self, name: str):
        """
        性能分析上下文
        
        Args:
            name: 分析名称
            
        Example:
            with profiler.profile('database_query'):
                # 执行数据库查询
                pass
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            if name not in self.profiles:
                self.profiles[name] = []
            
            self.profiles[name].append(duration)
            
            logger.info(f"Profile '{name}': {duration:.3f}s")
    
    def get_stats(self) -> Dict:
        """获取性能统计"""
        stats = {}
        
        for name, durations in self.profiles.items():
            if durations:
                stats[name] = {
                    'count': len(durations),
                    'total': sum(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'avg': sum(durations) / len(durations)
                }
        
        return stats
    
    def reset(self):
        """重置分析"""
        self.profiles = {}

class CacheOptimizer:
    """缓存优化器"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        """
        初始化缓存优化器
        
        Args:
            max_size: 最大缓存大小
            ttl_seconds: 默认 TTL (秒)
        """
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Any:
        """获取缓存"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry['expires_at']:
                self.hits += 1
                return entry['value']
            else:
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = None):
        """设置缓存"""
        if ttl_seconds is None:
            ttl_seconds = self.ttl_seconds
        
        # 清理过期缓存
        self._cleanup()
        
        # 检查大小限制
        if len(self.cache) >= self.max_size:
            # 删除最旧的缓存
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['created_at'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'created_at': time.time(),
            'expires_at': time.time() + ttl_seconds
        }
    
    def _cleanup(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time >= entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }
    
    def clear(self):
        """清空缓存"""
        self.cache = {}
        self.hits = 0
        self.misses = 0

def cached(ttl_seconds: int = 300):
    """缓存装饰器"""
    cache = CacheOptimizer(ttl_seconds=ttl_seconds)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试缓存
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 保存缓存
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator

def timed(func: Callable) -> Callable:
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Function '{func.__name__}' executed in {duration:.3f}s")
    return wrapper

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.cache = CacheOptimizer()
    
    def optimize_data_loading(self, data_loader: Callable, cache_key: str, ttl: int = 300):
        """优化数据加载"""
        # 尝试缓存
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Cache hit for {cache_key}")
            return cached_data
        
        # 加载数据
        with self.profiler.profile(f'data_loading:{cache_key}'):
            data = data_loader()
        
        # 保存缓存
        self.cache.set(cache_key, data, ttl)
        
        return data
    
    def optimize_batch_processing(self, items: List, processor: Callable, batch_size: int = 100):
        """优化批量处理"""
        results = []
        
        with self.profiler.profile('batch_processing'):
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                with self.profiler.profile(f'batch_{i // batch_size}'):
                    batch_results = [processor(item) for item in batch]
                    results.extend(batch_results)
        
        return results
    
    def get_optimization_report(self) -> Dict:
        """获取优化报告"""
        return {
            'profiler': self.profiler.get_stats(),
            'cache': self.cache.get_stats()
        }

if __name__ == "__main__":
    # 测试性能优化器
    optimizer = PerformanceOptimizer()
    
    # 测试数据加载优化
    def load_data():
        time.sleep(0.5)  # 模拟慢速加载
        return {"data": "test"}
    
    # 第一次加载 (缓存未命中)
    result1 = optimizer.optimize_data_loading(load_data, "test_key", ttl=60)
    print(f"Result 1: {result1}")
    
    # 第二次加载 (缓存命中)
    result2 = optimizer.optimize_data_loading(load_data, "test_key", ttl=60)
    print(f"Result 2: {result2}")
    
    # 测试批量处理优化
    def process_item(item):
        time.sleep(0.1)  # 模拟处理
        return item * 2
    
    items = list(range(1000))
    results = optimizer.optimize_batch_processing(items, process_item, batch_size=100)
    print(f"Processed {len(results)} items")
    
    # 获取优化报告
    report = optimizer.get_optimization_report()
    print(f"Optimization report: {report}")
