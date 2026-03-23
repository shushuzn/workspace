#!/usr/bin/env python3
"""
RSS Aggregator Server - Your own RSS feeds
Usage:
  python rss_server.py        # Start server
  python rss_server.py update # Update cache only
"""
import asyncio, aiohttp, re, json, time, sys, urllib.request
from datetime import datetime
from pathlib import Path
from html import unescape
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8888
CACHE_DIR = Path(__file__).parent / "rss_cache"
SOURCES = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.investing.com/rss/news.rss",
    "https://seekingalpha.com/market_currents.xml",
]
STOCKS = {
    "NVDA": ["Nvidia", "NVIDIA"],
    "TSLA": ["Tesla", "Elon Musk"],
    "MSFT": ["Microsoft"],
    "AAPL": ["Apple"],
    "GOOGL": ["Google"],
    "META": ["Meta"],
    "AMZN": ["Amazon"],
}


def fetch_jin10():
    """Fetch free flash news from flash.jin10.com"""
    news = []
    
    try:
        url = "https://flash.jin10.com/"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://flash.jin10.com/',
        })
        
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode('utf-8')
        
        # Extract detail IDs
        ids = re.findall(r'/detail/(\d{17,20})', content)
        ids = list(dict.fromkeys(ids))[:50]  # Dedupe, limit to 50
        
        for id in ids:
            detail_url = f"https://flash.jin10.com/detail/{id}"
            try:
                req2 = urllib.request.Request(detail_url, headers={
                    'User-Agent': 'Mozilla/5.0',
                })
                with urllib.request.urlopen(req2, timeout=8) as r2:
                    detail = r2.read().decode('utf-8')
                
                # Extract title
                title_match = re.search(r'<title>([^<]+)</title>', detail)
                if title_match:
                    title = title_match.group(1).replace(' - 金十数据', '').strip()
                    # Remove 【金十数据】 prefix for cleaner display
                    title = re.sub(r'^【金十数据】', '', title)
                    
                    news.append({
                        "title": title,
                        "content": "",
                        "link": detail_url,
                        "date": id[:8],
                        "ts": time.time(),
                        "source": "金十快讯"
                    })
            except:
                pass
    except:
        pass
    
    return news

class Cache:
    def __init__(self):
        CACHE_DIR.mkdir(exist_ok=True)
        self.news = []
        self.jin10_news = []
        self.last_update = 0
    
    def save(self, news):
        self.news = news
        self.last_update = time.time()
        with open(CACHE_DIR / "cache.json", "w", encoding="utf-8") as f:
            json.dump({"news": news, "t": self.last_update}, f, ensure_ascii=False)
    
    def load(self):
        try:
            with open(CACHE_DIR / "cache.json", "r", encoding="utf-8") as f:
                d = json.load(f)
            self.news = d.get("news", [])
            self.last_update = d.get("t", 0)
            # Load Jin10 news
            self.jin10_news = fetch_jin10()
            return True
        except:
            return False
    
    def get_all_news(self):
        """Return all news: Jin10 first, then RSS"""
        return self.jin10_news + self.news

async def fetch(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r:
            return await r.text()
    except:
        return ""

def parse(text):
    news = []
    for item in re.findall(r'<item[^>]*>(.*?)</item>', text, re.DOTALL):
        t = re.search(r'<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', item)
        if not t:
            continue
        title = unescape(t.group(1)).strip()
        if len(title) < 10:
            continue
        l = re.search(r'<link[^>]*href=["\']([^"\']+)["\']', item)
        d = re.search(r'<description[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>', item)
        p = re.search(r'<pubDate>(.*?)</pubDate>', item)
        content = unescape(re.sub(r'<[^>]+>', '', d.group(1) if d else "")).strip()
        date = p.group(1)[:25] if p else ""
        try:
            ts = datetime.strptime(date[:24], "%a, %d %b %Y %H:%M:%S").timestamp()
        except:
            ts = time.time()
        news.append({
            "title": title,
            "link": l.group(1) if l else "",
            "content": content,
            "date": date,
            "ts": ts,
        })
    return news

async def update(cache):
    import platform
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        texts = await asyncio.gather(*[fetch(session, u) for u in SOURCES])
    all_news = []
    for t in texts:
        all_news.extend(parse(t))
    seen, unique = set(), []
    for n in all_news:
        k = n["title"][:80]
        if k not in seen:
            seen.add(k)
            unique.append(n)
    unique.sort(key=lambda x: x["ts"], reverse=True)
    cache.save(unique)
    return len(unique)

def rss(news, title):
    now = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = ""
    for n in news[:50]:
        c = n["content"][:500].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        d = datetime.fromtimestamp(n["ts"]).strftime("%a, %d %b %Y %H:%M:%S +0000")
        items += f'<item><title><![CDATA[{n["title"]}]]></title><link>{n["link"]}</link><description><![CDATA[{c}]]></description><pubDate>{d}</pubDate></item>'
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>{title}</title><lastBuildDate>{now}</lastBuildDate><ttl>5</ttl>{items}</channel></rss>'

def html_page(news, title):
    h = '<html><head><meta charset="utf-8"><title>' + title + '</title>'
    h += '<style>body{font:16px sans-serif;max-width:900px;margin:0 auto;padding:20px}.item{border-bottom:1px solid #eee;padding:12px 0}.title{font-size:18px;font-weight:bold}.meta{color:#888;font-size:12px}.content{margin-top:5px;color:#555}</style>'
    h += '</head><body>'
    h += '<h1>' + title + '</h1><p>Updated: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '</p>'
    for n in news[:30]:
        h += '<div class="item"><div class="title">' + n["title"] + '</div><div class="meta">' + n["date"] + '</div>'
        if n["content"]:
            h += '<div class="content">' + n["content"][:200] + '...</div>'
        h += '</div>'
    return h + '</body></html>'

class Handler(BaseHTTPRequestHandler):
    cache = None
    
    def do_GET(self):
        path = self.path.strip("/").lower()
        cache.load()
        jin10_news = fetch_jin10()  # 实时获取！
        rss_news = self.cache.news
        all_news = jin10_news + rss_news  # 金十在前
        
        if self.cache.last_update:
            last = datetime.fromtimestamp(self.cache.last_update).strftime("%H:%M:%S")
        else:
            last = "Never"
        
        if path in ["", "index", "index.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            h = '<html><head><meta charset="utf-8"><title>RSS Server</title>'
            h += '<style>body{font:14px sans-serif;max-width:600px;margin:50px auto;padding:20px}a{display:block;padding:10px;background:#f5f5f5;margin:5px 0;text-decoration:none;border-radius:5px}h1{margin-bottom:5px}p{color:#888}h3{margin-top:20px}</style>'
            h += '</head><body><h1>RSS Aggregator</h1>'
            h += '<p>Total: ' + str(len(all_news)) + ' | RSS: ' + str(len(rss_news)) + ' | Jin10: ' + str(len(jin10_news)) + ' | Last: ' + last + '</p>'
            h += '<h3>Chinese News (金十数据)</h3>'
            h += '<a href="/jin10">金十快讯 (网页版) 🔥</a>'
            h += '<a href="/jin10.xml">金十 RSS (XML)</a>'
            h += '<h3>All News</h3>'
            h += '<a href="/all.xml">All News (RSS)</a><a href="/all.html">All News (HTML)</a>'
            h += '<h3>By Stock</h3>'
            for s in STOCKS:
                h += '<a href="/' + s.lower() + '.xml">' + s + '</a>'
            self.wfile.write(h.encode())
            return
        
        # Jin10 RSS (Chinese financial news)
        if path == "jin10.xml":
            self.send_response(200)
            self.send_header("Content-type", "application/xml; charset=utf-8")
            self.end_headers()
            self.wfile.write(rss(jin10_news, "金十数据").encode())
            return
        
        # Jin10 HTML page (flash news)
        if path == "jin10":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            h = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>金十快讯</title>
<style>
body{font-family:system-ui,sans-serif;max-width:900px;margin:0 auto;padding:20px;background:#1a1a2e;color:#eee}
h1{color:#ffd700;text-align:center;border-bottom:2px solid #ffd700;padding-bottom:15px}
.item{background:#16213e;padding:15px;margin:10px 0;border-radius:8px;border-left:4px solid #ffd700}
.item h3{color:#4cc9f0;margin:0 0 8px 0;font-size:15px}
.item .source{color:#888;font-size:12px;margin-bottom:5px}
.item a{color:#4cc9f0;text-decoration:none}
.item a:hover{text-decoration:underline}
.stats{text-align:center;color:#888;margin:20px 0}
a.back{color:#ffd700}
</style></head><body>
<h1>📰 金十快讯</h1>
<p class="stats">实时快讯 · 免费内容 · ''' + str(len(jin10_news)) + ''' 条</p>
<a href="/" class="back">← 返回首页</a>
'''
            for n in jin10_news:
                link = n.get('link', '#')
                title = n.get('title', '')
                source = n.get('source', '金十快讯')
                h += f'''<div class="item">
<div class="source">📌 {source}</div>
<h3>{title}</h3>
<a href="{link}" target="_blank">查看详情 →</a>
</div>'''
            h += '<p class="stats">更新时间: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '</p></body></html>'
            self.wfile.write(h.encode())
            return
        
        if path == "all.xml":
            self.send_response(200)
            self.send_header("Content-type", "application/xml; charset=utf-8")
            self.end_headers()
            self.wfile.write(rss(all_news, "All News").encode())
            return
        if path == "all.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_page(all_news, "All News").encode())
            return
        
        for sym, kws in STOCKS.items():
            if path == sym.lower() + ".xml":
                filtered = [n for n in all_news if any(kw.lower() in (n["title"]+n.get("content","")).lower() for kw in kws)]
                self.send_response(200)
                self.send_header("Content-type", "application/xml; charset=utf-8")
                self.end_headers()
                self.wfile.write(rss(filtered, sym + " News").encode())
                return
        
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    cache = Cache()
    cache.load()
    
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        print("Updating...")
        import platform
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        count = asyncio.run(update(cache))
        print(f"Updated {count} news")
    else:
        print(f"Starting RSS server on http://localhost:{PORT}")
        print(f"Endpoints: / /all.xml /all.html /nvda.xml /tsla.xml ...")
        Handler.cache = cache
        server = HTTPServer(("0.0.0.0", PORT), Handler)
        print(f"Server running. Press Ctrl+C to stop.")
        server.serve_forever()