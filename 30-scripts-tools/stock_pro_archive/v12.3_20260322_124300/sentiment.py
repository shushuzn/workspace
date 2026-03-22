"""News and Sentiment Analysis"""
from datetime import datetime, timedelta
from stock_pro.core import A, analyze_multiple

# Simulated news data (in real implementation, fetch from news API)
NEWS_DATA = {
    "NVDA": [
        {"date": "2026-03-21", "headline": "NVIDIA Reports Record AI Chip Demand", "sentiment": 0.85, "source": "Reuters"},
        {"date": "2026-03-20", "headline": "NVIDIA Announces New GPU Architecture", "sentiment": 0.78, "source": "TechCrunch"},
        {"date": "2026-03-18", "headline": "AI Chip Market Growth Exceeds Expectations", "sentiment": 0.72, "source": "Bloomberg"},
    ],
    "META": [
        {"date": "2026-03-21", "headline": "Meta AI Users Reach New Milestone", "sentiment": 0.75, "source": "CNBC"},
        {"date": "2026-03-19", "headline": "Meta Announces VR Headset Sales", "sentiment": 0.62, "source": "WSJ"},
    ],
    "AAPL": [
        {"date": "2026-03-20", "headline": "iPhone Sales Show Strong Growth in Asia", "sentiment": 0.68, "source": "Reuters"},
        {"date": "2026-03-18", "headline": "Apple Services Revenue Hits Record", "sentiment": 0.82, "source": "Bloomberg"},
    ],
    "MSFT": [
        {"date": "2026-03-21", "headline": "Microsoft Cloud Revenue Surges", "sentiment": 0.80, "source": "CNBC"},
        {"date": "2026-03-19", "headline": "Azure Expands AI Capabilities", "sentiment": 0.77, "source": "TechCrunch"},
    ],
    "GOOGL": [
        {"date": "2026-03-20", "headline": "Google Search Volume Increases", "sentiment": 0.65, "source": "Reuters"},
        {"date": "2026-03-17", "headline": "YouTube Ad Revenue Beats Estimates", "sentiment": 0.70, "source": "Bloomberg"},
    ],
    "TSLA": [
        {"date": "2026-03-21", "headline": "Tesla Deliveries Meet Expectations", "sentiment": 0.45, "source": "WSJ"},
        {"date": "2026-03-19", "headline": "EV Market Competition Intensifies", "sentiment": 0.35, "source": "Reuters"},
    ],
    "AMZN": [
        {"date": "2026-03-21", "headline": "AWS Revenue Growth Accelerates", "sentiment": 0.78, "source": "CNBC"},
        {"date": "2026-03-18", "headline": "Amazon Prime Membership Grows", "sentiment": 0.72, "source": "Bloomberg"},
    ],
}


def get_news(symbol, days=7):
    """Get recent news for a symbol"""
    today = datetime.now()
    cutoff = today - timedelta(days=days)
    
    news = NEWS_DATA.get(symbol, [])
    
    filtered = []
    for n in news:
        date = datetime.strptime(n["date"], "%Y-%m-%d")
        if date >= cutoff:
            filtered.append(n)
    
    return filtered


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
