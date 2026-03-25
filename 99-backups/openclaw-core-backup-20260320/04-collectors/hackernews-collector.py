#!/usr/bin/env python3
"""
Hacker News Collector
Collects trending AI/tech stories from Hacker News and saves to Obsidian vault
"""

import feedparser
import requests
from datetime import datetime
import os
import re

# ============ 代理配置 (Clash) ============
# 解决 Python 进程无法继承系统代理的问题
PROXY_ADDR = "http://127.0.0.1:7897"
os.environ['HTTP_PROXY'] = PROXY_ADDR
os.environ['HTTPS_PROXY'] = PROXY_ADDR
# ==========================================

OUTPUT_DIR = r"D:\obsidian\Vault\HackerNews"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_filename(title):
    """Remove invalid characters from filename"""
    title = re.sub(r'[<>:"/\\|？*]', '', title)
    title = title.replace('&', 'and')
    title = title[:100]
    return title.strip()

def fetch_hackernews(max_stories=20):
    """Fetch top stories from Hacker News RSS"""
    rss_url = 'https://hnrss.org/frontpage'

    try:
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        stories = []

        for entry in feed.entries[:max_stories]:
            # Filter for AI/tech related content
            title_lower = entry.title.lower()
            ai_keywords = ['ai', 'machine learning', 'llm', 'gpt', 'claude', 'anthropic',
                          'openai', 'neural', 'deep learning', 'transformer', 'model',
                          'algorithm', 'automation', 'robot', 'agentic']

            is_relevant = any(kw in title_lower for kw in ai_keywords)

            story = {
                'title': entry.title,
                'link': entry.link,
                'description': entry.get('description', ''),
                'published': entry.get('published', ''),
                'author': entry.get('author', 'Unknown'),
                'is_ai_related': is_relevant
            }
            stories.append(story)

        return stories
    except Exception as e:
        print(f"Error fetching Hacker News: {e}")
        return []

def save_story(story):
    """Save story as markdown note"""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    title_slug = sanitize_filename(story['title'])[:50]
    filename = f"{timestamp}-{title_slug}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    tags = "#HackerNews #Tech"
    if story['is_ai_related']:
        tags += " #AI #MachineLearning"

    content = f"""# {story['title']}

## 元数据
- **来源:** Hacker News
- **链接:** {story['link']}
- **作者:** {story['author']}
- **发布时间:** {story['published']}
- **抓取时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **AI 相关:** {'是' if story['is_ai_related'] else '否'}

## 内容

{story['description'] if story['description'] else '*点击链接查看原文*'}

## 标签

{tags}

---
*自动收集*
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filename

def main():
    print("=" * 60)
    print("Hacker News Collector")
    print("=" * 60)

    stories = fetch_hackernews(max_stories=25)

    if not stories:
        print("No stories found or error occurred")
        return

    print(f"Found {len(stories)} stories")

    ai_count = sum(1 for s in stories if s['is_ai_related'])
    print(f"AI-related: {ai_count}")

    new_count = 0
    for story in stories:
        filename = save_story(story)
        new_count += 1
        print(f"  Saved: {filename}")

    print(f"\n[SUCCESS] Collected {new_count} stories ({ai_count} AI-related)")
    print("=" * 60)

if __name__ == '__main__':
    main()
