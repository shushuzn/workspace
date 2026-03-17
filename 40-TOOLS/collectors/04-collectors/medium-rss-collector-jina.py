# medium-rss-collector-jina.py - 混合使用 Jina AI + feedparser
import feedparser
import json
import os
import re
import time
import sqlite3
import subprocess
import sys
import requests
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

CONFIG_PATH = r"D:\scripts\medium-rss-config.json"
DB_PATH = r"D:\scripts\medium_seen_rss.db"
LOG_PATH = r"D:\scripts\medium_rss.log"
OBSIDIAN_OUT_DIR = r"D:\obsidian\Vault\Medium"

MEDIUM_URL_RE = re.compile(r"https?://medium\.com/[^\s\?\"]+", re.I)

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except: pass

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS seen (
        url TEXT PRIMARY KEY,
        title TEXT,
        fetched_at TEXT
    )""")
    conn.commit()
    return conn

def is_seen(conn, url):
    c = conn.cursor()
    c.execute("SELECT 1 FROM seen WHERE url=?", (url,))
    return c.fetchone() is not None

def mark_seen(conn, url, title):
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO seen VALUES (?, ?, ?)", (url, title, datetime.now().isoformat()))
    conn.commit()

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def fetch_medium_via_jina(conn, feed_info, max_articles):
    """Medium feeds: 使用 Jina AI 阅读器"""
    url = feed_info["url"]
    name = feed_info["name"]
    log(f"Fetching (Jina): {name}")
    
    try:
        jina_url = 'https://r.jina.ai/' + url
        response = requests.get(jina_url, timeout=30)
        content = response.text
        
        # 提取标题和链接
        articles = []
        lines = content.split('\n')
        current_title = None
        
        for line in lines:
            if line.startswith('<![CDATA[') and ']]>' in line:
                current_title = line.replace('<![CDATA[', '').replace(']]>', '').strip()
            elif 'medium.com/p/' in line and current_title:
                match = re.search(r'(https://medium\.com/p/[a-f0-9]+)', line)
                if match:
                    article_url = match.group(1)
                    if not is_seen(conn, article_url):
                        articles.append({
                            "url": article_url,
                            "title": current_title[:200],
                            "published": ""
                        })
                        mark_seen(conn, article_url, current_title[:200])
                        if len(articles) >= max_articles:
                            break
                    current_title = None
        
        log(f"  Found {len(articles)} new articles")
        return articles
        
    except Exception as e:
        log(f"  Error: {e}")
        return []

def fetch_feed_direct(conn, feed_info, max_articles):
    """非 Medium feeds: 使用 feedparser 直接解析"""
    url = feed_info["url"]
    name = feed_info["name"]
    log(f"Fetching: {name}")
    
    try:
        feed = feedparser.parse(url)
        
        if not feed.entries:
            log(f"  No entries in feed")
            return []
        
        articles = []
        for entry in feed.entries[:max_articles * 2]:
            article_url = entry.get('link', '')
            
            if not article_url:
                continue
            
            if is_seen(conn, article_url):
                continue
            
            title = entry.get('title', f"Article ({article_url.split('/')[-1][:30]})")
            published = entry.get('published', '')
            
            articles.append({
                "url": article_url,
                "title": title,
                "published": published
            })
            
            mark_seen(conn, article_url, title)
            
            if len(articles) >= max_articles:
                break
        
        log(f"  Found {len(articles)} new articles")
        return articles
        
    except Exception as e:
        log(f"  Error: {e}")
        return []

def process_article(article):
    log(f"Processing: {article['title'][:60]}")
    save_to_obsidian(article["url"], article["title"])
    log(f"  -> Saved to Obsidian")

def save_to_obsidian(url, title=""):
    os.makedirs(OBSIDIAN_OUT_DIR, exist_ok=True)
    stem = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{url.split('/')[-1][:50]}"
    path = os.path.join(OBSIDIAN_OUT_DIR, f"{stem}.md")
    content = f"""---
url: {url}
title: {title}
fetched: {datetime.now().isoformat()}
status: pending_analysis
---

# {title or "Article"}

[原文]({url})

---
*待分析 - 由 RSS Collector 自动收集*
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def is_medium_feed(url):
    return 'medium.com/feed' in url or 'medium.com/topic' in url

def main():
    log("=" * 50)
    log("RSS Collector (Hybrid: Jina + feedparser) started")
    config = load_config()
    conn = init_db()
    
    all_articles = []
    for feed_info in config["feeds"]:
        if feed_info.get("enabled", True):
            url = feed_info["url"]
            if is_medium_feed(url):
                articles = fetch_medium_via_jina(conn, feed_info, config["maxArticlesPerRun"] - len(all_articles))
            else:
                articles = fetch_feed_direct(conn, feed_info, config["maxArticlesPerRun"] - len(all_articles))
            
            all_articles.extend(articles)
            if len(all_articles) >= config["maxArticlesPerRun"]:
                break
    
    log(f"Total new articles: {len(all_articles)}")
    
    for article in all_articles[:config["maxArticlesPerRun"]]:
        process_article(article)
    
    conn.close()
    log("Complete")
    log("=" * 50)

if __name__ == "__main__":
    main()
