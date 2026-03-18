#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Tool Finder - Intelligent tool search

Features:
- Natural language search
- Fuzzy matching
- Category browsing
- Recent/popular tools
- Smart ranking
- Quick actions
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import difflib

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
DATA_DIR = WORKSPACE / 'data' / 'ai_suggestions'
DATA_DIR.mkdir(parents=True, exist_ok=True)

USAGE_HISTORY = DATA_DIR / 'usage_history.json'

class SmartSearcher:
    """Smart tool search with fuzzy matching"""
    
    def __init__(self):
        self.tools = []
        self.usage_data = self._load_usage_history()
    
    def _load_usage_history(self) -> Dict:
        """Load usage history"""
        if USAGE_HISTORY.exists():
            with open(USAGE_HISTORY, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'tools': {}, 'queries': []}
    
    def load_tools(self, tools_dir: Path) -> List[Dict]:
        """Load tools"""
        tools = []
        
        for py_file in tools_dir.glob('*.py'):
            if py_file.name.startswith('_'):
                continue
            
            tool_info = self._scan_tool(py_file)
            if tool_info:
                tools.append(tool_info)
        
        self.tools = tools
        return tools
    
    def _scan_tool(self, file_path: Path) -> Optional[Dict]:
        """Scan single tool"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract docstring
            docstring = ''
            if '"""' in content:
                start = content.find('"""')
                end = content.find('"""', start + 3)
                if end > start:
                    docstring = content[start+3:end]
            
            # Extract category
            category = self._categorize_tool(file_path.stem, docstring)
            
            return {
                'name': file_path.stem,
                'file': file_path.name,
                'path': str(file_path),
                'description': docstring.split('\n')[0] if docstring else '',
                'full_doc': docstring,
                'keywords': self._extract_keywords(file_path.stem, docstring),
                'category': category,
                'size_kb': round(file_path.stat().st_size / 1024, 2),
                'usage_count': self._get_usage_count(file_path.stem),
                'last_used': self._get_last_used(file_path.stem),
            }
        
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
            return None
    
    def _extract_keywords(self, name: str, docstring: str) -> List[str]:
        """Extract keywords"""
        keywords = name.lower().split('_')
        
        if docstring:
            words = docstring.lower().split()
            keywords.extend([w for w in words if len(w) > 2][:20])
        
        return list(set(keywords))
    
    def _categorize_tool(self, name: str, docstring: str) -> str:
        """Categorize tool"""
        name_lower = name.lower()
        doc_lower = docstring.lower() if docstring else ''
        
        categories = {
            'deployment': ['deploy', 'ci', 'cd', 'pipeline', 'release'],
            'analysis': ['analyze', 'analytics', 'predict', 'insight', 'report'],
            'automation': ['auto', 'schedule', 'cron', 'workflow', 'orchestrat'],
            'monitoring': ['monitor', 'health', 'watch', 'check', 'dashboard'],
            'data': ['data', 'cache', 'storage', 'database', 'redis'],
            'integration': ['integrat', 'connect', 'api', 'webhook', 'sync'],
            'optimization': ['optim', 'enhance', 'improve', 'tune', 'accelerat'],
            'utility': ['util', 'helper', 'common', 'config', 'setup'],
            'documentation': ['doc', 'readme', 'generate', 'template'],
            'security': ['security', 'audit', 'scan', 'vulnerability'],
        }
        
        for category, keywords in categories.items():
            if any(kw in name_lower or kw in doc_lower for kw in keywords):
                return category
        
        return 'other'
    
    def _get_usage_count(self, tool_name: str) -> int:
        """Get usage count"""
        return self.usage_data.get('tools', {}).get(tool_name, {}).get('count', 0)
    
    def _get_last_used(self, tool_name: str) -> Optional[str]:
        """Get last used timestamp"""
        return self.usage_data.get('tools', {}).get(tool_name, {}).get('last_used')
    
    def search(self, query: str, top_n: int = 10) -> List[Dict]:
        """Search tools with fuzzy matching"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        
        for tool in self.tools:
            # Calculate match scores
            name_score = self._name_match_score(tool, query_lower)
            keyword_score = self._keyword_match_score(tool, query_words)
            desc_score = self._description_match_score(tool, query_lower)
            
            # Popularity boost
            popularity_score = min(1.0, tool['usage_count'] / 10.0)
            
            # Recency boost
            recency_score = self._recency_score(tool['last_used'])
            
            # Combined score
            total_score = (
                max(name_score, keyword_score, desc_score) * 0.7 +
                popularity_score * 0.15 +
                recency_score * 0.15
            )
            
            if total_score > 0.15:  # Threshold
                results.append({
                    'tool': tool,
                    'score': round(total_score, 3),
                    'match_type': self._get_match_type(name_score, keyword_score, desc_score),
                    'highlights': self._get_highlights(tool, query_words),
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_n]
    
    def _name_match_score(self, tool: Dict, query: str) -> float:
        """Calculate name match score"""
        tool_name = tool['name'].lower()
        
        # Exact match
        if query in tool_name:
            return 1.0
        
        # Fuzzy match
        ratio = difflib.SequenceMatcher(None, tool_name, query).ratio()
        
        # Word overlap
        tool_words = set(tool_name.split('_'))
        query_words = set(query.split())
        overlap = len(tool_words & query_words) / max(len(tool_words), len(query_words))
        
        return max(ratio * 0.7, overlap)
    
    def _keyword_match_score(self, tool: Dict, query_words: set) -> float:
        """Calculate keyword match score"""
        tool_keywords = set(tool['keywords'])
        
        # Exact keyword match
        matches = tool_keywords & query_words
        if matches:
            return min(1.0, len(matches) / len(query_words))
        
        # Fuzzy keyword match
        for keyword in tool_keywords:
            for word in query_words:
                if difflib.SequenceMatcher(None, keyword, word).ratio() > 0.7:
                    return 0.8
        
        return 0.0
    
    def _description_match_score(self, tool: Dict, query: str) -> float:
        """Calculate description match score"""
        if not tool['description']:
            return 0.0
        
        desc_lower = tool['description'].lower()
        
        # Word overlap
        desc_words = set(desc_lower.split())
        query_words = set(query.split())
        overlap = len(desc_words & query_words) / max(len(desc_words), len(query_words))
        
        # Substring match
        if query in desc_lower:
            return 0.9
        
        return overlap * 0.7
    
    def _recency_score(self, last_used: Optional[str]) -> float:
        """Calculate recency score"""
        if not last_used:
            return 0.5
        
        try:
            last_dt = datetime.fromisoformat(last_used)
            days_ago = (datetime.now() - last_dt).days
            
            if days_ago == 0:
                return 1.0
            elif days_ago < 7:
                return 0.8
            elif days_ago < 30:
                return 0.6
            else:
                return 0.4
        except:
            return 0.5
    
    def _get_match_type(self, name_score: float, keyword_score: float, desc_score: float) -> str:
        """Get match type"""
        scores = [('name', name_score), ('keyword', keyword_score), ('desc', desc_score)]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]
    
    def _get_highlights(self, tool: Dict, query_words: set) -> List[str]:
        """Get highlight matches"""
        highlights = []
        
        # Check name
        tool_words = set(tool['name'].lower().split('_'))
        name_matches = tool_words & query_words
        highlights.extend([f"name:{w}" for w in name_matches])
        
        # Check keywords
        keyword_matches = set(tool['keywords']) & query_words
        highlights.extend([f"keyword:{w}" for w in keyword_matches])
        
        return highlights[:5]  # Limit highlights


class CategoryBrowser:
    """Browse tools by category"""
    
    def __init__(self, tools: List[Dict]):
        self.tools = tools
        self.categories = self._build_categories()
    
    def _build_categories(self) -> Dict[str, List[Dict]]:
        """Build category index"""
        categories = defaultdict(list)
        
        for tool in self.tools:
            category = tool.get('category', 'other')
            categories[category].append(tool)
        
        # Sort tools within each category by usage
        for category in categories:
            categories[category].sort(
                key=lambda t: t.get('usage_count', 0),
                reverse=True
            )
        
        return dict(categories)
    
    def browse(self, category: str = None) -> Dict:
        """Browse categories"""
        if category:
            tools = self.categories.get(category, [])
            return {
                'category': category,
                'tools': tools,
                'count': len(tools),
            }
        else:
            # Return all categories
            return {
                'categories': {
                    cat: {
                        'count': len(tools),
                        'top_tools': [t['name'] for t in tools[:3]],
                    }
                    for cat, tools in self.categories.items()
                },
                'total_categories': len(self.categories),
                'total_tools': len(self.tools),
            }


class SmartToolFinder:
    """
    Intelligent tool search and discovery
    
    Features:
    - Natural language search
    - Fuzzy matching
    - Category browsing
    - Recent/popular tools
    - Smart ranking
    - Quick actions
    """
    
    def __init__(self):
        self.searcher = SmartSearcher()
        self.category_browser = None
    
    def load_tools(self, tools_dir: Path) -> List[Dict]:
        """Load tools"""
        return self.searcher.load_tools(toools_dir)
    
    def find(self, query: str, top_n: int = 10) -> Dict:
        """Find tools matching query"""
        results = self.searcher.search(query, top_n)
        
        return {
            'query': query,
            'results': [
                {
                    'name': r['tool']['name'],
                    'file': r['tool']['file'],
                    'description': r['tool']['description'],
                    'category': r['tool']['category'],
                    'score': r['score'],
                    'match_type': r['match_type'],
                    'highlights': r['highlights'],
                    'usage_count': r['tool']['usage_count'],
                    'command': f"python {r['tool']['file']} --help",
                }
                for r in results
            ],
            'total_found': len(results),
            'timestamp': datetime.now().isoformat(),
        }
    
    def browse_categories(self, category: str = None) -> Dict:
        """Browse by category"""
        if not self.category_browser:
            self.category_browser = CategoryBrowser(self.searcher.tools)
        
        return self.category_browser.browse(category)
    
    def get_popular(self, top_n: int = 10) -> List[Dict]:
        """Get popular tools"""
        tools = sorted(
            self.searcher.tools,
            key=lambda t: t.get('usage_count', 0),
            reverse=True
        )[:top_n]
        
        return [
            {
                'name': t['name'],
                'usage_count': t['usage_count'],
                'category': t['category'],
                'description': t['description'],
            }
            for t in tools
        ]
    
    def get_recent(self, days: int = 7, top_n: int = 10) -> List[Dict]:
        """Get recently used tools"""
        cutoff = datetime.now() - timedelta(days=days)
        
        recent = []
        for tool in self.searcher.tools:
            last_used = tool.get('last_used')
            if last_used:
                try:
                    last_dt = datetime.fromisoformat(last_used)
                    if last_dt >= cutoff:
                        recent.append({
                            'tool': tool,
                            'last_used': last_used,
                        })
                except:
                    pass
        
        # Sort by recency
        recent.sort(key=lambda x: x['last_used'], reverse=True)
        
        return [
            {
                'name': r['tool']['name'],
                'last_used': r['last_used'][:16],
                'category': r['tool']['category'],
                'description': r['tool']['description'],
            }
            for r in recent[:top_n]
        ]
    
    def print_results(self, results: Dict):
        """Print search results"""
        print(f"\n🔍 Search: '{results['query']}'")
        print(f"📊 Found {results['total_found']} tools\n")
        
        for i, r in enumerate(results['results'], 1):
            print(f"{i}. {r['name']} ({r['category']})")
            print(f"   📄 {r['description']}")
            print(f"   📊 Score: {r['score']} | {r['match_type']} match")
            if r['highlights']:
                print(f"   🔍 Highlights: {', '.join(r['highlights'])}")
            print(f"   💻 {r['command']}")
            print()
    
    def interactive_mode(self):
        """Run interactive search mode"""
        print("\n🔍 Smart Tool Finder - Interactive Mode")
        print("=" * 60)
        print("Search for tools! (type 'categories' to browse, 'quit' to exit)")
        print("=" * 60)
        
        while True:
            try:
                query = input("\n🔍 Query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if query.lower() == 'categories':
                    result = self.browse_categories()
                    print(f"\n📁 Categories ({result['total_categories']}):")
                    for cat, info in sorted(result['categories'].items()):
                        print(f"   {cat}: {info['count']} tools")
                        print(f"      Top: {', '.join(info['top_tools'][:3])}")
                    continue
                
                if query.lower() == 'popular':
                    popular = self.get_popular(10)
                    print(f"\n🔥 Popular Tools:")
                    for i, t in enumerate(popular, 1):
                        print(f"   {i}. {t['name']} ({t['usage_count']} uses)")
                    continue
                
                if query.lower() == 'recent':
                    recent = self.get_recent(7, 10)
                    print(f"\n🕐 Recent Tools (last 7 days):")
                    for i, t in enumerate(recent, 1):
                        print(f"   {i}. {t['name']} - {t['last_used']}")
                    continue
                
                if not query:
                    continue
                
                # Search
                results = self.find(query)
                self.print_results(results)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Smart Tool Finder")
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--categories', action='store_true', help='Browse categories')
    parser.add_argument('--popular', action='store_true', help='Show popular tools')
    parser.add_argument('--recent', action='store_true', help='Show recent tools')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--top', type=int, default=10, help='Number of results')
    args = parser.parse_args()
    
    finder = SmartToolFinder()
    finder.load_tools(TOOLS_DIR)
    
    if args.interactive:
        finder.interactive_mode()
    
    elif args.search:
        results = finder.find(args.search, args.top)
        finder.print_results(results)
    
    elif args.categories:
        result = finder.browse_categories()
        print(f"\n📁 Categories ({result['total_categories']}):")
        for cat, info in sorted(result['categories'].items()):
            print(f"   {cat}: {info['count']} tools")
    
    elif args.popular:
        popular = finder.get_popular(args.top)
        print(f"\n🔥 Popular Tools:")
        for i, t in enumerate(popular, 1):
            print(f"   {i}. {t['name']}: {t['usage_count']} uses")
    
    elif args.recent:
        recent = finder.get_recent(7, args.top)
        print(f"\n🕐 Recent Tools:")
        for i, t in enumerate(recent, 1):
            print(f"   {i}. {t['name']}: {t['last_used']}")
    
    else:
        finder.interactive_mode()

if __name__ == "__main__":
    main()
