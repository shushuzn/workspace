#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cache Manager v2.0 - Core System Iteration
Production-ready two-level caching (memory + disk)
Features: TTL auto-refresh, LRU eviction, compression, stats tracking

Usage:
    python cache_manager.py --set key value --ttl 3600
    python cache_manager.py --get key
    python cache_manager.py --stats
    python cache_manager.py --clean
    python cache_manager.py --benchmark
"""

import os
import sys
import json
import time
import hashlib
import argparse
import threading
import zlib
from pathlib import Path
from datetime import datetime
from typing import Any, Optional, Dict
from collections import OrderedDict

# Workspace root
WORKSPACE = Path(__file__).parent.parent
CACHE_DIR = WORKSPACE / "50-cache"
STATS_FILE = CACHE_DIR / "cache_stats.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class TwoLevelCache:
    """Production two-level cache (L1: memory, L2: disk)"""
    
    def __init__(self, max_memory_items: int = 1000, compression_threshold: int = 1024):
        self.l1_cache = OrderedDict()  # LRU memory cache
        self.l2_cache_dir = CACHE_DIR / "data"
        self.max_memory_items = max_memory_items
        self.compression_threshold = compression_threshold  # bytes
        
        # TTL configuration (seconds)
        self.default_ttls = {
            'feishu_token': 7200,      # 2 hours
            'arxiv_data': 3600,        # 1 hour
            'github_trending': 1800,   # 30 minutes
            'medium_articles': 1800,   # 30 minutes
            'health_metrics': 300,     # 5 minutes
            'dashboard_data': 600,     # 10 minutes
            'model_status': 600,       # 10 minutes
            'default': 3600            # 1 hour
        }
        
        # Stats tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0,
            'l1_hits': 0,
            'l2_hits': 0,
            'size_bytes': 0
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Initialize
        self._init_cache_dir()
        self._load_stats()
    
    def _init_cache_dir(self):
        """Initialize cache directory"""
        self.l2_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_stats(self):
        """Load stats from disk"""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except:
                pass
    
    def _save_stats(self):
        """Save stats to disk"""
        self.stats['last_updated'] = datetime.now().isoformat()
        self.stats['size_bytes'] = self._calculate_size()
        
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def _calculate_size(self) -> int:
        """Calculate total cache size"""
        total = 0
        
        # L1 size (estimate)
        for key, value in self.l1_cache.items():
            total += len(str(value))
        
        # L2 size
        if self.l2_cache_dir.exists():
            for file in self.l2_cache_dir.glob("*.cache"):
                total += file.stat().st_size
        
        return total
    
    def _get_key_hash(self, key: str) -> str:
        """Get hashed key for file storage"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _compress(self, data: bytes) -> bytes:
        """Compress data if large enough"""
        if len(data) > self.compression_threshold:
            return zlib.compress(data)
        return data
    
    def _decompress(self, data: bytes) -> bytes:
        """Decompress data"""
        try:
            return zlib.decompress(data)
        except:
            return data
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        with self.lock:
            # Check L1 (memory)
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                
                # Check TTL
                if entry['expires_at'] > time.time():
                    # Move to end (LRU)
                    self.l1_cache.move_to_end(key)
                    self.stats['hits'] += 1
                    self.stats['l1_hits'] += 1
                    return entry['value']
                else:
                    # Expired, remove
                    del self.l1_cache[key]
            
            # Check L2 (disk)
            file_path = self.l2_cache_dir / f"{self._get_key_hash(key)}.cache"
            
            if file_path.exists():
                try:
                    with open(file_path, 'rb') as f:
                        data = self._decompress(f.read())
                        entry = json.loads(data.decode('utf-8'))
                    
                    # Check TTL
                    if entry['expires_at'] > time.time():
                        # Promote to L1
                        self.l1_cache[key] = entry
                        self._enforce_memory_limit()
                        
                        self.stats['hits'] += 1
                        self.stats['l2_hits'] += 1
                        return entry['value']
                    else:
                        # Expired, remove
                        file_path.unlink()
                
                except Exception as e:
                    print(f"[CACHE] L2 read error: {e}")
            
            # Cache miss
            self.stats['misses'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        with self.lock:
            # Determine TTL
            if ttl is None:
                # Auto-detect TTL based on key prefix
                ttl = self._auto_detect_ttl(key)
            
            expires_at = time.time() + ttl
            
            entry = {
                'key': key,
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time(),
                'size_bytes': len(str(value))
            }
            
            # Store in L1
            self.l1_cache[key] = entry
            self._enforce_memory_limit()
            
            # Store in L2
            file_path = self.l2_cache_dir / f"{self._get_key_hash(key)}.cache"
            
            try:
                data = json.dumps(entry, ensure_ascii=False).encode('utf-8')
                compressed = self._compress(data)
                
                with open(file_path, 'wb') as f:
                    f.write(compressed)
                
                self.stats['sets'] += 1
                self._save_stats()
                
                return True
            
            except Exception as e:
                print(f"[CACHE] L2 write error: {e}")
                return False
    
    def _auto_detect_ttl(self, key: str) -> int:
        """Auto-detect TTL based on key"""
        for prefix, ttl in self.default_ttls.items():
            if key.startswith(prefix):
                return ttl
        return self.default_ttls['default']
    
    def _enforce_memory_limit(self):
        """Enforce L1 memory limit (LRU eviction)"""
        while len(self.l1_cache) > self.max_memory_items:
            # Remove oldest (first) item
            oldest_key = next(iter(self.l1_cache))
            del self.l1_cache[oldest_key]
            self.stats['evictions'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self.lock:
            deleted = False
            
            # Delete from L1
            if key in self.l1_cache:
                del self.l1_cache[key]
                deleted = True
            
            # Delete from L2
            file_path = self.l2_cache_dir / f"{self._get_key_hash(key)}.cache"
            if file_path.exists():
                file_path.unlink()
                deleted = True
            
            return deleted
    
    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.l1_cache.clear()
            
            # Clear L2
            if self.l2_cache_dir.exists():
                for file in self.l2_cache_dir.glob("*.cache"):
                    file.unlink()
            
            self.stats['evictions'] += len(self.l1_cache)
            self._save_stats()
            
            print("[CACHE] Cleared all cache")
    
    def clean_expired(self) -> int:
        """Clean expired entries"""
        with self.lock:
            cleaned = 0
            now = time.time()
            
            # Clean L1
            expired_keys = [
                key for key, entry in self.l1_cache.items()
                if entry['expires_at'] <= now
            ]
            
            for key in expired_keys:
                del self.l1_cache[key]
                cleaned += 1
            
            # Clean L2
            if self.l2_cache_dir.exists():
                for file in self.l2_cache_dir.glob("*.cache"):
                    try:
                        with open(file, 'rb') as f:
                            data = self._decompress(f.read())
                            entry = json.loads(data.decode('utf-8'))
                        
                        if entry['expires_at'] <= now:
                            file.unlink()
                            cleaned += 1
                    except:
                        pass
            
            if cleaned > 0:
                self._save_stats()
                print(f"[CACHE] Cleaned {cleaned} expired entries")
            
            return cleaned
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            self._save_stats()
            
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate_percent': round(hit_rate, 2),
                'sets': self.stats['sets'],
                'evictions': self.stats['evictions'],
                'l1_hits': self.stats['l1_hits'],
                'l2_hits': self.stats['l2_hits'],
                'l1_items': len(self.l1_cache),
                'size_bytes': self._calculate_size(),
                'size_mb': round(self._calculate_size() / (1024 * 1024), 2),
                'last_updated': self.stats.get('last_updated', 'N/A')
            }
    
    def benchmark(self, iterations: int = 1000) -> Dict:
        """Run cache benchmark"""
        print(f"\n[CACHE] Running benchmark ({iterations} iterations)...")
        
        # Reset stats
        self.stats = {k: 0 for k in self.stats.keys()}
        
        start_time = time.time()
        
        # Write benchmark
        write_start = time.time()
        for i in range(iterations):
            self.set(f"bench_key_{i}", {"value": i, "data": "x" * 100})
        write_time = time.time() - write_start
        
        # Read benchmark
        read_start = time.time()
        hits = 0
        for i in range(iterations):
            value = self.get(f"bench_key_{i}")
            if value is not None:
                hits += 1
        read_time = time.time() - read_start
        
        total_time = time.time() - start_time
        
        stats = self.get_stats()
        
        results = {
            'iterations': iterations,
            'total_time_seconds': round(total_time, 3),
            'write_time_seconds': round(write_time, 3),
            'read_time_seconds': round(read_time, 3),
            'writes_per_second': round(iterations / write_time, 2),
            'reads_per_second': round(iterations / read_time, 2),
            'hit_rate_percent': stats['hit_rate_percent'],
            'l1_hits': stats['l1_hits'],
            'l2_hits': stats['l2_hits']
        }
        
        print(f"\n[BENCHMARK] Results:")
        print(f"  Total time: {results['total_time_seconds']}s")
        print(f"  Write speed: {results['writes_per_second']} ops/s")
        print(f"  Read speed: {results['reads_per_second']} ops/s")
        print(f"  Hit rate: {results['hit_rate_percent']}%")
        print(f"  L1 hits: {results['l1_hits']}")
        print(f"  L2 hits: {results['l2_hits']}")
        
        return results


# Global cache instance
_cache_instance = None


def get_cache() -> TwoLevelCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = TwoLevelCache()
    return _cache_instance


def main():
    parser = argparse.ArgumentParser(description='Cache Manager v2.0')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set cache value')
    parser.add_argument('--get', type=str, metavar='KEY', help='Get cache value')
    parser.add_argument('--delete', type=str, metavar='KEY', help='Delete cache key')
    parser.add_argument('--stats', action='store_true', help='Show cache stats')
    parser.add_argument('--clean', action='store_true', help='Clean expired entries')
    parser.add_argument('--clear', action='store_true', help='Clear all cache')
    parser.add_argument('--ttl', type=int, help='TTL in seconds (for --set)')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark')
    args = parser.parse_args()
    
    cache = get_cache()
    
    if args.set:
        key, value = args.set
        ttl = args.ttl
        success = cache.set(key, value, ttl=ttl)
        print(f"[OK] Set {key} = {value[:50]}..." if len(str(value)) > 50 else f"[OK] Set {key} = {value}")
    
    if args.get:
        value = cache.get(args.get)
        if value is not None:
            print(f"[OK] {args.get} = {value}")
        else:
            print(f"[MISS] {args.get} not found")
    
    if args.delete:
        success = cache.delete(args.delete)
        print(f"[OK] Deleted {args.delete}" if success else f"[MISS] {args.delete} not found")
    
    if args.stats:
        stats = cache.get_stats()
        print("\n" + "=" * 60)
        print("Cache Statistics")
        print("=" * 60)
        print(f"  Hit Rate: {stats['hit_rate_percent']}%")
        print(f"  Hits: {stats['hits']} (L1: {stats['l1_hits']}, L2: {stats['l2_hits']})")
        print(f"  Misses: {stats['misses']}")
        print(f"  Sets: {stats['sets']}")
        print(f"  Evictions: {stats['evictions']}")
        print(f"  L1 Items: {stats['l1_items']}")
        print(f"  Size: {stats['size_mb']} MB")
        print(f"  Last Updated: {stats['last_updated']}")
        print("=" * 60)
    
    if args.clean:
        cleaned = cache.clean_expired()
        print(f"[OK] Cleaned {cleaned} expired entries")
    
    if args.clear:
        cache.clear()
    
    if args.benchmark:
        cache.benchmark(iterations=1000)
    
    if not any([args.set, args.get, args.delete, args.stats, args.clean, args.clear, args.benchmark]):
        parser.print_help()


if __name__ == "__main__":
    main()
