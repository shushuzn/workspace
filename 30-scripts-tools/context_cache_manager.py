#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Cache Manager - Two-level caching for context data
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import pickle

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
CACHE_DIR = WORKSPACE / 'data' / 'context_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value_hash: str
    size: int
    created_at: str
    last_accessed: str
    access_count: int
    ttl_seconds: int
    priority: str = 'MEDIUM'  # CRITICAL, HIGH, MEDIUM, LOW

class ContextCacheManager:
    """
    Two-level context caching:
    L1: Memory cache (frequently accessed, fast)
    L2: Disk cache (all contexts, persistent)
    
    Features:
    - TTL-based expiration
    - LRU eviction
    - Priority-based retention
    - Automatic cleanup
    """
    
    def __init__(self, 
                 l1_max_size: int = 100,
                 l2_max_size: int = 1000,
                 default_ttl: int = 3600):
        self.l1_cache: Dict[str, Any] = {}
        self.l1_metadata: Dict[str, CacheEntry] = {}
        self.l2_index: Dict[str, Path] = {}
        
        self.l1_max_size = l1_max_size
        self.l2_max_size = l2_max_size
        self.default_ttl = default_ttl
        
        # Load L2 index
        self._load_l2_index()
    
    def _load_l2_index(self):
        """Load L2 cache index from disk"""
        index_file = CACHE_DIR / 'l2_index.json'
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, path_str in data.items():
                    self.l2_index[key] = Path(path_str)
    
    def _save_l2_index(self):
        """Save L2 cache index to disk"""
        index_file = CACHE_DIR / 'l2_index.json'
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(
                {k: str(v) for k, v in self.l2_index.items()},
                f, indent=2
            )
    
    def _hash_value(self, value: Any) -> str:
        """Generate hash for value"""
        return hashlib.md5(
            json.dumps(value, sort_keys=True).encode()
        ).hexdigest()
    
    def _create_entry(self, key: str, value: Any, 
                     ttl: int = None, priority: str = 'MEDIUM') -> CacheEntry:
        """Create cache entry metadata"""
        now = datetime.now().isoformat()
        ttl = ttl or self.default_ttl
        
        return CacheEntry(
            key=key,
            value_hash=self._hash_value(value),
            size=sys.getsizeof(value),
            created_at=now,
            last_accessed=now,
            access_count=0,
            ttl_seconds=ttl,
            priority=priority
        )
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        created = datetime.fromisoformat(entry.created_at)
        age = (datetime.now() - created).total_seconds()
        return age > entry.ttl_seconds
    
    def _evict_l1(self):
        """Evict from L1 cache using LRU + priority"""
        if len(self.l1_cache) < self.l1_max_size:
            return
        
        # Sort by (priority, last_accessed)
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        
        sorted_keys = sorted(
            self.l1_metadata.keys(),
            key=lambda k: (
                priority_order.get(self.l1_metadata[k].priority, 2),
                self.l1_metadata[k].last_accessed
            )
        )
        
        # Evict lowest priority + oldest
        evict_count = len(self.l1_cache) - self.l1_max_size + 1
        for key in sorted_keys[:evict_count]:
            del self.l1_cache[key]
            del self.l1_metadata[key]
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get value from cache (L1 then L2)"""
        # Check L1
        if key in self.l1_cache:
            entry = self.l1_metadata[key]
            
            # Check expiration
            if self._is_expired(entry):
                del self.l1_cache[key]
                del self.l1_metadata[key]
            else:
                # Update access
                entry.access_count += 1
                entry.last_accessed = datetime.now().isoformat()
                return self.l1_cache[key]
        
        # Check L2
        if key in self.l2_index:
            file_path = self.l2_index[key]
            if file_path.exists():
                try:
                    with open(file_path, 'rb') as f:
                        value = pickle.load(f)
                    
                    # Promote to L1
                    self.put(key, value, 
                           ttl=self.l1_metadata[key].ttl_seconds if key in self.l1_metadata else None,
                           priority=self.l1_metadata[key].priority if key in self.l1_metadata else 'MEDIUM')
                    
                    return value
                except Exception as e:
                    print(f"⚠️  L2 cache read error: {e}")
        
        return default
    
    def put(self, key: str, value: Any, 
            ttl: int = None, priority: str = 'MEDIUM') -> bool:
        """Put value in cache"""
        # Evict if necessary
        self._evict_l1()
        
        # Store in L1
        self.l1_cache[key] = value
        self.l1_metadata[key] = self._create_entry(key, value, ttl, priority)
        
        # Also save to L2
        self._save_l2(key, value)
        
        return True
    
    def _save_l2(self, key: str, value: Any):
        """Save to L2 disk cache"""
        file_path = CACHE_DIR / f'l2_{key}.pkl'
        
        with open(file_path, 'wb') as f:
            pickle.dump(value, f)
        
        self.l2_index[key] = file_path
        self._save_l2_index()
    
    def delete(self, key: str) -> bool:
        """Delete from cache"""
        # Delete from L1
        if key in self.l1_cache:
            del self.l1_cache[key]
            del self.l1_metadata[key]
        
        # Delete from L2
        if key in self.l2_index:
            file_path = self.l2_index[key]
            if file_path.exists():
                file_path.unlink()
            del self.l2_index[key]
            self._save_l2_index()
        
        return True
    
    def clear(self, level: str = 'all'):
        """Clear cache"""
        if level in ['all', 'l1']:
            self.l1_cache.clear()
            self.l1_metadata.clear()
        
        if level in ['all', 'l2']:
            for file_path in self.l2_index.values():
                if file_path.exists():
                    file_path.unlink()
            self.l2_index.clear()
            self._save_l2_index()
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        l1_size = len(self.l1_cache)
        l2_size = len(self.l2_index)
        
        l1_total_size = sum(
            entry.size for entry in self.l1_metadata.values()
        )
        
        l2_total_size = sum(
            f.stat().st_size 
            for f in self.l2_index.values() 
            if f.exists()
        )
        
        # Priority distribution
        priority_dist = {}
        for entry in self.l1_metadata.values():
            p = entry.priority
            priority_dist[p] = priority_dist.get(p, 0) + 1
        
        return {
            'l1_count': l1_size,
            'l1_max': self.l1_max_size,
            'l1_size_bytes': l1_total_size,
            'l2_count': l2_size,
            'l2_max': self.l2_max_size,
            'l2_size_bytes': l2_total_size,
            'priority_distribution': priority_dist,
            'hit_rate': 'N/A (track separately)'
        }
    
    def cleanup(self) -> Dict:
        """Cleanup expired entries"""
        cleaned = {'l1': 0, 'l2': 0}
        
        # Clean L1
        expired_l1 = [
            k for k, v in self.l1_metadata.items()
            if self._is_expired(v)
        ]
        for key in expired_l1:
            del self.l1_cache[key]
            del self.l1_metadata[key]
            cleaned['l1'] += 1
        
        # Clean L2
        expired_l2 = []
        for key, file_path in self.l2_index.items():
            if file_path.exists():
                # Check age from filename or metadata
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    age = (datetime.now() - mtime).total_seconds()
                    if age > 86400 * 7:  # 7 days
                        expired_l2.append(key)
                except:
                    pass
        
        for key in expired_l2:
            file_path = self.l2_index[key]
            if file_path.exists():
                file_path.unlink()
            del self.l2_index[key]
            cleaned['l2'] += 1
        
        if expired_l2:
            self._save_l2_index()
        
        return cleaned

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Context Cache Manager")
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--clear', action='store_true', help='Clear cache')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup expired')
    args = parser.parse_args()
    
    cache = ContextCacheManager()
    
    if args.demo:
        print("\n💾 Context Cache Manager Demo")
        print("=" * 80)
        
        # Test put/get
        print("\n1️⃣  Testing put/get...")
        cache.put('test_key', {'data': 'test_value'}, ttl=60, priority='HIGH')
        value = cache.get('test_key')
        print(f"   Stored: {{'data': 'test_value'}}")
        print(f"   Retrieved: {value}")
        
        # Test stats
        print("\n2️⃣  Cache Stats:")
        stats = cache.stats()
        for key, val in stats.items():
            print(f"   {key}: {val}")
        
        # Test expiration
        print("\n3️⃣  Testing expiration...")
        cache.put('expire_test', 'quick_expire', ttl=1, priority='LOW')
        print("   Stored with 1s TTL...")
        import time
        time.sleep(1.5)
        value = cache.get('expire_test')
        print(f"   After 1.5s: {value} (should be None)")
        
        # Test cleanup
        print("\n4️⃣  Running cleanup...")
        cleaned = cache.cleanup()
        print(f"   Cleaned: L1={cleaned['l1']}, L2={cleaned['l2']}")
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        print("\n📊 Cache Statistics")
        print("=" * 80)
        stats = cache.stats()
        for key, val in stats.items():
            print(f"{key}: {val}")
    
    elif args.clear:
        print("\n🗑️  Clearing cache...")
        cache.clear('all')
        print("✅ Cache cleared")
    
    elif args.cleanup:
        print("\n🧹 Running cleanup...")
        cleaned = cache.cleanup()
        print(f"✅ Cleaned: L1={cleaned['l1']}, L2={cleaned['l2']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
