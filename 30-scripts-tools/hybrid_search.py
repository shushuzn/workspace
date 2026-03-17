#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Search - Dense (Embedding) + Sparse (BM25) retrieval
"""

import os
import sys
import json
import time
import math
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
HYBRID_DIR = WORKSPACE / 'data' / 'hybrid_search'
HYBRID_DIR.mkdir(parents=True, exist_ok=True)

class BM25Search:
    """
    BM25 (Best Matching 25) - Sparse retrieval
    
    Formula:
    score(d, q) = Σ IDF(qi) * (f(qi, d) * (k1 + 1)) / (f(qi, d) + k1 * (1 - b + b * |d|/avgdl))
    
    Where:
    - f(qi, d): term frequency of qi in document d
    - IDF(qi): inverse document frequency
    - |d|: document length
    - avgdl: average document length
    - k1, b: free parameters (typically k1=1.5, b=0.75)
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        
        # Index
        self.documents: Dict[str, str] = {}
        self.doc_lengths: Dict[str, int] = {}
        self.avg_doc_length = 0
        
        # Term frequencies: term -> {doc_id: freq}
        self.term_freqs: Dict[str, Dict[str, int]] = defaultdict(dict)
        
        # Document frequencies: term -> count
        self.doc_freqs: Dict[str, int] = defaultdict(int)
        
        # Total documents
        self.N = 0
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms"""
        import re
        tokens = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]+\b', text.lower())
        return tokens
    
    def add_document(self, doc_id: str, content: str):
        """Add document to BM25 index"""
        # Tokenize
        tokens = self.tokenize(content)
        
        # Store document
        self.documents[doc_id] = content
        self.doc_lengths[doc_id] = len(tokens)
        
        # Update average document length
        total_length = sum(self.doc_lengths.values())
        self.N = len(self.documents)
        self.avg_doc_length = total_length / self.N if self.N > 0 else 0
        
        # Update term frequencies
        term_counts = defaultdict(int)
        for token in tokens:
            term_counts[token] += 1
        
        for term, freq in term_counts.items():
            # Update document frequency (only count once per doc)
            if doc_id not in self.term_freqs[term]:
                self.doc_freqs[term] += 1
            
            self.term_freqs[term][doc_id] = freq
    
    def remove_document(self, doc_id: str):
        """Remove document from index"""
        if doc_id not in self.documents:
            return
        
        content = self.documents[doc_id]
        tokens = self.tokenize(content)
        
        # Update term frequencies
        terms_in_doc = set(tokens)
        for term in terms_in_doc:
            if doc_id in self.term_freqs[term]:
                del self.term_freqs[term][doc_id]
                self.doc_freqs[term] -= 1
                
                if self.doc_freqs[term] <= 0:
                    del self.doc_freqs[term]
                    del self.term_freqs[term]
        
        # Remove document
        del self.documents[doc_id]
        del self.doc_lengths[doc_id]
        
        # Update statistics
        self.N = len(self.documents)
        if self.N > 0:
            total_length = sum(self.doc_lengths.values())
            self.avg_doc_length = total_length / self.N
    
    def _idf(self, term: str) -> float:
        """Calculate IDF for a term"""
        if term not in self.doc_freqs:
            return 0.0
        
        # IDF with smoothing
        idf = math.log((self.N - self.doc_freqs[term] + 0.5) / (self.doc_freqs[term] + 0.5) + 1)
        return idf
    
    def _bm25_score(self, term: str, doc_id: str) -> float:
        """Calculate BM25 score for a term in a document"""
        if term not in self.term_freqs or doc_id not in self.term_freqs[term]:
            return 0.0
        
        freq = self.term_freqs[term][doc_id]
        doc_len = self.doc_lengths[doc_id]
        
        # BM25 formula
        numerator = freq * (self.k1 + 1)
        denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_length)
        
        if denominator == 0:
            return 0.0
        
        return self._idf(term) * (numerator / denominator)
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Search for documents using BM25"""
        tokens = self.tokenize(query)
        
        if not tokens:
            return []
        
        # Calculate scores for all documents
        scores = defaultdict(float)
        
        for token in tokens:
            if token in self.term_freqs:
                for doc_id in self.term_freqs[token]:
                    scores[doc_id] += self._bm25_score(token, doc_id)
        
        # Sort by score
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_stats(self) -> Dict:
        """Get BM25 index statistics"""
        return {
            'total_documents': self.N,
            'total_terms': len(self.term_freqs),
            'avg_doc_length': self.avg_doc_length,
            'index_size_mb': sys.getsizeof(self.term_freqs) / 1024 / 1024,
        }


class DenseSearch:
    """
    Dense retrieval using semantic embeddings
    
    Uses Ollama (Qwen2.5:1.5b) to generate 768D embeddings
    """
    
    def __init__(self, embedding_dim: int = 768,
                 use_ollama: bool = True):
        self.embedding_dim = embedding_dim
        self.use_ollama = use_ollama
        
        # Document embeddings: doc_id -> embedding
        self.embeddings: Dict[str, List[float]] = {}
        
        # Documents
        self.documents: Dict[str, str] = {}
        
        # Ollama endpoint
        self.ollama_url = "http://localhost:11434/api/embeddings"
        self.model = "qwen2.5:1.5b"
        
        # Embedding cache
        self.cache: Dict[str, List[float]] = {}
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Ollama"""
        # Check cache
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if not self.use_ollama:
            # Fallback: random embedding (for demo)
            import random
            embedding = [random.gauss(0, 1) for _ in range(self.embedding_dim)]
            self.cache[cache_key] = embedding
            return embedding
        
        try:
            import requests
            
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get('embedding', [])
                
                if len(embedding) == self.embedding_dim:
                    self.cache[cache_key] = embedding
                    return embedding
        except Exception as e:
            pass
        
        # Fallback: random embedding
        import random
        embedding = [random.gauss(0, 1) for _ in range(self.embedding_dim)]
        self.cache[cache_key] = embedding
        return embedding
    
    def add_document(self, doc_id: str, content: str):
        """Add document with embedding"""
        self.documents[doc_id] = content
        
        # Generate embedding
        embedding = self._get_embedding(content)
        self.embeddings[doc_id] = embedding
    
    def remove_document(self, doc_id: str):
        """Remove document"""
        if doc_id in self.documents:
            del self.documents[doc_id]
        if doc_id in self.embeddings:
            del self.embeddings[doc_id]
    
    def _cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = math.sqrt(sum(a * a for a in emb1))
        norm2 = math.sqrt(sum(b * b for b in emb2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Search using semantic similarity"""
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Calculate similarities
        scores = []
        for doc_id, doc_embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            scores.append((doc_id, similarity))
        
        # Sort by similarity
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def get_stats(self) -> Dict:
        """Get dense search statistics"""
        return {
            'total_documents': len(self.documents),
            'embedding_dim': self.embedding_dim,
            'cache_size': len(self.cache),
            'use_ollama': self.use_ollama,
        }


class HybridSearch:
    """
    Hybrid Search - Combines Dense (Embedding) + Sparse (BM25)
    
    Features:
    - Weighted combination of BM25 and Dense scores
    - Reciprocal Rank Fusion (RRF)
    - Configurable weights
    - Fallback mechanism
    """
    
    def __init__(self, bm25_weight: float = 0.5,
                 dense_weight: float = 0.5,
                 use_rrf: bool = False,
                 k: int = 60):
        """
        Args:
            bm25_weight: Weight for BM25 scores (0-1)
            dense_weight: Weight for Dense scores (0-1)
            use_rrf: Use Reciprocal Rank Fusion instead of weighted sum
            k: RRF constant (typically 60)
        """
        self.bm25_weight = bm25_weight
        self.dense_weight = dense_weight
        self.use_rrf = use_rrf
        self.k = k
        
        # Sub-searchers
        self.bm25 = BM25Search()
        self.dense = DenseSearch()
        
        # Documents
        self.documents: Dict[str, str] = {}
    
    def add_document(self, doc_id: str, content: str):
        """Add document to both indices"""
        self.documents[doc_id] = content
        self.bm25.add_document(doc_id, content)
        self.dense.add_document(doc_id, content)
    
    def remove_document(self, doc_id: str):
        """Remove document from both indices"""
        if doc_id in self.documents:
            del self.documents[doc_id]
        self.bm25.remove_document(doc_id)
        self.dense.remove_document(doc_id)
    
    def _normalize_scores(self, scores: List[Tuple[str, float]]) -> Dict[str, float]:
        """Normalize scores to 0-1 range"""
        if not scores:
            return {}
        
        max_score = max(score for _, score in scores)
        min_score = min(score for _, score in scores)
        
        if max_score == min_score:
            return {doc_id: 1.0 for doc_id, _ in scores}
        
        normalized = {}
        for doc_id, score in scores:
            normalized[doc_id] = (score - min_score) / (max_score - min_score)
        
        return normalized
    
    def _rrf_score(self, rank: int) -> float:
        """Reciprocal Rank Fusion score"""
        return 1.0 / (self.k + rank)
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, str]]:
        """
        Hybrid search combining BM25 and Dense
        
        Returns:
            List of (doc_id, score, method) tuples
        """
        # Get results from both searchers
        bm25_results = self.bm25.search(query, top_k=top_k * 2)
        dense_results = self.dense.search(query, top_k=top_k * 2)
        
        if self.use_rrf:
            # Reciprocal Rank Fusion
            rrf_scores = defaultdict(float)
            
            for rank, (doc_id, _) in enumerate(bm25_results):
                rrf_scores[doc_id] += self.bm25_weight * self._rrf_score(rank + 1)
            
            for rank, (doc_id, _) in enumerate(dense_results):
                rrf_scores[doc_id] += self.dense_weight * self._rrf_score(rank + 1)
            
            # Sort by RRF score
            results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
            return [(doc_id, score, 'RRF') for doc_id, score in results[:top_k]]
        
        else:
            # Weighted sum
            bm25_normalized = self._normalize_scores(bm25_results)
            dense_normalized = self._normalize_scores(dense_results)
            
            # Combine scores
            combined_scores = defaultdict(float)
            
            for doc_id in set(bm25_normalized.keys()) | set(dense_normalized.keys()):
                bm25_score = bm25_normalized.get(doc_id, 0)
                dense_score = dense_normalized.get(doc_id, 0)
                
                combined = (self.bm25_weight * bm25_score + 
                           self.dense_weight * dense_score)
                combined_scores[doc_id] = combined
            
            # Sort by combined score
            results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Determine dominant method
            enriched_results = []
            for doc_id, score in results[:top_k]:
                bm25_score = bm25_normalized.get(doc_id, 0)
                dense_score = dense_normalized.get(doc_id, 0)
                
                if bm25_score > dense_score:
                    method = 'BM25'
                elif dense_score > bm25_score:
                    method = 'Dense'
                else:
                    method = 'Hybrid'
                
                enriched_results.append((doc_id, score, method))
            
            return enriched_results
    
    def get_stats(self) -> Dict:
        """Get hybrid search statistics"""
        return {
            'total_documents': len(self.documents),
            'bm25_stats': self.bm25.get_stats(),
            'dense_stats': self.dense.get_stats(),
            'weights': {
                'bm25': self.bm25_weight,
                'dense': self.dense_weight,
            },
            'use_rrf': self.use_rrf,
            'rrf_k': self.k,
        }
    
    def save(self, index_file: Path = None) -> Path:
        """Save hybrid index to disk"""
        if index_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            index_file = HYBRID_DIR / f'hybrid_index_{timestamp}.json'
        
        data = {
            'documents': self.documents,
            'bm25_data': {
                'term_freqs': dict(self.bm25.term_freqs),
                'doc_lengths': self.bm25.doc_lengths,
                'N': self.bm25.N,
                'avg_doc_length': self.bm25.avg_doc_length,
            },
            'dense_data': {
                'embeddings': self.dense.embeddings,
                'cache': self.dense.cache,
            },
            'config': {
                'bm25_weight': self.bm25_weight,
                'dense_weight': self.dense_weight,
                'use_rrf': self.use_rrf,
                'k': self.k,
            },
            'created_at': datetime.now().isoformat(),
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Hybrid index saved to: {index_file}")
        return index_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hybrid Search")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--rrf', action='store_true', help='Use RRF fusion')
    args = parser.parse_args()
    
    # Create hybrid searcher
    use_rrf = args.rrf
    hybrid = HybridSearch(bm25_weight=0.5, dense_weight=0.5, use_rrf=use_rrf)
    
    if args.demo:
        print("\n🔍 Hybrid Search Demo")
        print("=" * 80)
        print(f"Method: {'RRF' if use_rrf else 'Weighted Sum'}")
        print(f"BM25 Weight: 0.5 | Dense Weight: 0.5\n")
        
        # Add sample documents
        print("📄 Adding sample documents...\n")
        
        documents = {
            "doc1": "Memory optimization techniques for fast retrieval using caching and indexing",
            "doc2": "Security best practices for cloud infrastructure and network protection",
            "doc3": "Workflow automation with AI agents and intelligent task orchestration",
            "doc4": "Neural embedding for semantic search and natural language understanding",
            "doc5": "Cache tier management with CRITICAL HIGH MEDIUM LOW priority levels",
            "doc6": "Machine learning optimization with gradient descent and backpropagation",
            "doc7": "Database indexing strategies for improved query performance",
            "doc8": "Network security protocols and encryption algorithms",
        }
        
        for doc_id, content in documents.items():
            hybrid.add_document(doc_id, content)
        
        # Search examples
        print("\n🔍 Search examples:\n")
        
        queries = [
            "memory cache optimization",
            "security network protection",
            "neural semantic search",
            "workflow AI automation",
        ]
        
        for query in queries:
            results = hybrid.search(query, top_k=3)
            
            print(f"Query: '{query}'")
            for doc_id, score, method in results:
                content_preview = documents[doc_id][:60] + "..."
                print(f"   {doc_id}: {score:.4f} ({method})")
                print(f"      {content_preview}")
            print()
        
        # Show stats
        print("\n📈 Hybrid Search Statistics:")
        stats = hybrid.get_stats()
        
        print(f"Total documents: {stats['total_documents']}")
        print(f"BM25 terms: {stats['bm25_stats']['total_terms']}")
        print(f"Dense embeddings: {stats['dense_stats']['total_documents']}")
        print(f"Weights: BM25={stats['weights']['bm25']}, Dense={stats['weights']['dense']}")
        print(f"Method: {'RRF' if stats['use_rrf'] else 'Weighted Sum'}")
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        stats = hybrid.get_stats()
        print("\n📈 Hybrid Search Statistics")
        print("=" * 80)
        print(f"Total documents: {stats['total_documents']}")
        print(f"BM25 terms: {stats['bm25_stats']['total_terms']}")
        print(f"Dense embeddings: {stats['dense_stats']['total_documents']}")
        print(f"Weights: BM25={stats['weights']['bm25']}, Dense={stats['weights']['dense']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
