#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Indexer - Pre-computed keyword index for fast search
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory-记忆系统'
INDEX_DIR = WORKSPACE / 'data' / 'memory_index'
INDEX_DIR.mkdir(parents=True, exist_ok=True)

class MemoryIndexer:
    """
    Build inverted index for fast keyword search
    
    Index structure:
    {
        "keyword": {
            "memory": [(doc_id, position, score), ...],
            "evolution": [(doc_id, position, score), ...],
            ...
        }
    }
    
    Performance: O(1) lookup vs O(n) scan
    """
    
    def __init__(self):
        self.index: Dict[str, Dict[str, List[tuple]]] = defaultdict(lambda: defaultdict(list))
        self.metadata: Dict = {
            'total_docs': 0,
            'total_terms': 0,
            'index_size': 0,
            'built_at': None,
        }
        
        # Stopwords (common words to ignore)
        self.stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这', 'that',
            'it', 'for', 'not', 'with', 'his', 'her', 'but', 'this', 'that'
        }
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into keywords"""
        # Remove punctuation
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        
        # Lowercase
        text = text.lower()
        
        # Split into tokens
        tokens = text.split()
        
        # Remove stopwords and short tokens
        tokens = [
            t for t in tokens 
            if t not in self.stopwords and len(t) > 1
        ]
        
        return tokens
    
    def build_index(self, sources: List[str] = None) -> Dict:
        """
        Build inverted index from memory sources
        
        Args:
            sources: List of source files to index (default: all)
        
        Returns:
            Index statistics
        """
        print("\n🔨 Building Memory Index...")
        print("=" * 80)
        
        self.index = defaultdict(lambda: defaultdict(list))
        doc_id = 0
        
        # Index MEMORY.md sections
        memory_file = MEMORY_DIR / 'MEMORY.md'
        if memory_file.exists() and (not sources or 'MEMORY.md' in sources):
            print(f"\n📄 Indexing MEMORY.md...")
            content = memory_file.read_text(encoding='utf-8')
            
            # Split by sections
            sections = re.split(r'\n##+\s+', content)
            
            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                
                # Extract title
                lines = section.split('\n')
                title = lines[0].strip() if lines else f"Section_{i}"
                
                # Tokenize content
                tokens = self.tokenize(section)
                
                # Add to index
                for pos, token in enumerate(tokens):
                    # Calculate term frequency
                    tf = tokens.count(token) / len(tokens) if tokens else 0
                    
                    # Add posting
                    self.index[token]['memory'].append({
                        'doc_id': f'memory_{i}',
                        'title': title[:50],
                        'position': pos,
                        'tf': round(tf, 4),
                        'content_preview': section[:200].replace('\n', ' ')
                    })
                
                doc_id += 1
                if doc_id % 10 == 0:
                    print(f"   Indexed {doc_id} sections...")
        
        # Index daily notes
        daily_notes_dir = MEMORY_DIR / 'memory'
        if daily_notes_dir.exists() and (not sources or 'daily_notes' in sources):
            print(f"\n📄 Indexing daily notes...")
            note_count = 0
            
            for note_file in daily_notes_dir.glob('*.md'):
                try:
                    content = note_file.read_text(encoding='utf-8')
                    tokens = self.tokenize(content)
                    
                    for pos, token in enumerate(tokens):
                        tf = tokens.count(token) / len(tokens) if tokens else 0
                        
                        self.index[token]['daily_notes'].append({
                            'doc_id': f'daily_{note_file.stem}',
                            'title': note_file.stem,
                            'position': pos,
                            'tf': round(tf, 4),
                            'content_preview': content[:200].replace('\n', ' ')
                        })
                    
                    note_count += 1
                except Exception as e:
                    continue
            
            print(f"   Indexed {note_count} daily notes")
        
        # Update metadata
        total_terms = len(self.index)
        total_postings = sum(
            len(postings)
            for term_dict in self.index.values()
            for postings in term_dict.values()
        )
        
        self.metadata.update({
            'total_docs': doc_id,
            'total_terms': total_terms,
            'total_postings': total_postings,
            'built_at': datetime.now().isoformat(),
        })
        
        print(f"\n✅ Index built successfully!")
        print(f"   Total documents: {self.metadata['total_docs']}")
        print(f"   Unique terms: {self.metadata['total_terms']}")
        print(f"   Total postings: {self.metadata['total_postings']}")
        
        return self.metadata
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search using pre-computed index (O(1) lookup)
        
        Args:
            query: Search query
            max_results: Maximum results
        
        Returns:
            List of results with scores
        """
        tokens = self.tokenize(query)
        
        if not tokens:
            return []
        
        # Collect results from all tokens
        results_dict = defaultdict(list)
        
        for token in tokens:
            # Handle both old and new index format
            if token in self.index:
                term_data = self.index[token]
                
                # New format: dict with sources
                if isinstance(term_data, dict):
                    for source, postings in term_data.items():
                        for posting in postings:
                            doc_key = f"{source}:{posting.get('doc_id', 'unknown')}"
                            results_dict[doc_key].append({
                                'token': token,
                                'source': source,
                                **posting
                            })
                # Old format: list of postings
                elif isinstance(term_data, list):
                    for posting in term_data:
                        doc_key = f"unknown:{posting.get('doc_id', 'unknown')}"
                        results_dict[doc_key].append({
                            'token': token,
                            'source': 'unknown',
                            **posting
                        })
        
        # Score and rank results
        scored_results = []
        for doc_key, matches in results_dict.items():
            # Score = term frequency × query coverage
            tf_sum = sum(m.get('tf', 0) for m in matches)
            query_coverage = len(matches) / len(tokens)
            
            score = tf_sum * query_coverage
            
            scored_results.append({
                'doc_key': doc_key,
                'source': matches[0].get('source', 'unknown'),
                'doc_id': matches[0].get('doc_id', 'unknown'),
                'title': matches[0].get('title', 'N/A'),
                'content_preview': matches[0].get('content_preview', '')[:200],
                'matched_terms': [m['token'] for m in matches],
                'score': round(score, 4),
                'match_count': len(matches)
            })
        
        # Sort by score
        scored_results.sort(key=lambda r: r['score'], reverse=True)
        
        return scored_results[:max_results]
    
    def save_index(self, path: Path = None) -> Path:
        """Save index to disk"""
        if path is None:
            path = INDEX_DIR / 'memory_index.json'
        
        # Convert defaultdict to regular dict for JSON serialization
        serializable_index = {
            term: dict(sources)
            for term, sources in self.index.items()
        }
        
        data = {
            'index': serializable_index,
            'metadata': self.metadata
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Index saved to: {path}")
        print(f"   Size: {path.stat().st_size / 1024:.1f} KB")
        
        return path
    
    def load_index(self, path: Path = None) -> bool:
        """Load index from disk"""
        if path is None:
            path = INDEX_DIR / 'memory_index.json'
        
        if not path.exists():
            print(f"⚠️  Index not found: {path}")
            return False
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Restore index structure
        self.index = defaultdict(lambda: defaultdict(list))
        for term, sources in data['index'].items():
            for source, postings in sources.items():
                self.index[term][source] = postings
        
        self.metadata = data['metadata']
        
        print(f"✅ Index loaded from: {path}")
        print(f"   Terms: {self.metadata['total_terms']}")
        print(f"   Built: {self.metadata['built_at']}")
        
        return True
    
    def get_top_terms(self, n: int = 20) -> List[tuple]:
        """Get most frequent terms"""
        term_freq = {
            term: sum(len(postings) for postings in sources.values())
            for term, sources in self.index.items()
        }
        
        sorted_terms = sorted(term_freq.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_terms[:n]

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Indexer")
    parser.add_argument('--build', action='store_true', help='Build index')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--top', type=int, default=20, help='Top terms')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    args = parser.parse_args()
    
    indexer = MemoryIndexer()
    
    if args.build:
        stats = indexer.build_index()
        indexer.save_index()
    
    elif args.search:
        # Load index
        if not indexer.load_index():
            print("Building index first...")
            indexer.build_index()
            indexer.save_index()
        
        # Search
        print(f"\n🔍 Searching for: {args.search}")
        results = indexer.search(args.search, max_results=10)
        
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['source']}] {result['title'][:50]}")
            print(f"   Score: {result['score']:.4f} | Matches: {result['matched_terms']}")
            print(f"   Preview: {result['content_preview'][:150]}...")
            print()
    
    elif args.stats:
        if indexer.load_index():
            print("\n📊 Index Statistics")
            print("=" * 80)
            for key, val in indexer.metadata.items():
                print(f"   {key}: {val}")
        else:
            print("No index found. Run --build first.")
    
    elif args.demo:
        print("\n🔨 Memory Indexer Demo")
        print("=" * 80)
        
        # Build index
        stats = indexer.build_index()
        indexer.save_index()
        
        # Test search
        print("\n🔍 Testing search...")
        queries = ['memory', 'security', 'workflow']
        
        for query in queries:
            results = indexer.search(query, max_results=3)
            print(f"\n   Query '{query}': {len(results)} results")
            if results:
                print(f"   Top: [{results[0]['source']}] Score: {results[0]['score']:.4f}")
        
        # Show top terms
        print(f"\n📊 Top {args.top} terms:")
        for term, freq in indexer.get_top_terms(args.top):
            print(f"   {term}: {freq} occurrences")
        
        print("\n✅ Demo complete!")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
