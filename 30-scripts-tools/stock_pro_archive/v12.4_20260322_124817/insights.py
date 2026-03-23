"""Portfolio Insights - AI-powered portfolio insights"""
from stock_pro.core import A, analyze_multiple
from stock_pro.sectors import get_sector, get_all_sectors, get_symbols_by_sector


def get_portfolio_insights(symbols=None):
    """Generate comprehensive portfolio insights"""
    symbols = symbols or list(A.keys())
    results = analyze_multiple(symbols)

    total_score = sum(r["score"] for r in results)
    avg_score = total_score / len(results) if results else 0

    weighted_upside = sum(r["upside"] * r["score"] for r in results)
    total_weight = sum(r["score"] for r in results)
    weighted_upside = weighted_upside / total_weight if total_weight else 0

    sector_scores = {}
    for r in results:
        sector = get_sector(r["symbol"])
        sector_scores.setdefault(sector, []).append(r)

    return {
        "summary": {
            "total_stocks": len(results),
            "avg_score": avg_score,
            "weighted_upside": weighted_upside,
            "strong_buys": len([r for r in results if r["score"] >= 75]),
            "buys": len([r for r in results if 60 <= r["score"] < 75]),
            "holds": len([r for r in results if 40 <= r["score"] < 60]),
            "underweight": len([r for r in results if r["score"] < 40])
        },
        "top_performers": sorted(results, key=lambda x: x["score"], reverse=True)[:5],
        "best_upside": sorted(results, key=lambda x: x["upside"], reverse=True)[:5],
        "sectors": {s: len(stocks) for s, stocks in sector_scores.items()},
        "needs_attention": [r for r in results if r["score"] < 50]
    }


def generate_insights_report(symbols=None):
    """Generate detailed insights report"""
    insights = get_portfolio_insights(symbols)
    s = insights["summary"]

    report = "# Portfolio Insights\n\n"
    report += f"- **Total Stocks:** {s['total_stocks']}\n"
    report += f"- **Average Score:** {s['avg_score']:.0f}\n"
    report += f"- **Weighted Upside:** {s['weighted_upside']:+.1f}%\n"
    report += f"- **Strong Buys:** {s['strong_buys']}, **Buys:** {s['buys']}, **Holds:** {s['holds']}\n\n"

    report += "## Top Performers\n\n| Symbol | Score | Upside |\n|--------|-------|--------|\n"
    for r in insights["top_performers"]:
        report += f"| {r['symbol']} | {r['score']} | {r['upside']:+.1f}% |\n"

    report += "\n## Sector Allocation\n\n| Sector | Count |\n|--------|-------|\n"
    for sector, count in sorted(insights["sectors"].items(), key=lambda x: x[1], reverse=True):
        report += f"| {sector} | {count} |\n"
    return report


def risk_reward_analysis(symbols=None):
    """Analyze risk/reward for portfolio"""
    symbols = symbols or list(A.keys())
    results = analyze_multiple(symbols)

    categories = {"Low Risk, High Reward": [], "High Risk, High Reward": [], "Low Risk, Low Reward": [], "High Risk, Low Reward": []}

    for r in results:
        risk = "High" if r["score"] < 50 else "Low"
        reward = "High" if r["upside"] > 20 else "Low"
        key = f"{risk} Risk, {reward} Reward"
        categories[key].append(r)

    report = "# Risk/Reward Analysis\n\n| Category | Count |\n|----------|-------|\n"
    for k, v in categories.items():
        report += f"| {k} | {len(v)} |\n"

    best = categories.get("Low Risk, High Reward", [])
    if best:
        report += "\n## Best Risk/Reward Stocks\n\n| Symbol | Score | Upside |\n|--------|-------|--------|\n"
        for r in best[:10]:
            report += f"| {r['symbol']} | {r['score']} | {r['upside']:+.1f}% |\n"
    return report


def generate_investment_themes(symbols=None):
    """Generate investment themes based on market data"""
    symbols = symbols or list(A.keys())
    results = analyze_multiple(symbols)
    themes = []

    # Quality Growth
    quality_growth = [r for r in results if r["score"] >= 70 and r["upside"] > 15]
    if quality_growth:
        themes.append({"name": "Quality Growth", "desc": "High-scoring stocks with upside", "stocks": [r["symbol"] for r in quality_growth[:5]], "risk": "Moderate"})

    # Deep Value
    value = [r for r in results if r["upside"] > 25]
    if value:
        themes.append({"name": "Deep Value", "desc": "Stocks with significant upside", "stocks": [r["symbol"] for r in value[:5]], "risk": "High"})

    # Sector Leaders
    for sector in get_all_sectors()[:3]:
        sector_syms = get_symbols_by_sector(sector)
        sector_results = [r for r in results if r["symbol"] in sector_syms]
        if sector_results:
            top = max(sector_results, key=lambda x: x["score"])
            themes.append({"name": f"{sector} Leader", "desc": f"Top in {sector}", "stocks": [top["symbol"]], "risk": "Moderate"})

    report = "# Investment Themes\n\n"
    for i, t in enumerate(themes, 1):
        report += f"## {i}. {t['name']}\n\n**Desc:** {t['desc']}\n\n**Risk:** {t['risk']}\n\n**Stocks:** {', '.join(t['stocks'])}\n\n"
    return report
