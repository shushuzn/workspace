#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medium Article Collector
Automatically collect AI/tech articles from Medium

Usage:
    python medium_article_collector.py [--topic TOPIC] [--limit LIMIT]
"""

import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from bs4 import BeautifulSoup

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Import cache manager
try:
    from cache_manager import CacheManager
    CACHE_ENABLED = True
    cache = CacheManager()
except ImportError:
    CACHE_ENABLED = False
    cache = None

# Config
OUTPUT_DIR = Path(r"D:\OpenClaw\workspace\40-collectors\collected")
OUTPUT_FILE = OUTPUT_DIR / "medium-articles.json"

class MediumArticleCollector:
    """Collect articles from Medium"""
    
    def __init__(self):
        self.base_url = "https://medium.com/tag"
        self.topics = [
            "artificial-intelligence",
            "machine-learning",
            "data-science",
            "programming",
            "technology",
            "startup"
        ]
    
    def _fetch_articles(self, topic: str, limit: int = 25) -> List[Dict]:
        """Fetch articles from Medium (actual API call)"""
        url = f"{self.base_url}/{topic}/latest"
        
        try:
            headers = {
                'Accept': 'text/html,application/xhtml+xml',
                'User-Agent': 'Mozilla/5.0 (OpenClaw Bot)'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                articles = self._parse_html(response.text, topic)
                return articles[:limit]
            else:
                print(f"[ERROR] Medium returned {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[ERROR] Collection failed: {e}")
            return []
    
    def collect(self, topic: str, limit: int = 25) -> List[Dict]:
        """Collect articles from Medium (with caching)"""
        # Create cache key
        cache_key = f"medium_articles_{topic}"
        
        if CACHE_ENABLED and cache:
            # Use smart cache with auto-refresh
            return cache.get(cache_key, lambda: self._fetch_articles(topic, limit), ttl=1800)
        else:
            # No cache, fetch directly
            return self._fetch_articles(topic, limit)
    
    def _parse_html(self, html_text: str, topic: str) -> List[Dict]:
        """Parse Medium HTML"""
        articles = []
        
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            
            # Medium article cards
            article_divs = soup.find_all('div', {'data-testid': 'post-article'})
            
            for div in article_divs:
                # Title
                title_elem = div.find('h2')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # Link
                link_elem = div.find('a', href=True)
                if not link_elem:
                    continue
                article_url = link_elem['href']
                
                # Author
                author_elem = div.find('a', {'data-testid': 'post-author-link'})
                author = author_elem.get_text(strip=True) if author_elem else "Unknown"
                
                # Published time
                time_elem = div.find('time')
                published = time_elem.get('datetime', '') if time_elem else ""
                
                # Claps (likes)
                clap_elem = div.find('button', {'aria-label': lambda x: x and 'clap' in x.lower()})
                claps = 0
                if clap_elem:
                    clap_text = clap_elem.get_text(strip=True)
                    claps = self._parse_number(clap_text)
                
                # Reading time
                read_time_elem = div.find('span', string=lambda x: x and 'min read' in x.lower())
                reading_time = read_time_elem.get_text(strip=True) if read_time_elem else ""
                
                article = {
                    'title': title,
                    'url': article_url,
                    'author': author,
                    'topic': topic,
                    'published': published,
                    'claps': claps,
                    'reading_time': reading_time,
                    'collected_at': datetime.now().isoformat(),
                    'source': 'medium'
                }
                
                articles.append(article)
                
        except Exception as e:
            print(f"[ERROR] Parse failed: {e}")
        
        return articles
    
    def _parse_number(self, text: str) -> int:
        """Parse number string"""
        try:
            text = text.strip().lower()
            if 'k' in text:
                return int(float(text.replace('k', '')) * 1000)
            elif 'm' in text:
                return int(float(text.replace('m', '')) * 1000000)
            else:
                return int(float(text))
        except:
            return 0
    
    def collect_all_topics(self, limit_per_topic: int = 10) -> List[Dict]:
        """Collect from all topics"""
        all_articles = []
        
        for topic in self.topics:
            print(f"Collecting {topic}...")
            articles = self.collect(topic=topic, limit=limit_per_topic)
            all_articles.extend(articles)
            print(f"  ✅ {len(articles)} articles")
        
        return all_articles
    
    def save(self, articles: List[Dict], output_file: Path = None):
        """Save to JSON file"""
        if output_file is None:
            output_file = OUTPUT_FILE
        
        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing
        existing = []
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing = data.get('articles', [])
        
        # Merge (avoid duplicates by URL)
        existing_urls = {a.get('url') for a in existing}
        new_articles = [a for a in articles if a.get('url') not in existing_urls]
        all_articles = existing + new_articles
        
        # Sort by claps
        all_articles.sort(key=lambda x: x.get('claps', 0), reverse=True)
        
        # Save
        output_data = {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'total_articles': len(all_articles),
            'articles': all_articles
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(new_articles)} new articles to {output_file}")
        print(f"   Total: {len(all_articles)} articles")
    
    def preview(self, articles: List[Dict]):
        """Preview in console"""
        print(f"\n📰 Medium Articles ({len(articles)} articles)\n")
        
        for i, article in enumerate(articles[:10], 1):
            print(f"{i}. {article['title']}")
            print(f"   by {article['author']} | 👏 {article['claps']} | ⏱️ {article['reading_time']}")
            print(f"   {article['url'][:70]}")
            print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Medium Article Collector')
    parser.add_argument('--topic', '-t', type=str, help='Filter by topic')
    parser.add_argument('--limit', '-n', type=int, default=25, help='Max articles')
    parser.add_argument('--all-topics', action='store_true', help='Collect all topics')
    parser.add_argument('--preview', action='store_true', help='Preview in console')
    parser.add_argument('--save', action='store_true', help='Save to file')
    
    args = parser.parse_args()
    
    collector = MediumArticleCollector()
    
    if args.all_topics:
        articles = collector.collect_all_topics(limit_per_topic=args.limit)
    else:
        topic = args.topic or 'artificial-intelligence'
        articles = collector.collect(topic=topic, limit=args.limit)
    
    if args.preview or not args.save:
        collector.preview(articles)
    
    if args.save:
        collector.save(articles)


if __name__ == '__main__':
    main()
