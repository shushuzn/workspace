#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Cache - Cache similar queries using semantic similarity
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / '30-scripts-tools'))

from context_cache_manager import ContextCacheManager

class SemanticCache:
    """
    Cache semantically similar queries
    
    Example:
    - "memory evolution" ≈ "memory evolution engine" ≈ "evolution of memory"
    - Cache one, serve all
    
    Similarity threshold: 0.7 (70% similar)
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.cache = ContextCacheManager()
        self.similarity_threshold = similarity_threshold
        self.query_cache: Dict[str, Dict] = {}  # Normalized query -> result
        self.stats = {
            'semantic_hits': 0,
            'exact_hits': 0,
            'misses': 0,
        }
    
    def _normalize(self, query: str) -> str:
        """Normalize query for comparison"""
        # Lowercase
        query = query.lower()
        
        # Remove punctuation
        query = re.sub(r'[^\w\s]', ' ', query)
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'of', 'for', 'in', 'on', 'with'}
        tokens = [t for t in query.split() if t not in stopwords]
        
        return ' '.join(tokens)
    
    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (0-1)"""
        return SequenceMatcher(None, s1, s2).ratio()
    
    def _find_similar_query(self, query: str) -> Optional[str]:
        """Find semantically similar cached query"""
        normalized = self._normalize(query)
        
        for cached_query in self.query_cache.keys():
            if self._similarity(normalized, cached_query) >= self.similarity_threshold:
                return cached_query
        
        return None
    
    def get(self, query: str) -> Optional[Dict]:
        """
        Get cached result (exact or semantic match)
        
        Returns:
            Cached result or None
        """
        normalized = self._normalize(query)
        
        # Check exact match
        if normalized in self.query_cache:
            self.stats['exact_hits'] += 1
            print(f"⚡ Exact cache hit: {query}")
            return self.query_cache[normalized]
        
        # Check semantic match
        similar_query = self._find_similar_query(query)
        if similar_query:
            self.stats['semantic_hits'] += 1
            similarity = self._similarity(normalized, similar_query)
            print(f"⚡ Semantic cache hit: {query} ≈ {similar_query} ({similarity:.2f})")
            return self.query_cache[similar_query]
        
        self.stats['misses'] += 1
        return None
    
    def set(self, query: str, result: Dict, ttl: int = 600):
        """Cache result"""
        normalized = self._normalize(query)
        
        cache_data = {
            'query': normalized,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'ttl': ttl
        }
        
        # Store in L1 (conversation cache)
        self.query_cache[normalized] = cache_data
        
        # Store in L2 (persistent cache)
        cache_key = f"semantic:{normalized}"
        self.cache.put(cache_key, cache_data, ttl=ttl, priority='MEDIUM')
    
    def search(self, query: str, search_func=None, 
               max_results: int = 5,
               use_cache: bool = True) -> List:
        """
        Search with semantic caching
        
        Args:
            query: Search query
            search_func: Function to call if cache miss
            max_results: Maximum results
            use_cache: Enable caching
        
        Returns:
            Search results
        """
        # Check cache
        if use_cache:
            cached = self.get(query)
            if cached:
                return cached.get('result', {}).get('results', [])
        
        # Cache miss - perform search
        if search_func:
            results = search_func(query, max_results=max_results)
        else:
            # Default: use cached memory search
            from memory_search_cached import CachedMemorySearcher
            searcher = CachedMemorySearcher()
            results = searcher.search(query, max_results=max_results)
        
        # Cache results
        if use_cache and results:
            self.set(query, {'results': results}, ttl=600)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = sum(self.stats.values())
        if total == 0:
            return {'status': 'no_queries_yet'}
        
        hit_rate = (self.stats['exact_hits'] + self.stats['semantic_hits']) / total * 100
        
        return {
            'total_queries': total,
            'exact_hits': self.stats['exact_hits'],
            'semantic_hits': self.stats['semantic_hits'],
            'misses': self.stats['misses'],
            'hit_rate_percent': round(hit_rate, 2),
            'cache_size': len(self.query_cache),
            'similarity_threshold': self.similarity_threshold
        }
    
    def clear(self):
        """Clear semantic cache"""
        self.query_cache.clear()
        print("✅ Semantic cache cleared")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Semantic Cache")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--threshold', type=float, default=0.7, help='Similarity threshold')
    args = parser.parse_args()
    
    cache = SemanticCache(similarity_threshold=args.threshold)
    
    if args.demo:
        print("\n🧠 Semantic Cache Demo")
        print("=" * 80)
        
        # Simulate queries
        queries = [
            ("memory evolution engine", True),
            ("memory evolution", True),  # Should match semantically
            ("evolution of memory", True),  # Should match semantically
            ("security config", True),
            ("security configuration", True),  # Should match semantically
            ("workflow automation", True),
        ]
        
        print("\n📊 Running queries...\n")
        
        for query, should_cache in queries:
            print(f"Query: {query}")
            
            # Check cache
            cached = cache.get(query)
            
            if cached:
                print(f"   ✅ Cache hit!")
            else:
                print(f"   🔍 Cache miss - simulating search...")
                # Simulate search result
                result = {
                    'results': [
                        {'source': 'MEMORY.md', 'content': f'Result for {query}', 'score': 0.8}
                    ]
                }
                cache.set(query, result)
            
            print()
        
        # Show stats
        print("\n📈 Cache Statistics:")
        stats = cache.get_stats()
        for key, val in stats.items():
            print(f"   {key}: {val}")
        
        print(f"\n🎯 Semantic Matching:")
        print(f"   Threshold: {cache.similarity_threshold}")
        print(f"   Semantic hits: {cache.stats['semantic_hits']}")
        print(f"   Exact hits: {cache.stats['exact_hits']}")
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        stats = cache.get_stats()
        print("\n📊 Semantic Cache Statistics")
        print("=" * 80)
        for key, val in stats.items():
            print(f"   {key}: {val}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
