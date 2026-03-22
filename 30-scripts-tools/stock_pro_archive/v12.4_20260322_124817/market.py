"""Market Overview - Market-wide analysis and trends"""
from stock_pro.core import A, analyze_multiple
from stock_pro.sectors import get_all_sectors, get_symbols_by_sector


def get_market_overview():
    """Get comprehensive market overview"""
    all_symbols = list(A.keys())
    results = analyze_multiple(all_symbols)
    
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_upside = sum(r["upside"] for r in results) / len(results)
    
    strong_buys = [r for r in results if r["score"] >= 75]
    buys = [r for r in results if 60 <= r["score"] < 75]
    holds = [r for r in results if 40 <= r["score"] < 60]
    underweight = [r for r in results if r["score"] < 40]
    
    sentiment = "Bullish" if avg_score >= 60 else "Neutral" if avg_score >= 50 else "Bearish"
    
    sectors = get_all_sectors()
    sector_data = []
    
    for sector in sectors:
        symbols = get_symbols_by_sector(sector)
        sector_results = [r for r in results if r["symbol"] in symbols]
        if sector_results:
            sector_data.append({
                "name": sector,
                "stocks": len(sector_results),
                "avg_score": sum(r["score"] for r in sector_results) / len(sector_results),
                "avg_upside": sum(r["upside"] for r in sector_results) / len(sector_results)
            })
    
    sector_data.sort(key=lambda x: x["avg_score"], reverse=True)
    
    return {
        "total_stocks": len(results),
        "avg_score": avg_score,
        "avg_upside": avg_upside,
        "sentiment": sentiment,
        "distribution": {
            "strong_buys": len(strong_buys),
            "buys": len(buys),
            "holds": len(holds),
            "underweight": len(underweight)
        },
        "top_sectors": sector_data[:3],
        "bottom_sectors": sector_data[-2:] if len(sector_data) > 2 else sector_data,
        "top_stocks": sorted(results, key=lambda x: x["score"], reverse=True)[:5],
        "best_upside": sorted(results, key=lambda x: x["upside"], reverse=True)[:5]
    }


def market_report():
    """Generate comprehensive market report"""
    overview = get_market_overview()
    
    report = "# Market Overview\n\n"
    report += f"## Key Metrics\n\n"
    report += f"- **Total Stocks:** {overview['total_stocks']}\n"
    report += f"- **Average Score:** {overview['avg_score']:.0f}\n"
    report += f"- **Average Upside:** {overview['avg_upside']:+.1f}%\n"
    report += f"- **Sentiment:** {overview['sentiment']}\n\n"
    
    d = overview["distribution"]
    report += f"## Distribution\n\n"
    report += f"- Strong Buy: {d['strong_buys']}, Buy: {d['buys']}, Hold: {d['holds']}, Underweight: {d['underweight']}\n\n"
    
    report += "## Top Sectors\n\n"
    report += "| Sector | Score | Upside |\n|--------|-------|--------|\n"
    for s in overview["top_sectors"]:
        report += f"| {s['name']} | {s['avg_score']:.0f} | {s['avg_upside']:+.1f}% |\n"
    
    report += "\n## Top Stocks\n\n"
    report += "| Symbol | Score | Upside |\n|--------|-------|--------|\n"
    for r in overview["top_stocks"]:
        report += f"| {r['symbol']} | {r['score']} | {r['upside']:+.1f}% |\n"
    
    return report


def sector_rotation_report():
    """Analyze sector rotation patterns"""
    sectors = get_all_sectors()
    
    report = "# Sector Rotation Analysis\n\n"
    
    sector_momentum = []
    for sector in sectors:
        symbols = get_symbols_by_sector(sector)
        results = analyze_multiple(symbols)
        if results:
            momentum = (sum(r["score"] for r in results) / len(results) * 0.6) + \
                      (sum(r["upside"] for r in results) / len(results) * 0.4)
            sector_momentum.append({
                "name": sector,
                "momentum": momentum,
                "avg_score": sum(r["score"] for r in results) / len(results),
                "stocks": len(results)
            })
    
    sector_momentum.sort(key=lambda x: x["momentum"], reverse=True)
    
    report += "| Sector | Momentum | Score | Action |\n"
    report += "|--------|----------|-------|--------|\n"
    for i, s in enumerate(sector_momentum):
        action = "Overweight" if i == 0 else "Underweight" if i == len(sector_momentum) - 1 else "Neutral"
        report += f"| {s['name']} | {s['momentum']:.0f} | {s['avg_score']:.0f} | {action} |\n"
    
    return report


def market_breadth_indicator():
    """Calculate market breadth indicator"""
    all_symbols = list(A.keys())
    results = analyze_multiple(all_symbols)
    
    above_50 = len([r for r in results if r["score"] >= 50])
    above_75 = len([r for r in results if r["score"] >= 75])
    
    breadth = above_50 / len(results) * 100 if results else 0
    strength = above_75 / len(results) * 100 if results else 0
    
    return {
        "breadth": breadth,
        "strength": strength,
        "above_50": above_50,
        "above_75": above_75,
        "total": len(results)
    }
