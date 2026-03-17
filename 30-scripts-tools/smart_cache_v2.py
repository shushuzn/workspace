#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Cache v2.0 - Priority-based TTL caching

Features:
- Multi-tier TTL (priority-based)
- LRU eviction
- Compression for large entries
- Statistics tracking
- Auto cleanup

Author: OpenClaw Team
Date: 2026-03-16
Version: 2.0
"""

import sys
import json
import hashlib
import time
import zlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from collections import OrderedDict

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class SmartCacheV2:
    """Priority-based smart cache with TTL"""
    
    # Priority levels with TTL (in hours)
    PRIORITY_TTL = {
        'critical': 1,      # 1 hour (frequently updated)
        'high': 6,          # 6 hours
        'medium': 24,       # 24 hours
        'low': 168,         # 7 days
        'archive': 720      # 30 days
    }
    
    # Compression threshold (bytes)
    COMPRESSION_THRESHOLD = 1024  # 1 KB
    
    def __init__(self, cache_dir: str = 'data/cache', max_size_mb: float = 100.0):
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        self.index_file = self.cache_dir / 'cache_index.json'
        self.index: Dict[str, Dict] = OrderedDict()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'evictions': 0,
            'cleanups': 0
        }
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.load_index()
    
    def load_index(self):
        """Load cache index from disk"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.index = OrderedDict(data.get('entries', {}))
                self.stats = data.get('stats', self.stats)
    
    def save_index(self):
        """Save cache index to disk"""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump({
                'entries': dict(self.index),
                'stats': self.stats,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def _generate_key(self, key_data: Any) -> str:
        """Generate MD5 hash key"""
        if isinstance(key_data, str):
            data = key_data.encode('utf-8')
        else:
            data = json.dumps(key_data, ensure_ascii=False).encode('utf-8')
        return hashlib.md5(data).hexdigest()
    
    def _get_file_path(self, key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{key}.cache"
    
    def _is_expired(self, entry: Dict) -> bool:
        """Check if cache entry is expired"""
        expires_at = datetime.fromisoformat(entry['expires_at'])
        return datetime.now() >= expires_at
    
    def _get_size(self) -> float:
        """Get total cache size in MB"""
        total_size = 0
        for entry in self.index.values():
            file_path = self._get_file_path(entry['key'])
            if file_path.exists():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)
    
    def _evict_lru(self, target_mb: float = 10.0):
        """Evict least recently used entries"""
        evicted = 0
        freed_mb = 0
        
        # Sort by last_access
        sorted_keys = sorted(
            self.index.keys(),
            key=lambda k: self.index[k].get('last_access', '')
        )
        
        for key in sorted_keys:
            if freed_mb >= target_mb:
                break
            
            entry = self.index[key]
            file_path = self._get_file_path(key)
            
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                file_path.unlink()
                freed_mb += size_mb
                evicted += 1
            
            del self.index[key]
            self.stats['evictions'] += 1
        
        if evicted > 0:
            self.save_index()
        
        return {'evicted': evicted, 'freed_mb': freed_mb}
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value from cache"""
        cache_key = self._generate_key(key)
        
        if cache_key not in self.index:
            self.stats['misses'] += 1
            return default
        
        entry = self.index[cache_key]
        
        # Check expiration
        if self._is_expired(entry):
            self.delete(key)
            self.stats['misses'] += 1
            return default
        
        # Read from disk
        file_path = self._get_file_path(cache_key)
        if not file_path.exists():
            del self.index[cache_key]
            self.stats['misses'] += 1
            return default
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Decompress if needed
            if entry.get('compressed'):
                data = zlib.decompress(data)
            
            value = json.loads(data.decode('utf-8'))
            
            # Update access time
            entry['last_access'] = datetime.now().isoformat()
            entry['hits'] = entry.get('hits', 0) + 1
            self.index.move_to_end(cache_key)  # Move to end (most recently used)
            self.save_index()
            
            self.stats['hits'] += 1
            return value
            
        except Exception as e:
            self.delete(key)
            self.stats['misses'] += 1
            return default
    
    def set(self, key: Any, value: Any, priority: str = 'medium', 
            custom_ttl_hours: Optional[float] = None) -> bool:
        """Set value in cache with priority-based TTL"""
        
        # Validate priority
        if priority not in self.PRIORITY_TTL:
            priority = 'medium'
        
        # Calculate TTL
        ttl_hours = custom_ttl_hours or self.PRIORITY_TTL[priority]
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        cache_key = self._generate_key(key)
        
        # Check size and evict if needed
        while self._get_size() > self.max_size_mb:
            self._evict_lru(target_mb=10.0)
        
        # Serialize and compress
        data = json.dumps(value, ensure_ascii=False).encode('utf-8')
        compressed = len(data) > self.COMPRESSION_THRESHOLD
        
        if compressed:
            data = zlib.compress(data)
        
        # Write to disk
        file_path = self._get_file_path(cache_key)
        with open(file_path, 'wb') as f:
            f.write(data)
        
        # Update index
        self.index[cache_key] = {
            'key': cache_key,
            'original_key': str(key)[:100],  # Store truncated original key
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat(),
            'last_access': datetime.now().isoformat(),
            'size_bytes': len(data),
            'compressed': compressed,
            'hits': 0
        }
        
        self.index.move_to_end(cache_key)
        self.stats['writes'] += 1
        self.save_index()
        
        return True
    
    def delete(self, key: Any) -> bool:
        """Delete value from cache"""
        cache_key = self._generate_key(key)
        
        if cache_key in self.index:
            del self.index[cache_key]
            self.save_index()
        
        file_path = self._get_file_path(cache_key)
        if file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    def clear(self):
        """Clear all cache entries"""
        for entry in self.index.values():
            file_path = self._get_file_path(entry['key'])
            if file_path.exists():
                file_path.unlink()
        
        self.index.clear()
        self.save_index()
    
    def cleanup_expired(self) -> Dict:
        """Remove expired entries"""
        removed = 0
        freed_mb = 0
        
        expired_keys = [
            key for key, entry in self.index.items()
            if self._is_expired(entry)
        ]
        
        for key in expired_keys:
            entry = self.index[key]
            file_path = self._get_file_path(key)
            
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                file_path.unlink()
                freed_mb += size_mb
            
            del self.index[key]
            removed += 1
        
        if removed > 0:
            self.stats['cleanups'] += 1
            self.save_index()
        
        return {
            'removed': removed,
            'freed_mb': freed_mb
        }
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_size_mb = self._get_size()
        total_entries = len(self.index)
        
        # Priority breakdown
        priority_counts = {}
        for entry in self.index.values():
            p = entry.get('priority', 'medium')
            priority_counts[p] = priority_counts.get(p, 0) + 1
        
        # Hit rate
        total_accesses = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_accesses * 100) if total_accesses > 0 else 0
        
        return {
            'total_entries': total_entries,
            'total_size_mb': round(total_size_mb, 2),
            'max_size_mb': self.max_size_mb,
            'usage_percent': round(total_size_mb / self.max_size_mb * 100, 1),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'writes': self.stats['writes'],
            'evictions': self.stats['evictions'],
            'cleanups': self.stats['cleanups'],
            'hit_rate_percent': round(hit_rate, 1),
            'priority_breakdown': priority_counts
        }
    
    def show_stats(self):
        """Display cache statistics"""
        stats = self.get_stats()
        
        print(f"\n{'='*70}")
        print(f"💾 Smart Cache v2.0 Statistics")
        print(f"{'='*70}\n")
        
        print(f"📊 Usage:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Total size: {stats['total_size_mb']:.2f} MB / {stats['max_size_mb']:.0f} MB")
        print(f"  Usage: {stats['usage_percent']:.1f}%\n")
        
        print(f"🎯 Performance:")
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Hit rate: {stats['hit_rate_percent']:.1f}%")
        print(f"  Writes: {stats['writes']}")
        print(f"  Evictions: {stats['evictions']}")
        print(f"  Cleanups: {stats['cleanups']}\n")
        
        print(f"📈 Priority Breakdown:")
        for priority, count in sorted(stats['priority_breakdown'].items()):
            ttl = self.PRIORITY_TTL.get(priority, 24)
            print(f"  {priority}: {count} entries (TTL: {ttl}h)")
        
        print(f"\n{'='*70}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Cache v2.0')
    parser.add_argument('action', choices=['stats', 'clear', 'cleanup', 'test'],
                       help='Action to perform')
    parser.add_argument('--cache-dir', type=str, default='data/cache', help='Cache directory')
    parser.add_argument('--max-size', type=float, default=100.0, help='Max size in MB')
    args = parser.parse_args()
    
    cache = SmartCacheV2(cache_dir=args.cache_dir, max_size_mb=args.max_size)
    
    if args.action == 'stats':
        cache.show_stats()
    elif args.action == 'clear':
        cache.clear()
        print("✅ Cache cleared")
    elif args.action == 'cleanup':
        result = cache.cleanup_expired()
        print(f"✅ Cleanup complete: {result['removed']} entries removed, "
              f"{result['freed_mb']:.2f} MB freed")
    elif args.action == 'test':
        # Test cache operations
        print("\n🧪 Testing Smart Cache v2.0...\n")
        
        # Test set/get
        cache.set('test_key', {'data': 'test_value'}, priority='high')
        result = cache.get('test_key')
        print(f"✅ Set/Get test: {result}")
        
        # Test expiration
        cache.set('short_ttl', {'data': 'expires_soon'}, custom_ttl_hours=0.001)  # 3.6 seconds
        time.sleep(4)
        result = cache.get('short_ttl')
        print(f"✅ Expiration test: {result} (should be None)")
        
        # Test stats
        cache.show_stats()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
