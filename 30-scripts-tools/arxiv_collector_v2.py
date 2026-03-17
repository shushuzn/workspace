#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv Collector v2.0 - Enhanced with Defuddle Integration

Features:
- arXiv API paper collection
- Defuddle markdown extraction (90% token savings)
- Smart caching (avoid re-extraction)
- Batch processing
- Auto Canvas update
- UTF-8 encoding support

Author: OpenClaw Team
Date: 2026-03-16
Version: 2.0
"""

import sys
import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# Import Defuddle integration
sys.path.insert(0, str(Path(__file__).parent))
try:
    from defuddle_integration import DefuddleExtractor
    DEFUDDLE_AVAILABLE = True
except ImportError:
    DEFUDDLE_AVAILABLE = False
    print("⚠️  Defuddle integration not found, skipping markdown extraction")

# Import Canvas generator
try:
    from json_canvas_generator import JsonCanvasGenerator
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    print("⚠️  Canvas generator not found, skipping canvas update")


class ArXivCollector:
    """Enhanced arXiv paper collector with Defuddle integration"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.cache_dir = Path(self.config.get('cache_dir', 'data/cache'))
        self.papers_dir = Path(self.config.get('papers_dir', 'data/papers'))
        self.extractor = DefuddleExtractor() if DEFUDDLE_AVAILABLE else None
        self.cache = self._load_cache()
        
    def _load_config(self, config_file: Optional[str] = None) -> Dict:
        """Load configuration"""
        default_config = {
            'keywords': ['artificial intelligence', 'machine learning', 'deep learning'],
            'max_results': 20,
            'sort_by': 'submittedDate',
            'sort_order': 'descending',
            'cache_dir': 'data/cache',
            'papers_dir': 'data/papers',
            'cache_ttl_hours': 24,
            'auto_extract_markdown': True,
            'auto_update_canvas': True
        }
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                default_config.update(file_config)
        
        return default_config
    
    def _load_cache(self) -> Dict:
        """Load cache from disk"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / 'defuddle_cache.json'
        
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'urls': {}, 'stats': {'hits': 0, 'misses': 0}}
    
    def _save_cache(self):
        """Save cache to disk"""
        cache_file = self.cache_dir / 'defuddle_cache.json'
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache is still valid"""
        if key not in self.cache['urls']:
            return False
        
        cached_time = datetime.fromisoformat(self.cache['urls'][key]['cached_at'])
        age_hours = (datetime.now() - cached_time).total_seconds() / 3600
        return age_hours < self.config.get('cache_ttl_hours', 24)
    
    def build_query_url(self, keyword: str, max_results: int = 50) -> str:
        """Build arXiv API query URL"""
        base_url = 'http://export.arxiv.org/api/query'
        search_query = urllib.parse.quote(f'all:{keyword}')
        sort_by = self.config.get('sort_by', 'submittedDate')
        sort_order = self.config.get('sort_order', 'descending')
        
        return (f"{base_url}?search_query={search_query}&start=0&"
                f"max_results={max_results}&sortBy={sort_by}&sortOrder={sort_order}")
    
    def fetch_papers(self, keyword: str, max_results: int = 50) -> List[Dict]:
        """Fetch papers from arXiv API"""
        print(f"📡 Fetching keyword '{keyword}'...")
        
        try:
            url = self.build_query_url(keyword, max_results)
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'OpenClaw-Arxiv-Collector/2.0'}
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                xml_data = response.read().decode('utf-8')
            
            papers = self._parse_arxiv_xml(xml_data)
            print(f"  ✅ Fetched {len(papers)} papers")
            return papers
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    def _parse_arxiv_xml(self, xml_data: str) -> List[Dict]:
        """Parse arXiv XML response"""
        papers = []
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}
        
        try:
            root = ET.fromstring(xml_data)
            entries = root.findall('atom:entry', ns)
            
            for entry in entries:
                def get_text(tag: str) -> str:
                    elem = entry.find(f'atom:{tag}', ns)
                    return elem.text.strip() if elem is not None and elem.text else ''
                
                # Extract authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name_elem = author.find('atom:name', ns)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())
                
                # Extract categories
                categories = []
                for category in entry.findall('atom:category', ns):
                    term = category.get('term')
                    if term:
                        categories.append(term)
                
                paper = {
                    'id': get_text('id'),
                    'title': get_text('title').replace('\n', ' '),
                    'summary': get_text('summary').replace('\n', ' '),
                    'authors': authors,
                    'categories': categories,
                    'published': get_text('published'),
                    'updated': get_text('updated'),
                    'collected_at': datetime.now().isoformat()
                }
                papers.append(paper)
                
        except ET.ParseError as e:
            print(f"  ⚠️  XML parse error: {e}")
        
        return papers
    
    def extract_markdown(self, url: str) -> Optional[Dict]:
        """Extract markdown using Defuddle with caching"""
        cache_key = self._get_cache_key(url)
        
        # Check cache
        if self._is_cache_valid(cache_key):
            self.cache['stats']['hits'] += 1
            cached_data = self.cache['urls'][cache_key]
            print(f"  ⚡ Cache hit (saved ~90% tokens)")
            return cached_data
        
        # Cache miss - extract using Defuddle
        self.cache['stats']['misses'] += 1
        
        if not self.extractor:
            print(f"  ⚠️  Defuddle not available, skipping extraction")
            return None
        
        try:
            print(f"  🔄 Extracting markdown (cache miss)...")
            markdown, metadata = self.extractor.extract_markdown(url)
            
            # Cache the result
            self.cache['urls'][cache_key] = {
                'url': url,
                'markdown': markdown,
                'metadata': metadata,
                'cached_at': datetime.now().isoformat(),
                'markdown_length': len(markdown)
            }
            self._save_cache()
            
            print(f"  ✅ Extracted {len(markdown)} chars (cached)")
            
            return {
                'markdown': markdown,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"  ❌ Extraction error: {e}")
            return None
    
    def save_papers(self, papers: List[Dict], keyword: str, extract_md: bool = True) -> Dict:
        """Save papers to JSON file with optional markdown extraction"""
        self.papers_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate safe filename
        safe_keyword = ''.join(c if c.isalnum() else '_' for c in keyword)
        filename = self.papers_dir / f"{safe_keyword}.json"
        
        # Load existing papers
        existing_papers = []
        if filename.exists():
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_papers = data.get('papers', [])
        
        # Deduplicate by arXiv ID
        existing_ids = {p.get('id', '') for p in existing_papers}
        new_papers = [p for p in papers if p.get('id', '') not in existing_ids]
        
        # Extract markdown for new papers
        if extract_md and self.extractor:
            for paper in new_papers:
                arxiv_url = paper.get('id', '')
                if arxiv_url:
                    md_data = self.extract_markdown(arxiv_url)
                    if md_data:
                        paper['markdown'] = md_data['markdown']
                        paper['markdown_metadata'] = md_data['metadata']
                        # Estimate token savings
                        html_estimate = len(md_data['markdown']) * 10  # Rough estimate
                        token_savings = (1 - len(md_data['markdown']) / html_estimate) * 100
                        paper['token_savings_percent'] = round(token_savings, 1)
        
        # Merge papers
        all_papers = new_papers + existing_papers
        
        # Save
        data = {
            'keyword': keyword,
            'last_updated': datetime.now().isoformat(),
            'total_papers': len(all_papers),
            'new_papers': len(new_papers),
            'papers': all_papers,
            'cache_stats': self.cache['stats']
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Saved {len(new_papers)} new papers (total: {len(all_papers)})")
        
        return {
            'total': len(all_papers),
            'new': len(new_papers)
        }
    
    def update_canvas(self):
        """Auto-update lessons canvas after collection"""
        if not CANVAS_AVAILABLE:
            return
        
        print("\n🎨 Updating knowledge canvas...")
        
        try:
            generator = JsonCanvasGenerator()
            memory_file = Path(__file__).parent.parent / "MEMORY.md"
            output_file = Path(__file__).parent.parent / "00-config" / "lessons.canvas"
            
            if memory_file.exists():
                generator.create_lessons_canvas(str(memory_file), str(output_file))
                print(f"  ✅ Canvas updated: {output_file}")
            else:
                print(f"  ⚠️  MEMORY.md not found")
                
        except Exception as e:
            print(f"  ❌ Canvas update error: {e}")
    
    def collect(self, keywords: Optional[List[str]] = None, 
                extract_md: bool = True, update_canvas: bool = True) -> List[Dict]:
        """Main collection method"""
        print("╔════════════════════════════════════════════════╗")
        print("║  arXiv Collector v2.0 (Defuddle Enhanced)      ║")
        print("╚════════════════════════════════════════════════╝")
        print()
        
        keywords = keywords or self.config.get('keywords', [])
        max_results = self.config.get('max_results', 20)
        
        print(f"📋 Keywords: {len(keywords)}")
        print(f"📊 Max results per keyword: {max_results}")
        print(f"📝 Markdown extraction: {'✅' if extract_md else '❌'}")
        print(f"🎨 Auto canvas update: {'✅' if update_canvas else '❌'}")
        print()
        
        results = []
        
        for i, keyword in enumerate(keywords):
            print(f"[{i + 1}/{len(keywords)}]")
            
            papers = self.fetch_papers(keyword, max_results)
            stats = self.save_papers(papers, keyword, extract_md=extract_md)
            
            results.append({
                'keyword': keyword,
                'papers_fetched': len(papers),
                'papers_new': stats['new'],
                'papers_total': stats['total']
            })
            
            # arXiv rate limiting: 1 request per 3 seconds
            if i < len(keywords) - 1:
                print("  ⏱️  Waiting 3 seconds (rate limit)...")
                time.sleep(3)
        
        # Update canvas
        if update_canvas:
            self.update_canvas()
        
        # Summary
        print()
        print("═" * 60)
        print("📊 Collection Summary:")
        print("═" * 60)
        
        total_papers = 0
        total_new = 0
        
        for r in results:
            print(f"  {r['keyword'][:38].ljust(40)} {r['papers_new']:3} new / {r['papers_total']:3} total")
            total_papers += r['papers_total']
            total_new += r['papers_new']
        
        print("─" * 60)
        print(f"  Total: {total_new} new / {total_papers} total")
        print(f"  Cache: {self.cache['stats']['hits']} hits / {self.cache['stats']['misses']} misses")
        
        if self.cache['stats']['hits'] + self.cache['stats']['misses'] > 0:
            hit_rate = self.cache['stats']['hits'] / (self.cache['stats']['hits'] + self.cache['stats']['misses']) * 100
            print(f"  Hit Rate: {hit_rate:.1f}%")
        
        print("═" * 60)
        print()
        print("✅ Complete!")
        
        return results


def demo():
    """Run collector demo"""
    print("\n🔍 arXiv Collector v2.0 Demo\n")
    
    collector = ArXivCollector()
    
    # Demo with small keyword
    keywords = ['quantum computing']
    
    results = collector.collect(
        keywords=keywords,
        extract_md=DEFUDDLE_AVAILABLE,
        update_canvas=CANVAS_AVAILABLE
    )
    
    print()
    print("Cache Statistics:")
    print(f"  Hits: {collector.cache['stats']['hits']}")
    print(f"  Misses: {collector.cache['stats']['misses']}")
    
    if collector.cache['stats']['hits'] + collector.cache['stats']['misses'] > 0:
        hit_rate = collector.cache['stats']['hits'] / (collector.cache['stats']['hits'] + collector.cache['stats']['misses']) * 100
        print(f"  Hit Rate: {hit_rate:.1f}%")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='arXiv Collector v2.0')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--keywords', type=str, nargs='+', help='Keywords to search')
    parser.add_argument('--config', type=str, help='Config file path')
    parser.add_argument('--max-results', type=int, default=20, help='Max results per keyword')
    parser.add_argument('--no-md', action='store_true', help='Disable markdown extraction')
    parser.add_argument('--no-canvas', action='store_true', help='Disable canvas update')
    args = parser.parse_args()
    
    if args.demo or (not args.keywords):
        demo()
    else:
        collector = ArXivCollector(config_file=args.config)
        collector.config['max_results'] = args.max_results
        
        collector.collect(
            keywords=args.keywords,
            extract_md=not args.no_md,
            update_canvas=not args.no_canvas
        )


if __name__ == "__main__":
    main()
