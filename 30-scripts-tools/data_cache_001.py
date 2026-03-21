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

import sys
from pathlib import Path
from typing import Optional

from functools import wraps

# 添加项目路径
WORKSPACE = Path("D:/OpenClaw/workspace")
sys.path.insert(0, str(WORKSPACE / "30-scripts-tools"))

# Re-export StockDataCache from stock_data_cache_001 to avoid duplication
from stock_data_cache_001 import StockDataCache

# 装饰器：自动缓存函数结果
def cache_result(cache: StockDataCache, data_type: str, ttl: Optional[int] = None) -> None:
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
logging.basicConfig(level=logging.INFO)
def main() -> None:
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
