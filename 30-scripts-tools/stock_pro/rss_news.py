#!/usr/bin/env python3
"""
RSS News v1.0 - Unlimited, no rate limits
"""
import urllib.request
import re
import time
import json
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape

# RSS Feeds - unlimited access
RSS_FEEDS = {
    "investing": {"name": "Investing.com", "url": "https://www.investing.com/rss/news.rss"},
    "seekingalpha": {"name": "Seeking Alpha", "url": "https://seekingalpha.com/market_currents.xml"},
    "bbc_business": {"name": "BBC Business", "url": "http://feeds.bbci.co.uk/news/business/rss.xml"},
    "reuters": {"name": "Reuters", "url": "https://feeds.reuters.com/reuters/businessNews"},
    "ft": {"name": "Financial Times", "url": "https://www.ft.com/rss/home"},
    "techcrunch": {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
}

# Jin10 - Chinese financial news (embedded content)
JIN10_SOURCE = {"name": "金十数据", "url": "https://xnews.jin10.com/"}

STOCK_KW = {
    "NVDA": ["Nvidia", "NVIDIA", "GPU", "Jensen"],
    "TSLA": ["Tesla", "Elon Musk", "EV"],
    "MSFT": ["Microsoft", "Windows", "Azure"],
    "AAPL": ["Apple", "iPhone", "Tim Cook"],
    "GOOGL": ["Google", "Alphabet"],
    "META": ["Meta", "Facebook", "Zuckerberg"],
    "AMZN": ["Amazon", "AWS"],
    "AMD": ["AMD", "Lisa Su"],
}

_cache = {}
_cache_ttl = 60


def _fetch(url):
    if url in _cache:
        ts, data = _cache[url]
        if time.time() - ts < _cache_ttl:
            return data
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            _cache[url] = (time.time(), data)
            return data
    except:
        return None


def fetch_rss(key):
    news = []
    config = RSS_FEEDS.get(key)
    if not config:
        return news

    data = _fetch(config["url"])
    if not data:
        return news

    text = data.decode('utf-8', errors='ignore')

    for item_html in re.findall(r'<item[^>]*>(.*?)</item>', text, re.DOTALL):
        title = re.search(r'<title[^>]*><!\[CDATA\[(.*?)\]\]></title>|<title[^>]*>(.*?)</title>', item_html)
        if not title:
            continue
        title = unescape(title.group(1) or title.group(2)).strip()

        link = re.search(r'<link[^>]*href=["\'](.*?)["\']', item_html)
        link = link.group(1) if link else ""

        desc = re.search(r'<description[^>]*><!\[CDATA\[(.*?)\]\]></description>|<description[^>]*>(.*?)</description>', item_html)
        content = ""
        if desc:
            c = desc.group(1) or desc.group(2) or ""
            content = re.sub(r'<[^>]+>', '', c)
            content = unescape(content).strip()

        date = re.search(r'<pubDate>(.*?)</pubDate>', item_html)
        date = date.group(1)[:16] if date else datetime.now().strftime("%H:%M")

        if title and len(title) > 10:
            news.append({"source": config["name"], "title": title, "url": link, "content": content, "time": date})

    return news


def fetch_all_parallel():
    # Fetch Jin10 first (priority)
    jin10_news = fetch_jin10_rss()

    # Fetch RSS feeds in parallel
    rss_news = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(fetch_rss, k) for k in RSS_FEEDS]
        for f in as_completed(futures):
            try:
                rss_news.extend(f.result())
            except:
                pass

    # Jin10 first, then RSS
    return jin10_news + rss_news


def fetch_jin10_rss():
    """Fetch Jin10 news for RSS feed"""
    news = []
    cache_file = Path(__file__).parent / "data_jin10_news.json"

    # Try to load from cache
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data.get('news', []):
                title = item.get('title', '')
                url = item.get('url', '')

                # Jin10 format: title contains headline\n\ncontent
                if '\n' in title:
                    parts = title.split('\n', 2)
                    headline = parts[0].strip()
                    content = parts[2].strip() if len(parts) > 2 else ''
                    # Clean tags
                    content = re.sub(r'\s*HOT\s*', '', content)
                    content = re.sub(r'\s*\d+小时前\s*', '', content)
                    content = re.sub(r'\s*来自：.*', '', content)
                    content = re.sub(r'\s*订阅.*', '', content)
                    content = content.strip()
                else:
                    headline, content = title, ''

                if headline:
                    news.append({
                        "source": "金十数据",
                        "title": headline,
                        "url": url,
                        "content": content,
                        "time": "最近"
                    })
        except:
            pass

    # If no cache, fetch fresh
    if not news:
        try:
            url = JIN10_SOURCE["url"]
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('utf-8')

            # Extract all links
            links = re.findall(r'https://xnews\.jin10\.com/details/\d+', content)
            links = list(dict.fromkeys(links))[:15]

            for detail_url in links:
                try:
                    detail_req = urllib.request.Request(detail_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(detail_req, timeout=8) as r:
                        page = r.read().decode('utf-8')

                    title_match = re.search(r'<title>([^<]+)</title>', page)
                    title = title_match.group(1).replace('-市场参考-金十数据', '').strip() if title_match else ""

                    if title:
                        news.append({
                            "source": "金十数据",
                            "title": title,
                            "url": detail_url,
                            "content": "",
                            "time": "最近"
                        })
                    time.sleep(0.3)
                except:
                    pass
        except:
            pass

    return news


def filter_stock(news, symbol):
    kws = STOCK_KW.get(symbol.upper(), [symbol.upper()])
    result = []
    for n in news:
        t = n["title"].lower() + n.get("content", "").lower()
        if any(kw.lower() in t for kw in kws):
            result.append(n)
    return result


def get_news(symbol=None, limit=100):
    if symbol:
        news = filter_stock(fetch_all_parallel(), symbol)
    else:
        news = fetch_all_parallel()

    seen = set()
    unique = []
    for n in news:
        k = n["title"][:80]
        if k not in seen:
            seen.add(k)
            unique.append(n)
    return unique[:limit]


def format_report(symbol=None, limit=50):
    news = get_news(symbol, limit=limit)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source_count = len(RSS_FEEDS) + 1  # +1 for Jin10

    report = f"#{' ' + symbol if symbol else ''} RSS News\n\n_Feed: {ts} | {source_count} sources (金十+{len(RSS_FEEDS)} RSS)_\n\n"

    if not news:
        return report + "_No news_"

    for i, n in enumerate(news, 1):
        report += f"## {i}. {n['title']}\n\n"
        report += f"**{n['source']}** | {n['time']}\n\n"
        if n.get("content") and len(n["content"]) > 30:
            report += f"{n['content'][:300]}...\n\n"
        if n.get("url"):
            report += f"[Read more]({n['url']})\n"
        report += "\n---\n\n"

    return report


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    print(format_report(symbol))
