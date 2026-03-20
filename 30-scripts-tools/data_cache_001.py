#!/usr/bin/env py
# -*- coding: utf-8 -*-
"""
Data Cache Layer for Stock Analysis

功能：缓存股票数据，避免重复 API 调用
支持：内存缓存 + 磁盘缓存
过期策略：可配置 TTL

作者：Claw
创建：2026-03-20
版本：v1.0.0
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
from functools import wraps

# 添加项目路径
WORKSPACE = Path("D:/OpenClaw/workspace")
sys.path.insert(0, str(WORKSPACE / "30-scripts-tools"))


class StockDataCache:
    """股票数据缓存层"""
    
    def __init__(self, cache_dir: Optional[Path] = None, default_ttl: int = 3600):
        """
        初始化缓存
        
        Args:
            cache_dir: 缓存目录 (默认：60-DATA/stock_cache/)
            default_ttl: 默认过期时间 (秒)，默认 1 小时
        """
        self.cache_dir = cache_dir or (WORKSPACE / "60-DATA" / "stock_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        
        # 内存缓存 (LRU)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_cache_max_size = 1000
        
        # 缓存统计
        self.stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "evictions": 0,
            "expired": 0
        }
        
        print(f"[CACHE] Data Cache initialized")
        print(f"   Directory: {self.cache_dir}")
        print(f"   Default TTL: {default_ttl}s")
        print(f"   Memory cache size: {len(self.memory_cache)}/{self.memory_cache_max_size}")
    
    def _generate_key(self, symbol: str, data_type: str, params: Optional[Dict] = None) -> str:
        """
        生成缓存键
        
        Args:
            symbol: 股票代码
            data_type: 数据类型 (e.g., "historical", "indicators", "financials")
            params: 额外参数
        
        Returns:
            缓存键字符串
        """
        key_data = f"{symbol}:{data_type}"
        if params:
            key_data += ":" + json.dumps(params, sort_keys=True)
        
        # 使用 MD5 哈希缩短键长度
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
        return f"{symbol}_{data_type}_{key_hash}"
    
    def _get_cache_path(self, key: str) -> Path:
        """获取磁盘缓存文件路径"""
        return self.cache_dir / f"{key}.json"
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """检查缓存是否过期"""
        if "expires_at" not in cache_entry:
            return False
        
        expires_at = datetime.fromisoformat(cache_entry["expires_at"])
        return datetime.now() > expires_at
    
    def get(self, symbol: str, data_type: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        从缓存获取数据
        
        Args:
            symbol: 股票代码
            data_type: 数据类型
            params: 额外参数
        
        Returns:
            缓存的数据，如果不存在或已过期则返回 None
        """
        key = self._generate_key(symbol, data_type, params)
        
        # 1. 尝试内存缓存
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if not self._is_expired(entry):
                self.stats["hits"] += 1
                print(f"[CACHE HIT] {key} (memory)")
                return entry["data"]
            else:
                # 内存缓存过期，删除
                del self.memory_cache[key]
                self.stats["expired"] += 1
        
        # 2. 尝试磁盘缓存
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                
                if not self._is_expired(entry):
                    # 加载到内存缓存
                    self._add_to_memory(key, entry)
                    self.stats["hits"] += 1
                    print(f"[CACHE HIT] {key} (disk)")
                    return entry["data"]
                else:
                    # 磁盘缓存过期，删除文件
                    cache_path.unlink()
                    self.stats["expired"] += 1
                    print(f"[CACHE EXPIRED] {key}")
            except Exception as e:
                print(f"[CACHE ERROR] Read failed: {e}")
        
        # 3. 缓存未命中
        self.stats["misses"] += 1
        print(f"[CACHE MISS] {key}")
        return None
    
    def set(self, symbol: str, data_type: str, data: Any, ttl: Optional[int] = None, 
            params: Optional[Dict] = None) -> str:
        """
        写入缓存
        
        Args:
            symbol: 股票代码
            data_type: 数据类型
            data: 要缓存的数据
            ttl: 过期时间 (秒)，使用默认值如果为 None
            params: 额外参数
        
        Returns:
            缓存键
        """
        key = self._generate_key(symbol, data_type, params)
        ttl = ttl or self.default_ttl
        
        # 创建缓存条目
        entry = {
            "data": data,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat(),
            "ttl": ttl,
            "symbol": symbol,
            "data_type": data_type
        }
        
        # 1. 写入内存缓存
        self._add_to_memory(key, entry)
        
        # 2. 写入磁盘缓存
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)
            self.stats["writes"] += 1
            print(f"[CACHE WRITE] {key} -> {cache_path.name}")
        except Exception as e:
            print(f"[CACHE ERROR] Write failed: {e}")
        
        return key
    
    def _add_to_memory(self, key: str, entry: Dict[str, Any]):
        """添加到内存缓存 (带 LRU 淘汰)"""
        # 如果缓存已满，淘汰最旧的条目
        if len(self.memory_cache) >= self.memory_cache_max_size:
            # 删除最旧的 10% 条目
            evict_count = max(1, self.memory_cache_max_size // 10)
            keys_to_evict = list(self.memory_cache.keys())[:evict_count]
            for k in keys_to_evict:
                del self.memory_cache[k]
                self.stats["evictions"] += 1
        
        self.memory_cache[key] = entry
    
    def invalidate(self, symbol: str, data_type: Optional[str] = None):
        """
        使缓存失效
        
        Args:
            symbol: 股票代码
            data_type: 数据类型 (可选，为 None 时清除该股票所有缓存)
        """
        # 清除内存缓存
        keys_to_remove = []
        for key in self.memory_cache:
            if key.startswith(symbol):
                if data_type is None or data_type in key:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.memory_cache[key]
        
        # 清除磁盘缓存
        pattern = f"{symbol}_" if data_type is None else f"{symbol}_{data_type}_"
        for cache_file in self.cache_dir.glob(f"{pattern}*.json"):
            cache_file.unlink()
        
        print(f"[CACHE INVALIDATE] {symbol}{'.' + data_type if data_type else '.*'}")
    
    def clear_all(self):
        """清除所有缓存"""
        # 清除内存缓存
        self.memory_cache.clear()
        
        # 清除磁盘缓存
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        
        print(f"[CACHE CLEAR] All cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        # 计算磁盘缓存大小
        disk_cache_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
        disk_cache_count = len(list(self.cache_dir.glob("*.json")))
        
        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.2f}%",
            "memory_cache_size": len(self.memory_cache),
            "disk_cache_size_bytes": disk_cache_size,
            "disk_cache_count": disk_cache_count,
            "cache_directory": str(self.cache_dir)
        }
    
    def print_stats(self):
        """打印缓存统计信息"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print(" Data Cache Statistics")
        print("=" * 60)
        print(f" Hit Rate: {stats['hit_rate']}")
        print(f" Hits: {stats['hits']}")
        print(f" Misses: {stats['misses']}")
        print(f" Writes: {stats['writes']}")
        print(f" Evictions: {stats['evictions']}")
        print(f" Expired: {stats['expired']}")
        print(f" Memory Cache: {stats['memory_cache_size']} entries")
        print(f" Disk Cache: {stats['disk_cache_count']} files ({stats['disk_cache_size_bytes'] / 1024:.2f} KB)")
        print("=" * 60)


# 装饰器：自动缓存函数结果
def cache_result(cache: StockDataCache, data_type: str, ttl: Optional[int] = None):
    """
    自动缓存装饰器
    
    用法:
        @cache_result(cache, "indicators", ttl=3600)
        def calculate_indicators(symbol):
            # ... 计算逻辑
            return indicators
    """
    def decorator(func):
        @wraps(func)
        def wrapper(symbol, *args, **kwargs):
            # 尝试从缓存获取
            cached = cache.get(symbol, data_type)
            if cached is not None:
                return cached
            
            # 执行函数
            result = func(symbol, *args, **kwargs)
            
            # 写入缓存
            cache.set(symbol, data_type, result, ttl)
            
            return result
        return wrapper
    return decorator


# CLI 接口
def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stock Data Cache Manager")
    parser.add_argument("action", choices=["stats", "clear", "invalidate"], 
                        help="Action to perform")
    parser.add_argument("--symbol", "-s", type=str, help="Stock symbol (for invalidate)")
    parser.add_argument("--type", "-t", type=str, help="Data type (for invalidate)")
    parser.add_argument("--cache-dir", type=Path, help="Custom cache directory")
    
    args = parser.parse_args()
    
    # 创建缓存实例
    cache = StockDataCache(cache_dir=args.cache_dir)
    
    if args.action == "stats":
        cache.print_stats()
    
    elif args.action == "clear":
        confirm = input("Are you sure you want to clear all cache? [y/N]: ")
        if confirm.lower() == 'y':
            cache.clear_all()
            print("[OK] Cache cleared")
        else:
            print("[CANCELLED] Cache clear cancelled")
    
    elif args.action == "invalidate":
        if not args.symbol:
            print("[ERROR] --symbol is required for invalidate action")
            sys.exit(1)
        cache.invalidate(args.symbol, args.type)
        print(f"[OK] Cache invalidated for {args.symbol}")


if __name__ == "__main__":
    main()
