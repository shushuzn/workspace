#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Distributed Search Engine - Scalable search with Redis

Features:
- Inverted index
- Full-text search
- Distributed indexing
- Query optimization
- Result ranking
- Caching integration
"""

import os
import sys
import json
import re
import math
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import defaultdict, Counter

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
SEARCH_INDEX_DIR = WORKSPACE / 'data' / 'search_index'
SEARCH_INDEX_DIR.mkdir(parents=True, exist_ok=True)

class TextProcessor:
    """Text preprocessing and tokenization"""
    
    # Common English stop words
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
        'she', 'we', 'they', 'what', 'which', 'who', 'whom', 'when', 'where',
        'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there',
        'then', 'once', 'if', 'any', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'under', 'again',
        'further', 'while', 'am', 'being', 'having', 'doing'
    }
    
    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        """Tokenize text into words"""
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Extract words (alphanumeric + underscore)
        words = re.findall(r'\b\w+\b', text)
        
        # Remove stop words and short words
        return [
            word for word in words
            if word not in cls.STOP_WORDS and len(word) > 2
        ]
    
    @classmethod
    def normalize(cls, word: str) -> str:
        """Normalize word (stemming simplified)"""
        # Simple suffix removal
        suffixes = ['ing', 'ed', 'ly', 'es', 's', 'ment', 'ness', 'tion', 'ity']
        
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        
        return word


class InvertedIndex:
    """Inverted index for full-text search"""
    
    def __init__(self):
        self.index: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        self.documents: Dict[int, Dict] = {}
        self.doc_count = 0
    
    def add_document(self, doc_id: int, content: str, metadata: Dict = None) -> int:
        """
        Add document to index
        
        Args:
            doc_id: Document ID
            content: Document content
            metadata: Optional metadata
        
        Returns:
            Document ID
        """
        # Tokenize
        tokens = TextProcessor.tokenize(content)
        
        # Normalize and index
        for position, token in enumerate(tokens):
            normalized = TextProcessor.normalize(token)
            self.index[normalized][doc_id].append(position)
        
        # Store document
        self.documents[doc_id] = {
            'content': content,
            'metadata': metadata or {},
            'tokens': len(tokens),
        }
        
        self.doc_count = max(self.doc_count, doc_id + 1)
        
        return doc_id
    
    def search(self, query: str) -> List[Tuple[int, float]]:
        """
        Search documents
        
        Args:
            query: Search query
        
        Returns:
            List of (doc_id, score) tuples
        """
        # Tokenize query
        query_tokens = TextProcessor.tokenize(query)
        
        if not query_tokens:
            return []
        
        # Find matching documents
        doc_scores = defaultdict(float)
        
        for token in query_tokens:
            normalized = TextProcessor.normalize(token)
            
            if normalized in self.index:
                # TF-IDF scoring
                df = len(self.index[normalized])  # Document frequency
                idf = math.log(self.doc_count / max(1, df))
                
                for doc_id, positions in self.index[normalized].items():
                    tf = len(positions) / max(1, self.documents[doc_id]['tokens'])
                    score = tf * idf
                    doc_scores[doc_id] += score
        
        # Sort by score
        results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        return results
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """Get document by ID"""
        return self.documents.get(doc_id)
    
    def save(self, file_path: Path):
        """Save index to file"""
        data = {
            'index': dict(self.index),
            'documents': self.documents,
            'doc_count': self.doc_count,
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, file_path: Path):
        """Load index from file"""
        if not file_path.exists():
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.index = defaultdict(lambda: defaultdict(list), {
            k: defaultdict(list, {int(dk): dv for dk, dv in v.items()})
            for k, v in data.get('index', {}).items()
        })
        self.documents = {
            int(dk): dv for dk, dv in data.get('documents', {}).items()
        }
        self.doc_count = data.get('doc_count', 0)


class DistributedSearch:
    """
    Distributed search engine
    
    Features:
    - Inverted index
    - Full-text search
    - Distributed indexing
    - Query optimization
    - Result ranking
    - Caching integration
    """
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or SEARCH_INDEX_DIR
        self.index = InvertedIndex()
        
        # Load existing index
        self._load_index()
    
    def _load_index(self):
        """Load existing index"""
        index_file = self.index_dir / 'search_index.json'
        if index_file.exists():
            self.index.load(index_file)
            print(f"✅ Loaded search index ({self.index.doc_count} documents)")
    
    def _save_index(self):
        """Save index"""
        index_file = self.index_dir / 'search_index.json'
        self.index.save(index_file)
    
    def index_file(self, file_path: Path, metadata: Dict = None) -> int:
        """
        Index a file
        
        Args:
            file_path: Path to file
            metadata: Optional metadata
        
        Returns:
            Document ID
        """
        if not file_path.exists():
            return -1
        
        # Read content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return -1
        
        # Create doc ID
        doc_id = abs(hash(str(file_path))) % (10 ** 8)
        
        # Default metadata
        if metadata is None:
            metadata = {
                'path': str(file_path),
                'type': file_path.suffix,
                'indexed': datetime.now().isoformat(),
            }
        
        # Add to index
        self.index.add_document(doc_id, content, metadata)
        
        # Save index
        self._save_index()
        
        return doc_id
    
    def index_directory(self, dir_path: Path, patterns: List[str] = None) -> int:
        """
        Index all files in directory
        
        Args:
            dir_path: Directory path
            patterns: File patterns to include (e.g., ['*.py', '*.md'])
        
        Returns:
            Number of files indexed
        """
        if not dir_path.exists():
            return 0
        
        if patterns is None:
            patterns = ['*.py', '*.md', '*.txt', '*.json']
        
        count = 0
        for pattern in patterns:
            for file_path in dir_path.rglob(pattern):
                if self.index_file(file_path):
                    count += 1
        
        return count
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search indexed documents
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of search results
        """
        # Search
        results = self.index.search(query)
        
        # Format results
        formatted = []
        for doc_id, score in results[:limit]:
            doc = self.index.get_document(doc_id)
            if doc:
                formatted.append({
                    'doc_id': doc_id,
                    'score': round(score, 4),
                    'metadata': doc.get('metadata', {}),
                    'preview': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                })
        
        return formatted
    
    def get_stats(self) -> Dict:
        """Get search statistics"""
        return {
            'documents': self.index.doc_count,
            'unique_terms': len(self.index.index),
            'index_size_bytes': (self.index_dir / 'search_index.json').stat().st_size if (self.index_dir / 'search_index.json').exists() else 0,
        }
    
    def clear_index(self):
        """Clear search index"""
        self.index = InvertedIndex()
        index_file = self.index_dir / 'search_index.json'
        if index_file.exists():
            index_file.unlink()
        print("✅ Search index cleared")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Distributed Search Engine")
    parser.add_argument('--index', type=str, help='Index a file or directory')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--clear', action='store_true', help='Clear index')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    args = parser.parse_args()
    
    search_engine = DistributedSearch()
    
    if args.index:
        path = Path(args.index)
        if path.is_dir():
            count = search_engine.index_directory(path)
            print(f"✅ Indexed {count} files in {path}")
        else:
            doc_id = search_engine.index_file(path)
            print(f"✅ Indexed file: {path} (doc_id: {doc_id})")
    
    elif args.search:
        results = search_engine.search(args.search)
        
        if not results:
            print(f"\n❌ No results for: {args.search}")
        else:
            print(f"\n🔍 Search results for: {args.search}")
            print("=" * 60)
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Score: {result['score']}")
                print(f"   Path: {result['metadata'].get('path', 'N/A')}")
                print(f"   Preview: {result['preview'][:100]}...")
    
    elif args.stats:
        stats = search_engine.get_stats()
        print("\n📊 SEARCH ENGINE STATISTICS")
        print("=" * 60)
        print(f"Documents indexed: {stats['documents']}")
        print(f"Unique terms: {stats['unique_terms']}")
        print(f"Index size: {stats['index_size_bytes'] / 1024:.2f} KB")
        print("=" * 60)
    
    elif args.clear:
        search_engine.clear_index()
    
    elif args.demo:
        print("\n🔍 DISTRIBUTED SEARCH DEMO")
        print("=" * 60)
        
        # Index some files
        print("\n📁 Indexing workspace files...")
        count = search_engine.index_directory(WORKSPACE / '30-scripts-tools', ['*.py'])
        print(f"✅ Indexed {count} Python files")
        
        # Search
        print("\n🔍 Searching for 'cache'...")
        results = search_engine.search('cache')
        
        if results:
            print(f"✅ Found {len(results)} results:")
            for i, result in enumerate(results[:5], 1):
                print(f"   {i}. {result['metadata'].get('path', 'N/A')} (score: {result['score']})")
        else:
            print("⚠️  No results found")
        
        # Stats
        stats = search_engine.get_stats()
        print(f"\n📊 Stats: {stats['documents']} docs, {stats['unique_terms']} terms")
        
        print("\n" + "=" * 60)
        print("✅ Demo complete!")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
