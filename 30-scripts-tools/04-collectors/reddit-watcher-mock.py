#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reddit Watcher v1 - 模拟数据版本
用于测试流程，等待正式 API 认证
"""

from datetime import datetime
from pathlib import Path
import random

# 配置
REDDIT_SAVE_DIR = Path(r"D:\obsidian\Vault\Reddit")

# 模拟数据
SUBREDDITS = ["MachineLearning", "artificial", "deeplearning", "reinforcementlearning", "LocalLLaMA"]

SAMPLE_TITLES = [
    "New paper: Efficient Fine-tuning of Large Language Models",
    "Discussion: Best practices for RLHF implementation",
    "Tutorial: Getting started with Diffusion Models",
    "Question: How to improve transformer inference speed?",
    "News: Major breakthrough in multimodal learning",
    "Resource: Collection of AI research papers",
    "Tool: Open-source library for model compression",
    "Debate: Is scaling law still valid?",
    "Showcase: My project on code generation",
    "Meta: State of AI research in 2026",
]

def generate_mock_posts(subreddit, count=20):
    """生成模拟帖子"""
    posts = []
    for i in range(count):
        score = random.randint(10, 500)
        comments = random.randint(5, 100)

        posts.append({
            'subreddit': subreddit,
            'title': f"{random.choice(SAMPLE_TITLES)} ({i+1})",
            'score': score,
            'num_comments': comments,
            'url': f"https://reddit.com/r/{subreddit}/mock/{i}",
            'permalink': f"/r/{subreddit}/comments/mock_{i}",
            'author': f"user_{random.randint(1, 100)}",
            'selftext': f"This is a mock post about AI/ML topic...",
        })

    return posts

def classify_post(post):
    """内容质量评估"""
    score = post.get('score', 0)
    comments = post.get('num_comments', 0)

    quality_score = 0
    tags = ['AI', 'ML']

    if score > 100:
        quality_score += 2
    if score > 300:
        quality_score += 2
    if comments > 50:
        quality_score += 1

    priority = min(5, max(1, quality_score))

    return {
        'tags': tags,
        'priority': priority,
        'is_high_quality': quality_score >= 3,
        'quality_score': quality_score
    }

def save_posts(posts, subreddit):
    """保存帖子"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    save_dir = REDDIT_SAVE_DIR / date_str
    save_dir.mkdir(parents=True, exist_ok=True)

    high_quality = [p for p in posts if classify_post(p)['is_high_quality']]

    filename = f"{subreddit}-{date_str}-mock.md"
    filepath = save_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# r/{subreddit} - {date_str} (模拟数据)\n\n")
        f.write(f"**注:** 等待 Reddit API 认证，当前为模拟数据\n\n")
        f.write(f"**总数:** {len(posts)} | **高质量:** {len(high_quality)}\n\n")
        f.write("---\n\n")

        if high_quality:
            f.write("## 🔥 高质量讨论\n\n")
            for i, post in enumerate(high_quality, 1):
                f.write(f"### {i}. {post['title']}\n\n")
                f.write(f"**分数:** {post['score']} | **评论:** {post['num_comments']}\n")
                f.write(f"**链接:** [Reddit]({post['permalink']})\n\n")
                f.write("---\n\n")

    print(f"  [OK] r/{subreddit}: Saved {len(posts)} mock posts ({len(high_quality)} high quality)")
    return filepath

def monitor_reddit_mock():
    """模拟 Reddit 监听"""
    print("=" * 60)
    print("Reddit Watcher v1 - Mock Data (等待 API 认证)")
    print("=" * 60)

    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"\nDate: {date_str}")
    print(f"Subreddits: {len(SUBREDDITS)}")
    print("-" * 60)

    total_posts = 0

    for subreddit in SUBREDDITS:
        print(f"\nGenerating mock posts for r/{subreddit}...")
        posts = generate_mock_posts(subreddit)
        save_posts(posts, subreddit)
        total_posts += len(posts)

    print("-" * 60)
    print(f"\n[COMPLETE] Total mock posts: {total_posts}")
    print(f"Save dir: {REDDIT_SAVE_DIR / date_str}")
    print("\n⚠️ 注：正式版本需要 Reddit API 认证")
    print("=" * 60)

    return total_posts

if __name__ == "__main__":
    monitor_reddit_mock()
