#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graded Fallback - Confidence-based degradation with 3-tier fallback
"""

import os
import sys
import json
import time
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
FALLBACK_DIR = WORKSPACE / 'data' / 'graded_fallback'
FALLBACK_DIR.mkdir(parents=True, exist_ok=True)

class GradedFallbackSearch:
    """
    Graded Fallback Search - Confidence-based degradation
    
    3-Tier Fallback Strategy:
    1. Tier 1 (High Confidence): Hybrid Search (BM25 + Dense) - Target: >0.8
    2. Tier 2 (Medium Confidence): BM25 Only - Target: >0.5
    3. Tier 3 (Low Confidence): Keyword Match + Expansion - Target: >0.2
    
    Features:
    - Confidence scoring per tier
    - Automatic fallback when confidence < threshold
    - Query expansion for low confidence
    - Result fusion across tiers
    - Performance tracking
    """
    
    # Confidence thresholds
    TIER1_THRESHOLD = 0.8  # High confidence
    TIER2_THRESHOLD = 0.5  # Medium confidence
    TIER3_THRESHOLD = 0.2  # Low confidence
    
    def __init__(self, 
                 tier1_weight: float = 1.0,
                 tier2_weight: float = 0.7,
                 tier3_weight: float = 0.4,
                 enable_expansion: bool = True,
                 max_expansion_terms: int = 5):
        """
        Args:
            tier1_weight: Weight for Tier 1 results
            tier2_weight: Weight for Tier 2 results
            tier3_weight: Weight for Tier 3 results
            enable_expansion: Enable query expansion for Tier 3
            max_expansion_terms: Maximum expansion terms to add
        """
        self.tier1_weight = tier1_weight
        self.tier2_weight = tier2_weight
        self.tier3_weight = tier3_weight
        self.enable_expansion = enable_expansion
        self.max_expansion_terms = max_expansion_terms
        
        # Tier 1: Hybrid search (BM25 + Dense)
        from hybrid_search import HybridSearch
        self.tier1_search = HybridSearch(bm25_weight=0.5, dense_weight=0.5)
        
        # Tier 2: BM25 only (faster, less accurate)
        from hybrid_search import BM25Search
        self.tier2_search = BM25Search()
        
        # Tier 3: Simple keyword match with expansion
        self.tier3_index: Dict[str, List[str]] = defaultdict(list)  # term -> [doc_ids]
        self.documents: Dict[str, str] = {}
        
        # Statistics
        self.stats = {
            'tier1_queries': 0,
            'tier2_queries': 0,
            'tier3_queries': 0,
            'tier1_avg_confidence': 0.0,
            'tier2_avg_confidence': 0.0,
            'tier3_avg_confidence': 0.0,
            'fallback_count': 0,
        }
        
        # Query expansion synonyms (simple version)
        self.synonyms = {
            'memory': ['cache', 'retrieval', 'storage'],
            'security': ['protection', 'safety', 'defense'],
            'optimization': ['improvement', 'enhancement', 'tuning'],
            'search': ['query', 'lookup', 'retrieval'],
            'neural': ['embedding', 'semantic', 'vector'],
            'workflow': ['automation', 'pipeline', 'orchestration'],
        }
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        import re
        tokens = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]+\b', text.lower())
        return tokens
    
    def add_document(self, doc_id: str, content: str):
        """Add document to all tiers"""
        self.documents[doc_id] = content
        
        # Tier 1: Hybrid
        self.tier1_search.add_document(doc_id, content)
        
        # Tier 2: BM25
        self.tier2_search.add_document(doc_id, content)
        
        # Tier 3: Keyword index
        tokens = self.tokenize(content)
        for token in set(tokens):
            if doc_id not in self.tier3_index[token]:
                self.tier3_index[token].append(doc_id)
    
    def _calculate_confidence(self, score: float, max_score: float) -> float:
        """Calculate confidence score (0-1)"""
        if max_score == 0:
            return 0.0
        return min(1.0, score / max_score)
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms"""
        if not self.enable_expansion:
            return [query]
        
        tokens = self.tokenize(query)
        expanded = set(tokens)
        
        for token in tokens:
            if token in self.synonyms:
                for synonym in self.synonyms[token][:self.max_expansion_terms]:
                    expanded.add(synonym)
        
        return list(expanded)
    
    def _tier1_search(self, query: str, top_k: int = 10) -> Tuple[List[Tuple], float]:
        """Tier 1: Hybrid search"""
        results = self.tier1_search.search(query, top_k=top_k)
        
        if not results:
            return [], 0.0
        
        # Calculate confidence based on top score
        max_possible_score = 1.0  # Normalized
        top_score = results[0][1] if results else 0.0
        confidence = self._calculate_confidence(top_score, max_possible_score)
        
        self.stats['tier1_queries'] += 1
        self._update_avg_confidence('tier1', confidence)
        
        return results, confidence
    
    def _tier2_search(self, query: str, top_k: int = 10) -> Tuple[List[Tuple], float]:
        """Tier 2: BM25 only"""
        results = self.tier2_search.search(query, top_k=top_k)
        
        if not results:
            return [], 0.0
        
        # Calculate confidence
        max_possible_score = 10.0  # BM25 typical max
        top_score = results[0][1] if results else 0.0
        confidence = self._calculate_confidence(top_score, max_possible_score)
        
        self.stats['tier2_queries'] += 1
        self._update_avg_confidence('tier2', confidence)
        
        return results, confidence
    
    def _tier3_search(self, query: str, top_k: int = 10) -> Tuple[List[Tuple], float]:
        """Tier 3: Keyword match with expansion"""
        # Expand query
        expanded_terms = self._expand_query(query)
        
        # Count document matches
        doc_scores = defaultdict(int)
        
        for term in expanded_terms:
            if term in self.tier3_index:
                for doc_id in self.tier3_index[term]:
                    doc_scores[doc_id] += 1
        
        # Convert to sorted results
        results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        results = [(doc_id, float(score)) for doc_id, score in results[:top_k]]
        
        # Calculate confidence
        max_possible_score = len(expanded_terms)
        top_score = results[0][1] if results else 0.0
        confidence = self._calculate_confidence(top_score, max_possible_score)
        
        self.stats['tier3_queries'] += 1
        self._update_avg_confidence('tier3', confidence)
        
        return results, confidence
    
    def _update_avg_confidence(self, tier: str, confidence: float):
        """Update running average confidence for tier"""
        key = f'{tier}_avg_confidence'
        count_key = f'{tier}_queries'
        
        count = self.stats[count_key]
        old_avg = self.stats[key]
        
        # Running average
        new_avg = ((old_avg * (count - 1)) + confidence) / count
        self.stats[key] = new_avg
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, str, int]]:
        """
        Graded fallback search
        
        Returns:
            List of (doc_id, score, tier_used, confidence) tuples
        """
        # Try Tier 1 first (Hybrid)
        tier1_results, tier1_confidence = self._tier1_search(query, top_k=top_k)
        
        if tier1_confidence >= self.TIER1_THRESHOLD:
            # High confidence - return Tier 1 results
            return [
                (doc_id, score * self.tier1_weight, 'Tier1', tier1_confidence)
                for doc_id, score, _ in tier1_results
            ]
        
        # Tier 1 confidence too low - try Tier 2
        tier2_results, tier2_confidence = self._tier2_search(query, top_k=top_k)
        
        if tier2_confidence >= self.TIER2_THRESHOLD:
            # Medium confidence - fuse Tier 1 and Tier 2
            self.stats['fallback_count'] += 1
            
            # Combine results
            combined = self._fuse_results([
                (tier1_results, self.tier1_weight, 'Tier1'),
                (tier2_results, self.tier2_weight, 'Tier2'),
            ], top_k=top_k)
            
            return [
                (doc_id, score, tier, max(tier1_confidence, tier2_confidence))
                for doc_id, score, tier in combined
            ]
        
        # Tier 2 confidence too low - try Tier 3
        tier3_results, tier3_confidence = self._tier3_search(query, top_k=top_k)
        
        # Low confidence - fuse all tiers
        self.stats['fallback_count'] += 1
        
        combined = self._fuse_results([
            (tier1_results, self.tier1_weight, 'Tier1'),
            (tier2_results, self.tier2_weight, 'Tier2'),
            (tier3_results, self.tier3_weight, 'Tier3'),
        ], top_k=top_k)
        
        return [
            (doc_id, score, tier, max(tier1_confidence, tier2_confidence, tier3_confidence))
            for doc_id, score, tier in combined
        ]
    
    def _fuse_results(self, tier_results: List, top_k: int = 10) -> List[Tuple[str, float, str]]:
        """Fuse results from multiple tiers"""
        combined_scores = defaultdict(lambda: {'score': 0.0, 'tiers': set()})
        
        for results, weight, tier_name in tier_results:
            for doc_id, score, *_ in results:
                combined_scores[doc_id]['score'] += score * weight
                combined_scores[doc_id]['tiers'].add(tier_name)
        
        # Sort by combined score
        fused = [
            (doc_id, data['score'], '/'.join(sorted(data['tiers'])))
            for doc_id, data in combined_scores.items()
        ]
        
        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:top_k]
    
    def get_stats(self) -> Dict:
        """Get search statistics"""
        return {
            'total_documents': len(self.documents),
            'tier_usage': {
                'tier1': self.stats['tier1_queries'],
                'tier2': self.stats['tier2_queries'],
                'tier3': self.stats['tier3_queries'],
            },
            'avg_confidence': {
                'tier1': round(self.stats['tier1_avg_confidence'], 4),
                'tier2': round(self.stats['tier2_avg_confidence'], 4),
                'tier3': round(self.stats['tier3_avg_confidence'], 4),
            },
            'fallback_count': self.stats['fallback_count'],
            'fallback_rate': round(
                self.stats['fallback_count'] / 
                max(1, self.stats['tier1_queries']) * 100, 2
            ),
            'expansion_enabled': self.enable_expansion,
        }
    
    def save(self, index_file: Path = None) -> Path:
        """Save index to disk"""
        if index_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            index_file = FALLBACK_DIR / f'graded_fallback_index_{timestamp}.json'
        
        data = {
            'documents': self.documents,
            'tier3_index': dict(self.tier3_index),
            'stats': self.stats,
            'config': {
                'tier1_weight': self.tier1_weight,
                'tier2_weight': self.tier2_weight,
                'tier3_weight': self.tier3_weight,
                'enable_expansion': self.enable_expansion,
            },
            'created_at': datetime.now().isoformat(),
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Graded fallback index saved to: {index_file}")
        return index_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Graded Fallback Search")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--no-expansion', action='store_true', help='Disable query expansion')
    args = parser.parse_args()
    
    # Create searcher
    enable_expansion = not args.no_expansion
    searcher = GradedFallbackSearch(enable_expansion=enable_expansion)
    
    if args.demo:
        print("\n🎯 Graded Fallback Search Demo")
        print("=" * 80)
        print(f"Query Expansion: {'Enabled' if enable_expansion else 'Disabled'}\n")
        
        # Add sample documents
        print("📄 Adding sample documents...\n")
        
        documents = {
            "doc1": "Memory optimization with caching strategies for fast data retrieval",
            "doc2": "Network security protocols and firewall configuration best practices",
            "doc3": "AI workflow automation using intelligent agents and task orchestration",
            "doc4": "Semantic search with neural embeddings and vector similarity",
            "doc5": "Database performance tuning and query optimization techniques",
            "doc6": "Cloud infrastructure security and access control management",
            "doc7": "Machine learning pipeline automation and model deployment",
            "doc8": "Distributed caching systems and memory management",
        }
        
        for doc_id, content in documents.items():
            searcher.add_document(doc_id, content)
        
        # Search examples
        print("\n🔍 Search examples:\n")
        
        queries = [
            "memory cache optimization",      # Should hit Tier 1
            "security firewall",               # Should hit Tier 1-2
            "AI automation workflow",          # Should hit Tier 1
            "database tuning",                 # May need Tier 2-3
            "unknown topic xyz",               # Will fallback to Tier 3
        ]
        
        for query in queries:
            results = searcher.search(query, top_k=3)
            
            print(f"Query: '{query}'")
            for doc_id, score, tier, confidence in results:
                content_preview = documents[doc_id][:50] + "..."
                tier_indicator = "🟢" if tier == "Tier1" else "🟡" if tier == "Tier2" else "🔴"
                print(f"   {tier_indicator} {doc_id}: {score:.4f} ({tier}, conf: {confidence:.2f})")
                print(f"      {content_preview}")
            print()
        
        # Show stats
        print("\n📈 Graded Fallback Statistics:")
        stats = searcher.get_stats()
        
        print(f"Total documents: {stats['total_documents']}")
        print(f"\nTier Usage:")
        print(f"   Tier 1 (Hybrid): {stats['tier_usage']['tier1']} queries")
        print(f"   Tier 2 (BM25): {stats['tier_usage']['tier2']} queries")
        print(f"   Tier 3 (Keyword): {stats['tier_usage']['tier3']} queries")
        
        print(f"\nAverage Confidence:")
        print(f"   Tier 1: {stats['avg_confidence']['tier1']}")
        print(f"   Tier 2: {stats['avg_confidence']['tier2']}")
        print(f"   Tier 3: {stats['avg_confidence']['tier3']}")
        
        print(f"\nFallback Rate: {stats['fallback_rate']}%")
        print(f"Fallback Count: {stats['fallback_count']}")
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        stats = searcher.get_stats()
        print("\n📈 Graded Fallback Statistics")
        print("=" * 80)
        print(f"Total documents: {stats['total_documents']}")
        print(f"Fallback rate: {stats['fallback_rate']}%")
        print(f"Tier 1 avg confidence: {stats['avg_confidence']['tier1']}")
        print(f"Tier 2 avg confidence: {stats['avg_confidence']['tier2']}")
        print(f"Tier 3 avg confidence: {stats['avg_confidence']['tier3']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
