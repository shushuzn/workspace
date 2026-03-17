#!/usr/bin/env python3
"""
Memory Semantic Search - Fast semantic search for MEMORY.md
Enables finding similar concepts and principles quickly
"""

import sys
import os
import re
import json
from datetime import datetime
from typing import List, Dict, Tuple

sys.stdout.reconfigure(encoding='utf-8')

MEMORY_FILE = r"MEMORY.md"
INDEX_FILE = r"data/memory_search_index.json"

class MemorySearchEngine:
    """Semantic search engine for MEMORY.md"""
    
    def __init__(self):
        self.memory_content = ""
        self.sections = []
        self.index = {}
        
    def load_memory(self) -> bool:
        """Load MEMORY.md content"""
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                self.memory_content = f.read()
            print(f"✅ Loaded MEMORY.md ({len(self.memory_content)} chars)")
            return True
        except Exception as e:
            print(f"❌ Error loading MEMORY.md: {e}")
            return False
    
    def parse_sections(self) -> List[Dict]:
        """Parse MEMORY.md into sections"""
        sections = []
        current_section = None
        current_content = []
        
        lines = self.memory_content.split('\n')
        for line in lines:
            if line.startswith('## '):
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content),
                        'preview': current_content[0][:100] if current_content else ''
                    })
                current_section = line.replace('## ', '').strip()
                current_content = []
            elif current_section and line.strip():
                current_content.append(line)
        
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content),
                'preview': current_content[0][:100] if current_content else ''
            })
        
        self.sections = sections
        print(f"✅ Parsed {len(sections)} sections")
        return sections
    
    def keyword_search(self, query: str) -> List[Tuple[str, str, float]]:
        """Simple keyword-based search"""
        results = []
        query_terms = query.lower().split()
        
        for section in self.sections:
            content_lower = section['content'].lower()
            title_lower = section['title'].lower()
            
            # Calculate relevance score
            score = 0
            for term in query_terms:
                if term in title_lower:
                    score += 5.0  # Title match is more important
                if term in content_lower:
                    score += 1.0
                # Bonus for exact phrase match
                if query.lower() in content_lower:
                    score += 3.0
            
            if score > 0:
                results.append((section['title'], section['preview'], score))
        
        # Sort by relevance
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:10]  # Return top 10
    
    def semantic_search(self, query: str) -> List[Tuple[str, str, float]]:
        """
        Enhanced search with semantic similarity
        Uses keyword expansion and context matching
        """
        # Expand query with synonyms
        synonyms = {
            'compression': ['compress', 'reduce', 'size', 'compact'],
            'quality': ['score', 'metric', 'standard', 'excellence'],
            'encoding': ['utf-8', 'charset', 'garbled', 'text'],
            'principle': ['rule', 'guideline', 'core', 'belief'],
            'tool': ['script', 'utility', 'system', 'engine'],
            'memory': ['distill', 'insight', 'archive', 'recall'],
            'search': ['find', 'locate', 'retrieve', 'query'],
            'innovation': ['breakthrough', 'creative', 'novel', 'new'],
        }
        
        expanded_terms = [query.lower()]
        for term in query.lower().split():
            if term in synonyms:
                expanded_terms.extend(synonyms[term])
        
        results = []
        for section in self.sections:
            content_lower = section['content'].lower()
            title_lower = section['title'].lower()
            
            score = 0
            matched_terms = []
            
            for term in expanded_terms:
                if term in title_lower:
                    score += 3.0
                    matched_terms.append(term)
                if term in content_lower:
                    score += 0.5
                    if term not in matched_terms:
                        matched_terms.append(term)
            
            if score > 0:
                # Create enhanced preview with context
                preview = self._get_context_preview(section['content'], query_terms=expanded_terms)
                results.append((section['title'], preview, score))
        
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:10]
    
    def _get_context_preview(self, content: str, query_terms: List[str], context_size: int = 150) -> str:
        """Get preview with highlighted context around matched terms"""
        content_lower = content.lower()
        
        # Find first match
        for term in query_terms:
            idx = content_lower.find(term)
            if idx != -1:
                start = max(0, idx - context_size // 2)
                end = min(len(content), idx + context_size // 2)
                preview = content[start:end].strip()
                if start > 0:
                    preview = "..." + preview
                if end < len(content):
                    preview = preview + "..."
                return preview
        
        # No match, return first line
        first_line = content.split('\n')[0][:context_size]
        return first_line
    
    def build_index(self) -> Dict:
        """Build search index for faster queries"""
        self.index = {
            'timestamp': datetime.now().isoformat(),
            'total_sections': len(self.sections),
            'sections': [
                {
                    'title': s['title'],
                    'word_count': len(s['content'].split()),
                    'keywords': self._extract_keywords(s['content'])
                }
                for s in self.sections
            ]
        }
        return self.index
    
    def _extract_keywords(self, content: str, top_k: int = 5) -> List[str]:
        """Extract top keywords from content"""
        # Simple frequency-based extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_k]]
    
    def save_index(self) -> bool:
        """Save search index to file"""
        try:
            os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
            with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved index to {INDEX_FILE}")
            return True
        except Exception as e:
            print(f"❌ Error saving index: {e}")
            return False
    
    def search(self, query: str, mode: str = 'semantic') -> List[Tuple[str, str, float]]:
        """Unified search interface"""
        if mode == 'keyword':
            return self.keyword_search(query)
        else:
            return self.semantic_search(query)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Semantic Search')
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--mode', choices=['keyword', 'semantic'], default='semantic',
                       help='Search mode (default: semantic)')
    parser.add_argument('--build-index', action='store_true',
                       help='Build search index')
    parser.add_argument('--stats', action='store_true',
                       help='Show memory statistics')
    
    args = parser.parse_args()
    
    print("🔍 Memory Search Engine")
    print("=" * 50)
    
    engine = MemorySearchEngine()
    
    if not engine.load_memory():
        sys.exit(1)
    
    if args.stats:
        print(f"\n📊 Memory Statistics:")
        print(f"  Total characters: {len(engine.memory_content)}")
        print(f"  Total lines: {len(engine.memory_content.splitlines())}")
        print(f"  Sections: {len(engine.sections)}")
        sys.exit(0)
    
    if args.build_index:
        engine.parse_sections()
        index = engine.build_index()
        engine.save_index()
        print(f"\n✅ Index built: {index['total_sections']} sections")
        sys.exit(0)
    
    if not args.query:
        print("\nUsage:")
        print("  python memory_semantic_search.py <query>")
        print("  python memory_semantic_search.py --build-index")
        print("  python memory_semantic_search.py --stats")
        print("\nExamples:")
        print("  python memory_semantic_search.py \"compression\"")
        print("  python memory_semantic_search.py \"quality principles\"")
        print("  python memory_semantic_search.py \"memory tools\" --mode semantic")
        sys.exit(0)
    
    # Parse sections and search
    engine.parse_sections()
    results = engine.search(args.query, mode=args.mode)
    
    print(f"\n🔎 Search: \"{args.query}\" ({args.mode} mode)")
    print("-" * 50)
    
    if not results:
        print("No results found.")
    else:
        print(f"Found {len(results)} results:\n")
        for i, (title, preview, score) in enumerate(results, 1):
            print(f"{i}. **{title}** (score: {score:.2f})")
            print(f"   {preview}")
            print()
    
    print("-" * 50)
    print(f"Total: {len(results)} results")


if __name__ == '__main__':
    main()
