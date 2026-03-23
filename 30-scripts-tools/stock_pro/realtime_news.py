#!/usr/bin/env python3
"""
Realtime News v3.0 - Full content, no rate limits
"""
import urllib.request
import json
import re
import time
import random
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape

YAHOO_BASE = "https://query1.finance.yahoo.com/v1/finance/search?q={}&quotesCount=0&newsCount=10"
SINA = "https://finance.sina.com.cn/"


class SmartRequester:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 120

    def get(self, url, retries=5):
        if url in self.cache:
            ts, data = self.cache[url]
            if time.time() - ts < self.cache_ttl:
                return data

        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                    self.cache[url] = (time.time(), data)
                    return data
            except Exception as e:
                if '429' in str(e):
                    time.sleep(2 ** attempt + random.uniform(1, 3))
                    continue
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
        return None


def fetch_article_content(url, source=""):
    """Fetch full article content from URL"""
    try:
        req = SmartRequester()
        data = req.get(url)
        if not data:
            return ""

        html = data.decode('utf-8', errors='ignore')

        # Remove scripts and styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

        # Try to find article body
        patterns = [
            r'<div[^>]*class="[^"]*article[^"]*"[^>]*>(.*?)</div>',
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*id="[^"]*content[^"]*"[^>]*>(.*?)</div>',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1)
                content = re.sub(r'<[^>]+>', ' ', content)
                content = unescape(content)
                content = re.sub(r'\s+', ' ', content).strip()
                if len(content) > 100:
                    return content[:600]

        # Fallback: get first few paragraphs
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        content = ' '.join([re.sub(r'<[^>]+>', '', p) for p in paragraphs[:3]])
        content = unescape(content).strip()
        if len(content) > 50:
            return content[:600]

    except:
        pass

    return ""


def fetch_yahoo_news(symbol):
    news = []
    req = SmartRequester()

    for q in [symbol.upper(), f"{symbol.upper()} stock"]:
        try:
            data = req.get(YAHOO_BASE.format(q))
            if data:
                result = json.loads(data.decode('utf-8', errors='ignore'))
                for item in result.get("news", []):
                    news.append({
                        "source": "Yahoo Finance",
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "content": item.get("summary", ""),  # Yahoo often has summary
                        "time": item.get("pubDate", ""),
                    })
                if news:
                    break
        except:
            continue

    return news


def fetch_sina_news():
    news = []
    req = SmartRequester()

    try:
        data = req.get(SINA)
        if not data:
            return news

        html = data.decode('utf-8', errors='ignore')
        pattern = r'<a[^>]*href="(https?://finance\.sina\.com\.cn/[^"]+)"[^>]*>\s*([^<]{15,100})\s*</a>'

        seen = set()
        for href, title in re.findall(pattern, html):
            title = title.strip()
            if title and title not in seen and len(title) > 15:
                seen.add(title)
                news.append({
                    "source": "Sina Finance",
                    "title": title,
                    "url": href,
                    "content": "",
                    "time": datetime.now().strftime("%H:%M"),
                })
    except:
        pass

    return news[:20]


def fetch_content_parallel(news_list):
    """Fetch article content in parallel"""
    def fetch_one(item):
        if item.get("url") and not item.get("content"):
            content = fetch_article_content(item["url"], item.get("source", ""))
            return {**item, "content": content}
        return item

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(fetch_one, n) for n in news_list]
        return [f.result() for f in as_completed(futures)]


def get_realtime_news(symbol=None, with_content=False):
    """Get news with optional full content"""
    if symbol:
        news = fetch_yahoo_news(symbol.upper())
    else:
        news = fetch_sina_news()

        # Add Yahoo market news
        req = SmartRequester()
        try:
            data = req.get(YAHOO_BASE.format("stock market news"))
            if data:
                result = json.loads(data.decode('utf-8', errors='ignore'))
                for item in result.get("news", [])[:10]:
                    news.append({
                        "source": "Yahoo Finance",
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "content": item.get("summary", ""),
                        "time": item.get("pubDate", ""),
                    })
        except:
            pass

    # Dedupe
    seen = set()
    unique = []
    for n in news:
        if n["title"] not in seen and n["title"]:
            seen.add(n["title"])
            unique.append(n)
    news = unique[:20]

    # Fetch content if requested
    if with_content and news:
        news = fetch_content_parallel(news)

    return news


def format_report(symbol=None, with_content=False):
    """Format news as readable report"""
    news = get_realtime_news(symbol, with_content)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = f"#{' ' + symbol if symbol else ''} News"
    report = f"{header}\n\n_Fetched: {ts}_\n\n"

    if not news:
        report += "_No news available_"
    else:
        for i, n in enumerate(news[:12], 1):
            title = n["title"].strip()
            content = n.get("content", "")

            report += f"## {i}. {title}\n\n"
            report += f"**Source:** {n['source']}\n\n"

            if content and len(content) > 30:
                report += f"{content[:400]}\n\n"

            if n.get("url"):
                report += f"[Read more]({n['url']})\n"

            report += "\n---\n\n"

    return report


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    content = "--content" in sys.argv or "-c" in sys.argv

    print(format_report(symbol, with_content=content))
