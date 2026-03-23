#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HackerNews Comment Analyzer v1
评论分析 - 提取高价值讨论
"""

import requests
from datetime import datetime
from pathlib import Path

# 配置
HN_BASE_URL = "https://hacker-news.firebaseio.com/v0"
OUTPUT_DIR = Path(r"D:\obsidian\Vault\HackerNews\Comments")

def get_top_stories(limit=10):
    """获取热门故事"""
    url = f"{HN_BASE_URL}/topstories.json"
    response = requests.get(url, timeout=10)
    return response.json()[:limit]

def get_story_comments(story_id, max_comments=50):
    """获取故事评论"""
    url = f"{HN_BASE_URL}/item/{story_id}.json"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return []
    
    story = response.json()
    kids = story.get('kids', [])[:max_comments]
    
    comments = []
    for kid_id in kids[:20]:  # 限制前 20 条评论
        comment_url = f"{HN_BASE_URL}/item/{kid_id}.json"
        try:
            comment_resp = requests.get(comment_url, timeout=5)
            if comment_resp.status_code == 200:
                comment = comment_resp.json()
                if comment and comment.get('text'):
                    comments.append({
                        'id': kid_id,
                        'author': comment.get('by', 'anonymous'),
                        'text': comment.get('text', '')[:500],
                        'score': comment.get('score', 0),
                    })
        except Exception:
            continue
    
    return comments

def analyze_comments(comments):
    """分析评论质量"""
    high_value = []
    
    for comment in comments:
        # 简单质量评估
        score = comment.get('score', 0)
        text_len = len(comment.get('text', ''))
        
        if score > 10 or text_len > 200:
            comment['quality'] = 'high'
            high_value.append(comment)
        else:
            comment['quality'] = 'normal'
    
    return high_value

def save_comments(story_id, comments, high_value):
    """保存评论分析"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = f"story-{story_id}-comments-{date_str}.md"
    filepath = OUTPUT_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# HN Story {story_id} 评论分析\n\n")
        f.write(f"**分析时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**总评论:** {len(comments)} | **高价值:** {len(high_value)}\n\n")
        f.write("---\n\n")
        
        if high_value:
            f.write("## 💎 高价值评论\n\n")
            for i, comment in enumerate(high_value, 1):
                f.write(f"### {i}. u/{comment['author']}\n\n")
                f.write(f"**分数:** {comment['score']}\n\n")
                f.write(f"{comment['text']}\n\n")
                f.write("---\n\n")
    
    print(f"  [OK] Story {story_id}: {len(high_value)}/{len(comments)} high value comments")
    return filepath

def analyze_top_stories():
    """分析热门故事评论"""
    print("=" * 60)
    print("HN Comment Analyzer v1")
    print("=" * 60)
    
    print("\n[1/3] Fetching top stories...")
    story_ids = get_top_stories(5)
    print(f"  Found {len(story_ids)} stories")
    
    print("\n[2/3] Analyzing comments...")
    total_comments = 0
    total_high_value = 0
    
    for story_id in story_ids:
        comments = get_story_comments(story_id)
        if comments:
            high_value = analyze_comments(comments)
            save_comments(story_id, comments, high_value)
            total_comments += len(comments)
            total_high_value += len(high_value)
    
    print("\n[3/3] Summary...")
    print(f"  Total comments: {total_comments}")
    print(f"  High value: {total_high_value}")
    
    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    analyze_top_stories()
