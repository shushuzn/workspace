#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reddit Watcher v1
监听 Reddit 技术版块热门讨论
"""

import requests
from datetime import datetime
import os
from pathlib import Path

# 配置
REDDIT_SAVE_DIR = Path(r"D:\obsidian\Vault\Reddit")
CHECK_INTERVAL_HOURS = 6  # 每 6 小时检查一次

# 监听的技术版块
SUBREDDITS = [
    "MachineLearning",
    "artificial",
    "deeplearning",
    "reinforcementlearning",
    "LocalLLaMA",
]

# Reddit API (免认证访问公开内容)
REDDIT_BASE_URL = "https://www.reddit.com/r"

def get_hot_posts(subreddit, limit=20):
    """获取热门帖子 (使用旧版 Reddit API)"""
    # 使用旧版 API (无需认证)
    url = f"https://old.reddit.com/r/{subreddit}/hot.json"
    params = {'limit': limit}

    try:
        response = requests.get(url, params=params, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            print(f"  [WARN] {subreddit}: API error")
            return []

        posts = []
        for child in data.get('data', {}).get('children', []):
            post = child.get('data', {})
            posts.append({
                'subreddit': subreddit,
                'title': post.get('title', ''),
                'score': post.get('score', 0),
                'num_comments': post.get('num_comments', 0),
                'url': post.get('url', ''),
                'permalink': f"https://reddit.com{post.get('permalink', '')}",
                'author': post.get('author', 'deleted'),
                'created_utc': post.get('created_utc', 0),
                'selftext': post.get('selftext', '')[:500],
            })

        return posts
    except Exception as e:
        print(f"  [WARN] {subreddit}: {e}")
        return []

def classify_post(post):
    """内容质量评估"""
    title = post.get('title', '').lower()
    score = post.get('score', 0)
    comments = post.get('num_comments', 0)

    # 关键词匹配
    ai_keywords = ['llm', 'transformer', 'gpt', 'bert', 'diffusion', 'rlhf']
    ml_keywords = ['pytorch', 'tensorflow', 'training', 'fine-tuning', 'prompt']

    quality_score = 0
    tags = []

    # 基于互动评分
    if score > 100:
        quality_score += 2
    if score > 500:
        quality_score += 2
    if comments > 50:
        quality_score += 1

    # 关键词匹配
    for kw in ai_keywords:
        if kw in title:
            quality_score += 1
            tags.append(kw.upper())

    for kw in ml_keywords:
        if kw in title:
            quality_score += 1
            tags.append(kw.title())

    # 优先级 (1-5)
    priority = min(5, max(1, quality_score))

    return {
        'tags': tags,
        'priority': priority,
        'is_high_quality': quality_score >= 4,
        'quality_score': quality_score
    }

def identify_experts(posts):
    """识别专家用户"""
    author_stats = {}

    for post in posts:
        author = post.get('author', 'deleted')
        if author == 'deleted':
            continue

        if author not in author_stats:
            author_stats[author] = {
                'posts': 0,
                'total_score': 0,
                'total_comments': 0
            }

        author_stats[author]['posts'] += 1
        author_stats[author]['total_score'] += post.get('score', 0)
        author_stats[author]['total_comments'] += post.get('num_comments', 0)

    # 计算专家分数
    experts = []
    for author, stats in author_stats.items():
        expert_score = (
            stats['posts'] * 1 +
            stats['total_score'] * 0.1 +
            stats['total_comments'] * 0.05
        )

        if expert_score > 10:  # 阈值
            experts.append({
                'username': author,
                'expert_score': round(expert_score, 2),
                'posts': stats['posts'],
                'avg_score': round(stats['total_score'] / stats['posts'], 1)
            })

    # 按专家分数排序
    experts.sort(key=lambda x: x['expert_score'], reverse=True)
    return experts[:10]  # 返回前 10 名

def save_posts(posts, subreddit):
    """保存帖子到文件"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    save_dir = REDDIT_SAVE_DIR / date_str
    save_dir.mkdir(parents=True, exist_ok=True)

    # 分类
    high_quality = []
    other = []

    for post in posts:
        classification = classify_post(post)
        post['classification'] = classification

        if classification['is_high_quality']:
            high_quality.append(post)
        else:
            other.append(post)

    # 保存为 Markdown
    filename = f"{subreddit}-{date_str}.md"
    filepath = save_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# r/{subreddit} - {date_str}\n\n")
        f.write(f"**收集时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**总数:** {len(posts)} | **高质量:** {len(high_quality)}\n\n")
        f.write("---\n\n")

        # 高质量帖子
        if high_quality:
            f.write("## 🔥 高质量讨论\n\n")
            for i, post in enumerate(high_quality, 1):
                f.write(f"### {i}. {post['title']}\n\n")
                f.write(f"**分数:** {post['score']} | **评论:** {post['num_comments']}\n")
                f.write(f"**作者:** u/{post['author']}\n")
                f.write(f"**链接:** [Reddit]({post['permalink']})\n")
                f.write(f"**标签:** {', '.join(post['classification']['tags'])}\n")
                f.write(f"**优先级:** {'⭐' * post['classification']['priority']}\n\n")
                if post['selftext']:
                    f.write(f"{post['selftext']}...\n\n")
                f.write("---\n\n")

        # 其他帖子
        if other:
            f.write("## 📰 其他帖子\n\n")
            for i, post in enumerate(other, 1):
                f.write(f"{i}. [{post['title']}]({post['permalink']}) - {post['score']} 分\n\n")

    print(f"  [OK] r/{subreddit}: Saved {len(posts)} posts ({len(high_quality)} high quality)")
    return filepath

def monitor_reddit():
    """监听 Reddit"""
    print("=" * 60)
    print("Reddit Watcher v1 - Technical Subreddits")
    print("=" * 60)

    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"\nDate: {date_str}")
    print(f"Subreddits: {len(SUBREDDITS)}")
    print(f"Check interval: {CHECK_INTERVAL_HOURS} hours")
    print("-" * 60)

    all_posts = []
    all_experts = []

    for subreddit in SUBREDDITS:
        print(f"\nFetching r/{subreddit}...")
        posts = get_hot_posts(subreddit)
        if posts:
            save_posts(posts, subreddit)
            all_posts.extend(posts)

    # 识别专家
    print("\n" + "-" * 60)
    print("Identifying experts...")
    all_experts = identify_experts(all_posts)

    # 保存专家列表
    experts_file = REDDIT_SAVE_DIR / date_str / "experts.md"
    save_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在
    with open(experts_file, 'w', encoding='utf-8') as f:
        f.write(f"# Reddit 技术版块专家 - {date_str}\n\n")
        f.write(f"**识别时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**专家数量:** {len(all_experts)}\n\n")
        f.write("---\n\n")

        for i, expert in enumerate(all_experts, 1):
            f.write(f"### {i}. u/{expert['username']}\n\n")
            f.write(f"**专家分数:** {expert['expert_score']}\n")
            f.write(f"**帖子数:** {expert['posts']}\n")
            f.write(f"**平均分:** {expert['avg_score']}\n\n")

    print(f"  [OK] Identified {len(all_experts)} experts")

    print("-" * 60)
    print(f"\n[COMPLETE] Total posts: {len(all_posts)}")
    print(f"Save dir: {REDDIT_SAVE_DIR / date_str}")
    print("=" * 60)

    return len(all_posts)

if __name__ == "__main__":
    monitor_reddit()
