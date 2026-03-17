#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adaptive TTL Cache - Intelligent cache expiration based on usage patterns
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / '30-scripts-tools'))

from context_cache_manager import ContextCacheManager

class AdaptiveTTLCache:
    """
    Intelligent cache with adaptive TTL based on:
    1. Query frequency (popular = longer TTL)
    2. Query recency (recent = longer TTL)
    3. Query importance (critical = longer TTL)
    4. Time of day (peak hours = longer TTL)
    
    TTL Formula:
    base_ttl × frequency_multiplier × importance_multiplier × time_multiplier
    """
    
    def __init__(self, base_ttl: int = 600):
        self.cache = ContextCacheManager()
        self.base_ttl = base_ttl  # 10 minutes default
        
        # Query tracking
        self.query_history: Dict[str, List[datetime]] = defaultdict(list)
        self.query_importance: Dict[str, str] = {}  # query -> priority
        
        # Configuration
        self.config = {
            'max_ttl': 7200,      # 2 hours max
            'min_ttl': 60,        # 1 minute min
            'frequency_threshold': 3,  # queries/hour for popularity
            'peak_hours': [9, 10, 11, 14, 15, 16],  # Peak business hours
        }
        
        # Statistics
        self.stats = {
            'queries_tracked': 0,
            'ttl_adjustments': 0,
            'avg_ttl': base_ttl,
        }
    
    def _get_frequency_multiplier(self, query: str) -> float:
        """Calculate multiplier based on query frequency"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Count queries in last hour
        recent_queries = [
            t for t in self.query_history[query]
            if t > hour_ago
        ]
        
        frequency = len(recent_queries)
        
        # Multiplier: 1.0 (rare) to 3.0 (very popular)
        if frequency >= 10:
            return 3.0
        elif frequency >= 5:
            return 2.5
        elif frequency >= 3:
            return 2.0
        elif frequency >= 1:
            return 1.5
        else:
            return 1.0
    
    def _get_importance_multiplier(self, query: str) -> float:
        """Calculate multiplier based on query importance"""
        importance = self.query_importance.get(query, 'MEDIUM')
        
        multipliers = {
            'CRITICAL': 3.0,
            'HIGH': 2.0,
            'MEDIUM': 1.0,
            'LOW': 0.5,
        }
        
        return multipliers.get(importance, 1.0)
    
    def _get_time_multiplier(self) -> float:
        """Calculate multiplier based on time of day"""
        hour = datetime.now().hour
        
        if hour in self.config['peak_hours']:
            return 1.5  # Peak hours: longer TTL
        elif hour in [0, 1, 2, 3, 4, 5]:
            return 0.7  # Night: shorter TTL
        else:
            return 1.0  # Normal hours
    
    def _calculate_ttl(self, query: str) -> int:
        """Calculate adaptive TTL for query"""
        freq_mult = self._get_frequency_multiplier(query)
        imp_mult = self._get_importance_multiplier(query)
        time_mult = self._get_time_multiplier()
        
        # Calculate TTL
        ttl = int(
            self.base_ttl * freq_mult * imp_mult * time_mult
        )
        
        # Clamp to min/max
        ttl = max(self.config['min_ttl'], min(ttl, self.config['max_ttl']))
        
        return ttl
    
    def get(self, query: str) -> Optional[Dict]:
        """Get cached result"""
        cache_key = f"adaptive:{query.lower()}"
        return self.cache.get(cache_key)
    
    def set(self, query: str, result: Dict, 
            importance: str = 'MEDIUM',
            verbose: bool = False) -> int:
        """
        Cache result with adaptive TTL
        
        Args:
            query: Search query
            result: Result to cache
            importance: CRITICAL/HIGH/MEDIUM/LOW
            verbose: Show TTL calculation
        
        Returns:
            Calculated TTL in seconds
        """
        # Track query
        self.query_history[query].append(datetime.now())
        self.query_importance[query] = importance
        self.stats['queries_tracked'] += 1
        
        # Calculate TTL
        ttl = self._calculate_ttl(query)
        self.stats['ttl_adjustments'] += 1
        
        # Update average TTL
        total_queries = self.stats['queries_tracked']
        old_avg = self.stats['avg_ttl']
        self.stats['avg_ttl'] = ((old_avg * (total_queries - 1)) + ttl) / total_queries
        
        # Cache with calculated TTL
        cache_key = f"adaptive:{query.lower()}"
        cache_data = {
            'query': query,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'ttl': ttl,
            'importance': importance,
            'frequency': len(self.query_history[query])
        }
        
        self.cache.put(cache_key, cache_data, ttl=ttl, priority=importance)
        
        if verbose:
            freq_mult = self._get_frequency_multiplier(query)
            imp_mult = self._get_importance_multiplier(query)
            time_mult = self._get_time_multiplier()
            
            print(f"\n⏰ Adaptive TTL Calculation:")
            print(f"   Query: {query}")
            print(f"   Base TTL: {self.base_ttl}s")
            print(f"   Frequency multiplier: {freq_mult}x ({len(self.query_history[query])} queries/hour)")
            print(f"   Importance multiplier: {imp_mult}x ({importance})")
            print(f"   Time multiplier: {time_mult}x (hour {datetime.now().hour})")
            print(f"   Final TTL: {ttl}s ({ttl/60:.1f} minutes)")
        
        return ttl
    
    def search(self, query: str, search_func=None,
               importance: str = 'MEDIUM',
               max_results: int = 5,
               verbose: bool = False) -> List:
        """
        Search with adaptive TTL caching
        
        Args:
            query: Search query
            search_func: Function to call if cache miss
            importance: Query importance level
            max_results: Maximum results
            verbose: Show details
        
        Returns:
            Search results
        """
        # Check cache
        cached = self.get(query)
        if cached:
            if verbose:
                ttl = cached.get('ttl', 0)
                print(f"✅ Cache hit (TTL: {ttl}s)")
            return cached.get('result', {}).get('results', [])
        
        # Cache miss - perform search
        if search_func:
            results = search_func(query, max_results=max_results)
        else:
            from ultra_fast_memory_search import UltraFastMemorySearch
            searcher = UltraFastMemorySearch()
            results = searcher.search(query, max_results=max_results)
        
        # Cache results
        self.set(query, {'results': results}, importance=importance, verbose=verbose)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        # Calculate frequency distribution
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        frequency_dist = {
            'very_popular': 0,  # 10+ queries/hour
            'popular': 0,       # 5-9 queries/hour
            'moderate': 0,      # 2-4 queries/hour
            'rare': 0,          # 1 query/hour
            'never': 0,         # 0 queries
        }
        
        for query, timestamps in self.query_history.items():
            recent = len([t for t in timestamps if t > hour_ago])
            if recent >= 10:
                frequency_dist['very_popular'] += 1
            elif recent >= 5:
                frequency_dist['popular'] += 1
            elif recent >= 2:
                frequency_dist['moderate'] += 1
            elif recent == 1:
                frequency_dist['rare'] += 1
            else:
                frequency_dist['never'] += 1
        
        # Importance distribution
        importance_dist = defaultdict(int)
        for query, importance in self.query_importance.items():
            importance_dist[importance] += 1
        
        return {
            'queries_tracked': self.stats['queries_tracked'],
            'ttl_adjustments': self.stats['ttl_adjustments'],
            'avg_ttl_seconds': round(self.stats['avg_ttl'], 2),
            'avg_ttl_minutes': round(self.stats['avg_ttl'] / 60, 2),
            'base_ttl': self.base_ttl,
            'max_ttl': self.config['max_ttl'],
            'min_ttl': self.config['min_ttl'],
            'frequency_distribution': frequency_dist,
            'importance_distribution': dict(importance_dist),
            'unique_queries': len(self.query_history),
        }
    
    def clear(self):
        """Clear all tracked data"""
        self.query_history.clear()
        self.query_importance.clear()
        print("✅ Adaptive TTL cache cleared")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Adaptive TTL Cache")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--base-ttl', type=int, default=600, help='Base TTL in seconds')
    args = parser.parse_args()
    
    cache = AdaptiveTTLCache(base_ttl=args.base_ttl)
    
    if args.demo:
        print("\n⏰ Adaptive TTL Cache Demo")
        print("=" * 80)
        
        # Simulate queries with different patterns
        queries = [
            ("memory evolution", "HIGH"),
            ("memory evolution", "HIGH"),  # Repeat - higher frequency
            ("memory evolution", "HIGH"),  # Repeat - even higher
            ("security config", "MEDIUM"),
            ("workflow automation", "LOW"),
            ("critical system query", "CRITICAL"),
        ]
        
        print("\n📊 Caching queries with adaptive TTL...\n")
        
        for query, importance in queries:
            print(f"Query: {query} ({importance})")
            
            # Simulate search result
            result = {
                'results': [
                    {'source': 'MEMORY.md', 'content': f'Result for {query}', 'score': 0.8}
                ]
            }
            
            # Cache with adaptive TTL
            ttl = cache.set(query, result, importance=importance, verbose=False)
            print(f"   TTL: {ttl}s ({ttl/60:.1f} minutes)")
        
        # Show stats
        print("\n📈 Cache Statistics:")
        stats = cache.get_stats()
        for key, val in stats.items():
            print(f"   {key}: {val}")
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        stats = cache.get_stats()
        print("\n📊 Adaptive TTL Statistics")
        print("=" * 80)
        for key, val in stats.items():
            print(f"   {key}: {val}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
