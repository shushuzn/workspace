#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Manager
缓存管理器
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
from functools import wraps

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = None, ttl_seconds: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            ttl_seconds: 默认 TTL (秒)
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / 'cache'
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.memory_cache = {}  # 内存缓存
    
    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        # 先检查内存缓存
        if key in self.memory_cache:
            cached = self.memory_cache[key]
            if datetime.now() < cached['expires_at']:
                return cached['value']
            else:
                del self.memory_cache[key]
        
        # 检查文件缓存
        cache_key = self._generate_key(key)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                
                expires_at = datetime.fromisoformat(cached['expires_at'])
                if datetime.now() < expires_at:
                    # 加载到内存缓存
                    self.memory_cache[key] = cached
                    return cached['value']
                else:
                    # 过期删除
                    cache_file.unlink()
            except Exception as e:
                # 缓存文件损坏
                cache_file.unlink(missing_ok=True)
        
        return default
    
    def set(self, key: str, value: Any, ttl_seconds: int = None) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl_seconds: TTL (秒)
            
        Returns:
            是否成功
        """
        try:
            if ttl_seconds is None:
                ttl_seconds = self.ttl_seconds
            
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            cached = {
                'key': key,
                'value': value,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat()
            }
            
            # 保存到内存缓存
            self.memory_cache[key] = cached
            
            # 保存到文件缓存
            cache_key = self._generate_key(key)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        # 删除内存缓存
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # 删除文件缓存
        cache_key = self._generate_key(key)
        cache_file = self.cache_dir / f"{cache_key}.json"
        cache_file.unlink(missing_ok=True)
        
        return True
    
    def clear(self) -> int:
        """
        清空缓存
        
        Returns:
            删除的缓存文件数
        """
        # 清空内存缓存
        self.memory_cache.clear()
        
        # 清空文件缓存
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        
        return count
    
    def cleanup_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            删除的缓存文件数
        """
        count = 0
        
        # 清理内存缓存
        expired_keys = [
            key for key, cached in self.memory_cache.items()
            if datetime.now() >= cached['expires_at']
        ]
        for key in expired_keys:
            del self.memory_cache[key]
            count += 1
        
        # 清理文件缓存
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                
                expires_at = datetime.fromisoformat(cached['expires_at'])
                if datetime.now() >= expires_at:
                    cache_file.unlink()
                    count += 1
            except:
                cache_file.unlink(missing_ok=True)
                count += 1
        
        return count
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            'memory_cache_size': len(self.memory_cache),
            'file_cache_size': len(list(self.cache_dir.glob("*.json"))),
            'ttl_seconds': self.ttl_seconds
        }

def cached(ttl_seconds: int = 3600):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试获取缓存
            cache_manager = CacheManager()
            cached_value = cache_manager.get(cache_key)
            
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 保存到缓存
            cache_manager.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator

if __name__ == "__main__":
    # 测试缓存
    cache = CacheManager(ttl_seconds=60)
    
    # 设置缓存
    cache.set('test_key', {'data': 'test_data'})
    
    # 获取缓存
    value = cache.get('test_key')
    print(f"Cache value: {value}")
    
    # 获取统计
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    # 清理过期
    cleaned = cache.cleanup_expired()
    print(f"Cleaned {cleaned} expired items")
