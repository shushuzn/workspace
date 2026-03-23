#!/usr/bin/env python3
"""News API - Real-time news from local cache"""
from pathlib import Path
import sqlite3
from datetime import datetime

DB = Path(__file__).parent / "news_cache.db"

# Stock keywords
KW = {
    "NVDA": ["NVIDIA", "英伟达", "算力", "黄仁勋"],
    "TSLA": ["Tesla", "特斯拉", "马斯克", "电动车"],
    "MSFT": ["微软", "Azure", "纳德拉"],
    "AAPL": ["苹果", "iPhone", "库克"],
    "GOOGL": ["谷歌", "Google", "搜索"],
    "META": ["Meta", "Facebook", "元宇宙"],
    "AMZN": ["亚马逊", "AWS", "贝索斯"],
    "AMD": ["AMD", "苏姿丰", "芯片"],
    "JPM": ["摩根", "银行"],
    "AI": ["AI", "人工智能", "大模型", "DeepSeek"],
    "CHIP": ["芯片", "半导体"],
    "CRYPTO": ["比特币", "BTC", "以太坊", "ETH", "加密货币"],
    "OIL": ["原油", "石油", "OPEC"],
    "GOLD": ["黄金", "白银"],
}

def get_news(symbol=None, hours=24, limit=50):
    """Get news from cache (millisecond response)"""
    if not DB.exists():
        return {"error": "No news cache", "count": 0, "news": []}
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    if symbol:
        kws = KW.get(symbol.upper(), [symbol])
        sql = " OR ".join(["t LIKE ?" for _ in kws])
        params = [f"%{k}%" for k in kws] + [f"-{hours} hours", limit]
        query = f"SELECT s,t,u,ts FROM n WHERE ({sql}) AND ts>datetime('now', ?) ORDER BY ts DESC LIMIT ?"
    else:
        query = f"SELECT s,t,u,ts FROM n WHERE ts>datetime('now', ?) ORDER BY ts DESC LIMIT ?"
        params = [f"-{hours} hours", limit]
    
    rows = c.execute(query, params).fetchall()
    conn.close()
    
    return {
        "count": len(rows),
        "news": [
            {"source": r[0], "title": r[1], "url": r[2], "time": r[3]}
            for r in rows
        ]
    }


def get_stats():
    """Get cache statistics"""
    if not DB.exists():
        return {"total": 0}
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM n")
    total = c.fetchone()[0]
    
    c.execute("SELECT MAX(ts) FROM n")
    last = c.fetchone()[0]
    
    c.execute("SELECT s, COUNT(*) FROM n GROUP BY s")
    by_source = dict(c.fetchall())
    
    conn.close()
    
    return {
        "total": total,
        "last_update": last,
        "by_source": by_source
    }


def news_report(symbol=None):
    """Generate formatted news report"""
    if symbol:
        result = get_news(symbol)
        report = f"# {symbol} News\n\n"
        report += f"_Cache: {result['count']} items_\n\n"
        for n in result["news"][:15]:
            report += f"**{n['title']}**\n"
            report += f"[{n['source']}] {n['time'][:16]}\n\n"
    else:
        stats = get_stats()
        result = get_news()
        report = "# Real-time Financial News\n\n"
        report += f"| Stats | Value |\n|---|---|\n"
        report += f"| Total | {stats['total']} |\n"
        report += f"| Last Update | {stats.get('last_update', 'N/A')[:16]} |\n"
        for src, cnt in stats.get("by_source", {}).items():
            report += f"| {src} | {cnt} |\n"
        report += "\n## Latest News\n\n"
        for n in result["news"][:20]:
            report += f"**{n['title']}**\n"
            report += f"[{n['source']}] {n['time'][:16]}\n\n"
    
    return report


if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    print(news_report(symbol))
