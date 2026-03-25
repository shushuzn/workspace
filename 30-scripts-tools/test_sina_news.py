import sys
import subprocess
import urllib.request
import json
import re
from datetime import datetime
from pathlib import Path


def fetch_sina_news():
    """抓取新浪财经新闻"""
    url = "https://finance.sina.com.cn/"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-CN,zh;q=0.9",
        },
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode("utf-8", errors="ignore")

    # 提取新闻标题
    pattern = r'"title"\s*:\s*"([^"]+)"'
    titles = re.findall(pattern, content)

    news = []
    for t in titles:
        t = t.strip()
        if len(t) > 15 and "app" not in t.lower():
            news.append(
                {
                    "title": t,
                    "source": "sina",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )

    return news[:20]


if __name__ == "__main__":
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize", "--auto"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        sys.exit(1)
    print("[OK] Critic Review Passed")

    print("=" * 60)
    print("新浪财经新闻抓取测试")
    print("=" * 60)

    news = fetch_sina_news()
    print(f"\n获取到 {len(news)} 条新闻:\n")

    for i, n in enumerate(news[:15], 1):
        print(f"{i}. {n['title'][:60]}...")
