#!/usr/bin/env python3
"""
X/Twitter AI Research Monitor
监听 AI 研究者、机构、话题的 Twitter/X 动态
输出到 Obsidian vault
"""

import sys
import requests
import os
import re
import json
import sqlite3
from datetime import datetime
from typing import List, Dict

# Windows UTF-8 编码支持
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ============ 配置 ============
OUTPUT_DIR = r"D:\OpenClaw\workspace\X-Twitter\daily"
DB_PATH = r"D:\OpenClaw\workspace\scripts\x-twitter-seen.db"
LOG_PATH = r"D:\OpenClaw\workspace\scripts\x-twitter.log"

# 代理配置（Clash）
PROXY_ADDR = "http://127.0.0.1:7897"
os.environ['HTTP_PROXY'] = PROXY_ADDR
os.environ['HTTPS_PROXY'] = PROXY_ADDR

# 监听列表（可扩展）
TARGETS = {
    "researchers": [
        "ylecun", "karpathy", "AndrewYNg", "fchollet",
        "DemisHassabis", "sama", "OpenAI", "AnthropicAI"
    ],
    "topics": [
        "#AI", "#MachineLearning", "#LLM", "#DeepLearning",
        "#AgenticAI", "#MCP", "#RAG"
    ]
}

# ============ 工具函数 ============
def log(msg: str):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS seen (
        tweet_id TEXT PRIMARY KEY,
        author TEXT,
        text TEXT,
        fetched_at TEXT
    )""")
    conn.commit()
    return conn

def is_seen(conn, tweet_id: str) -> bool:
    c = conn.cursor()
    c.execute("SELECT 1 FROM seen WHERE tweet_id=?", (tweet_id,))
    return c.fetchone() is not None

def mark_seen(conn, tweet_id: str, author: str, text: str):
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO seen VALUES (?, ?, ?, ?)",
              (tweet_id, author, text, datetime.now().isoformat()))
    conn.commit()

def sanitize_filename(text: str, max_len: int = 80) -> str:
    text = re.sub(r'[<>:"/\\|？*]', '', text)
    text = text.replace('&', 'and').replace('\n', ' ')
    return text[:max_len].strip()

def get_today_dir() -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = os.path.join(OUTPUT_DIR, today[:4], today)
    os.makedirs(today_dir, exist_ok=True)
    return today_dir

# ============ 数据收集 ============
def fetch_twitter_via_api(target_type: str, target_name: str) -> List[Dict]:
    """
    使用 Twitter API v2 获取推文
    需要配置 BEARER_TOKEN 环境变量
    """
    bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')
    if not bearer_token:
        log(f"⚠️ 未配置 TWITTER_BEARER_TOKEN，跳过 {target_name}")
        return []

    if target_type == "researchers":
        url = f"https://api.twitter.com/2/users/by/username/{target_name}"
        headers = {"Authorization": f"Bearer {bearer_token}"}

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                user_data = resp.json()
                user_id = user_data['data']['id']

                # 获取最近推文
                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                params = {
                    "max_results": 10,
                    "tweet.fields": "created_at,text,author_id",
                    "expansions": "author_id"
                }
                tweets_resp = requests.get(tweets_url, headers=headers, params=params, timeout=30)
                if tweets_resp.status_code == 200:
                    tweets_data = tweets_resp.json()
                    return tweets_data.get('data', [])
        except Exception as e:
            log(f"❌ API 错误 {target_name}: {e}")

    return []

def fetch_twitter_via_nitter(target_name: str) -> List[Dict]:
    """
    使用 Nitter 实例获取推文（免 API）
    Nitter 是 Twitter 的开源替代前端
    """
    nitter_instances = [
        "https://nitter.net",
        "https://nitter.privacy.com.de",
        "https://nitter.dark.fail"
    ]

    tweets = []
    for instance in nitter_instances:
        try:
            url = f"{instance}/{target_name}/rss"
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                # 解析 RSS
                import feedparser
                feed = feedparser.parse(resp.content)
                for entry in feed.entries[:10]:
                    tweets.append({
                        "id": entry.id.split('#')[-1] if '#' in entry.id else entry.id,
                        "author": target_name,
                        "text": entry.title,
                        "link": entry.link,
                        "published": entry.published
                    })
                break
        except Exception as e:
            log(f"⚠️ Nitter {instance} 失败：{e}")
            continue

    return tweets

def search_twitter_topics(topic: str) -> List[Dict]:
    """
    搜索话题标签
    使用 Nitter 搜索功能
    """
    nitter = "https://nitter.net"
    tweets = []

    try:
        search_url = f"{nitter}/search?q={topic}&f=tweets"
        resp = requests.get(search_url, timeout=30)
        if resp.status_code == 200:
            # 简单提取（实际应该用更好的解析）
            log(f"📝 话题 {topic} 搜索结果已获取")
    except Exception as e:
        log(f"❌ 话题搜索失败 {topic}: {e}")

    return tweets

# ============ 输出生成 ============
def generate_markdown(tweets: List[Dict], date_str: str) -> str:
    md = f"""# X/Twitter 监听 - {date_str}

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**监听目标:** {len(set(t['author'] for t in tweets))} 个账号
**收集推文:** {len(tweets)} 条

---

"""

    # 按作者分组
    by_author = {}
    for tweet in tweets:
        author = tweet.get('author', 'unknown')
        if author not in by_author:
            by_author[author] = []
        by_author[author].append(tweet)

    for author, author_tweets in by_author.items():
        md += f"## @{author}\n\n"
        for tweet in author_tweets[:5]:  # 每个作者最多 5 条
            text = tweet.get('text', '')
            link = tweet.get('link', '')
            published = tweet.get('published', '')

            md += f"### {text[:200]}{'...' if len(text) > 200 else ''}\n\n"
            if link:
                md += f"🔗 [{link}]({link})\n\n"
            if published:
                md += f"📅 {published}\n\n"
            md += "---\n\n"

    md += f"\n**结束时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    return md

# ============ 主流程 ============
def main():
    log("🚀 启动 X/Twitter 监听")

    conn = init_db()
    all_tweets = []

    # 收集研究者推文
    for researcher in TARGETS["researchers"]:
        log(f"📝 收集 @{researcher}")

        # 优先尝试 Nitter（免 API）
        tweets = fetch_twitter_via_nitter(researcher)

        # 过滤已见过的
        new_tweets = [t for t in tweets if not is_seen(conn, t.get('id', ''))]

        for tweet in new_tweets:
            mark_seen(conn, tweet.get('id', ''), tweet.get('author', ''), tweet.get('text', ''))
            all_tweets.append(tweet)

        log(f"✅ @{researcher}: {len(new_tweets)} 条新推文")

    # 生成输出
    if all_tweets:
        today_dir = get_today_dir()
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = sanitize_filename(f"x-twitter-{date_str}.md")
        filepath = os.path.join(today_dir, filename)

        md_content = generate_markdown(all_tweets, date_str)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        log(f"💾 已保存到 {filepath}")
    else:
        log("ℹ️ 无新推文")

    conn.close()
    log("✅ 完成")

if __name__ == "__main__":
    main()
