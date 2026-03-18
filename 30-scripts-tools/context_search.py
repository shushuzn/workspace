#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Search - Intelligent context search with semantic ranking
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from collections import Counter

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
CONTEXT_DIR = WORKSPACE / 'data' / 'context_cache'
MEMORY_DIR = WORKSPACE / '13-memory-记忆系统'

@dataclass
class SearchResult:
    """Search result with relevance score"""
    source: str
    content: str
    score: float
    matched_terms: List[str]
    context_before: str = ""
    context_after: str = ""
    timestamp: str = ""

class ContextSearcher:
    """
    Intelligent context search with:
    1. Keyword matching
    2. Semantic similarity (basic)
    3. Recency boost
    4. Priority boost
    5. Context window extraction
    """
    
    def __init__(self):
        self.weights = {
            'keyword_match': 0.4,
            'semantic_match': 0.3,
            'recency': 0.2,
            'priority': 0.1,
        }
        
        self.stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这'
        }
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Remove punctuation
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        
        # Simple tokenization (split on whitespace)
        tokens = text.lower().split()
        
        # Remove stopwords and short tokens
        tokens = [
            t for t in tokens 
            if t not in self.stopwords and len(t) > 1
        ]
        
        return tokens
    
    def keyword_match_score(self, query_tokens: List[str], 
                           text: str) -> Tuple[float, List[str]]:
        """Calculate keyword match score"""
        text_tokens = set(self.tokenize(text))
        
        matched = []
        for qt in query_tokens:
            if qt in text_tokens:
                matched.append(qt)
            # Fuzzy match - substring
            elif any(qt in tt for tt in text_tokens):
                matched.append(qt)
        
        if not query_tokens:
            return 0.0, []
        
        score = len(matched) / len(query_tokens)
        return score, list(set(matched))
    
    def semantic_match_score(self, query: str, text: str) -> float:
        """
        Basic semantic similarity using word overlap
        (Full semantic would require embeddings)
        """
        query_tokens = set(self.tokenize(query))
        text_tokens = set(self.tokenize(text))
        
        if not query_tokens or not text_tokens:
            return 0.0
        
        # Jaccard similarity
        intersection = query_tokens & text_tokens
        union = query_tokens | text_tokens
        
        return len(intersection) / len(union) if union else 0.0
    
    def recency_score(self, timestamp: str) -> float:
        """Calculate recency score (newer = higher)"""
        if not timestamp:
            return 0.5  # Default
        
        try:
            doc_time = datetime.fromisoformat(timestamp)
            age_hours = (datetime.now() - doc_time).total_seconds() / 3600
            
            # Exponential decay
            score = 1.0 / (1.0 + age_hours / 24)  # Half-life: 24 hours
            return min(1.0, score)
        except:
            return 0.5
    
    def priority_score(self, source: str) -> float:
        """Calculate priority score based on source"""
        priority_map = {
            'MEMORY.md': 1.0,
            'TODO.md': 0.9,
            'context_cache': 0.7,
            'daily_note': 0.8,
            'session': 0.6,
        }
        
        for key, score in priority_map.items():
            if key in source:
                return score
        
        return 0.5
    
    def extract_context(self, text: str, match_start: int, 
                       match_end: int, window: int = 100) -> Tuple[str, str]:
        """Extract context window around match"""
        start = max(0, match_start - window)
        end = min(len(text), match_end + window)
        
        before = text[start:match_start].strip()
        after = text[match_end:end].strip()
        
        return before, after
    
    def search(self, query: str, sources: List[str] = None,
               max_results: int = 10, min_score: float = 0.3) -> List[SearchResult]:
        """
        Search across context sources
        """
        query_tokens = self.tokenize(query)
        results = []
        
        # Search in MEMORY.md
        memory_file = MEMORY_DIR / 'MEMORY.md'
        if memory_file.exists() and (not sources or 'MEMORY.md' in sources):
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Search by sections
            sections = re.split(r'\n##+\s+', content)
            for section in sections:
                if not section.strip():
                    continue
                
                keyword_score, matched = self.keyword_match_score(query_tokens, section)
                if keyword_score < min_score:
                    continue
                
                semantic_score = self.semantic_match_score(query, section)
                recency = self.recency_score('')  # No timestamp for sections
                priority = self.priority_score('MEMORY.md')
                
                # Weighted score
                total_score = (
                    keyword_score * self.weights['keyword_match'] +
                    semantic_score * self.weights['semantic_match'] +
                    recency * self.weights['recency'] +
                    priority * self.weights['priority']
                )
                
                # Find match position for context
                match = re.search(re.escape(matched[0]) if matched else query, 
                                section, re.IGNORECASE)
                if match:
                    before, after = self.extract_context(
                        section, match.start(), match.end()
                    )
                else:
                    before, after = "", section[:200]
                
                results.append(SearchResult(
                    source='MEMORY.md',
                    content=section[:500],
                    score=total_score,
                    matched_terms=matched,
                    context_before=before,
                    context_after=after,
                    timestamp=''
                ))
        
        # Search in context cache
        if CONTEXT_DIR.exists() and (not sources or 'context_cache' in sources):
            for cache_file in CONTEXT_DIR.glob('*.json'):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    content = data.get('summary', '') or str(data)
                    
                    keyword_score, matched = self.keyword_match_score(query_tokens, content)
                    if keyword_score < min_score:
                        continue
                    
                    semantic_score = self.semantic_match_score(query, content)
                    recency = self.recency_score(data.get('timestamp', ''))
                    priority = self.priority_score('context_cache')
                    
                    total_score = (
                        keyword_score * self.weights['keyword_match'] +
                        semantic_score * self.weights['semantic_match'] +
                        recency * self.weights['recency'] +
                        priority * self.weights['priority']
                    )
                    
                    results.append(SearchResult(
                        source=f'context_cache/{cache_file.name}',
                        content=content[:500],
                        score=total_score,
                        matched_terms=matched,
                        timestamp=data.get('timestamp', '')
                    ))
                except Exception as e:
                    continue
        
        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results[:max_results]
    
    def search_conversations(self, conversations: List[Dict], 
                            query: str,
                            max_results: int = 5) -> List[SearchResult]:
        """Search within conversation history"""
        query_tokens = self.tokenize(query)
        results = []
        
        for i, conv in enumerate(conversations):
            content = conv.get('content', '')
            
            keyword_score, matched = self.keyword_match_score(query_tokens, content)
            if keyword_score < 0.2:
                continue
            
            semantic_score = self.semantic_match_score(query, content)
            recency = self.recency_score(conv.get('timestamp', ''))
            
            total_score = (
                keyword_score * 0.5 +
                semantic_score * 0.3 +
                recency * 0.2
            )
            
            results.append(SearchResult(
                source=f'conversation_{i}',
                content=content[:500],
                score=total_score,
                matched_terms=matched,
                timestamp=conv.get('timestamp', '')
            ))
        
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:max_results]

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Context Search")
    parser.add_argument('--query', type=str, help='Search query')
    parser.add_argument('--max', type=int, default=5, help='Max results')
    parser.add_argument('--min-score', type=float, default=0.3, help='Min score')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    args = parser.parse_args()
    
    searcher = ContextSearcher()
    
    if args.demo:
        print("\n🔍 Context Search Demo")
        print("=" * 80)
        
        query = "memory evolution engine"
        print(f"\nQuery: {query}")
        
        results = searcher.search(query, max_results=args.max)
        
        print(f"\nFound {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result.source}] (Score: {result.score:.2f})")
            print(f"   Matched: {', '.join(result.matched_terms)}")
            print(f"   Content: {result.content[:150]}...")
            print()
    
    elif args.query:
        results = searcher.search(args.query, 
                                 max_results=args.max,
                                 min_score=args.min_score)
        
        print(f"\n🔍 Search Results for '{args.query}'")
        print("=" * 80)
        print(f"Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result.source}] (Score: {result.score:.2f})")
            print(f"   Matched: {', '.join(result.matched_terms)}")
            print(f"   Content: {result.content[:200]}...")
            print()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
