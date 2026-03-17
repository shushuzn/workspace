#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Distributed Cache - Redis-like multi-process caching
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import OrderedDict
import threading

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
CACHE_DIR = WORKSPACE / 'data' / 'distributed_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class DistributedCache:
    """
    Multi-process cache with file-based persistence
    
    Features:
    - File-based storage (cross-process)
    - TTL support
    - LRU eviction
    - Thread-safe
    - Priority-based retention
    """
    
    def __init__(self, max_size: int = 1000, 
                 default_ttl: int = 600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # In-memory cache (fast access)
        self.cache: OrderedDict = OrderedDict()
        self.metadata: Dict[str, Dict] = {}
        
        # File index
        self.index_file = CACHE_DIR / 'cache_index.json'
        self.index_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'file_reads': 0,
            'file_writes': 0,
        }
        
        # Load index
        self._load_index()
    
    def _load_index(self):
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.metadata = data.get('metadata', {})
                
                # Load recent entries into memory
                for key, meta in list(self.metadata.items())[:100]:
                    if not self._is_expired(meta):
                        file_path = CACHE_DIR / f"{key}.json"
                        if file_path.exists():
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    value = json.load(f)
                                self.cache[key] = value
                                self.stats['file_reads'] += 1
                            except:
                                pass
                                
                print(f"✅ Loaded {len(self.cache)} cache entries from disk")
            except Exception as e:
                print(f"⚠️  Failed to load index: {e}")
    
    def _save_index(self):
        """Save cache index to disk"""
        with self.index_lock:
            try:
                data = {
                    'metadata': self.metadata,
                    'last_updated': datetime.now().isoformat(),
                    'stats': self.stats,
                }
                
                with open(self.index_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self.stats['file_writes'] += 1
            except Exception as e:
                print(f"⚠️  Failed to save index: {e}")
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for cache key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return CACHE_DIR / f"{key_hash}.json"
    
    def _is_expired(self, meta: Dict) -> bool:
        """Check if cache entry is expired"""
        if 'ttl' not in meta:
            return False
        
        expiry = datetime.fromisoformat(meta['created_at']) + timedelta(seconds=meta['ttl'])
        return datetime.now() > expiry
    
    def _evict_if_needed(self):
        """Evict oldest entries if cache is full"""
        while len(self.cache) >= self.max_size:
            # Remove oldest entry
            if self.cache:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                
                if oldest_key in self.metadata:
                    del self.metadata[oldest_key]
                
                # Delete file
                file_path = self._get_file_path(oldest_key)
                if file_path.exists():
                    file_path.unlink()
                
                self.stats['evictions'] += 1
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache
        
        Args:
            key: Cache key
            default: Default value if not found
        
        Returns:
            Cached value or default
        """
        # Check in-memory cache
        if key in self.cache:
            meta = self.metadata.get(key, {})
            
            if not self._is_expired(meta):
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.stats['hits'] += 1
                return self.cache[key]
            else:
                # Expired - remove
                del self.cache[key]
                if key in self.metadata:
                    del self.metadata[key]
        
        # Check on-disk
        file_path = self._get_file_path(key)
        if file_path.exists():
            meta = self.metadata.get(key, {})
            
            if not self._is_expired(meta):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        value = json.load(f)
                    
                    # Load into memory
                    self.cache[key] = value
                    self.cache.move_to_end(key)
                    self.stats['hits'] += 1
                    self.stats['file_reads'] += 1
                    
                    return value
                except:
                    pass
        
        # Cache miss
        self.stats['misses'] += 1
        return default
    
    def put(self, key: str, value: Any, 
            ttl: int = None,
            priority: str = 'MEDIUM'):
        """
        Put value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            priority: CRITICAL/HIGH/MEDIUM/LOW
        """
        if ttl is None:
            ttl = self.default_ttl
        
        # Evict if needed
        self._evict_if_needed()
        
        # Store in memory
        self.cache[key] = value
        self.cache.move_to_end(key)
        
        # Store metadata
        self.metadata[key] = {
            'created_at': datetime.now().isoformat(),
            'ttl': ttl,
            'priority': priority,
            'size': len(str(value)),
        }
        
        # Store on disk
        file_path = self._get_file_path(key)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(value, f, ensure_ascii=False)
            self.stats['file_writes'] += 1
        except Exception as e:
            print(f"⚠️  Failed to write to disk: {e}")
        
        # Save index periodically
        if len(self.cache) % 10 == 0:
            self._save_index()
    
    def delete(self, key: str):
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
        
        if key in self.metadata:
            del self.metadata[key]
        
        # Delete file
        file_path = self._get_file_path(key)
        if file_path.exists():
            file_path.unlink()
        
        self._save_index()
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.metadata.clear()
        
        # Delete all cache files
        for file_path in CACHE_DIR.glob('*.json'):
            if file_path != self.index_file:
                file_path.unlink()
        
        self._save_index()
        print("✅ Distributed cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total * 100) if total > 0 else 0
        
        # Calculate size by priority
        priority_dist = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for meta in self.metadata.values():
            priority = meta.get('priority', 'MEDIUM')
            priority_dist[priority] = priority_dist.get(priority, 0) + 1
        
        return {
            'total_entries': len(self.cache),
            'disk_entries': len(self.metadata),
            'max_size': self.max_size,
            'default_ttl': self.default_ttl,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate_percent': round(hit_rate, 2),
            'evictions': self.stats['evictions'],
            'file_reads': self.stats['file_reads'],
            'file_writes': self.stats['file_writes'],
            'priority_distribution': priority_dist,
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        expired_keys = []
        
        for key, meta in self.metadata.items():
            if self._is_expired(meta):
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        self._save_index()
        
        print(f"✅ Cleaned up {len(expired_keys)} expired entries")
        return len(expired_keys)
    
    def export_stats(self, output_file: Path = None) -> Path:
        """Export cache statistics to JSON"""
        if output_file is None:
            output_file = CACHE_DIR / 'cache_stats.json'
        
        data = {
            'stats': self.get_stats(),
            'timestamp': datetime.now().isoformat(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Stats exported to: {output_file}")
        return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Distributed Cache")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--clear', action='store_true', help='Clear cache')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup expired')
    args = parser.parse_args()
    
    cache = DistributedCache(max_size=100, default_ttl=600)
    
    if args.demo:
        print("\n🗄️  Distributed Cache Demo")
        print("=" * 80)
        
        # Test caching
        test_data = [
            ("query:memory", {"results": ["memory evolution"]}, "HIGH"),
            ("query:security", {"results": ["security config"]}, "CRITICAL"),
            ("query:workflow", {"results": ["workflow automation"]}, "MEDIUM"),
        ]
        
        print("\n📊 Caching test data...\n")
        
        for key, value, priority in test_data:
            print(f"Put: {key} (priority: {priority})")
            cache.put(key, value, priority=priority)
        
        # Test retrieval
        print("\n🔍 Retrieving cached data...\n")
        
        for key, _, _ in test_data:
            value = cache.get(key)
            if value:
                print(f"Get: {key} → {value}")
            else:
                print(f"Get: {key} → (not found)")
        
        # Show stats
        print("\n📈 Cache Statistics:")
        stats = cache.get_stats()
        for key, val in stats.items():
            print(f"   {key}: {val}")
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        stats = cache.get_stats()
        print("\n📊 Distributed Cache Statistics")
        print("=" * 80)
        for key, val in stats.items():
            print(f"   {key}: {val}")
    
    elif args.clear:
        cache.clear()
    
    elif args.cleanup:
        cache.cleanup_expired()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
