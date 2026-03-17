#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neural Embedding - Ollama-based semantic embeddings
"""

import os
import sys
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / '30-scripts-tools'))

try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  requests not available. Install: pip install requests")

class NeuralEmbedding:
    """
    Generate semantic embeddings using Ollama (Qwen2.5:1.5b)
    
    Features:
    - Local execution (no cloud API)
    - 768-dimensional vectors
    - Semantic similarity search
    - Automatic caching
    """
    
    def __init__(self, model: str = "qwen2.5:1.5b", 
                 ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self.cache: Dict[str, List[float]] = {}
        self.cache_file = WORKSPACE / 'data' / 'embeddings' / 'neural_cache.json'
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'embeddings_generated': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_time_ms': 0,
        }
        
        # Load cache
        self._load_cache()
    
    def _load_cache(self):
        """Load embedding cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.cache = data.get('embeddings', {})
                print(f"✅ Loaded {len(self.cache)} cached embeddings")
            except Exception as e:
                print(f"⚠️  Failed to load cache: {e}")
    
    def _save_cache(self):
        """Save embedding cache to disk"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({'embeddings': self.cache}, f, indent=2)
            print(f"💾 Saved {len(self.cache)} embeddings")
        except Exception as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def generate_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """
        Generate embedding for text using Ollama
        
        Args:
            text: Input text
            use_cache: Use cached embeddings
        
        Returns:
            768-dimensional vector or None
        """
        if not OLLAMA_AVAILABLE:
            print("⚠️  Ollama not available. Install: pip install requests")
            return None
        
        # Check cache
        cache_key = self._get_cache_key(text)
        
        if use_cache and cache_key in self.cache:
            self.stats['cache_hits'] += 1
            return self.cache[cache_key]
        
        self.stats['cache_misses'] += 1
        
        # Generate embedding using Ollama
        start_time = time.time()
        
        try:
            # Use Ollama embeddings API
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                embedding = response.json().get('embedding', [])
                
                # Cache result
                self.cache[cache_key] = embedding
                self.stats['embeddings_generated'] += 1
                
                elapsed = (time.time() - start_time) * 1000
                self.stats['avg_time_ms'] = (
                    (self.stats['avg_time_ms'] * (self.stats['embeddings_generated'] - 1) + elapsed) /
                    self.stats['embeddings_generated']
                )
                
                # Save cache periodically
                if self.stats['embeddings_generated'] % 10 == 0:
                    self._save_cache()
                
                return embedding
            else:
                print(f"⚠️  Ollama error: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("⚠️  Ollama not running. Start: ollama serve")
            return None
        except Exception as e:
            print(f"⚠️  Error generating embedding: {e}")
            return None
    
    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not v1 or not v2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def search_similar(self, query: str, 
                      candidates: List[str],
                      top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar texts using neural embeddings
        
        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of results
        
        Returns:
            List of (candidate, similarity) tuples
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        if not query_embedding:
            return []
        
        # Calculate similarities
        similarities = []
        
        for candidate in candidates:
            candidate_embedding = self.generate_embedding(candidate)
            
            if candidate_embedding:
                sim = self.cosine_similarity(query_embedding, candidate_embedding)
                similarities.append((candidate, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def batch_generate(self, texts: List[str], 
                      batch_size: int = 10) -> Dict[str, List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts
            batch_size: Batch size for processing
        
        Returns:
            Dict mapping text to embedding
        """
        results = {}
        
        print(f"\n🧠 Generating {len(texts)} embeddings...")
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            for text in batch:
                embedding = self.generate_embedding(text)
                if embedding:
                    results[text] = embedding
        
        # Save cache
        self._save_cache()
        
        return results
    
    def get_stats(self) -> Dict:
        """Get embedding statistics"""
        return {
            'cache_size': len(self.cache),
            'embeddings_generated': self.stats['embeddings_generated'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': round(
                self.stats['cache_hits'] / 
                (self.stats['cache_hits'] + self.stats['cache_misses']) * 100, 2
            ) if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 else 0,
            'avg_generation_time_ms': round(self.stats['avg_time_ms'], 2),
        }
    
    def clear_cache(self):
        """Clear embedding cache"""
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        print("✅ Embedding cache cleared")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Neural Embedding")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--clear', action='store_true', help='Clear cache')
    parser.add_argument('--text', type=str, help='Generate embedding for text')
    args = parser.parse_args()
    
    embedder = NeuralEmbedding()
    
    if args.demo:
        print("\n🧠 Neural Embedding Demo")
        print("=" * 80)
        
        # Test texts
        test_texts = [
            "Memory evolution engine provides automatic quality scoring",
            "Security configuration includes API keys and authentication",
            "Workflow automation enables automatic task execution",
            "Memory system manages long-term knowledge storage",
            "Security audit scans for vulnerabilities and risks"
        ]
        
        print("\n📊 Generating embeddings...\n")
        
        embeddings = {}
        for text in test_texts:
            print(f"Text: {text[:50]}...")
            embedding = embedder.generate_embedding(text)
            
            if embedding:
                embeddings[text] = embedding
                print(f"   ✅ Generated: {len(embedding)} dimensions")
            else:
                print(f"   ⚠️  Failed (Ollama not available?)")
            print()
        
        # Test similarity search
        if embeddings:
            print("\n🔍 Testing similarity search...")
            query = "Memory management system"
            print(f"Query: {query}")
            
            results = embedder.search_similar(query, list(embeddings.keys()), top_k=3)
            
            print("\nTop similar texts:")
            for i, (text, sim) in enumerate(results, 1):
                print(f"{i}. {text[:60]}... (similarity: {sim:.4f})")
        
        # Show stats
        print("\n📈 Embedding Statistics:")
        stats = embedder.get_stats()
        for key, val in stats.items():
            print(f"   {key}: {val}")
        
        print("\n✅ Demo complete!")
    
    elif args.text:
        print(f"\n🧠 Generating embedding for: {args.text}")
        embedding = embedder.generate_embedding(args.text)
        
        if embedding:
            print(f"✅ Generated: {len(embedding)} dimensions")
            print(f"First 10 values: {embedding[:10]}")
        else:
            print("⚠️  Failed to generate embedding")
    
    elif args.stats:
        stats = embedder.get_stats()
        print("\n📊 Neural Embedding Statistics")
        print("=" * 80)
        for key, val in stats.items():
            print(f"   {key}: {val}")
    
    elif args.clear:
        embedder.clear_cache()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
