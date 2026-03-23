#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HackerNews Watcher v1
使用 Firebase API 监听 HackerNews 热门文章
"""

import requests
from datetime import datetime
import os
from pathlib import Path

# 配置
HN_SAVE_DIR = Path(r"D:\obsidian\Vault\HackerNews")
CHECK_INTERVAL_HOURS = 2  # 每 2 小时检查一次
MAX_STORIES = 30  # 每次获取 30 篇

# Firebase API (HackerNews 官方)
HN_BASE_URL = "https://hacker-news.firebaseio.com/v0"

def get_top_stories(limit=30):
    """获取热门故事"""
    url = f"{HN_BASE_URL}/topstories.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()[:limit]

def get_story_details(story_id):
    """获取故事详情"""
    url = f"{HN_BASE_URL}/item/{story_id}.json"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_hn_stories():
    """获取 HN 故事列表"""
    print(f"Fetching top {MAX_STORIES} stories...")
    story_ids = get_top_stories(MAX_STORIES)

    stories = []
    for story_id in story_ids:
        try:
            story = get_story_details(story_id)
            if story and 'url' in story:  # 只保留有链接的
                stories.append(story)
        except Exception as e:
            print(f"  [WARN] Story {story_id}: {e}")

    return stories

def classify_story(story):
    """AI 分类故事 (简化版：基于标题关键词)"""
    title = story.get('title', '').lower()

    ai_keywords = ['ai', 'machine learning', 'llm', 'gpt', 'transformer', 'neural']
    ml_keywords = ['python', 'data', 'algorithm', 'model', 'training']

    score = 0
    tags = []

    for kw in ai_keywords:
        if kw in title:
            score += 2
            tags.append(kw.upper())

    for kw in ml_keywords:
        if kw in title:
            score += 1
            tags.append(kw.title())

    # 优先级评分 (1-5)
    priority = min(5, max(1, score))

    return {
        'tags': tags,
        'priority': priority,
        'is_ai_related': score >= 2
    }

def save_stories(stories):
    """保存故事到文件"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    save_dir = HN_SAVE_DIR / date_str
    save_dir.mkdir(parents=True, exist_ok=True)

    # 保存为 Markdown
    filename = f"hn-daily-{date_str}.md"
    filepath = save_dir / filename

    ai_stories = []
    other_stories = []

    for story in stories:
        classification = classify_story(story)
        story['classification'] = classification

        if classification['is_ai_related']:
            ai_stories.append(story)
        else:
            other_stories.append(story)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# HackerNews Daily - {date_str}\n\n")
        f.write(f"**收集时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**总数:** {len(stories)} | **AI 相关:** {len(ai_stories)}\n\n")
        f.write("---\n\n")

        # AI 相关文章
        if ai_stories:
            f.write("## 🤖 AI/ML 相关文章\n\n")
            for i, story in enumerate(ai_stories, 1):
                f.write(f"### {i}. {story['title']}\n\n")
                f.write(f"**分数:** {story.get('score', 'N/A')} | **评论:** {story.get('descendants', 0)}\n")
                f.write(f"**链接:** [{story.get('url', 'N/A')}]({story.get('url', 'N/A')})\n")
                f.write(f"**标签:** {', '.join(story['classification']['tags'])}\n")
                f.write(f"**优先级:** {'⭐' * story['classification']['priority']}\n\n")
                f.write("---\n\n")

        # 其他文章
        if other_stories:
            f.write("## 📰 其他文章\n\n")
            for i, story in enumerate(other_stories, 1):
                f.write(f"{i}. [{story['title']}]({story.get('url', '#')}) - {story.get('score', 'N/A')} 分\n\n")

    print(f"  [OK] Saved {len(stories)} stories to {filename}")
    print(f"       AI/ML related: {len(ai_stories)}")
    return filepath

def monitor_hn():
    """监听 HackerNews"""
    print("=" * 60)
    print("HackerNews Watcher v1 - Firebase API")
    print("=" * 60)

    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"\nDate: {date_str}")
    print(f"Check interval: {CHECK_INTERVAL_HOURS} hours")
    print("-" * 60)

    stories = fetch_hn_stories()
    save_stories(stories)

    print("-" * 60)
    print(f"\n[COMPLETE] Total: {len(stories)} stories")
    print(f"Save dir: {HN_SAVE_DIR / date_str}")
    print("=" * 60)

    return len(stories)

if __name__ == "__main__":
    monitor_hn()
