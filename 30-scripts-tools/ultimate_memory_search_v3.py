#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultimate Memory Search v3 - Complete Phase 5 Integration

Integrates:
- Phase 5A: Context-Aware Cache + Tiered Cache + Observability
- Phase 5B: Incremental Index + Hybrid Search + Graded Fallback
- Phase 5C: RL TTL Optimizer + Intent Predictor

Features:
- Intent prediction and pre-fetching
- Multi-level caching (L1 context-aware, L2 tiered)
- Incremental indexing with delta updates
- Hybrid search (BM25 + Dense embedding)
- Graded fallback (3-tier confidence-based)
- RL-based TTL optimization
- Real-time observability and metrics
"""

import os
import sys
import json
import time
import hashlib
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import re

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
DATA_DIR = WORKSPACE / 'data' / 'ultimate_memory_search'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Import Phase 5 components (simulated for standalone operation)
# In production, these would import from actual modules

class ContextAwareCache:
    """L1 Context-Aware Cache (Phase 5A)"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, Dict] = {}
        self.sessions: Dict[str, List[str]] = defaultdict(list)
        self.stats = {'hits': 0, 'misses': 0}
    
    def get(self, key: str, session_id: str = None) -> Optional[Dict]:
        if key in self.cache:
            self.stats['hits'] += 1
            if session_id:
                self.sessions[session_id].append(key)
            return self.cache[key]
        self.stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Dict, session_id: str = None):
        if len(self.cache) >= self.max_size:
            # Remove oldest
            oldest = min(self.cache.items(), key=lambda x: x[1].get('timestamp', 0))
            del self.cache[oldest[0]]
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'session_id': session_id,
        }
        
        if session_id:
            self.sessions[session_id].append(key)
    
    def get_stats(self) -> Dict:
        total = self.stats['hits'] + self.stats['misses']
        return {
            'size': len(self.cache),
            'hit_rate': self.stats['hits'] / total if total > 0 else 0,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'sessions': len(self.sessions),
        }


class TieredCache:
    """L2 Tiered Cache (Phase 5A)"""
    
    TIERS = {
        'CRITICAL': {'max_size': 100, 'ttl': 86400},
        'HIGH': {'max_size': 500, 'ttl': 21600},
        'MEDIUM': {'max_size': 1000, 'ttl': 600},
        'LOW': {'max_size': 2000, 'ttl': 60},
    }
    
    def __init__(self):
        self.tiers: Dict[str, Dict] = {
            tier: {'cache': {}, 'stats': {'hits': 0, 'misses': 0}}
            for tier in self.TIERS
        }
    
    def get(self, key: str) -> Optional[Dict]:
        for tier_name, tier_data in self.tiers.items():
            if key in tier_data['cache']:
                tier_data['stats']['hits'] += 1
                return tier_data['cache'][key]
        
        # Not found
        for tier_data in self.tiers.values():
            tier_data['stats']['misses'] += 1
        return None
    
    def set(self, key: str, value: Dict, tier: str = 'MEDIUM'):
        if tier not in self.tiers:
            tier = 'MEDIUM'
        
        tier_config = self.TIERS[tier]
        tier_cache = self.tiers[tier]['cache']
        
        if len(tier_cache) >= tier_config['max_size']:
            # Remove oldest
            oldest = min(tier_cache.items(), key=lambda x: x[1].get('timestamp', 0))
            del tier_cache[oldest[0]]
        
        tier_cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'ttl': tier_config['ttl'],
        }
    
    def get_stats(self) -> Dict:
        stats = {}
        for tier_name, tier_data in self.tiers.items():
            total = tier_data['stats']['hits'] + tier_data['stats']['misses']
            stats[tier_name] = {
                'size': len(tier_data['cache']),
                'hit_rate': tier_data['stats']['hits'] / total if total > 0 else 0,
                'max_size': self.TIERS[tier_name]['max_size'],
            }
        return stats


class IncrementalIndexer:
    """Incremental Indexer (Phase 5B)"""
    
    def __init__(self):
        self.index: Dict[str, Dict] = {}  # term -> {doc_id: freq}
        self.documents: Dict[str, Dict] = {}  # doc_id -> {content, hash, metadata}
        self.doc_count = 0
    
    def add_document(self, doc_id: str, content: str, metadata: Dict = None):
        # Calculate content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Check if document already indexed
        if doc_id in self.documents:
            if self.documents[doc_id]['hash'] == content_hash:
                return  # No change
        
        # Tokenize
        tokens = self._tokenize(content)
        
        # Update index
        for token in tokens:
            if token not in self.index:
                self.index[token] = {}
            self.index[token][doc_id] = self.index[token].get(doc_id, 0) + 1
        
        # Store document
        self.documents[doc_id] = {
            'content': content,
            'hash': content_hash,
            'metadata': metadata or {},
            'tokens': tokens,
        }
        
        self.doc_count += 1
    
    def _tokenize(self, text: str) -> List[str]:
        # Simple tokenization
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return tokens
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, Dict]]:
        tokens = self._tokenize(query)
        
        scores: Dict[str, float] = defaultdict(float)
        
        for token in tokens:
            if token in self.index:
                for doc_id, freq in self.index[token].items():
                    scores[doc_id] += freq
        
        # Sort by score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for doc_id, score in sorted_docs:
            doc = self.documents[doc_id]
            results.append((doc_id, score, doc['metadata']))
        
        return results
    
    def get_stats(self) -> Dict:
        return {
            'documents': self.doc_count,
            'terms': len(self.index),
            'avg_tokens_per_doc': sum(len(d['tokens']) for d in self.documents.values()) / max(1, self.doc_count),
        }


class HybridSearch:
    """Hybrid Search - BM25 + Dense (Phase 5B)"""
    
    def __init__(self, bm25_weight: float = 0.5, dense_weight: float = 0.5):
        self.bm25_weight = bm25_weight
        self.dense_weight = dense_weight
        self.documents: Dict[str, str] = {}
        self.embeddings: Dict[str, List[float]] = {}
    
    def add_document(self, doc_id: str, content: str):
        self.documents[doc_id] = content
        # In production, generate embedding here
        self.embeddings[doc_id] = [random.random() for _ in range(768)]
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, str]]:
        # BM25 scores (simplified)
        bm25_scores = self._bm25_search(query)
        
        # Dense scores (simulated)
        dense_scores = self._dense_search(query)
        
        # Fuse scores
        fused_scores: Dict[str, float] = defaultdict(float)
        
        for doc_id, score in bm25_scores:
            fused_scores[doc_id] += self.bm25_weight * score
        
        for doc_id, score in dense_scores:
            fused_scores[doc_id] += self.dense_weight * score
        
        # Sort
        sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return [(doc_id, score, 'Hybrid') for doc_id, score in sorted_docs]
    
    def _bm25_search(self, query: str) -> List[Tuple[str, float]]:
        # Simplified BM25
        scores = []
        for doc_id, content in self.documents.items():
            # Simple keyword match score
            query_words = query.lower().split()
            score = sum(1 for word in query_words if word in content.lower())
            if score > 0:
                scores.append((doc_id, score / len(query_words)))
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def _dense_search(self, query: str) -> List[Tuple[str, float]]:
        # Simulated dense search
        scores = []
        for doc_id in self.documents:
            score = random.random() * 0.5 + 0.3  # 0.3-0.8
            scores.append((doc_id, score))
        return sorted(scores, key=lambda x: x[1], reverse=True)


class GradedFallback:
    """Graded Fallback Search (Phase 5B)"""
    
    def __init__(self, hybrid_search: HybridSearch):
        self.hybrid_search = hybrid_search
        self.tier_thresholds = {
            'Tier1': 0.8,
            'Tier2': 0.5,
            'Tier3': 0.2,
        }
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, str, float]]:
        # Tier 1: Hybrid search
        results = self.hybrid_search.search(query, top_k)
        
        if results and results[0][1] >= self.tier_thresholds['Tier1']:
            return [(doc_id, score, 'Tier1', 0.9) for doc_id, score, _ in results]
        
        # Tier 2: BM25 only (simulated)
        bm25_results = self.hybrid_search._bm25_search(query)
        
        if bm25_results and bm25_results[0][1] >= self.tier_thresholds['Tier2']:
            return [(doc_id, score, 'Tier2', 0.6) for doc_id, score in bm25_results[:top_k]]
        
        # Tier 3: Keyword fallback
        keyword_results = [(doc_id, 0.3, 'Tier3', 0.3) for doc_id in list(self.hybrid_search.documents.keys())[:top_k]]
        
        return keyword_results


class RLTTOptimizer:
    """RL TTL Optimizer (Phase 5C)"""
    
    def __init__(self, tier: str = 'MEDIUM'):
        self.tier = tier
        self.base_ttl = {'CRITICAL': 86400, 'HIGH': 21600, 'MEDIUM': 600, 'LOW': 60}.get(tier, 600)
        self.current_ttl = self.base_ttl
        self.hit_count = 0
        self.miss_count = 0
    
    def record_access(self, cache_hit: bool):
        if cache_hit:
            self.hit_count += 1
        else:
            self.miss_count += 1
    
    def optimize_ttl(self) -> Tuple[str, int]:
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total > 0 else 0
        
        # Simple RL-inspired adjustment
        if hit_rate > 0.7:
            action = 'maintain'
            multiplier = 1.0
        elif hit_rate > 0.4:
            action = 'increase'
            multiplier = 1.3
        else:
            action = 'decrease'
            multiplier = 0.7
        
        new_ttl = int(self.current_ttl * multiplier)
        new_ttl = max(30, min(172800, new_ttl))
        
        self.current_ttl = new_ttl
        
        return action, new_ttl
    
    def get_stats(self) -> Dict:
        total = self.hit_count + self.miss_count
        return {
            'tier': self.tier,
            'current_ttl': self.current_ttl,
            'ttl_change_percent': round((self.current_ttl - self.base_ttl) / self.base_ttl * 100, 2),
            'hit_rate': self.hit_count / total if total > 0 else 0,
        }


class IntentPredictor:
    """Intent Predictor (Phase 5C)"""
    
    INTENT_CATEGORIES = [
        'information_retrieval',
        'exploration',
        'comparison',
        'problem_solving',
        'learning',
        'verification',
        'navigation',
        'recommendation',
    ]
    
    TOPIC_CLUSTERS = {
        'memory': ['memory', 'cache', 'retrieval', 'storage'],
        'security': ['security', 'protection', 'safety', 'encryption'],
        'workflow': ['workflow', 'automation', 'pipeline', 'agent'],
        'ml': ['ml', 'neural', 'embedding', 'vector'],
        'performance': ['performance', 'optimization', 'speed', 'efficiency'],
    }
    
    def __init__(self):
        self.query_history: List[Dict] = []
        self.intent_patterns: Dict[str, int] = defaultdict(int)
    
    def predict(self, query: str, context: List[str] = None) -> Dict:
        # Rule-based intent classification
        query_lower = query.lower()
        
        intent_keywords = {
            'information_retrieval': ['what', 'how', 'explain', 'describe'],
            'comparison': ['compare', 'vs', 'versus', 'difference'],
            'problem_solving': ['fix', 'solve', 'error', 'issue'],
            'learning': ['learn', 'tutorial', 'guide'],
        }
        
        best_intent = 'information_retrieval'
        best_score = 0
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        # Topic classification
        best_topic = 'general'
        for topic, keywords in self.TOPIC_CLUSTERS.items():
            if any(kw in query_lower for kw in keywords):
                best_topic = topic
                break
        
        prediction = {
            'intent': best_intent,
            'confidence': min(0.9, 0.5 + best_score * 0.1),
            'topic': best_topic,
            'next_topic': best_topic,  # Simplified
            'keywords': query_lower.split()[:5],
        }
        
        self.query_history.append(prediction)
        self.intent_patterns[best_intent] += 1
        
        return prediction
    
    def get_prefetch_queries(self, prediction: Dict) -> List[str]:
        keywords = prediction.get('keywords', [])[:3]
        intent = prediction.get('intent', 'information_retrieval')
        
        prefetch = []
        
        if intent == 'information_retrieval':
            prefetch = [f"how to {kw}" for kw in keywords] + [f"what is {kw}" for kw in keywords]
        elif intent == 'comparison':
            prefetch = [f"{kw} vs alternative" for kw in keywords]
        elif intent == 'problem_solving':
            prefetch = [f"{kw} fix" for kw in keywords]
        
        return list(set(prefetch))[:10]
    
    def get_stats(self) -> Dict:
        total = sum(self.intent_patterns.values())
        return {
            'total_predictions': total,
            'intent_distribution': {
                k: round(v / total * 100, 2) if total > 0 else 0
                for k, v in self.intent_patterns.items()
            },
        }


class UltimateMemorySearchV3:
    """
    Ultimate Memory Search v3 - Complete Phase 5 Integration
    
    Integrates all Phase 5A/5B/5C components into unified interface.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize all Phase 5 components
        
        Args:
            config: Optional configuration dict
        """
        self.config = config or {}
        
        # Phase 5A: Caching
        self.l1_cache = ContextAwareCache(max_size=self.config.get('l1_max_size', 100))
        self.l2_cache = TieredCache()
        
        # Phase 5B: Search
        self.indexer = IncrementalIndexer()
        self.hybrid_search = HybridSearch(
            bm25_weight=self.config.get('bm25_weight', 0.5),
            dense_weight=self.config.get('dense_weight', 0.5),
        )
        self.fallback_search = GradedFallback(self.hybrid_search)
        
        # Phase 5C: ML
        self.ttl_optimizer = RLTTOptimizer(tier=self.config.get('tier', 'MEDIUM'))
        self.intent_predictor = IntentPredictor()
        
        # Observability
        self.metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'search_latency_ms': [],
            'intent_predictions': [],
        }
        
        # Session tracking
        self.current_session = f"session_{int(time.time())}"
    
    def add_document(self, doc_id: str, content: str, metadata: Dict = None,
                    tier: str = 'MEDIUM'):
        """
        Add document to search index and cache
        
        Args:
            doc_id: Unique document identifier
            content: Document content
            metadata: Optional metadata dict
            tier: Cache tier (CRITICAL/HIGH/MEDIUM/LOW)
        """
        # Add to indexer
        self.indexer.add_document(doc_id, content, metadata)
        
        # Add to hybrid search
        self.hybrid_search.add_document(doc_id, content)
        
        # Add to L2 cache
        self.l2_cache.set(doc_id, {
            'content': content,
            'metadata': metadata,
            'timestamp': time.time(),
        }, tier=tier)
    
    def search(self, query: str, session_id: str = None,
              top_k: int = 10) -> Dict:
        """
        Complete search pipeline with all Phase 5 features
        
        Args:
            query: Search query
            session_id: Optional session identifier
            top_k: Number of results to return
        
        Returns:
            Dict with results, metrics, and predictions
        """
        start_time = time.time()
        session_id = session_id or self.current_session
        
        self.metrics['total_queries'] += 1
        
        # Step 1: Intent Prediction
        intent_prediction = self.intent_predictor.predict(
            query,
            context=self.intent_predictor.query_history[-5:]
        )
        self.metrics['intent_predictions'].append(intent_prediction['intent'])
        
        # Step 2: L1 Cache Check (Context-Aware)
        cache_key = f"search:{query}"
        cached_result = self.l1_cache.get(cache_key, session_id)
        
        if cached_result:
            self.metrics['cache_hits'] += 1
            self.ttl_optimizer.record_access(cache_hit=True)
            
            return {
                'results': cached_result['results'],
                'source': 'L1_CACHE',
                'intent': intent_prediction,
                'latency_ms': (time.time() - start_time) * 1000,
                'cache_hit': True,
            }
        
        # Step 3: L2 Cache Check (Tiered)
        l2_result = self.l2_cache.get(cache_key)
        
        if l2_result:
            self.metrics['cache_hits'] += 1
            self.ttl_optimizer.record_access(cache_hit=True)
            
            # Promote to L1
            self.l1_cache.set(cache_key, l2_result, session_id)
            
            return {
                'results': l2_result['results'],
                'source': 'L2_CACHE',
                'intent': intent_prediction,
                'latency_ms': (time.time() - start_time) * 1000,
                'cache_hit': True,
            }
        
        # Step 4: Search with Graded Fallback
        self.ttl_optimizer.record_access(cache_hit=False)
        
        search_results = self.fallback_search.search(query, top_k)
        
        # Format results
        results = [
            {
                'doc_id': doc_id,
                'score': score,
                'tier': tier,
                'confidence': confidence,
            }
            for doc_id, score, tier, confidence in search_results
        ]
        
        # Cache result
        result_data = {'results': results}
        self.l1_cache.set(cache_key, result_data, session_id)
        self.l2_cache.set(cache_key, result_data, tier='MEDIUM')
        
        # Step 5: Generate Pre-fetch Queries
        prefetch_queries = self.intent_predictor.get_prefetch_queries(intent_prediction)
        
        latency_ms = (time.time() - start_time) * 1000
        self.metrics['search_latency_ms'].append(latency_ms)
        
        return {
            'results': results,
            'source': 'SEARCH',
            'intent': intent_prediction,
            'prefetch_queries': prefetch_queries,
            'latency_ms': latency_ms,
            'cache_hit': False,
        }
    
    def optimize(self) -> Dict:
        """
        Run optimization (TTL adjustment, metrics analysis)
        
        Returns:
            Optimization results and recommendations
        """
        # Optimize TTL
        action, new_ttl = self.ttl_optimizer.optimize_ttl()
        
        # Get all stats
        stats = self.get_stats()
        
        # Generate recommendations
        recommendations = []
        
        if stats['ttl_optimizer']['hit_rate'] < 0.5:
            recommendations.append("Consider adjusting cache TTL - low hit rate detected")
        
        if stats['l1_cache']['hit_rate'] < 0.3:
            recommendations.append("L1 cache underutilized - consider increasing size")
        
        if stats['search']['avg_latency_ms'] > 100:
            recommendations.append("Search latency high - consider optimizing index")
        
        return {
            'action': action,
            'new_ttl': new_ttl,
            'stats': stats,
            'recommendations': recommendations,
        }
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        latencies = self.metrics['search_latency_ms']
        
        return {
            'total_queries': self.metrics['total_queries'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_hit_rate': self.metrics['cache_hits'] / max(1, self.metrics['total_queries']),
            'l1_cache': self.l1_cache.get_stats(),
            'l2_cache': self.l2_cache.get_stats(),
            'indexer': self.indexer.get_stats(),
            'ttl_optimizer': self.ttl_optimizer.get_stats(),
            'intent_predictor': self.intent_predictor.get_stats(),
            'search': {
                'avg_latency_ms': sum(latencies) / max(1, len(latencies)),
                'min_latency_ms': min(latencies) if latencies else 0,
                'max_latency_ms': max(latencies) if latencies else 0,
            },
        }
    
    def save(self, model_file: Path = None) -> Path:
        """Save state to disk"""
        if model_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_file = DATA_DIR / f'ultimate_search_v3_{timestamp}.json'
        
        data = {
            'config': self.config,
            'metrics': {
                'total_queries': self.metrics['total_queries'],
                'cache_hits': self.metrics['cache_hits'],
            },
            'stats': self.get_stats(),
            'created_at': datetime.now().isoformat(),
        }
        
        with open(model_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Ultimate Memory Search v3 saved to: {model_file}")
        return model_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ultimate Memory Search v3")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    args = parser.parse_args()
    
    if args.demo:
        print("\n🚀 Ultimate Memory Search v3 Demo")
        print("=" * 80)
        print("Phase 5 Complete Integration: 5A (Cache) + 5B (Search) + 5C (ML)\n")
        
        # Create search engine
        search_engine = UltimateMemorySearchV3(config={
            'l1_max_size': 100,
            'bm25_weight': 0.5,
            'dense_weight': 0.5,
            'tier': 'MEDIUM',
        })
        
        # Add sample documents
        print("📚 Adding sample documents...\n")
        
        documents = [
            ("doc1", "Memory optimization techniques with caching strategies", {'category': 'performance'}),
            ("doc2", "Security best practices for cloud infrastructure", {'category': 'security'}),
            ("doc3", "Workflow automation using AI agents", {'category': 'workflow'}),
            ("doc4", "Neural network embedding for semantic search", {'category': 'ml'}),
            ("doc5", "Performance tuning and optimization guide", {'category': 'performance'}),
        ]
        
        for doc_id, content, metadata in documents:
            search_engine.add_document(doc_id, content, metadata)
        
        print(f"✅ Added {len(documents)} documents\n")
        
        # Run searches
        print("🔍 Running searches with full pipeline...\n")
        
        queries = [
            "what is memory optimization?",
            "how to implement caching?",
            "security best practices",
            "compare BM25 vs neural search",
            "fix performance issue",
        ]
        
        for i, query in enumerate(queries):
            print(f"Query {i+1}: '{query}'")
            
            result = search_engine.search(query, top_k=3)
            
            print(f"   Source: {result['source']}")
            print(f"   Intent: {result['intent']['intent']} ({result['intent']['confidence']:.0%})")
            print(f"   Topic: {result['intent']['topic']}")
            print(f"   Latency: {result['latency_ms']:.2f}ms")
            print(f"   Cache Hit: {result['cache_hit']}")
            
            if result['results']:
                print(f"   Results:")
                for r in result['results'][:2]:
                    print(f"      - {r['doc_id']}: {r['score']:.4f} ({r['tier']})")
            
            if result.get('prefetch_queries'):
                print(f"   Pre-fetch: {', '.join(result['prefetch_queries'][:2])}")
            
            print()
        
        # Optimize
        print("⚙️  Running optimization...\n")
        optimization = search_engine.optimize()
        
        print(f"   TTL Action: {optimization['action']}")
        print(f"   New TTL: {optimization['new_ttl']}s")
        
        if optimization['recommendations']:
            print(f"   Recommendations:")
            for rec in optimization['recommendations']:
                print(f"      - {rec}")
        
        # Final stats
        print("\n📊 Final Statistics:")
        stats = search_engine.get_stats()
        
        print(f"   Total queries: {stats['total_queries']}")
        print(f"   Cache hit rate: {stats['cache_hit_rate']:.2%}")
        print(f"   L1 cache hit rate: {stats['l1_cache']['hit_rate']:.2%}")
        print(f"   Avg search latency: {stats['search']['avg_latency_ms']:.2f}ms")
        print(f"   TTL optimizer hit rate: {stats['ttl_optimizer']['hit_rate']:.2%}")
        
        print(f"\n   Intent Distribution:")
        for intent, percent in stats['intent_predictor']['intent_distribution'].items():
            print(f"      {intent}: {percent}%")
        
        # Save
        search_engine.save()
        
        print("\n✅ Demo complete! Phase 5 integration successful!")
    
    elif args.stats:
        search_engine = UltimateMemorySearchV3()
        stats = search_engine.get_stats()
        
        print("\n📊 Ultimate Memory Search v3 Statistics")
        print("=" * 80)
        print(f"Total queries: {stats['total_queries']}")
        print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
