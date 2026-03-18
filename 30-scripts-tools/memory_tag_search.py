#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Tag Search - 记忆标签搜索

基于索引的快速标签搜索工具
支持标签过滤、关键词搜索、组合查询

使用:
  py memory_tag_search.py --tag critical
  py memory_tag_search.py --tag system tool
  py memory_tag_search.py --query "research"
  py memory_tag_search.py --list-tags
"""

import sys
import json
import argparse
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
INDEX_FILE = MEMORY_DIR / 'memory_index.json'
MEMORY_FILE = WORKSPACE / 'MEMORY.md'


class MemoryTagSearch:
    def __init__(self):
        self.index = None
        self.content_lines = []
    
    def load_index(self) -> bool:
        """加载索引"""
        if not INDEX_FILE.exists():
            print(f"[ERROR] Index not found: {INDEX_FILE}")
            print(f"[HINT] Run: py memory_index_generator.py --rebuild")
            return False
        
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            self.index = json.load(f)
        
        if MEMORY_FILE.exists():
            self.content_lines = MEMORY_FILE.read_text(encoding='utf-8').split('\n')
        
        return True
    
    def search(self, tags=None, query=None, linked_to=None) -> list:
        """搜索记忆"""
        if not self.index:
            return []
        
        results = []
        
        # Strip quotes from query if present
        if query:
            query = query.strip('"\'')
        
        for entry in self.index['entries']:
            match = True
            
            if tags:
                search_tags = [t if t.startswith('#') else f'#{t}' for t in tags]
                if not any(tag in entry['tags'] for tag in search_tags):
                    match = False
            
            if query and match:
                if query.lower() not in entry['title'].lower():
                    match = False
            
            if linked_to and match:
                if linked_to not in entry['backlinks']:
                    match = False
            
            if match:
                results.append(entry)
        
        return results
    
    def display_results(self, results, show_snippet=False):
        """显示结果"""
        if not results:
            print("[INFO] No results found")
            return
        
        print(f"\n{'='*60}")
        print(f"[RESULTS] Found {len(results)} entries")
        print(f"{'='*60}\n")
        
        for entry in results:
            print(f"[{entry['id']}] {entry['title']}")
            print(f"   Line: {entry['line_start']}-{entry['line_end']}")
            
            if entry['tags']:
                print(f"   Tags: {' '.join(entry['tags'])}")
            
            if entry['backlinks']:
                print(f"   Links: {', '.join(entry['backlinks'])}")
            
            if show_snippet and self.content_lines:
                start = entry['line_start'] - 1
                end = min(start + 3, len(self.content_lines))
                if start < len(self.content_lines):
                    print(f"   Snippet:")
                    for i in range(start, end):
                        line = self.content_lines[i][:80]
                        if line.strip():
                            print(f"     {line}")
            
            print()
    
    def list_tags(self):
        """列出所有标签"""
        if not self.index:
            return
        
        print(f"\n{'='*60}")
        print(f"[TAGS] Available tags ({len(self.index['tag_index'])} total)")
        print(f"{'='*60}\n")
        
        for tag, entries in sorted(self.index['tag_index'].items()):
            print(f"  #{tag:20} ({len(entries):2} entries)")


def main():
    parser = argparse.ArgumentParser(description='Memory Tag Search')
    parser.add_argument('--tag', '-t', nargs='+', help='Search by tags')
    parser.add_argument('--query', '-q', help='Search by keyword')
    parser.add_argument('--linked-to', '-l', help='Find entries linked to ID')
    parser.add_argument('--list-tags', action='store_true', help='List all tags')
    parser.add_argument('--snippet', '-s', action='store_true', help='Show snippets')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    search = MemoryTagSearch()
    
    if not search.load_index():
        return 1
    
    if args.list_tags:
        search.list_tags()
        return 0
    
    results = search.search(
        tags=args.tag,
        query=args.query,
        linked_to=args.linked_to
    )
    
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        search.display_results(results, show_snippet=args.snippet)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
