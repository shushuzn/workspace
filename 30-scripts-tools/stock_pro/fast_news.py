#!/usr/bin/env python3
"""
Fast News v1.0 - Async RSS + Article Content (Windows compatible)
"""
import asyncio
import aiohttp
import re
import sys
from datetime import datetime
from html import unescape
from concurrent.futures import ThreadPoolExecutor

# RSS feeds - sources that don't block bots
RSS_URLS = {
    "investing": "https://www.investing.com/rss/news.rss",
    "reuters": "https://feeds.reuters.com/reuters/businessNews",
    "seekingalpha": "https://seekingalpha.com/market_currents.xml",
    # Tech news with good content
    "techcrunch": "https://techcrunch.com/feed/",
    "verge": "https://www.theverge.com/rss/index.xml",
}

STOCK_KW = {
    "NVDA": ["Nvidia", "NVIDIA", "GPU", "Jensen", "NVD", "graphics", "chip", "semicon"],
    "TSLA": ["Tesla", "Elon Musk", "Elon", "Musk", "EV", "electric", "TSLA", " automotive", "car"],
    "MSFT": ["Microsoft", "Windows", "MSFT", "Azure", "Satya"],
    "AAPL": ["Apple", "iPhone", "Tim Cook", "AAPL", "iOS", "Mac"],
    "GOOGL": ["Google", "Alphabet", "GOOGL", "search", "Alphabet"],
    "META": ["Meta", "Facebook", "META", "Instagram", "Zuckerberg", "social"],
    "AMZN": ["Amazon", "AWS", "AMZN", "Bezos", "e-commerce"],
    "AMD": ["AMD", "AMD", "processor", "Lisa Su", "Ryzen"],
    "NVAX": ["vaccine", "Novavax", "NVAX"],
    "BABA": ["Alibaba", "BABA", "Jack Ma", "e-commerce"],
}

_cache = {}
_cache_ttl = 30


async def fetch_url(session, url, timeout=10):
    """Async fetch with cache"""
    if url in _cache:
        ts, data = _cache[url]
        if datetime.now().timestamp() - ts < _cache_ttl:
            return data

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            data = await resp.read()
            _cache[url] = (datetime.now().timestamp(), data)
            return data
    except:
        return None


async def fetch_rss(session, key):
    """Fetch single RSS feed"""
    url = RSS_URLS.get(key)
    if not url:
        return []

    data = await fetch_url(session, url)
    if not data:
        return []

    text = data.decode('utf-8', errors='ignore')
    news = []

    for item in re.findall(r'<item[^>]*>(.*?)</item>', text, re.DOTALL):
        title = re.search(r'<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', item)
        if not title:
            continue
        title = unescape(title.group(1)).strip()

        link = re.search(r'<link[^>]*href=["\']([^"\']+)["\']', item)
        link = link.group(1) if link else ""

        desc = re.search(r'<description[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>', item)
        content = ""
        if desc:
            c = re.sub(r'<[^>]+>', '', desc.group(1))
            content = unescape(c).strip()

        date = re.search(r'<pubDate>(.*?)</pubDate>', item)
        date = date.group(1)[:16] if date else ""

        if title and len(title) > 10:
            news.append({
                "source": key,
                "title": title,
                "url": link,
                "content": content,
                "time": date
            })

    return news


async def fetch_article(session, item):
    """Fetch full article from URL (only for non-blocking sources)"""
    url = item.get("url")
    if not url or not url.startswith('http'):
        return item

    # Only fetch from known good sources
    allowed = ['reuters.com', 'investing.com', 'seekingalpha.com', 'techcrunch.com']
    if not any(d in url for d in allowed):
        return item

    # Skip non-article URLs
    skip = ['youtube.com', 'twitter.com', 'x.com', 'facebook.com', 'video']
    if any(d in url for d in skip):
        return item

    data = await fetch_url(session, url, timeout=20)
    if not data:
        return item

    html = data.decode('utf-8', errors='ignore')
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

    # Better patterns for full content
    patterns = [
        # Standard article
        r'<article[^>]*>(.*?)</article>',
        # Main content divs
        r'<div[^>]*class="[^"]*(?:article-content|article-body|story-body|post-content|entry-content)[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*id="(?:article|story|content|main)"[^>]*>(.*?)</div>',
        # Main tag
        r'<main[^>]*>(.*?)</main>',
        # Paragraphs in body
        r'<body[^>]*>(.*?)</body>',
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1)
            # Extract paragraphs
            paras = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
            if paras:
                text = ' '.join([re.sub(r'<[^>]+>', '', p).strip() for p in paras if len(p) > 50])
                text = unescape(text)
                if len(text) > 200:
                    item["content"] = text[:3000]
                    return item

    return item


async def main_async(symbol, with_content, limit):
    """Main async function"""
    # Use Windows-compatible event loop
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Fetch all RSS in parallel
        tasks = [fetch_rss(session, k) for k in RSS_URLS]
        results = await asyncio.gather(*tasks)

        all_news = []
        for r in results:
            all_news.extend(r)

        # Filter by stock (or return all if no match)
        if symbol:
            kws = STOCK_KW.get(symbol.upper(), [symbol.upper()])
            filtered = []
            for n in all_news:
                t = (n["title"] + " " + n.get("content", "")).lower()
                if any(kw.lower() in t for kw in kws):
                    filtered.append(n)

            # If no matches, return all news for that symbol
            if filtered:
                all_news = filtered
            else:
                # Try partial match on symbol code
                sym_upper = symbol.upper()
                for n in all_news:
                    if sym_upper in n["title"] or sym_upper in n.get("content", ""):
                        filtered.append(n)
                all_news = filtered if filtered else all_news[:5]  # Show top 5 if nothing matches

        # Dedupe
        seen = set()
        unique = []
        for n in all_news:
            k = n["title"][:80]
            if k not in seen:
                seen.add(k)
                unique.append(n)
        all_news = unique[:limit]

        # Fetch full content
        if with_content and all_news:
            tasks = [fetch_article(session, n) for n in all_news]
            all_news = await asyncio.gather(*tasks)

        return all_news


def get_news(symbol=None, with_content=True, limit=20):
    """Sync wrapper"""
    # Use SelectorEventLoop for Windows
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(main_async(symbol, with_content, limit))
    finally:
        loop.close()


def format_report(symbol=None, with_content=True):
    """Format news report"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching...", file=sys.stderr)

    news = get_news(symbol, with_content)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = f"#{' ' + symbol if symbol else ''} News"
    report = f"{header}\n\n_Feed: {ts} | {len(news)} items_\n\n"

    if not news:
        report += "_No news_"
    else:
        for i, n in enumerate(news[:12], 1):
            report += f"## {i}. {n['title']}\n\n"
            report += f"**{n['source']}** | {n['time']}\n\n"

            content = n.get("content", "")
            if content and len(content) > 30:
                report += f"{content[:800]}...\n\n"

            if n.get("url"):
                report += f"[Read more]({n['url']})\n"
            report += "\n---\n\n"

    return report


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    no_content = "--no-content" in sys.argv

    print(format_report(symbol, with_content=not no_content))
