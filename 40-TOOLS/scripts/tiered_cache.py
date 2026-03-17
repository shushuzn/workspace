#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tiered Cache - L2++ with hotspot-based tier management
"""

import os
import sys
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import OrderedDict
from enum import Enum

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
CACHE_DIR = WORKSPACE / 'data' / 'tiered_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class CacheTier(Enum):
    """Cache tiers based on access frequency and importance"""
    CRITICAL = "CRITICAL"  # Permanent or very long TTL (1 day+)
    HIGH = "HIGH"          # Long TTL (1-6 hours)
    MEDIUM = "MEDIUM"      # Normal TTL (10-60 min)
    LOW = "LOW"            # Short TTL (1-5 min) or no cache

class TieredCache:
    """
    L2++ Cache with hotspot-based tier management
    
    Features:
    - Automatic tier classification (CRITICAL/HIGH/MEDIUM/LOW)
    - Tier-specific TTL (60s → 86400s)
    - Frequency-based promotion/demotion
    - Importance-aware retention
    - File-based persistence per tier
    """
    
    # Tier configuration
    TIER_CONFIG = {
        CacheTier.CRITICAL: {
            'ttl': 86400,      # 24 hours
            'max_size': 100,
            'priority': 4,
            'eviction_order': 'last',
        },
        CacheTier.HIGH: {
            'ttl': 21600,      # 6 hours
            'max_size': 500,
            'priority': 3,
            'eviction_order': 'third',
        },
        CacheTier.MEDIUM: {
            'ttl': 600,        # 10 minutes
            'max_size': 1000,
            'priority': 2,
            'eviction_order': 'second',
        },
        CacheTier.LOW: {
            'ttl': 60,         # 1 minute
            'max_size': 2000,
            'priority': 1,
            'eviction_order': 'first',
        },
    }
    
    def __init__(self, auto_promote: bool = True,
                 auto_demote: bool = True):
        self.auto_promote = auto_promote
        self.auto_demote = auto_demote
        
        # Separate cache per tier
        self.caches: Dict[CacheTier, OrderedDict] = {
            tier: OrderedDict() for tier in CacheTier
        }
        
        # Metadata for all entries
        self.metadata: Dict[str, Dict] = {}
        
        # Access frequency tracking
        self.access_counts: Dict[str, int] = {}
        self.access_times: Dict[str, List[datetime]] = {}
        
        # Statistics
        self.stats = {
            'total_queries': 0,
            'tier_hits': {tier.value: 0 for tier in CacheTier},
            'misses': 0,
            'promotions': 0,
            'demotions': 0,
            'evictions': {tier.value: 0 for tier in CacheTier},
        }
        
        # Load persisted cache
        self._load_cache()
    
    def _get_tier(self, query: str, 
                  access_count: int = 0,
                  importance: str = None) -> CacheTier:
        """
        Determine appropriate tier for query
        
        Args:
            query: Search query
            access_count: Number of times accessed
            importance: Explicit importance level
        
        Returns:
            CacheTier
        """
        # Explicit importance overrides
        if importance:
            importance_map = {
                'CRITICAL': CacheTier.CRITICAL,
                'HIGH': CacheTier.HIGH,
                'MEDIUM': CacheTier.MEDIUM,
                'LOW': CacheTier.LOW,
            }
            return importance_map.get(importance.upper(), CacheTier.MEDIUM)
        
        # Automatic tier assignment based on frequency
        if access_count >= 50:
            return CacheTier.CRITICAL
        elif access_count >= 20:
            return CacheTier.HIGH
        elif access_count >= 5:
            return CacheTier.MEDIUM
        else:
            return CacheTier.LOW
    
    def _get_file_path(self, key: str, tier: CacheTier) -> Path:
        """Get file path for cache entry"""
        tier_dir = CACHE_DIR / tier.value
        tier_dir.mkdir(parents=True, exist_ok=True)
        
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return tier_dir / f"{key_hash}.json"
    
    def _is_expired(self, entry: Dict) -> bool:
        """Check if cache entry is expired"""
        if 'ttl' not in entry:
            return False
        
        expiry = entry['created_at'] + timedelta(seconds=entry['ttl'])
        return datetime.now() > expiry
    
    def _load_cache(self):
        """Load cache from disk"""
        total_entries = 0
        
        for tier in CacheTier:
            tier_dir = CACHE_DIR / tier.value
            if not tier_dir.exists():
                continue
            
            for file_path in tier_dir.glob('*.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                    
                    key = entry.get('key')
                    if key and not self._is_expired(entry):
                        self.caches[tier][key] = entry
                        total_entries += 1
                except Exception as e:
                    pass
        
        if total_entries > 0:
            print(f"✅ Loaded {total_entries} tiered cache entries")
    
    def _save_entry(self, key: str, entry: Dict, tier: CacheTier):
        """Save cache entry to disk"""
        file_path = self._get_file_path(key, tier)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(entry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Failed to save entry: {e}")
    
    def _delete_entry(self, key: str, tier: CacheTier):
        """Delete cache entry from disk"""
        file_path = self._get_file_path(key, tier)
        
        if file_path.exists():
            file_path.unlink()
    
    def _promote(self, key: str, from_tier: CacheTier, to_tier: CacheTier):
        """Promote entry to higher tier"""
        if from_tier == to_tier or from_tier.value > to_tier.value:
            return
        
        if key in self.caches[from_tier]:
            entry = self.caches[from_tier][key]
            del self.caches[from_tier][key]
            
            # Update tier and TTL
            entry['tier'] = to_tier.value
            entry['ttl'] = self.TIER_CONFIG[to_tier]['ttl']
            entry['promoted_at'] = datetime.now()
            
            # Add to new tier
            self.caches[to_tier][key] = entry
            
            self.stats['promotions'] += 1
            
            # Save to new tier
            self._save_entry(key, entry, to_tier)
            
            # Delete from old tier
            self._delete_entry(key, from_tier)
    
    def _demote(self, key: str, from_tier: CacheTier, to_tier: CacheTier):
        """Demote entry to lower tier"""
        if from_tier == to_tier or from_tier.value < to_tier.value:
            return
        
        if key in self.caches[from_tier]:
            entry = self.caches[from_tier][key]
            del self.caches[from_tier][key]
            
            # Update tier and TTL
            entry['tier'] = to_tier.value
            entry['ttl'] = self.TIER_CONFIG[to_tier]['ttl']
            entry['demoted_at'] = datetime.now()
            
            # Add to new tier
            self.caches[to_tier][key] = entry
            
            self.stats['demotions'] += 1
            
            # Save to new tier
            self._save_entry(key, entry, to_tier)
            
            # Delete from old tier
            self._delete_entry(key, from_tier)
    
    def _evict_if_needed(self, tier: CacheTier):
        """Evict entries if tier is full"""
        max_size = self.TIER_CONFIG[tier]['max_size']
        
        while len(self.caches[tier]) >= max_size:
            # Find oldest entry (considering eviction order)
            if self.caches[tier]:
                oldest_key = next(iter(self.caches[tier]))
                del self.caches[tier][oldest_key]
                
                if oldest_key in self.metadata:
                    del self.metadata[oldest_key]
                
                # Delete file
                self._delete_entry(oldest_key, tier)
                
                self.stats['evictions'][tier.value] += 1
    
    def get(self, query: str, 
            importance: str = None) -> Optional[Any]:
        """
        Get value from tiered cache
        
        Args:
            query: Search query
            importance: Explicit importance level
        
        Returns:
            Cached value or None
        """
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        key = hashlib.md5(query.encode()).hexdigest()
        
        # Track access
        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        
        if key not in self.access_times:
            self.access_times[key] = []
        self.access_times[key].append(datetime.now())
        
        # Keep only recent access times
        if len(self.access_times[key]) > 100:
            self.access_times[key] = self.access_times[key][-50:]
        
        # Search all tiers (priority order: CRITICAL → LOW)
        for tier in [CacheTier.CRITICAL, CacheTier.HIGH, CacheTier.MEDIUM, CacheTier.LOW]:
            if key in self.caches[tier]:
                entry = self.caches[tier][key]
                
                if not self._is_expired(entry):
                    # Update access count
                    entry['access_count'] = entry.get('access_count', 0) + 1
                    self.caches[tier].move_to_end(key)
                    
                    # Auto-promote if access count increased significantly
                    if self.auto_promote:
                        current_tier = self._get_tier(query, entry['access_count'], importance)
                        if current_tier.value < tier.value:  # Higher priority
                            self._promote(key, tier, current_tier)
                    
                    elapsed = (time.time() - start_time) * 1000
                    self.stats['tier_hits'][tier.value] += 1
                    
                    return entry['value']
                else:
                    # Expired - remove
                    del self.caches[tier][key]
                    self._delete_entry(key, tier)
        
        # Cache miss
        self.stats['misses'] += 1
        return None
    
    def put(self, query: str, value: Any,
            importance: str = None,
            ttl: int = None):
        """
        Put value in tiered cache
        
        Args:
            query: Search query
            value: Value to cache
            importance: Explicit importance level
            ttl: Custom TTL (overrides tier default)
        """
        key = hashlib.md5(query.encode()).hexdigest()
        access_count = self.access_counts.get(key, 0)
        
        # Determine tier
        tier = self._get_tier(query, access_count, importance)
        
        # Evict if needed
        self._evict_if_needed(tier)
        
        # Get TTL
        if ttl is None:
            ttl = self.TIER_CONFIG[tier]['ttl']
        
        # Create entry
        entry = {
            'key': query,
            'value': value,
            'tier': tier.value,
            'created_at': datetime.now(),
            'ttl': ttl,
            'access_count': 1,
            'importance': importance,
        }
        
        # Store in cache
        self.caches[tier][key] = entry
        self.caches[tier].move_to_end(key)
        
        # Store metadata
        self.metadata[key] = {
            'query': query,
            'tier': tier.value,
            'importance': importance,
        }
        
        # Save to disk
        self._save_entry(key, entry, tier)
    
    def get_tier_stats(self) -> Dict:
        """Get statistics per tier"""
        tier_stats = {}
        
        for tier in CacheTier:
            config = self.TIER_CONFIG[tier]
            cache = self.caches[tier]
            
            # Calculate hit rate for this tier
            tier_hits = self.stats['tier_hits'][tier.value]
            total = self.stats['total_queries']
            hit_rate = (tier_hits / total * 100) if total > 0 else 0
            
            tier_stats[tier.value] = {
                'size': len(cache),
                'max_size': config['max_size'],
                'ttl': config['ttl'],
                'priority': config['priority'],
                'hits': tier_hits,
                'hit_rate_percent': round(hit_rate, 2),
                'evictions': self.stats['evictions'][tier.value],
                'utilization_percent': round(len(cache) / config['max_size'] * 100, 2),
            }
        
        return tier_stats
    
    def get_overall_stats(self) -> Dict:
        """Get overall cache statistics"""
        total = self.stats['total_queries']
        total_hits = sum(self.stats['tier_hits'].values())
        hit_rate = (total_hits / total * 100) if total > 0 else 0
        
        total_size = sum(len(cache) for cache in self.caches.values())
        
        return {
            'total_queries': total,
            'total_hits': total_hits,
            'misses': self.stats['misses'],
            'overall_hit_rate_percent': round(hit_rate, 2),
            'promotions': self.stats['promotions'],
            'demotions': self.stats['demotions'],
            'total_entries': total_size,
            'tier_distribution': {
                tier.value: len(self.caches[tier])
                for tier in CacheTier
            },
            'tier_stats': self.get_tier_stats(),
        }
    
    def clear(self, tier: CacheTier = None):
        """Clear cache (specific tier or all)"""
        if tier:
            self.caches[tier].clear()
            
            # Delete files
            tier_dir = CACHE_DIR / tier.value
            if tier_dir.exists():
                for file_path in tier_dir.glob('*.json'):
                    file_path.unlink()
            
            print(f"✅ Cleared {tier.value} tier")
        else:
            for t in CacheTier:
                self.caches[t].clear()
                
                # Delete files
                tier_dir = CACHE_DIR / t.value
                if tier_dir.exists():
                    for file_path in tier_dir.glob('*.json'):
                        file_path.unlink()
            
            print("✅ Cleared all tiers")
    
    def export_stats(self, output_file: Path = None) -> Path:
        """Export statistics to JSON"""
        if output_file is None:
            output_file = CACHE_DIR / 'tiered_cache_stats.json'
        
        data = {
            'stats': self.get_overall_stats(),
            'timestamp': datetime.now().isoformat(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Stats exported to: {output_file}")
        return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tiered Cache")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--clear', action='store_true', help='Clear cache')
    args = parser.parse_args()
    
    cache = TieredCache(auto_promote=True, auto_demote=True)
    
    if args.demo:
        print("\n🏆 Tiered Cache Demo")
        print("=" * 80)
        
        # Simulate queries with different frequencies
        print("\n📊 Simulating queries with varying frequency...\n")
        
        queries = [
            ("memory optimization", "HIGH", 10),
            ("security config", "MEDIUM", 5),
            ("workflow automation", "LOW", 2),
            ("neural embedding", "CRITICAL", 20),
        ]
        
        for query, importance, count in queries:
            print(f"Query: {query} (importance: {importance}, count: {count})")
            
            for i in range(count):
                result = cache.get(query, importance)
                
                if result is None:
                    cache.put(query, f"Results for: {query}", importance)
                else:
                    pass  # Cache hit
            
            # Check tier assignment
            key = hashlib.md5(query.encode()).hexdigest()
            access_count = cache.access_counts.get(key, 0)
            tier = cache._get_tier(query, access_count, importance)
            
            print(f"   → Assigned to: {tier.value} tier")
            print()
        
        # Show stats
        print("\n📈 Tier Statistics:")
        stats = cache.get_overall_stats()
        
        print(f"Total queries: {stats['total_queries']}")
        print(f"Overall hit rate: {stats['overall_hit_rate_percent']}%")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Promotions: {stats['promotions']}")
        print(f"Demotions: {stats['demotions']}")
        
        print("\nTier Distribution:")
        for tier, count in stats['tier_distribution'].items():
            tier_stats = stats['tier_stats'][tier]
            print(f"   {tier}: {count} entries ({tier_stats['utilization_percent']}% utilized)")
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        stats = cache.get_overall_stats()
        print("\n📊 Tiered Cache Statistics")
        print("=" * 80)
        print(f"Total queries: {stats['total_queries']}")
        print(f"Overall hit rate: {stats['overall_hit_rate_percent']}%")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Promotions: {stats['promotions']}")
        print(f"Demotions: {stats['demotions']}")
        
        print("\nTier Distribution:")
        for tier, count in stats['tier_distribution'].items():
            tier_stats = stats['tier_stats'][tier]
            print(f"   {tier}: {count} entries")
            print(f"      Hit rate: {tier_stats['hit_rate_percent']}%")
            print(f"      Utilization: {tier_stats['utilization_percent']}%")
    
    elif args.clear:
        cache.clear()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
