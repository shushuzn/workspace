#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Watcher v1
使用 Nitter RSS 监听 Twitter 账号 (无需 API Key)
"""

import feedparser
import requests
from datetime import datetime
import os
from pathlib import Path

# 配置
TWITTER_SAVE_DIR = Path(r"D:\obsidian\Vault\Twitter")
CHECK_INTERVAL_HOURS = 4  # 每 4 小时检查一次

# 监听账号列表 (AI 研究者)
ACCOUNTS = [
    "elonmusk",
    "sama",
    "DemisHassabis",
    "AndrewYNg",
    "ylecun",
    "karpathy",
    "jeremyphoward",
    "fchollet",
    "hardmaru",
    "natfriedman",
]

# Nitter 实例 (多个备选)
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacy.com.de",
    "https://nitter.lunar.icu",
]

def get_nitter_url(username):
    """获取 Nitter RSS 链接"""
    for instance in NITTER_INSTANCES:
        try:
            url = f"{instance}/{username}/rss"
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return url
        except:
            continue
    return None

def fetch_tweets(username):
    """获取用户推文"""
    rss_url = get_nitter_url(username)
    if not rss_url:
        print(f"[WARN] No working Nitter instance for @{username}")
        return []

    feed = feedparser.parse(rss_url)
    tweets = []

    for entry in feed.entries[:20]:  # 最近 20 条
        tweet = {
            'username': username,
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'content': entry.summary if hasattr(entry, 'summary') else '',
        }
        tweets.append(tweet)

    return tweets

def save_tweets(tweets, username):
    """保存推文到文件"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    save_dir = TWITTER_SAVE_DIR / date_str
    save_dir.mkdir(parents=True, exist_ok=True)

    # 保存为 Markdown
    filename = f"{username}-{date_str}.md"
    filepath = save_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# @{username} - {date_str}\n\n")
        f.write(f"**来源:** Twitter (via Nitter)\n")
        f.write(f"**收集时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        for i, tweet in enumerate(tweets, 1):
            f.write(f"## {i}. {tweet['title']}\n\n")
            f.write(f"**时间:** {tweet['published']}\n")
            f.write(f"**链接:** {tweet['link']}\n\n")
            f.write(f"{tweet['content']}\n\n")
            f.write("---\n\n")

    print(f"  [OK] Saved {len(tweets)} tweets to {filename}")
    return filepath

def monitor_accounts():
    """监听所有账号"""
    print("=" * 60)
    print("Twitter Watcher v1 - Nitter RSS")
    print("=" * 60)

    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"\nDate: {date_str}")
    print(f"Accounts: {len(ACCOUNTS)}")
    print(f"Check interval: {CHECK_INTERVAL_HOURS} hours")
    print("-" * 60)

    total_tweets = 0

    for username in ACCOUNTS:
        print(f"\nFetching @{username}...")
        try:
            tweets = fetch_tweets(username)
            if tweets:
                save_tweets(tweets, username)
                total_tweets += len(tweets)
        except Exception as e:
            print(f"  [ERROR] {e}")

    print("-" * 60)
    print(f"\n[COMPLETE] Total tweets: {total_tweets}")
    print(f"Save dir: {TWITTER_SAVE_DIR / date_str}")
    print("=" * 60)

    return total_tweets

if __name__ == "__main__":
    monitor_accounts()
