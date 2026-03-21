#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SMART-CACHE-001 智能缓存工具
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
# Purpose: 提供跨工具的智能缓存功能
# Data Flow: check_cache -> store -> retrieve -> invalidate
# Files: smart_cache_001.py, cache_store.json
# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================
"""
import json
import hashlib
import time
from pathlib import Path
from functools import lru_cache
from typing import Any, Optional, Callable

# Cache configuration
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "smart_cache.json"
DEFAULT_TTL = 3600  # 1 hour


def _load_cache() -> dict:
    """Load cache from disk"""
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {"entries": {}, "stats": {"hits": 0, "misses": 0}}


def _save_cache(cache: dict) -> None:
    """Save cache to disk"""
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def _make_key(key: str) -> str:
    """Create cache key hash"""
    return hashlib.md5(key.encode()).hexdigest()


def get(key: str, ttl: int = DEFAULT_TTL) -> Optional[Any]:
    """
    Get value from cache if not expired
    
    Args:
        key: Cache key
        ttl: Time to live in seconds
    
    Returns:
        Cached value or None
    """
    cache = _load_cache()
    entries = cache.get("entries", {})
    
    if key in entries:
        entry = entries[key]
        if time.time() - entry["timestamp"] < ttl:
            cache["stats"]["hits"] += 1
            _save_cache(cache)
            return entry["value"]
        else:
            del entries[key]
    
    cache["stats"]["misses"] += 1
    _save_cache(cache)
    return None


def set(key: str, value: Any) -> None:
    """
    Store value in cache
    
    Args:
        key: Cache key
        value: Value to cache
    """
    cache = _load_cache()
    if "entries" not in cache:
        cache["entries"] = {}
    
    cache["entries"][key] = {
        "value": value,
        "timestamp": time.time()
    }
    _save_cache(cache)


def invalidate(key: Optional[str] = None) -> int:
    """
    Invalidate cache entries
    
    Args:
        key: Specific key to invalidate, or None for all
    
    Returns:
        Number of entries invalidated
    """
    cache = _load_cache()
    
    if key is None:
        count = len(cache.get("entries", {}))
        cache["entries"] = {}
    elif key in cache.get("entries", {}):
        del cache["entries"][key]
        count = 1
    else:
        count = 0
    
    _save_cache(cache)
    return count


def cached(ttl: int = DEFAULT_TTL) -> Callable:
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @lru_cache(maxsize=128)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            result = get(key, ttl)
            if result is None:
                result = func(*args, **kwargs)
                set(key, result)
            return result
        return wrapper
    return decorator


def stats() -> dict:
    """Get cache statistics"""
    cache = _load_cache()
    total = cache["stats"]["hits"] + cache["stats"]["misses"]
    hit_rate = (cache["stats"]["hits"] / total * 100) if total > 0 else 0
    
    return {
        "hits": cache["stats"]["hits"],
        "misses": cache["stats"]["misses"],
        "hit_rate": f"{hit_rate:.1f}%",
        "entries": len(cache.get("entries", {}))
    }


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SMART-CACHE-001 智能缓存工具")
    parser.add_argument("--stats", action="store_true", help="显示缓存统计")
    parser.add_argument("--clear", action="store_true", help="清空所有缓存")
    parser.add_argument("--invalidate", metavar="KEY", help="删除指定缓存")
    
    args = parser.parse_args()
    
    if args.stats:
        print(json.dumps(stats(), indent=2, ensure_ascii=False))
    elif args.clear:
        print(f"[OK] Cleared {invalidate()} entries")
    elif args.invalidate:
        print(f"[OK] Invalidated {invalidate(args.invalidate)} entries")
    else:
        print(stats())


if __name__ == "__main__":
    main()

# ==============================================================================
# STAGE 3: ASK 询问确认
# ==============================================================================
"""
Usage:
    from smart_cache_001 import get, set, cached, stats
    
    # Simple get/set
    value = get("my_key")
    if value is None:
        value = compute_expensive()
        set("my_key", value)
    
    # Decorator style
    @cached(ttl=3600)
    def expensive_function(x):
        return x ** 2
    
    # Stats
    print(stats())

Test:
    py smart_cache_001.py --stats
    py smart_cache_001.py --clear
"""

# STAGE 4: DEBUG
# ==============================================================================
"""
DEBUG:
    - 2026-03-21: Created smart_cache_001.py
    - Provides: get(), set(), cached(), stats(), invalidate()
    - TTL default: 3600 seconds (1 hour)
    - Storage: data/cache/smart_cache.json
"""
