"""News and Sentiment Analysis + Research Reports + Jin10 News"""
from datetime import datetime, timedelta
from stock_pro.core import A, analyze_multiple
import urllib.request
import json
import re

# Simulated news data (in real implementation, fetch from news API)
NEWS_DATA = {
    "NVDA": [
        {"date": "2026-03-22", "headline": "NVIDIA Reports Record AI Chip Demand", "sentiment": 0.85, "source": "Reuters", "impact": "high"},
        {"date": "2026-03-21", "headline": "NVIDIA Announces New GPU Architecture", "sentiment": 0.78, "source": "TechCrunch", "impact": "medium"},
        {"date": "2026-03-20", "headline": "AI Chip Market Growth Exceeds Expectations", "sentiment": 0.72, "source": "Bloomberg", "impact": "medium"},
        {"date": "2026-03-19", "headline": "Major Cloud Providers Increase NVIDIA Orders", "sentiment": 0.82, "source": "CNBC", "impact": "high"},
    ],
    "MSFT": [
        {"date": "2026-03-22", "headline": "Microsoft Azure Growth Accelerates", "sentiment": 0.80, "source": "CNBC", "impact": "high"},
        {"date": "2026-03-21", "headline": "Microsoft Copilot AI Integration Expands", "sentiment": 0.75, "source": "WSJ", "impact": "medium"},
        {"date": "2026-03-20", "headline": "Enterprise Software Demand Remains Strong", "sentiment": 0.72, "source": "Bloomberg", "impact": "medium"},
    ],
    "GOOGL": [
        {"date": "2026-03-22", "headline": "Google AI Search Gains Market Share", "sentiment": 0.78, "source": "TechCrunch", "impact": "high"},
        {"date": "2026-03-21", "headline": "Alphabet Cloud Revenue Surges", "sentiment": 0.76, "source": "Reuters", "impact": "medium"},
        {"date": "2026-03-19", "headline": "YouTube Ad Revenue Beats Estimates", "sentiment": 0.70, "source": "CNBC", "impact": "medium"},
    ],
    "AAPL": [
        {"date": "2026-03-22", "headline": "Apple iPhone Sales Beat Expectations", "sentiment": 0.68, "source": "Reuters", "impact": "medium"},
        {"date": "2026-03-21", "headline": "Apple Services Revenue Growth", "sentiment": 0.72, "source": "Bloomberg", "impact": "medium"},
        {"date": "2026-03-20", "headline": "Apple Vision Pro Sales Update", "sentiment": 0.55, "source": "WSJ", "impact": "low"},
        {"date": "2026-03-18", "headline": "EU Regulatory Concerns for App Store", "sentiment": 0.40, "source": "FT", "impact": "high"},
    ],
    "META": [
        {"date": "2026-03-22", "headline": "Meta AI Users Reach 500M Milestone", "sentiment": 0.80, "source": "CNBC", "impact": "high"},
        {"date": "2026-03-21", "headline": "Meta Announces VR Headset Sales", "sentiment": 0.62, "source": "WSJ", "impact": "medium"},
        {"date": "2026-03-19", "headline": "Meta Advertising Revenue Beats", "sentiment": 0.75, "source": "Bloomberg", "impact": "medium"},
    ],
    "TSLA": [
        {"date": "2026-03-22", "headline": "Tesla Deliveries Meet Expectations", "sentiment": 0.55, "source": "WSJ", "impact": "medium"},
        {"date": "2026-03-21", "headline": "EV Market Competition Intensifies", "sentiment": 0.40, "source": "Reuters", "impact": "high"},
        {"date": "2026-03-19", "headline": "Tesla FSD Progress Update", "sentiment": 0.60, "source": "TechCrunch", "impact": "medium"},
    ],
    "AMZN": [
        {"date": "2026-03-22", "headline": "AWS Revenue Growth Accelerates", "sentiment": 0.78, "source": "CNBC", "impact": "high"},
        {"date": "2026-03-21", "headline": "Amazon Prime Membership Grows", "sentiment": 0.72, "source": "Bloomberg", "impact": "medium"},
    ],
    "AVGO": [
        {"date": "2026-03-22", "headline": "Broadcom AI Chip Demand Surges", "sentiment": 0.82, "source": "Reuters", "impact": "high"},
        {"date": "2026-03-20", "headline": "Broadcom Enterprise Sales Beat", "sentiment": 0.75, "source": "Bloomberg", "impact": "medium"},
    ],
    "NOW": [
        {"date": "2026-03-22", "headline": "ServiceNow AI Features Drive Growth", "sentiment": 0.78, "source": "CNBC", "impact": "high"},
        {"date": "2026-03-20", "headline": "Enterprise Automation Demand Strong", "sentiment": 0.72, "source": "Bloomberg", "impact": "medium"},
    ],
}

# Jin10 News Cache
_JIN10_NEWS_CACHE = None
_JIN10_CACHE_TIME = None
_JIN10_CACHE_TTL = 300  # 5 minutes cache


# Stock keyword mapping for Jin10 news
_STOCK_KEYWORDS = {
    "NVDA": ["英伟达", "NVIDIA", "nvidia", "显卡", "GPU", "AI芯片", "图形处理器", "黄仁勋", "算力"],
    "MSFT": ["微软", "Microsoft", "microsoft", "Windows", "Azure", "Office", "纳德拉"],
    "AAPL": ["苹果", "Apple", "apple", "iPhone", "iOS", "Mac", "库克", "iPad"],
    "GOOGL": ["谷歌", "Google", "google", "Alphabet", "搜索", "AI", "皮查伊"],
    "META": ["Meta", "meta", "Facebook", "facebook", "Instagram", "社交", "元宇宙", "扎克伯格"],
    "TSLA": ["特斯拉", "Tesla", "tesla", "电动车", "电动汽车", "马斯克", "新能源车"],
    "AMZN": ["亚马逊", "Amazon", "amazon", "AWS", "电商", "贝索斯"],
    "AMD": ["AMD", "amd", "超威", "处理器", "芯片", "苏姿丰"],
    "JPM": ["摩根大通", "JP Morgan", "jpmorgan", "摩根", "银行"],
    "NFLX": ["Netflix", "netflix", "奈飞", "流媒体", "网飞"],
    "AI": ["人工智能", "AI", "大模型", "ChatGPT", "DeepSeek"],
    "CHIP": ["芯片", "半导体", "晶圆", "光刻"],
}

# News source URLs
_NEWS_SOURCES = {
    "sina": {
        "name": "新浪财经",
        "urls": [
            "https://finance.sina.com.cn/",
            "https://finance.sina.com.cn/stock/",
            "https://finance.sina.com.cn/stock/usstock/",
        ],
        "pattern": r'<a[^>]*href="(https?://finance\.sina\.com\.cn/[^"]+)"[^>]*>\s*([^<]{15,150})\s*</a>',
    },
    "netease": {
        "name": "网易财经",
        "urls": ["https://money.163.com/"],
        "pattern": r'<a[^>]*href="([^"]+)"[^>]*>\s*([^<]{15,100})\s*</a>',
    },
    "ifeng": {
        "name": "凤凰网财经",
        "urls": ["https://finance.ifeng.com/"],
        "pattern": r'<a[^>]*href="([^"]+)"[^>]*>\s*([^<]{15,100})\s*</a>',
    },
}


def fetch_cn_news(source="sina", max_items=50):
    """Fetch Chinese financial news from various sources"""
    import urllib.request
    
    source_config = _NEWS_SOURCES.get(source, _NEWS_SOURCES["sina"])
    
    all_news = []
    seen_titles = set()
    
    for url in source_config["urls"]:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
            })
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                
                matches = re.findall(source_config["pattern"], content)
                
                for href, title in matches:
                    title = title.strip()
                    if title and title not in seen_titles and len(title) > 15 and len(title) < 200:
                        seen_titles.add(title)
                        all_news.append({
                            "title": title,
                            "url": href if href.startswith("http") else "",
                            "source": source_config["name"],
                            "time": datetime.now().strftime("%H:%M")
                        })
        
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    
    return all_news[:max_items]


def get_cn_news_for_stock(symbol):
    """Get Chinese news related to a specific stock"""
    keywords = _STOCK_KEYWORDS.get(symbol.upper(), [])
    if not keywords:
        return []
    
    all_news = []
    seen_titles = set()
    
    # Fetch from multiple sources
    for source in ["sina", "netease", "ifeng"]:
        news = fetch_cn_news(source, max_items=100)
        
        for n in news:
            title = n["title"]
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    if title not in seen_titles:
                        seen_titles.add(title)
                        all_news.append(n)
                    break
    
    return all_news


def fetch_jin10_news():
    """Fetch latest news from Jin10 (xnews.jin10.com)"""
    global _JIN10_NEWS_CACHE, _JIN10_CACHE_TIME
    
    now = datetime.now()
    
    # Check memory cache
    if _JIN10_NEWS_CACHE is not None and _JIN10_CACHE_TIME is not None:
        if (now - _JIN10_CACHE_TIME).total_seconds() < _JIN10_CACHE_TTL:
            return _JIN10_NEWS_CACHE
    
    try:
        url = "https://xnews.jin10.com/"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
            
            # Extract news titles
            pattern = r'<a href="(https://xnews\.jin10\.com/details/\d+)"[^>]*>(.*?)</a>'
            matches = re.findall(pattern, content, re.DOTALL)
            
            news_items = []
            for href, title_html in matches:
                # Clean HTML tags
                title = re.sub(r'<[^>]+>', '', title_html).strip()
                title = title.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
                
                if title and len(title) > 10:
                    # Extract time if available
                    time_match = re.search(r'(\d+天|\d+小时|\d+分钟)', title)
                    time_ago = time_match.group(1) if time_match else "N/A"
                    
                    news_items.append({
                        'url': href,
                        'title': title[:200],
                        'time_ago': time_ago,
                        'source': 'Jin10'
                    })
            
            # Remove duplicates
            seen = set()
            unique_news = []
            for item in news_items:
                if item['title'] not in seen:
                    seen.add(item['title'])
                    unique_news.append(item)
            
            _JIN10_NEWS_CACHE = unique_news[:50]
            _JIN10_CACHE_TIME = now
            
            # Save to file cache for fetch_jin10_full
            _save_jin10_cache(unique_news[:20])
            
            return _JIN10_NEWS_CACHE
    
    except Exception as e:
        print(f"Jin10 fetch error: {e}")
        return _JIN10_NEWS_CACHE or []


def _save_jin10_cache(news_items):
    """Save Jin10 news to file cache for persistent storage"""
    try:
        cache_file = Path(__file__).parent / "data_jin10_news.json"
        cached_data = {
            "source": "jin10",
            "fetched_at": datetime.now().isoformat(),
            "news": [{"url": n["url"], "title": n["title"]} for n in news_items]
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f, ensure_ascii=False, indent=2)
    except:
        pass


def get_jin10_news_for_stock(symbol):
    """Get Jin10 news related to a specific stock"""
    keywords = _STOCK_KEYWORDS.get(symbol.upper(), [])
    if not keywords:
        return []
    
    all_news = fetch_jin10_news()
    matched_news = []
    
    for news in all_news:
        title = news['title']
        for keyword in keywords:
            if keyword.lower() in title.lower():
                matched_news.append(news)
                break
    
    return matched_news


def fetch_jin10_full(max_items=20, use_cache=True):
    """Fetch Jin10 news with content summary from details pages
    
    This function:
    1. First checks the file cache (data_jin10_news.json)
    2. If cache is empty or old (>1 hour), fetches fresh data from details pages
    3. Returns news with both headline and content summary
    """
    import time
    
    cache_file = Path(__file__).parent / "data_jin10_news.json"
    cache_ttl = 3600  # 1 hour
    
    # Check cache first
    if use_cache and cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            # Check if cache is fresh
            fetched_at = cached.get('fetched_at', '')
            if fetched_at:
                cache_age = time.time() - datetime.fromisoformat(fetched_at).timestamp()
                if cache_age < cache_ttl and cached.get('news'):
                    news_list = []
                    for item in cached['news'][:max_items]:
                        title = item.get('title', '')
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
                        
                        news_list.append({
                            'title': headline,
                            'content': content,
                            'url': item.get('url', ''),
                            'source': 'jin10',
                        })
                    return news_list
        except:
            pass
    
    # Fetch fresh data - visit details pages
    try:
        url = "https://xnews.jin10.com/"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
        
        # Extract details links
        links = list(dict.fromkeys(re.findall(r'https://xnews\.jin10\.com/details/\d+', content)))[:max_items]
        
        news_list = []
        for detail_url in links[:10]:  # Limit to avoid rate limit
            try:
                detail_req = urllib.request.Request(detail_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                })
                with urllib.request.urlopen(detail_req, timeout=10) as r:
                    page = r.read().decode('utf-8')
                
                # Extract title
                title_match = re.search(r'<title>([^<]+)</title>', page)
                title = title_match.group(1).replace('-市场参考-金十数据', '').strip() if title_match else ""
                
                # Extract content
                p_pattern = r'<p[^>]*>(.*?)</p>'
                paragraphs = re.findall(p_pattern, page, re.DOTALL)
                
                content = ""
                for p in paragraphs:
                    clean = re.sub(r'<[^>]+>', '', p).strip()
                    if len(clean) > 60:
                        content = clean
                        break
                
                news_list.append({
                    'title': title,
                    'content': content,
                    'url': detail_url,
                    'source': 'jin10',
                })
                
                time.sleep(0.5)  # Rate limit
                
            except:
                pass
        
        return news_list
    
    except Exception as e:
        print(f"Jin10 error: {e}")
        return []


def get_news(symbol, days=7):
    """Get recent news for a symbol (combines local + Jin10)"""
    today = datetime.now()
    cutoff = today - timedelta(days=days)
    
    # Get local news
    news = NEWS_DATA.get(symbol, [])
    
    # Get Jin10 news
    jin10_news = get_jin10_news_for_stock(symbol)
    
    # Combine and dedupe
    all_news = []
    seen_titles = set()
    
    # Add local news first
    for n in news:
        date = datetime.strptime(n["date"], "%Y-%m-%d")
        if date >= cutoff:
            all_news.append(n)
            seen_titles.add(n.get("headline", "").lower())
    
    # Add Jin10 news
    for jn in jin10_news:
        title = jn['title']
        if title.lower() not in seen_titles:
            all_news.append({
                "date": today.strftime("%Y-%m-%d"),
                "headline": title,
                "sentiment": 0.5,  # Default neutral for Jin10 (need NLP for actual sentiment)
                "source": "Jin10",
                "impact": "medium"
            })
            seen_titles.add(title.lower())
    
    return all_news


def calculate_sentiment(symbol):
    """Calculate overall sentiment score"""
    news = get_news(symbol, days=30)
    
    if not news:
        return {"sentiment": 0.5, "news_count": 0, "trend": "Neutral"}
    
    avg_sentiment = sum(n["sentiment"] for n in news) / len(news)
    
    # Determine trend
    if len(news) >= 3:
        recent = sum(n["sentiment"] for n in news[:3]) / min(3, len(news))
        older = sum(n["sentiment"] for n in news[3:]) / max(1, len(news) - 3)
        if recent > older + 0.05:
            trend = "Improving"
        elif recent < older - 0.05:
            trend = "Declining"
        else:
            trend = "Stable"
    else:
        trend = "Stable"
    
    return {
        "sentiment": avg_sentiment,
        "news_count": len(news),
        "trend": trend,
        "latest": news[0] if news else None
    }


def jin10_news_report():
    """Generate Jin10 latest news report"""
    news = fetch_jin10_news()
    
    report = "# Jin10 Latest News\n\n"
    report += f"_Source: xnews.jin10.com | Items: {len(news)} | Updated: {datetime.now().strftime('%H:%M:%S')}_\n\n"
    
    for i, n in enumerate(news[:20], 1):
        report += f"**{i}. {n['title'][:150]}...**\n"
        report += f"   - Time: {n['time_ago']} | Source: {n['source']}\n\n"
    
    return report


def jin10_stock_news(symbol):
    """Get Jin10 news related to a specific stock with analysis"""
    jin10_news = get_jin10_news_for_stock(symbol)
    local_news = get_news(symbol, days=7)
    
    # Categorize sentiment based on keywords
    bullish_keywords = ["涨", "突破", "新高", "利好", "增长", "买入", "看涨", "增持"]
    bearish_keywords = ["跌", "破", "新低", "利空", "下跌", "卖出", "看跌", "减持", "裁员", "调查"]
    
    def estimate_sentiment(title):
        title_lower = title.lower()
        bull_count = sum(1 for k in bullish_keywords if k in title)
        bear_count = sum(1 for k in bearish_keywords if k in title)
        
        if bull_count > bear_count:
            return 0.7 + (bull_count - bear_count) * 0.05
        elif bear_count > bull_count:
            return 0.4 - (bear_count - bull_count) * 0.05
        return 0.5
    
    report = f"# Jin10 News: {symbol}\n\n"
    
    if not jin10_news and not local_news:
        report += "_No recent news found._\n"
        return report
    
    report += f"## Stock-Specific News ({len(jin10_news)} from Jin10, {len(local_news)} total)\n\n"
    
    for n in jin10_news[:10]:
        sentiment = estimate_sentiment(n['title'])
        indicator = "[+]" if sentiment > 0.55 else ("[-]" if sentiment < 0.45 else "[=]")
        report += f"{indicator} {n['title'][:120]}...\n"
        report += f"    [{n['time_ago']}] {n['source']}\n\n"
    
    # Local news
    if local_news:
        report += f"\n## Local News ({len(local_news)} items)\n\n"
        for n in local_news[:5]:
            indicator = "[+]" if n.get("sentiment", 0.5) > 0.55 else ("[-]" if n.get("sentiment", 0.5) < 0.45 else "[=]")
            report += f"{indicator} {n.get('headline', '')[:100]}...\n"
            report += f"    [{n.get('date', '')}] {n.get('source', 'Unknown')}\n\n"
    
    return report


def sentiment_report(symbols=None):
    """Generate sentiment report"""
    from stock_pro.sectors import get_sector
    
    if symbols is None:
        symbols = list(A.keys())
    
    results = []
    
    for sym in symbols:
        sentiment = calculate_sentiment(sym)
        analysis = analyze_multiple([sym])[0] if sym in A else None
        
        results.append({
            "symbol": sym,
            "sector": get_sector(sym),
            "sentiment": sentiment["sentiment"],
            "news_count": sentiment["news_count"],
            "trend": sentiment["trend"],
            "score": analysis["score"] if analysis else 0,
            "latest_news": sentiment.get("latest")
        })
    
    # Sort by sentiment
    results.sort(key=lambda x: x["sentiment"], reverse=True)
    
    report = "# News Sentiment Analysis\n\n"
    report += "| Symbol | Sector | Sentiment | Trend | News | Score |\n"
    report += "|--------|--------|-----------|-------|------|-------|\n"
    
    bullish = bearish = neutral = 0
    
    for r in results:
        if r["sentiment"] >= 0.65:
            sentiment_label = "Bullish"
            bullish += 1
        elif r["sentiment"] <= 0.45:
            sentiment_label = "Bearish"
            bearish += 1
        else:
            sentiment_label = "Neutral"
            neutral += 1
        
        report += f"| {r['symbol']} | {r['sector']} | {r['sentiment']:.0%} | {r['trend']} | {r['news_count']} | {r['score']} |\n"
    
    report += f"\n**Summary:** {bullish} Bullish, {neutral} Neutral, {bearish} Bearish\n"
    
    # Top bullish
    top_bullish = [r for r in results if r["sentiment"] >= 0.70][:5]
    if top_bullish:
        report += f"\n**Top Bullish:** {', '.join(r['symbol'] for r in top_bullish)}\n"
    
    return report


# Research Reports Data (Brokerage Research)
RESEARCH_REPORTS = {
    "NVDA": [
        {"date": "2026-03-22", "firm": "Morgan Stanley", "action": "Upgrade", "target": 280, "note": "AI Chip Demand Strong", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Goldman Sachs", "action": "Buy", "target": 275, "note": "Data Center Growth", "conviction": "Medium"},
        {"date": "2026-03-18", "firm": "JPMorgan", "action": "Overweight", "target": 290, "note": "AI Leadership", "conviction": "High"},
        {"date": "2026-03-15", "firm": "Bank of America", "action": "Buy", "target": 270, "note": "Gaming & AI", "conviction": "High"},
    ],
    "MSFT": [
        {"date": "2026-03-21", "firm": "BofA", "action": "Buy", "target": 520, "note": "Cloud Momentum", "conviction": "High"},
        {"date": "2026-03-19", "firm": "UBS", "action": "Buy", "target": 500, "note": "AI Integration", "conviction": "Medium"},
        {"date": "2026-03-17", "firm": "Deutsche Bank", "action": "Buy", "target": 510, "note": "Enterprise Strength", "conviction": "High"},
    ],
    "GOOGL": [
        {"date": "2026-03-22", "firm": "Deutsche Bank", "action": "Buy", "target": 400, "note": "AI Search Improvement", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Morgan Stanley", "action": "Overweight", "target": 390, "note": "Cloud Growth", "conviction": "Medium"},
        {"date": "2026-03-18", "firm": "Goldman Sachs", "action": "Buy", "target": 385, "note": "Ad Market Recovery", "conviction": "Medium"},
    ],
    "AAPL": [
        {"date": "2026-03-21", "firm": "Citigroup", "action": "Neutral", "target": 280, "note": "iPhone Cycle Mature", "conviction": "Medium"},
        {"date": "2026-03-19", "firm": "Barclays", "action": "Underweight", "target": 250, "note": "China Risk", "conviction": "High"},
        {"date": "2026-03-17", "firm": "Morgan Stanley", "action": "Equal-Weight", "target": 270, "note": "Services Growth", "conviction": "Medium"},
    ],
    "META": [
        {"date": "2026-03-22", "firm": "Wedbush", "action": "Outperform", "target": 900, "note": "AI Ad Targeting", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Loop Capital", "action": "Buy", "target": 850, "note": "Reels Growth", "conviction": "Medium"},
        {"date": "2026-03-18", "firm": "Piper Sandler", "action": "Overweight", "target": 880, "note": "Monetization", "conviction": "High"},
    ],
    "TSLA": [
        {"date": "2026-03-21", "firm": "Bernstein", "action": "Market Perform", "target": 250, "note": "Margin Pressure", "conviction": "Medium"},
        {"date": "2026-03-19", "firm": "Goldman Sachs", "action": "Sell", "target": 220, "note": "Competition Concerns", "conviction": "High"},
        {"date": "2026-03-17", "firm": "Morgan Stanley", "action": "Equal-Weight", "target": 240, "note": "EV Competition", "conviction": "Medium"},
    ],
    "AMZN": [
        {"date": "2026-03-22", "firm": "Evercore", "action": "Outperform", "target": 450, "note": "AWS AI Services", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Mizuho", "action": "Buy", "target": 420, "note": "Retail Margins", "conviction": "Medium"},
        {"date": "2026-03-18", "firm": "UBS", "action": "Buy", "target": 430, "note": "Cloud Expansion", "conviction": "High"},
    ],
    "AVGO": [
        {"date": "2026-03-22", "firm": "Morgan Stanley", "action": "Overweight", "target": 1800, "note": "AI Infrastructure", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Goldman Sachs", "action": "Buy", "target": 1750, "note": "Networking Growth", "conviction": "Medium"},
    ],
}


def get_research_reports(symbol, days=30):
    """Get recent research reports for symbol"""
    today = datetime.now()
    cutoff = today - timedelta(days=days)
    
    reports = RESEARCH_REPORTS.get(symbol, [])
    filtered = []
    for r in reports:
        date = datetime.strptime(r["date"], "%Y-%m-%d")
        if date >= cutoff:
            filtered.append(r)
    return filtered


def research_report(symbols=None):
    """Generate research reports summary"""
    if symbols is None:
        symbols = ["NVDA", "MSFT", "GOOGL", "AAPL", "META", "AMZN", "TSLA", "AMD"]
    
    report = "# Research Reports Summary\n\n"
    
    strong_buys = []
    upgrades = []
    downgrades = []
    
    for sym in symbols:
        reports = get_research_reports(sym)
        if not reports:
            continue
        
        # Aggregate
        actions = [r["action"] for r in reports]
        avg_target = sum(r["target"] for r in reports) / len(reports)
        
        for r in reports:
            if r["action"] in ("Upgrade", "Outperform", "Strong Buy", "Buy"):
                strong_buys.append((sym, r))
            elif r["action"] in ("Downgrade", "Underperform", "Sell"):
                downgrades.append((sym, r))
    
    # Sort by conviction
    strong_buys.sort(key=lambda x: x[1]["conviction"] == "High", reverse=True)
    downgrades.sort(key=lambda x: x[1]["conviction"] == "High", reverse=True)
    
    report += "## Upgrades & Initiations\n"
    report += "| Date | Symbol | Firm | Action | Target | Note |\n"
    report += "|------|--------|------|--------|--------|------|\n"
    for sym, r in strong_buys[:10]:
        report += f"| {r['date']} | {sym} | {r['firm']} | {r['action']} | ${r['target']} | {r['note']} |\n"
    
    report += "\n## Downgrades\n"
    report += "| Date | Symbol | Firm | Action | Target | Note |\n"
    report += "|------|--------|------|--------|--------|------|\n"
    for sym, r in downgrades[:10]:
        report += f"| {r['date']} | {sym} | {r['firm']} | {r['action']} | ${r['target']} | {r['note']} |\n"
    
    return report


def combined_analysis(symbol):
    """Combined technical + news + research analysis"""
    from stock_pro.core import detect_trend, analyze
    
    data = analyze(symbol) if symbol in A else None
    sentiment = calculate_sentiment(symbol)
    reports = get_research_reports(symbol)
    trend = detect_trend(symbol, data["price"]) if data else None
    
    # Combine scores
    technical_score = data["score"] if data else 50
    sentiment_score = sentiment["sentiment"] * 100
    research_score = 50  # Neutral baseline
    
    # Adjust based on research
    for r in reports:
        if r["action"] in ("Buy", "Outperform", "Upgrade"):
            research_score += 10
        elif r["action"] in ("Sell", "Underperform", "Downgrade"):
            research_score -= 10
    
    # Weighted composite
    composite = (
        technical_score * 0.40 +
        sentiment_score * 0.30 +
        research_score * 0.30
    )
    
    # Recommendation
    if composite >= 75: recommendation = "STRONG BUY"
    elif composite >= 65: recommendation = "BUY"
    elif composite >= 55: recommendation = "HOLD"
    elif composite >= 45: recommendation = "WEAK HOLD"
    else: recommendation = "SELL"
    
    return {
        "symbol": symbol,
        "composite_score": round(composite, 1),
        "recommendation": recommendation,
        "technical_score": technical_score,
        "sentiment_score": round(sentiment_score, 1),
        "research_score": research_score,
        "news_count": sentiment["news_count"],
        "report_count": len(reports),
        "trend": trend["trend"] if trend else "N/A",
        "signals": trend["signals"] if trend else []
    }


def sentiment_report_full(symbols=None):
    """Full sentiment + research + technical combined report"""
    if symbols is None:
        symbols = ["NVDA", "MSFT", "GOOGL", "AAPL", "META", "AMZN", "TSLA"]
    
    results = [combined_analysis(sym) for sym in symbols if sym in A]
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    
    report = "# Combined Analysis Report\n"
    report += "## Technical + Sentiment + Research\n\n"
    report += "| Symbol | Composite | Rec | Tech | Sentiment | Research | Trend |\n"
    report += "|--------|-----------|-----|------|-----------|----------|-------|\n"
    
    for r in results:
        report += f"| {r['symbol']} | {r['composite_score']:.0f} | {r['recommendation']} | {r['technical_score']} | {r['sentiment_score']:.0f} | {r['research_score']} | {r['trend']} |\n"
    
    report += "\n**Composite Score** = Tech(40%) + Sentiment(30%) + Research(30%)\n"

    return report


def message_sentiment_report(symbols=None, days=7):
    """Comprehensive Message Sentiment Analysis Report (消息面分析)

    Combines:
    - News sentiment (30%)
    - Research/brokerage reports (30%)
    - Technical signals (40%)
    """
    if symbols is None:
        symbols = ["NVDA", "MSFT", "GOOGL", "AAPL", "META", "AMZN", "TSLA", "AMD", "AVGO", "PANW"]

    report = "# Message Sentiment Analysis (消息面分析)\n\n"
    report += f"**Analysis Period:** Last {days} days\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    results = []

    for sym in symbols:
        if sym not in A:
            continue

        # Get news
        news = get_news(sym, days=days)
        news_sentiment = sum(n["sentiment"] for n in news) / len(news) if news else 0.5

        # Get research
        reports = get_research_reports(sym, days=days)
        research_sentiment = 0.5
        if reports:
            for r in reports:
                if r["action"] in ("Buy", "Outperform", "Upgrade", "Strong Buy"):
                    research_sentiment += 0.15
                elif r["action"] in ("Sell", "Underperform", "Downgrade"):
                    research_sentiment -= 0.15

        # Get technical
        from stock_pro.core import detect_trend, analyze
        data = analyze(sym)
        if data:
            trend = detect_trend(sym, data["price"])
            trend_score = 0.5
            for signal, sig_type in trend.get("signals", []):
                if sig_type == "bullish":
                    trend_score += 0.1
                elif sig_type == "bearish":
                    trend_score -= 0.1
        else:
            trend = {"trend": "N/A"}
            trend_score = 0.5

        # Composite message sentiment
        message_score = (
            news_sentiment * 0.35 +
            research_sentiment * 0.35 +
            trend_score * 0.30
        ) * 100

        results.append({
            "symbol": sym,
            "news_count": len(news),
            "news_sentiment": news_sentiment,
            "report_count": len(reports),
            "research_sentiment": research_sentiment,
            "trend": trend["trend"],
            "message_score": round(message_score, 1)
        })

    # Sort by message sentiment
    results.sort(key=lambda x: x["message_score"], reverse=True)

    # Report table
    report += "| Symbol | Msg Score | News | News Sent | Reports | Research | Trend |\n"
    report += "|--------|-----------|------|-----------|---------|----------|-------|\n"

    bullish = neutral = bearish = 0

    for r in results:
        if r["message_score"] >= 65:
            status = "[*] Bullish"
            bullish += 1
        elif r["message_score"] <= 45:
            status = "[-] Bearish"
            bearish += 1
        else:
            status = "[ ] Neutral"
            neutral += 1

        report += f"| {r['symbol']} | {r['message_score']:.0f} | {r['news_count']} | {r['news_sentiment']:.0%} | {r['report_count']} | {r['research_sentiment']:.0%} | {r['trend']} |\n"

    # Summary
    report += "\n## Summary\n\n"
    report += f"- **Bullish:** {bullish} stocks\n"
    report += f"- **Neutral:** {neutral} stocks\n"
    report += f"- **Bearish:** {bearish} stocks\n"

    # Top bullish
    top_bullish = [r for r in results if r["message_score"] >= 65][:5]
    if top_bullish:
        report += f"\n## Top Bullish ({len(top_bullish)} stocks)\n\n"
        for r in top_bullish:
            report += f"- **{r['symbol']}**: Score {r['message_score']:.0f} ({r['trend']})\n"

    # Top bearish
    top_bearish = [r for r in results if r["message_score"] <= 45][:5]
    if top_bearish:
        report += f"\n## Top Bearish ({len(top_bearish)} stocks)\n\n"
        for r in top_bearish:
            report += f"- **{r['symbol']}**: Score {r['message_score']:.0f} ({r['trend']})\n"

    # Methodology
    report += "\n## Methodology\n\n"
    report += "- **News Sentiment (35%):** Average sentiment from recent news articles\n"
    report += "- **Research Sentiment (35%):** Based on analyst actions (Buy/Sell ratings)\n"
    report += "- **Trend Signal (30%):** Based on technical signals (undervalued/overvalued)\n"
    report += "- **Composite Score:** 0-100 (higher = more bullish)\n"

    return report


def message_sentiment_json(symbols=None, days=7):
    """Get message sentiment as JSON for API/integration"""
    if symbols is None:
        symbols = list(A.keys())[:20]

    results = []
    for sym in symbols:
        if sym not in A:
            continue

        news = get_news(sym, days=days)
        reports = get_research_reports(sym, days=days)

        news_sentiment = sum(n["sentiment"] for n in news) / len(news) if news else 0.5
        research_sentiment = 0.5
        if reports:
            for r in reports:
                if r["action"] in ("Buy", "Outperform", "Upgrade"):
                    research_sentiment += 0.15
                elif r["action"] in ("Sell", "Underperform", "Downgrade"):
                    research_sentiment -= 0.15

        message_score = (
            news_sentiment * 0.35 +
            research_sentiment * 0.35 +
            0.50 * 0.30
        ) * 100

        results.append({
            "symbol": sym,
            "message_score": round(message_score, 1),
            "news_count": len(news),
            "news_sentiment": round(news_sentiment, 2),
            "report_count": len(reports),
            "research_sentiment": round(research_sentiment, 2),
            "latest_news": news[0] if news else None,
            "latest_report": reports[0] if reports else None
        })

    return results


# ============================================================
# INSTITUTIONAL OWNERSHIP ANALYSIS (特色功能)
# ============================================================

INSTITUTIONAL_DATA = {
    "NVDA": {
        "institutional_ownership": 0.78,  # 78% held by institutions
        "insider_ownership": 0.04,
        "qoq_change": 2.1,  # Quarter over quarter change (%)
        "top_holders": [
            {"name": "BlackRock", "shares": 1.2, "change": 0.8},
            {"name": "Vanguard", "shares": 1.1, "change": 1.2},
            {"name": "Fidelity", "shares": 0.45, "change": -0.3},
        ],
        "short_interest_ratio": 1.2,
    },
    "MSFT": {
        "institutional_ownership": 0.72,
        "insider_ownership": 0.08,
        "qoq_change": 1.5,
        "top_holders": [
            {"name": "Vanguard", "shares": 1.8, "change": 0.9},
            {"name": "BlackRock", "shares": 1.5, "change": 1.1},
            {"name": "State Street", "shares": 0.8, "change": 0.4},
        ],
        "short_interest_ratio": 0.9,
    },
    "AAPL": {
        "institutional_ownership": 0.59,
        "insider_ownership": 0.05,
        "qoq_change": -0.8,
        "top_holders": [
            {"name": "Vanguard", "shares": 3.2, "change": -0.2},
            {"name": "BlackRock", "shares": 2.8, "change": 0.1},
            {"name": "Berkshire", "shares": 0.9, "change": 0.0},
        ],
        "short_interest_ratio": 0.7,
    },
    "GOOGL": {
        "institutional_ownership": 0.68,
        "insider_ownership": 0.10,
        "qoq_change": 2.3,
        "top_holders": [
            {"name": "Vanguard", "shares": 1.5, "change": 1.5},
            {"name": "BlackRock", "shares": 1.3, "change": 2.1},
            {"name": "Fidelity", "shares": 0.6, "change": 0.8},
        ],
        "short_interest_ratio": 1.0,
    },
    "META": {
        "institutional_ownership": 0.80,
        "insider_ownership": 0.06,
        "qoq_change": 3.2,
        "top_holders": [
            {"name": "Vanguard", "shares": 0.9, "change": 2.1},
            {"name": "BlackRock", "shares": 0.8, "change": 1.8},
            {"name": "Tech Fund", "shares": 0.4, "change": 3.5},
        ],
        "short_interest_ratio": 1.5,
    },
    "TSLA": {
        "institutional_ownership": 0.44,
        "insider_ownership": 0.20,
        "qoq_change": -5.2,
        "top_holders": [
            {"name": "Vanguard", "shares": 0.8, "change": -2.1},
            {"name": "BlackRock", "shares": 0.7, "change": -1.8},
            {"name": "Elon Musk", "shares": 0.65, "change": 0.0},
        ],
        "short_interest_ratio": 4.2,
    },
    "AMZN": {
        "institutional_ownership": 0.65,
        "insider_ownership": 0.07,
        "qoq_change": 1.8,
        "top_holders": [
            {"name": "Vanguard", "shares": 2.1, "change": 1.2},
            {"name": "BlackRock", "shares": 1.8, "change": 1.5},
            {"name": "Bezos", "shares": 0.5, "change": 0.0},
        ],
        "short_interest_ratio": 1.1,
    },
    "AMD": {
        "institutional_ownership": 0.62,
        "insider_ownership": 0.03,
        "qoq_change": 4.1,
        "top_holders": [
            {"name": "Vanguard", "shares": 0.4, "change": 2.5},
            {"name": "BlackRock", "shares": 0.35, "change": 3.1},
            {"name": "Fidelity", "shares": 0.2, "change": 1.8},
        ],
        "short_interest_ratio": 2.1,
    },
}


def get_institutional_data(symbol):
    """Get institutional ownership data for symbol"""
    return INSTITUTIONAL_DATA.get(symbol, {
        "institutional_ownership": 0.50,
        "insider_ownership": 0.05,
        "qoq_change": 0.0,
        "top_holders": [],
        "short_interest_ratio": 1.0,
    })


def institutional_analysis(symbol):
    """Analyze institutional ownership and generate signal"""
    from stock_pro.core import detect_trend, analyze
    
    data = get_institutional_data(symbol)
    
    io = data["institutional_ownership"]
    qoq = data["qoq_change"]
    si = data["short_interest_ratio"]
    
    # Signals
    signals = []
    
    # Institutional ownership signal (>60% is positive)
    if io >= 0.70:
        signals.append(("INST_STRONG_SUPPORT", "High institutional backing"))
    elif io >= 0.50:
        signals.append(("INST_MODERATE", "Moderate institutional interest"))
    else:
        signals.append(("INST_LOW", "Low institutional interest"))
    
    # Quarter over quarter change
    if qoq >= 3.0:
        signals.append(("INST_ACCUMULATION", "Heavy accumulation"))
    elif qoq >= 1.0:
        signals.append(("INST_BUILDING", "Building position"))
    elif qoq <= -3.0:
        signals.append(("INST_DISTRIBUTION", "Distribution/selling"))
    elif qoq <= -1.0:
        signals.append(("INST_REDUCING", "Reducing position"))
    
    # Short interest analysis
    if si >= 4.0:
        signals.append(("HIGH_SHORT_SQUEEZE_RISK", "High short squeeze risk"))
    elif si >= 2.0:
        signals.append(("ELEVATED_SHORT", "Elevated short interest"))
    elif si < 0.5:
        signals.append(("LOW_SHORT_BULLISH", "Low short interest - bullish"))
    
    # Institutional score (0-100)
    score = min(100, int(
        io * 40 +  # Institutional ownership weight
        max(0, qoq) * 5 +  # Positive accumulation
        (20 - min(si, 10)) * 2  # Low short interest bonus
    ))
    
    return {
        "symbol": symbol,
        "institutional_ownership": f"{io*100:.1f}%",
        "qoq_change": f"{qoq:+.1f}%",
        "short_interest_ratio": si,
        "score": score,
        "signals": signals,
        "top_holders": data["top_holders"][:3],
    }


def institutional_report(symbols=None):
    """Generate institutional ownership report"""
    if symbols is None:
        symbols = ["NVDA", "MSFT", "GOOGL", "AAPL", "META", "AMZN", "TSLA", "AMD"]
    
    results = [institutional_analysis(sym) for sym in symbols]
    results.sort(key=lambda x: x["score"], reverse=True)
    
    report = "# Institutional Ownership Analysis\n\n"
    report += "## Institutional Activity\n\n"
    report += "| Symbol | IO % | QoQ | Short | Score | Key Signal |\n"
    report += "|--------|------|-----|-------|-------|------------|\n"
    
    for r in results:
        signal = r["signals"][0][0] if r["signals"] else "N/A"
        report += f"| {r['symbol']} | {r['institutional_ownership']} | {r['qoq_change']} | {r['short_interest_ratio']} | {r['score']} | {signal} |\n"
    
    report += "\n## Signal Legend\n"
    report += "- **INST_STRONG_SUPPORT**: >70% institutional ownership\n"
    report += "- **INST_ACCUMULATION**: QoQ change >3%\n"
    report += "- **HIGH_SHORT_SQUEEZE_RISK**: Short interest >4%\n"
    
    return report


def sector_sentiment():
    """Get sector-level sentiment"""
    from stock_pro.sectors import get_all_sectors, get_symbols_by_sector
    
    sectors = get_all_sectors()
    
    sector_sentiments = []
    for sector in sectors:
        symbols = get_symbols_by_sector(sector)
        
        sentiments = []
        for sym in symbols:
            s = calculate_sentiment(sym)
            if s["news_count"] > 0:
                sentiments.append(s["sentiment"])
        
        if sentiments:
            avg = sum(sentiments) / len(sentiments)
            sector_sentiments.append({
                "sector": sector,
                "avg_sentiment": avg,
                "stocks_with_news": len(sentiments)
            })
    
    sector_sentiments.sort(key=lambda x: x["avg_sentiment"], reverse=True)
    
    report = "# Sector Sentiment\n\n"
    report += "| Sector | Avg Sentiment | Active Stocks |\n"
    report += "|--------|---------------|----------------|\n"
    
    for s in sector_sentiments:
        report += f"| {s['sector']} | {s['avg_sentiment']:.0%} | {s['stocks_with_news']} |\n"
    
    return report


# Research Reports Data (Brokerage Research)
RESEARCH_REPORTS = {
    "NVDA": [
        {"date": "2026-03-22", "firm": "Morgan Stanley", "action": "Upgrade", "target": 280, "note": "AI Chip Demand Strong", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Goldman Sachs", "action": "Buy", "target": 275, "note": "Data Center Growth", "conviction": "Medium"},
        {"date": "2026-03-18", "firm": "JPMorgan", "action": "Overweight", "target": 290, "note": "AI Leadership", "conviction": "High"},
        {"date": "2026-03-15", "firm": "Bank of America", "action": "Buy", "target": 270, "note": "Gaming & AI", "conviction": "High"},
    ],
    "MSFT": [
        {"date": "2026-03-21", "firm": "BofA", "action": "Buy", "target": 520, "note": "Cloud Momentum", "conviction": "High"},
        {"date": "2026-03-19", "firm": "UBS", "action": "Buy", "target": 500, "note": "AI Integration", "conviction": "Medium"},
        {"date": "2026-03-17", "firm": "Deutsche Bank", "action": "Buy", "target": 510, "note": "Enterprise Strength", "conviction": "High"},
    ],
    "GOOGL": [
        {"date": "2026-03-22", "firm": "Deutsche Bank", "action": "Buy", "target": 400, "note": "AI Search Improvement", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Morgan Stanley", "action": "Overweight", "target": 390, "note": "Cloud Growth", "conviction": "Medium"},
        {"date": "2026-03-18", "firm": "Goldman Sachs", "action": "Buy", "target": 385, "note": "Ad Market Recovery", "conviction": "Medium"},
    ],
    "AAPL": [
        {"date": "2026-03-21", "firm": "Citigroup", "action": "Neutral", "target": 280, "note": "iPhone Cycle Mature", "conviction": "Medium"},
        {"date": "2026-03-19", "firm": "Barclays", "action": "Underweight", "target": 250, "note": "China Risk", "conviction": "High"},
        {"date": "2026-03-17", "firm": "Morgan Stanley", "action": "Equal-Weight", "target": 270, "note": "Services Growth", "conviction": "Medium"},
    ],
    "META": [
        {"date": "2026-03-22", "firm": "Wedbush", "action": "Outperform", "target": 900, "note": "AI Ad Targeting", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Loop Capital", "action": "Buy", "target": 850, "note": "Reels Growth", "conviction": "Medium"},
        {"date": "2026-03-18", "firm": "Piper Sandler", "action": "Overweight", "target": 880, "note": "Monetization", "conviction": "High"},
    ],
    "TSLA": [
        {"date": "2026-03-21", "firm": "Bernstein", "action": "Market Perform", "target": 250, "note": "Margin Pressure", "conviction": "Medium"},
        {"date": "2026-03-19", "firm": "Goldman Sachs", "action": "Sell", "target": 220, "note": "Competition Concerns", "conviction": "High"},
        {"date": "2026-03-17", "firm": "Morgan Stanley", "action": "Equal-Weight", "target": 240, "note": "EV Competition", "conviction": "Medium"},
    ],
    "AMZN": [
        {"date": "2026-03-22", "firm": "Evercore", "action": "Outperform", "target": 450, "note": "AWS AI Services", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Mizuho", "action": "Buy", "target": 420, "note": "Retail Margins", "conviction": "Medium"},
        {"date": "2026-03-18", "firm": "UBS", "action": "Buy", "target": 430, "note": "Cloud Expansion", "conviction": "High"},
    ],
    "AVGO": [
        {"date": "2026-03-22", "firm": "Morgan Stanley", "action": "Overweight", "target": 1800, "note": "AI Infrastructure", "conviction": "High"},
        {"date": "2026-03-20", "firm": "Goldman Sachs", "action": "Buy", "target": 1750, "note": "Networking Growth", "conviction": "Medium"},
    ],
}


def get_research_reports(symbol, days=30):
    """Get recent research reports for symbol"""
    today = datetime.now()
    cutoff = today - timedelta(days=days)
    
    reports = RESEARCH_REPORTS.get(symbol, [])
    filtered = []
    for r in reports:
        date = datetime.strptime(r["date"], "%Y-%m-%d")
        if date >= cutoff:
            filtered.append(r)
    return filtered


def research_report(symbols=None):
    """Generate research reports summary"""
    if symbols is None:
        symbols = ["NVDA", "MSFT", "GOOGL", "AAPL", "META", "AMZN", "TSLA", "AMD"]
    
    report = "# Research Reports Summary\n\n"
    
    strong_buys = []
    upgrades = []
    downgrades = []
    
    for sym in symbols:
        reports = get_research_reports(sym)
        if not reports:
            continue
        
        # Aggregate
        actions = [r["action"] for r in reports]
        avg_target = sum(r["target"] for r in reports) / len(reports)
        
        for r in reports:
            if r["action"] in ("Upgrade", "Outperform", "Strong Buy", "Buy"):
                strong_buys.append((sym, r))
            elif r["action"] in ("Downgrade", "Underperform", "Sell"):
                downgrades.append((sym, r))
    
    # Sort by conviction
    strong_buys.sort(key=lambda x: x[1]["conviction"] == "High", reverse=True)
    downgrades.sort(key=lambda x: x[1]["conviction"] == "High", reverse=True)
    
    report += "## Upgrades & Initiations\n"
    report += "| Date | Symbol | Firm | Action | Target | Note |\n"
    report += "|------|--------|------|--------|--------|------|\n"
    for sym, r in strong_buys[:10]:
        report += f"| {r['date']} | {sym} | {r['firm']} | {r['action']} | ${r['target']} | {r['note']} |\n"
    
    report += "\n## Downgrades\n"
    report += "| Date | Symbol | Firm | Action | Target | Note |\n"
    report += "|------|--------|------|--------|--------|------|\n"
    for sym, r in downgrades[:10]:
        report += f"| {r['date']} | {sym} | {r['firm']} | {r['action']} | ${r['target']} | {r['note']} |\n"
    
    return report


def combined_analysis(symbol):
    """Combined technical + news + research analysis"""
    from stock_pro.core import detect_trend, analyze
    
    data = analyze(symbol) if symbol in A else None
    sentiment = calculate_sentiment(symbol)
    reports = get_research_reports(symbol)
    trend = detect_trend(symbol, data["price"]) if data else None
    
    # Combine scores
    technical_score = data["score"] if data else 50
    sentiment_score = sentiment["sentiment"] * 100
    research_score = 50  # Neutral baseline
    
    # Adjust based on research
    for r in reports:
        if r["action"] in ("Buy", "Outperform", "Upgrade"):
            research_score += 10
        elif r["action"] in ("Sell", "Underperform", "Downgrade"):
            research_score -= 10
    
    # Weighted composite
    composite = (
        technical_score * 0.40 +
        sentiment_score * 0.30 +
        research_score * 0.30
    )
    
    # Recommendation
    if composite >= 75: recommendation = "STRONG BUY"
    elif composite >= 65: recommendation = "BUY"
    elif composite >= 55: recommendation = "HOLD"
    elif composite >= 45: recommendation = "WEAK HOLD"
    else: recommendation = "SELL"
    
    return {
        "symbol": symbol,
        "composite_score": round(composite, 1),
        "recommendation": recommendation,
        "technical_score": technical_score,
        "sentiment_score": round(sentiment_score, 1),
        "research_score": research_score,
        "news_count": sentiment["news_count"],
        "report_count": len(reports),
        "trend": trend["trend"] if trend else "N/A",
        "signals": trend["signals"] if trend else []
    }


def sentiment_report_full(symbols=None):
    """Full sentiment + research + technical combined report"""
    if symbols is None:
        symbols = ["NVDA", "MSFT", "GOOGL", "AAPL", "META", "AMZN", "TSLA"]
    
    results = [combined_analysis(sym) for sym in symbols if sym in A]
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    
    report = "# Combined Analysis Report\n"
    report += "## Technical + Sentiment + Research\n\n"
    report += "| Symbol | Composite | Rec | Tech | Sentiment | Research | Trend |\n"
    report += "|--------|-----------|-----|------|-----------|----------|-------|\n"
    
    for r in results:
        report += f"| {r['symbol']} | {r['composite_score']:.0f} | {r['recommendation']} | {r['technical_score']} | {r['sentiment_score']:.0f} | {r['research_score']} | {r['trend']} |\n"
    
    report += "\n**Composite Score** = Tech(40%) + Sentiment(30%) + Research(30%)\n"

    return report


def message_sentiment_report(symbols=None, days=7):
    """Comprehensive Message Sentiment Analysis Report (消息面分析)

    Combines:
    - News sentiment (30%)
    - Research/brokerage reports (30%)
    - Technical signals (40%)
    """
    if symbols is None:
        symbols = ["NVDA", "MSFT", "GOOGL", "AAPL", "META", "AMZN", "TSLA", "AMD", "AVGO", "PANW"]

    report = "# Message Sentiment Analysis (消息面分析)\n\n"
    report += f"**Analysis Period:** Last {days} days\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    results = []

    for sym in symbols:
        if sym not in A:
            continue

        # Get news
        news = get_news(sym, days=days)
        news_sentiment = sum(n["sentiment"] for n in news) / len(news) if news else 0.5

        # Get research
        reports = get_research_reports(sym, days=days)
        research_sentiment = 0.5
        if reports:
            for r in reports:
                if r["action"] in ("Buy", "Outperform", "Upgrade", "Strong Buy"):
                    research_sentiment += 0.15
                elif r["action"] in ("Sell", "Underperform", "Downgrade"):
                    research_sentiment -= 0.15

        # Get technical
        from stock_pro.core import detect_trend, analyze
        data = analyze(sym)
        if data:
            trend = detect_trend(sym, data["price"])
            trend_score = 0.5
            for signal, sig_type in trend.get("signals", []):
                if sig_type == "bullish":
                    trend_score += 0.1
                elif sig_type == "bearish":
                    trend_score -= 0.1
        else:
            trend = {"trend": "N/A"}
            trend_score = 0.5

        # Composite message sentiment
        message_score = (
            news_sentiment * 0.35 +
            research_sentiment * 0.35 +
            trend_score * 0.30
        ) * 100

        results.append({
            "symbol": sym,
            "news_count": len(news),
            "news_sentiment": news_sentiment,
            "report_count": len(reports),
            "research_sentiment": research_sentiment,
            "trend": trend["trend"],
            "message_score": round(message_score, 1)
        })

    # Sort by message sentiment
    results.sort(key=lambda x: x["message_score"], reverse=True)

    # Report table
    report += "| Symbol | Msg Score | News | News Sent | Reports | Research | Trend |\n"
    report += "|--------|-----------|------|-----------|---------|----------|-------|\n"

    bullish = neutral = bearish = 0

    for r in results:
        if r["message_score"] >= 65:
            status = "[*] Bullish"
            bullish += 1
        elif r["message_score"] <= 45:
            status = "[-] Bearish"
            bearish += 1
        else:
            status = "[ ] Neutral"
            neutral += 1

        report += f"| {r['symbol']} | {r['message_score']:.0f} | {r['news_count']} | {r['news_sentiment']:.0%} | {r['report_count']} | {r['research_sentiment']:.0%} | {r['trend']} |\n"

    # Summary
    report += "\n## Summary\n\n"
    report += f"- **Bullish:** {bullish} stocks\n"
    report += f"- **Neutral:** {neutral} stocks\n"
    report += f"- **Bearish:** {bearish} stocks\n"

    # Top bullish
    top_bullish = [r for r in results if r["message_score"] >= 65][:5]
    if top_bullish:
        report += f"\n## Top Bullish ({len(top_bullish)} stocks)\n\n"
        for r in top_bullish:
            report += f"- **{r['symbol']}**: Score {r['message_score']:.0f} ({r['trend']})\n"

    # Top bearish
    top_bearish = [r for r in results if r["message_score"] <= 45][:5]
    if top_bearish:
        report += f"\n## Top Bearish ({len(top_bearish)} stocks)\n\n"
        for r in top_bearish:
            report += f"- **{r['symbol']}**: Score {r['message_score']:.0f} ({r['trend']})\n"

    # Methodology
    report += "\n## Methodology\n\n"
    report += "- **News Sentiment (35%):** Average sentiment from recent news articles\n"
    report += "- **Research Sentiment (35%):** Based on analyst actions (Buy/Sell ratings)\n"
    report += "- **Trend Signal (30%):** Based on technical signals (undervalued/overvalued)\n"
    report += "- **Composite Score:** 0-100 (higher = more bullish)\n"

    return report


def message_sentiment_json(symbols=None, days=7):
    """Get message sentiment as JSON for API/integration"""
    if symbols is None:
        symbols = list(A.keys())[:20]

    results = []
    for sym in symbols:
        if sym not in A:
            continue

        news = get_news(sym, days=days)
        reports = get_research_reports(sym, days=days)

        news_sentiment = sum(n["sentiment"] for n in news) / len(news) if news else 0.5
        research_sentiment = 0.5
        if reports:
            for r in reports:
                if r["action"] in ("Buy", "Outperform", "Upgrade"):
                    research_sentiment += 0.15
                elif r["action"] in ("Sell", "Underperform", "Downgrade"):
                    research_sentiment -= 0.15

        message_score = (
            news_sentiment * 0.35 +
            research_sentiment * 0.35 +
            0.50 * 0.30
        ) * 100

        results.append({
            "symbol": sym,
            "message_score": round(message_score, 1),
            "news_count": len(news),
            "news_sentiment": round(news_sentiment, 2),
            "report_count": len(reports),
            "research_sentiment": round(research_sentiment, 2),
            "latest_news": news[0] if news else None,
            "latest_report": reports[0] if reports else None
        })

    return results


# ============================================================
# INSTITUTIONAL OWNERSHIP ANALYSIS (特色功能)
# ============================================================

INSTITUTIONAL_DATA = {
    "NVDA": {
        "institutional_ownership": 0.78,  # 78% held by institutions
        "insider_ownership": 0.04,
        "qoq_change": 2.1,  # Quarter over quarter change (%)
        "top_holders": [
            {"name": "BlackRock", "shares": 1.2, "change": 0.8},
            {"name": "Vanguard", "shares": 1.1, "change": 1.2},
            {"name": "Fidelity", "shares": 0.45, "change": -0.3},
        ],
        "short_interest_ratio": 1.2,
    },
    "MSFT": {
        "institutional_ownership": 0.72,
        "insider_ownership": 0.08,
        "qoq_change": 1.5,
        "top_holders": [
            {"name": "Vanguard", "shares": 1.8, "change": 0.9},
            {"name": "BlackRock", "shares": 1.5, "change": 1.1},
            {"name": "State Street", "shares": 0.8, "change": 0.4},
        ],
        "short_interest_ratio": 0.9,
    },
    "AAPL": {
        "institutional_ownership": 0.59,
        "insider_ownership": 0.05,
        "qoq_change": -0.8,
        "top_holders": [
            {"name": "Vanguard", "shares": 3.2, "change": -0.2},
            {"name": "BlackRock", "shares": 2.8, "change": 0.1},
            {"name": "Berkshire", "shares": 0.9, "change": 0.0},
        ],
        "short_interest_ratio": 0.7,
    },
    "GOOGL": {
        "institutional_ownership": 0.68,
        "insider_ownership": 0.10,
        "qoq_change": 2.3,
        "top_holders": [
            {"name": "Vanguard", "shares": 1.5, "change": 1.5},
            {"name": "BlackRock", "shares": 1.3, "change": 2.1},
            {"name": "Fidelity", "shares": 0.6, "change": 0.8},
        ],
        "short_interest_ratio": 1.0,
    },
    "META": {
        "institutional_ownership": 0.80,
        "insider_ownership": 0.06,
        "qoq_change": 3.2,
        "top_holders": [
            {"name": "Vanguard", "shares": 0.9, "change": 2.1},
            {"name": "BlackRock", "shares": 0.8, "change": 1.8},
            {"name": "Tech Fund", "shares": 0.4, "change": 3.5},
        ],
        "short_interest_ratio": 1.5,
    },
    "TSLA": {
        "institutional_ownership": 0.44,
        "insider_ownership": 0.20,
        "qoq_change": -5.2,
        "top_holders": [
            {"name": "Vanguard", "shares": 0.8, "change": -2.1},
            {"name": "BlackRock", "shares": 0.7, "change": -1.8},
            {"name": "Elon Musk", "shares": 0.65, "change": 0.0},
        ],
        "short_interest_ratio": 4.2,
    },
    "AMZN": {
        "institutional_ownership": 0.65,
        "insider_ownership": 0.07,
        "qoq_change": 1.8,
        "top_holders": [
            {"name": "Vanguard", "shares": 2.1, "change": 1.2},
            {"name": "BlackRock", "shares": 1.8, "change": 1.5},
            {"name": "Bezos", "shares": 0.5, "change": 0.0},
        ],
        "short_interest_ratio": 1.1,
    },
    "AMD": {
        "institutional_ownership": 0.62,
        "insider_ownership": 0.03,
        "qoq_change": 4.1,
        "top_holders": [
            {"name": "Vanguard", "shares": 0.4, "change": 2.5},
            {"name": "BlackRock", "shares": 0.35, "change": 3.1},
            {"name": "Fidelity", "shares": 0.2, "change": 1.8},
        ],
        "short_interest_ratio": 2.1,
    },
}


def get_institutional_data(symbol):
    """Get institutional ownership data for symbol"""
    return INSTITUTIONAL_DATA.get(symbol, {
        "institutional_ownership": 0.50,
        "insider_ownership": 0.05,
        "qoq_change": 0.0,
        "top_holders": [],
        "short_interest_ratio": 1.0,
    })


def institutional_analysis(symbol):
    """Analyze institutional ownership and generate signal"""
    from stock_pro.core import detect_trend, analyze
    
    data = get_institutional_data(symbol)
    
    io = data["institutional_ownership"]
    qoq = data["qoq_change"]
    si = data["short_interest_ratio"]
    
    # Signals
    signals = []
    
    # Institutional ownership signal (>60% is positive)
    if io >= 0.70:
        signals.append(("INST_STRONG_SUPPORT", "High institutional backing"))
    elif io >= 0.50:
        signals.append(("INST_MODERATE", "Moderate institutional interest"))
    else:
        signals.append(("INST_LOW", "Low institutional interest"))
    
    # Quarter over quarter change
    if qoq >= 3.0:
        signals.append(("INST_ACCUMULATION", "Heavy accumulation"))
    elif qoq >= 1.0:
        signals.append(("INST_BUILDING", "Building position"))
    elif qoq <= -3.0:
        signals.append(("INST_DISTRIBUTION", "Distribution/selling"))
    elif qoq <= -1.0:
        signals.append(("INST_REDUCING", "Reducing position"))
    
    # Short interest analysis
    if si >= 4.0:
        signals.append(("HIGH_SHORT_SQUEEZE_RISK", "High short squeeze risk"))
    elif si >= 2.0:
        signals.append(("ELEVATED_SHORT", "Elevated short interest"))
    elif si < 0.5:
        signals.append(("LOW_SHORT_BULLISH", "Low short interest - bullish"))
    
    # Institutional score (0-100)
    score = min(100, int(
        io * 40 +  # Institutional ownership weight
        max(0, qoq) * 5 +  # Positive accumulation
        (20 - min(si, 10)) * 2  # Low short interest bonus
    ))
    
    return {
        "symbol": symbol,
        "institutional_ownership": f"{io*100:.1f}%",
        "qoq_change": f"{qoq:+.1f}%",
        "short_interest_ratio": si,
        "score": score,
        "signals": signals,
        "top_holders": data["top_holders"][:3],
    }

