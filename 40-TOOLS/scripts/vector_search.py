#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Search - Lightweight embedding-based semantic search
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import math

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
VECTOR_DIR = WORKSPACE / 'data' / 'vector_search'
VECTOR_DIR.mkdir(parents=True, exist_ok=True)

class SimpleVectorizer:
    """
    Lightweight TF-IDF based vectorization
    No external dependencies, pure Python
    """
    
    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.documents: List[Dict] = []
        self.doc_vectors: Dict[str, List[float]] = {}
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Simple tokenization
        text = text.lower()
        tokens = text.split()
        
        # Remove stopwords and short tokens
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'again', 'further', 'then', 'once',
            'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
            'neither', 'not', 'only', 'own', 'same', 'than', 'too',
            'very', 'just', 'also', 'now', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'each', 'every', 'both',
            'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'any', 'this', 'that', 'these', 'those', 'what', 'which'
        }
        
        tokens = [
            t for t in tokens
            if len(t) > 2 and t not in stopwords
        ]
        
        return tokens
    
    def fit(self, documents: List[Dict]):
        """
        Fit vectorizer on documents
        
        Args:
            documents: List of dicts with 'text' and 'id' keys
        """
        self.documents = documents
        self.vocabulary = {}
        self.idf = {}
        self.doc_vectors = {}
        
        # Build vocabulary
        term_freq = defaultdict(set)  # term -> set of doc_ids
        
        for doc in documents:
            doc_id = doc.get('id', str(len(self.documents)))
            text = doc.get('text', '')
            
            tokens = self._tokenize(text)
            
            for token in set(tokens):
                term_freq[token].add(doc_id)
        
        # Assign vocabulary indices
        for i, term in enumerate(sorted(term_freq.keys())):
            self.vocabulary[term] = i
        
        # Calculate IDF
        n_docs = len(documents)
        for term, doc_ids in term_freq.items():
            df = len(doc_ids)
            self.idf[term] = math.log((n_docs + 1) / (df + 1)) + 1
        
        # Calculate document vectors
        for doc in documents:
            doc_id = doc.get('id', str(len(self.documents)))
            text = doc.get('text', '')
            
            vector = self._transform_single(text)
            self.doc_vectors[doc_id] = vector
        
        print(f"✅ Vectorizer fitted: {len(self.vocabulary)} terms, {len(documents)} docs")
    
    def _transform_single(self, text: str) -> List[float]:
        """Transform single text to TF-IDF vector"""
        tokens = self._tokenize(text)
        
        # Calculate TF
        tf = defaultdict(int)
        for token in tokens:
            tf[token] += 1
        
        # Normalize TF
        max_freq = max(tf.values()) if tf else 1
        tf = {k: v / max_freq for k, v in tf.items()}
        
        # Create vector
        vector = [0.0] * len(self.vocabulary)
        
        for term, freq in tf.items():
            if term in self.vocabulary:
                idx = self.vocabulary[term]
                idf = self.idf.get(term, 1.0)
                vector[idx] = freq * idf
        
        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not v1 or not v2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Search documents by query
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            List of (doc_id, similarity_score) tuples
        """
        # Transform query to vector
        query_vector = self._transform_single(query)
        
        # Calculate similarities
        similarities = []
        
        for doc_id, doc_vector in self.doc_vectors.items():
            sim = self.cosine_similarity(query_vector, doc_vector)
            if sim > 0:
                similarities.append((doc_id, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def save(self, path: Path = None):
        """Save vectorizer state"""
        if path is None:
            path = VECTOR_DIR / 'vectorizer.json'
        
        data = {
            'vocabulary': self.vocabulary,
            'idf': self.idf,
            'doc_vectors': self.doc_vectors,
            'documents': self.documents,
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Vectorizer saved: {path}")
    
    def load(self, path: Path = None):
        """Load vectorizer state"""
        if path is None:
            path = VECTOR_DIR / 'vectorizer.json'
        
        if not path.exists():
            return False
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.vocabulary = data.get('vocabulary', {})
        self.idf = data.get('idf', {})
        self.doc_vectors = data.get('doc_vectors', {})
        self.documents = data.get('documents', [])
        
        print(f"✅ Vectorizer loaded: {len(self.vocabulary)} terms")
        return True


class VectorSearch:
    """
    Production-ready vector search with caching
    """
    
    def __init__(self):
        self.vectorizer = SimpleVectorizer()
        self.cache: Dict[str, List[Tuple[str, float]]] = {}
        self.cache_ttl: Dict[str, float] = {}
        self.loaded = False
    
    def index_documents(self, documents: List[Dict], cache_time: int = 3600):
        """
        Index documents for vector search
        
        Args:
            documents: List of dicts with 'id', 'text', 'metadata'
            cache_time: Cache TTL in seconds
        """
        # Fit vectorizer
        self.vectorizer.fit(documents)
        self.vectorizer.save()
        
        # Clear cache
        self.cache.clear()
        self.cache_ttl.clear()
        
        self.loaded = True
        print(f"✅ Indexed {len(documents)} documents")
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self.cache_ttl:
            return False
        
        return time.time() < self.cache_ttl[cache_key]
    
    def search(self, query: str, top_k: int = 10, 
               use_cache: bool = True) -> List[Dict]:
        """
        Search using vector similarity
        
        Args:
            query: Search query
            top_k: Number of results
            use_cache: Use cached results
        
        Returns:
            List of results with metadata
        """
        import time
        
        if not self.loaded:
            # Try to load
            if self.vectorizer.load():
                self.loaded = True
            else:
                print("⚠️  Vectorizer not loaded. Call index_documents first.")
                return []
        
        # Check cache
        cache_key = self._get_cache_key(query)
        
        if use_cache and self._is_cache_valid(cache_key):
            cached_results = self.cache[cache_key]
            return self._format_results(cached_results, top_k)
        
        # Perform search
        start_time = time.time()
        similarities = self.vectorizer.search(query, top_k=top_k)
        search_time = (time.time() - start_time) * 1000
        
        # Format results
        results = self._format_results(similarities, top_k)
        
        # Cache results
        self.cache[cache_key] = similarities
        self.cache_ttl[cache_key] = time.time() + 300  # 5 min TTL
        
        # Add timing info
        for result in results:
            result['search_time_ms'] = search_time
        
        return results
    
    def _format_results(self, similarities: List[Tuple[str, float]], 
                       top_k: int) -> List[Dict]:
        """Format search results"""
        results = []
        
        for doc_id, score in similarities[:top_k]:
            # Find document metadata
            doc = next(
                (d for d in self.vectorizer.documents if d.get('id') == doc_id),
                None
            )
            
            if doc:
                results.append({
                    'id': doc_id,
                    'score': round(score, 4),
                    'title': doc.get('title', 'N/A'),
                    'content': doc.get('text', '')[:200],
                    'metadata': doc.get('metadata', {}),
                })
        
        return results
    
    def get_stats(self) -> Dict:
        """Get search statistics"""
        return {
            'documents_indexed': len(self.vectorizer.documents),
            'vocabulary_size': len(self.vectorizer.vocabulary),
            'cache_size': len(self.cache),
            'loaded': self.loaded,
        }


def main():
    import argparse
    import time
    
    parser = argparse.ArgumentParser(description="Vector Search")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--search', type=str, help='Search query')
    args = parser.parse_args()
    
    search_engine = VectorSearch()
    
    if args.demo:
        print("\n🔍 Vector Search Demo")
        print("=" * 80)
        
        # Sample documents
        documents = [
            {
                'id': 'doc_1',
                'title': 'Memory Evolution Engine',
                'text': 'Memory evolution engine provides automatic quality scoring and forgetting mechanism for long-term memory management',
                'metadata': {'source': 'MEMORY.md'}
            },
            {
                'id': 'doc_2',
                'title': 'Security Configuration',
                'text': 'Security configuration includes API keys, authentication tokens, and access control policies',
                'metadata': {'source': 'config.json'}
            },
            {
                'id': 'doc_3',
                'title': 'Workflow Automation',
                'text': 'Workflow automation enables automatic execution of tasks through predefined pipelines and triggers',
                'metadata': {'source': 'workflows.yaml'}
            },
            {
                'id': 'doc_4',
                'title': 'Query Prediction',
                'text': 'Query prediction uses machine learning to anticipate user search queries based on historical patterns',
                'metadata': {'source': 'ml_models.json'}
            },
        ]
        
        print("\n📚 Indexing documents...")
        search_engine.index_documents(documents)
        
        # Test searches
        test_queries = [
            "memory management",
            "security settings",
            "automation workflow",
            "predict queries"
        ]
        
        print("\n🔍 Testing searches...\n")
        
        for query in test_queries:
            print(f"Query: {query}")
            
            results = search_engine.search(query, top_k=2)
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title']} (score: {result['score']})")
            
            print()
        
        # Show stats
        print("\n📊 Search Statistics:")
        stats = search_engine.get_stats()
        for key, val in stats.items():
            print(f"   {key}: {val}")
        
        print("\n✅ Demo complete!")
    
    elif args.search:
        results = search_engine.search(args.search)
        
        print(f"\n🔍 Search results for '{args.search}':")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   Score: {result['score']}")
            print(f"   Content: {result['content'][:100]}...")
            print()
    
    elif args.stats:
        stats = search_engine.get_stats()
        print("\n📊 Vector Search Statistics")
        print("=" * 80)
        for key, val in stats.items():
            print(f"   {key}: {val}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
