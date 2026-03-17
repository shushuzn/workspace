#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending Collector
Automatically collect trending repositories from GitHub

Usage:
    python github_trending_collector.py [--language LANGUAGE] [--since SINCE] [--limit LIMIT]
"""

import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
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
OUTPUT_FILE = OUTPUT_DIR / "github-trending.json"

class GithubTrendingCollector:
    """Collect trending repositories from GitHub"""
    
    def __init__(self):
        self.base_url = "https://github.com/trending"
        self.languages = [
            "Python", "JavaScript", "TypeScript", 
            "Rust", "Go", "C++", "Jupyter Notebook"
        ]
        self.since_options = ["daily", "weekly", "monthly"]
    
    def _fetch_trending(self, language: str = None, since: str = "daily") -> List[Dict]:
        """Fetch trending repos from GitHub (actual API call)"""
        url = self.base_url
        
        # Build query params
        params = {"since": since}
        if language:
            params["spoken_language_code"] = language
        
        try:
            headers = {
                'Accept': 'text/html,application/xhtml+xml',
                'User-Agent': 'Mozilla/5.0 (OpenClaw Bot)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                repos = self._parse_html(response.text, language, since)
                return repos
            else:
                print(f"[ERROR] GitHub returned {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[ERROR] Collection failed: {e}")
            return []
    
    def collect(self, language: str = None, since: str = "daily", 
                limit: int = 25) -> List[Dict]:
        """Collect trending repos (with caching)"""
        # Create cache key
        cache_key = f"github_trending_{language or 'all'}_{since}"
        
        if CACHE_ENABLED and cache:
            # Use smart cache with auto-refresh
            repos = cache.get(cache_key, lambda: self._fetch_trending(language, since), ttl=1800)
            return repos[:limit] if repos else []
        else:
            # No cache, fetch directly
            repos = self._fetch_trending(language, since)
            return repos[:limit]
    
    def _parse_html(self, html_text: str, language: str, since: str) -> List[Dict]:
        """Parse GitHub trending HTML"""
        repos = []
        
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            articles = soup.find_all('article', class_='Box-row')
            
            for article in articles:
                # Repo name
                h2 = article.find('h2', class_='h3 lh-condensed')
                if not h2:
                    continue
                
                link = h2.find('a')
                if not link:
                    continue
                
                repo_name = link.get('href').strip('/')
                repo_url = f"https://github.com{link.get('href')}"
                
                # Description
                desc_p = article.find('p', class_='col-9 color-fg-muted')
                description = desc_p.get_text(strip=True) if desc_p else ""
                
                # Language
                lang_span = article.find('span', itemprop="programmingLanguage")
                lang = lang_span.get_text(strip=True) if lang_span else "Unknown"
                
                # Stars
                star_svg = article.find('svg', {'aria-label': 'stars'})
                stars = 0
                if star_svg and star_svg.parent:
                    star_text = star_svg.parent.get_text(strip=True)
                    stars = self._parse_number(star_text)
                
                # Forks
                fork_svg = article.find('svg', {'aria-label': 'forks'})
                forks = 0
                if fork_svg and fork_svg.parent:
                    fork_text = fork_svg.parent.get_text(strip=True)
                    forks = self._parse_number(fork_text)
                
                repo = {
                    'name': repo_name,
                    'url': repo_url,
                    'description': description,
                    'language': lang,
                    'stars': stars,
                    'forks': forks,
                    'trending_since': since,
                    'filter_language': language,
                    'collected_at': datetime.now().isoformat(),
                    'source': 'github_trending'
                }
                
                repos.append(repo)
                
        except Exception as e:
            print(f"[ERROR] Parse failed: {e}")
        
        return repos
    
    def _parse_number(self, text: str) -> int:
        """Parse number string (e.g., '1.2k' -> 1200)"""
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
    
    def collect_all_languages(self, since: str = "daily", limit_per_lang: int = 10) -> List[Dict]:
        """Collect from all languages"""
        all_repos = []
        
        for lang in self.languages:
            print(f"Collecting {lang}...")
            repos = self.collect(language=lang, since=since, limit=limit_per_lang)
            all_repos.extend(repos)
            print(f"  ✅ {len(repos)} repos")
        
        return all_repos
    
    def save(self, repos: List[Dict], output_file: Path = None):
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
                existing = data.get('repositories', [])
        
        # Merge (avoid duplicates by URL)
        existing_urls = {r.get('url') for r in existing}
        new_repos = [r for r in repos if r.get('url') not in existing_urls]
        all_repos = existing + new_repos
        
        # Sort by stars
        all_repos.sort(key=lambda x: x.get('stars', 0), reverse=True)
        
        # Save
        output_data = {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'total_repositories': len(all_repos),
            'repositories': all_repos
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(new_repos)} new repos to {output_file}")
        print(f"   Total: {len(all_repos)} repositories")
    
    def preview(self, repos: List[Dict]):
        """Preview in console"""
        print(f"\n📊 GitHub Trending ({len(repos)} repos)\n")
        
        for i, repo in enumerate(repos[:10], 1):
            print(f"{i}. {repo['name']}")
            print(f"   {repo['description'][:80]}")
            print(f"   ⭐ {repo['stars']} | 🔱 {repo['forks']} | 💻 {repo['language']}")
            print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Trending Collector')
    parser.add_argument('--language', '-l', type=str, help='Filter by language')
    parser.add_argument('--since', '-s', type=str, default='daily', 
                       choices=['daily', 'weekly', 'monthly'], help='Time period')
    parser.add_argument('--limit', '-n', type=int, default=25, help='Max repos')
    parser.add_argument('--all-langs', action='store_true', help='Collect all languages')
    parser.add_argument('--preview', action='store_true', help='Preview in console')
    parser.add_argument('--save', action='store_true', help='Save to file')
    
    args = parser.parse_args()
    
    collector = GithubTrendingCollector()
    
    if args.all_langs:
        repos = collector.collect_all_languages(since=args.since, limit_per_lang=args.limit)
    else:
        repos = collector.collect(language=args.language, since=args.since, limit=args.limit)
    
    if args.preview or not args.save:
        collector.preview(repos)
    
    if args.save:
        collector.save(repos)


if __name__ == '__main__':
    main()
