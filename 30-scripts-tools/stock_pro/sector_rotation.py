"""Sector Rotation Analysis - Lightweight version"""
from stock_pro.data_target import A
from stock_pro.data_financial import F
from stock_pro.data_price import P, B, E


SECTOR_DATA = {
    "Technology": ["NVDA", "META", "AAPL", "MSFT", "GOOGL", "AMZN"],
    "Finance": ["JPM", "BAC", "WFC", "GS", "MS", "V", "MA"],
    "Healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK", "LLY"],
    "Consumer": ["AMZN", "TSLA", "NKE", "SBUX", "MCD", "KO"],
    "Industrial": ["BA", "CAT", "GE", "HON", "UPS", "RTX"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "PSX"],
}


def calc_sector_score(sector):
    """Quick sector score calculation"""
    symbols = SECTOR_DATA.get(sector, [])

    scores = []
    for sym in symbols[:5]:  # Limit to 5 per sector
        if sym in A:
            gm, pm, roe, roic, de, rg, fcf, div = F.get(sym, (0,0,0,0,0,0,0,0))
            beta = B.get(sym, 1.0)
            eps = E.get(sym, 0)
            price = P.get(sym, 0)

            if price <= 0 or eps <= 0:
                continue

            pe = price / eps
            score = min(100, max(0, 100 - pe * 1.5 + rg * 100 - de * 10))
            scores.append(score)

    if not scores:
        return {"sector": sector, "avg_score": 0, "stocks": 0}

    return {
        "sector": sector,
        "avg_score": sum(scores) / len(scores),
        "stocks": len(scores),
        "top_pick": symbols[0] if symbols else None
    }


def get_sector_rotation():
    """Get sector rotation analysis"""
    results = []
    for sector in SECTOR_DATA.keys():
        data = calc_sector_score(sector)
        results.append(data)

    results.sort(key=lambda x: x['avg_score'], reverse=True)

    report = "# Sector Rotation Analysis\n\n"
    report += "| Sector | Score | Stocks | Top Pick |\n"
    report += "|--------|-------|--------|----------|\n"

    for r in results:
        report += f"| {r['sector']} | {r['avg_score']:.0f} | {r['stocks']} | {r['top_pick']} |\n"

    report += "\n## Recommendations\n\n"

    for r in results[:3]:
        action = "Overweight" if r['avg_score'] > 60 else ("Neutral" if r['avg_score'] > 40 else "Underweight")
        report += f"**{action}:** {r['sector']} (Score: {r['avg_score']:.0f})\n"

    return report


def recommend_sectors(risk_tolerance="moderate"):
    """Recommend sectors based on risk tolerance"""
    results = []
    for sector in SECTOR_DATA.keys():
        data = calc_sector_score(sector)
        if data['stocks'] > 0:
            results.append(data)

    results.sort(key=lambda x: x['avg_score'], reverse=True)

    report = f"# Sector Recommendations ({risk_tolerance.capitalize()})\n\n"
    report += "| Rank | Sector | Score | Action |\n"
    report += "|------|--------|-------|--------|\n"

    for i, r in enumerate(results, 1):
        action = "Buy" if r['avg_score'] > 65 else ("Hold" if r['avg_score'] > 45 else "Avoid")
        report += f"| {i} | {r['sector']} | {r['avg_score']:.0f} | {action} |\n"

    return report
