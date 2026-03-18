#!/usr/bin/env python3
"""
Reddit AI/ML Monitor (RSS version)
监控 r/MachineLearning、r/ArtificialIntelligence 等子版块
使用 RSS Feed 无需 API 密钥
"""

import sys
import os
import re
import sqlite3
from datetime import datetime
from typing import List, Dict

# Windows UTF-8 编码支持
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import feedparser
import requests
from pathlib import Path

# ============ 配置 ============
OUTPUT_DIR = r"str(Path(__file__).parent.parent)\Reddit\daily"
DB_PATH = r"str(Path(__file__).parent.parent)\scripts\reddit-seen.db"
LOG_PATH = r"str(Path(__file__).parent.parent)\scripts\reddit-monitor.log"

# 代理配置（Clash）
PROXY_ADDR = "http://127.0.0.1:7897"
os.environ['HTTP_PROXY'] = PROXY_ADDR
os.environ['HTTPS_PROXY'] = PROXY_ADDR

# 监控的子版块
SUBREDDITS = [
    "MachineLearning",
    "ArtificialIntelligence",
    "deeplearning",
    "LearnMachineLearning",
    "LocalLLaMA",
    "singularity",
    "OpenAI",
    "StableDiffusion"
]

# 关键词过滤
AI_KEYWORDS = [
    'llm', 'transformer', 'diffusion', 'rag', 'agent',
    'fine-tune', 'training', 'inference', 'model',
    'neural', 'deep learning', 'machine learning',
    'gpt', 'claude', 'llama', 'mistral', 'qwen'
]

# ============ 工具函数 ============
def log(msg: str):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS seen (
        post_id TEXT PRIMARY KEY,
        title TEXT,
        subreddit TEXT,
        fetched_at TEXT
    )""")
    conn.commit()
    return conn

def is_seen(conn, post_id: str) -> bool:
    c = conn.cursor()
    c.execute("SELECT 1 FROM seen WHERE post_id=?", (post_id,))
    return c.fetchone() is not None

def mark_seen(conn, post_id: str, title: str, subreddit: str):
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO seen VALUES (?, ?, ?, ?)",
              (post_id, title, subreddit, datetime.now().isoformat()))
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

def is_relevant(title: str, content: str = "") -> bool:
    text = (title + " " + content).lower()
    return any(kw in text for kw in AI_KEYWORDS)

# ============ RSS 获取 ============
def fetch_subreddit_rss(subreddit: str, limit: int = 25) -> List[Dict]:
    """
    使用 Reddit RSS Feed 获取帖子
    无需 API 密钥
    """
    # Reddit RSS feed URL
    rss_url = f"https://www.reddit.com/r/{subreddit}/hot.rss?limit={limit}"
    
    # 备用：使用 Libreddit 实例（如果 Reddit 官方 RSS 被限制）
    libreddit_instances = [
        "https://libreddit.kavin.rocks",
        "https://libreddit.privacy.com.de",
        "https://reddit.r4fo.com"
    ]
    
    posts = []
    
    try:
        # 先尝试官方 RSS
        log(f"  → 尝试官方 RSS")
        response = requests.get(rss_url, timeout=30)
        
        if response.status_code != 200 or len(response.content) < 500:
            log(f"  → 官方 RSS 失败，尝试 Libreddit")
            # 尝试 Libreddit 实例
            for instance in libreddit_instances:
                try:
                    rss_url = f"{instance}/r/{subreddit}/.rss"
                    response = requests.get(rss_url, timeout=30)
                    if response.status_code == 200 and len(response.content) > 500:
                        log(f"  → Libreddit 成功：{instance}")
                        break
                except:
                    continue
        
        if response.status_code != 200:
            log(f"⚠️ r/{subreddit} RSS 返回状态码 {response.status_code}")
            return []
        
        # 解析 RSS
        feed = feedparser.parse(response.content)
        
        for entry in feed.entries[:limit]:
            # 提取帖子 ID
            post_id = entry.id.split('/')[-1] if '/' in entry.id else entry.id
            
            # 提取内容
            title = entry.title
            content = entry.get('summary', '')
            
            # 过滤相关帖子
            if not is_relevant(title, content):
                continue
            
            # 提取作者
            author = entry.get('author', '[deleted]')
            
            # 提取链接
            link = entry.get('link', '')
            
            # 提取发布时间
            published = entry.get('published', '')
            if published:
                try:
                    created = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z')
                    created_utc = created.isoformat()
                except:
                    created_utc = datetime.now().isoformat()
            else:
                created_utc = datetime.now().isoformat()
            
            posts.append({
                "id": post_id,
                "title": title,
                "subreddit": subreddit,
                "author": author,
                "score": 0,  # RSS 不提供分数
                "num_comments": 0,
                "url": link,
                "selftext": content[:500] if content else '',
                "link_flair_text": '',
                "created_utc": created_utc
            })
        
        return posts
        
    except Exception as e:
        log(f"❌ r/{subreddit} RSS 错误：{e}")
        return []

# ============ 输出生成 ============
def generate_markdown(posts: List[Dict], date_str: str) -> str:
    md = f"""# Reddit 监控 - {date_str}

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**监控版块:** {len(set(p['subreddit'] for p in posts))} 个
**收集帖子:** {len(posts)} 条

---

"""
    
    by_subreddit = {}
    for post in posts:
        sub = post['subreddit']
        if sub not in by_subreddit:
            by_subreddit[sub] = []
        by_subreddit[sub].append(post)
    
    for subreddit, sub_posts in sorted(by_subreddit.items()):
        md += f"## r/{subreddit}\n\n"
        
        # 按时间排序（最新在前）
        sub_posts.sort(key=lambda x: x['created_utc'], reverse=True)
        
        for post in sub_posts[:15]:  # 每个版块最多 15 条
            title = post['title']
            url = post['url']
            author = post.get('author', '')
            published = post.get('created_utc', '')[:10] if post.get('created_utc') else ''
            
            md += f"### {title}\n\n"
            md += f"👤 {author} | 📅 {published} | 🔗 [查看帖子]({url})\n\n"
            
            # 如果有内容摘要
            if post.get('selftext'):
                summary = post['selftext'][:200]
                if len(post['selftext']) > 200:
                    summary += "..."
                md += f"> {summary}\n\n"
            
            md += "---\n\n"
    
    md += f"\n**结束时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    return md

# ============ 主流程 ============
def main():
    log("🚀 启动 Reddit 监控 (RSS 模式)")
    
    conn = init_db()
    all_posts = []
    
    for subreddit in SUBREDDITS:
        log(f"📝 监控 r/{subreddit}")
        
        posts = fetch_subreddit_rss(subreddit, limit=25)
        
        # 过滤已见过的
        new_posts = [p for p in posts if not is_seen(conn, p['id'])]
        
        for post in new_posts:
            mark_seen(conn, post['id'], post['title'], post['subreddit'])
            all_posts.append(post)
        
        log(f"✅ r/{subreddit}: {len(new_posts)} 条新帖子")
    
    if all_posts:
        today_dir = get_today_dir()
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = sanitize_filename(f"reddit-monitor-{date_str}.md")
        filepath = os.path.join(today_dir, filename)
        
        md_content = generate_markdown(all_posts, date_str)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        log(f"💾 已保存到 {filepath}")
    else:
        log("ℹ️ 无新帖子")
    
    conn.close()
    log("✅ 完成")

if __name__ == "__main__":
    main()
