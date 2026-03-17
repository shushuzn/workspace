#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Optimization
性能优化系统
"""

import time
import redis
import logging
from typing import Any, Optional, Callable
from functools import wraps

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, redis_url='redis://localhost:6379'):
        self.redis_client = redis.from_url(redis_url)
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    def cached(self, key: str, ttl: int = 300):
        """Redis 缓存装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = f"{func.__name__}:{key}:{str(args)}:{str(kwargs)}"
                
                # 尝试从 Redis 获取
                try:
                    cached_value = self.redis_client.get(cache_key)
                    if cached_value:
                        self.cache_stats['hits'] += 1
                        logger.info(f"Cache hit: {cache_key}")
                        return cached_value
                except Exception as e:
                    logger.error(f"Redis error: {e}")
                
                # 执行函数
                self.cache_stats['misses'] += 1
                result = func(*args, **kwargs)
                
                # 保存到 Redis
                try:
                    self.redis_client.setex(cache_key, ttl, result)
                except Exception as e:
                    logger.error(f"Redis error: {e}")
                
                return result
            return wrapper
        return decorator
    
    def async_execute(self, func: Callable, *args, **kwargs):
        """异步执行"""
        import threading
        
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Async execution error: {e}")
        
        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()
        return thread
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': hit_rate
        }
    
    def clear_cache(self):
        """清空缓存"""
        try:
            self.redis_client.flushdb()
            self.cache_stats = {'hits': 0, 'misses': 0}
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Redis error: {e}")

# 使用示例
if __name__ == '__main__':
    optimizer = PerformanceOptimizer()
    
    @optimizer.cached('user_data', ttl=300)
    def get_user_data(user_id: str):
        # 模拟数据库查询
        time.sleep(1)
        return {'user_id': user_id, 'name': 'User'}
    
    # 第一次调用 (缓存未命中)
    start = time.time()
    result1 = get_user_data('user1')
    end = time.time()
    print(f"第一次调用：{end - start:.2f}s")
    
    # 第二次调用 (缓存命中)
    start = time.time()
    result2 = get_user_data('user1')
    end = time.time()
    print(f"第二次调用：{end - start:.2f}s")
    
    # 获取缓存统计
    stats = optimizer.get_cache_stats()
    print(f"缓存统计：{stats}")
