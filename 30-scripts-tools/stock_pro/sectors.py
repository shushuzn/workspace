"""Sector classification for stocks"""

SECTORS = {
    # Technology
    "META": "Technology",
    "NVDA": "Technology",
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Technology",
    "AMZN": "Technology",
    "AMD": "Technology",
    "TSLA": "Technology/Auto",
    "NFLX": "Technology",
    "CRM": "Technology",
    "INTC": "Technology",
    "QCOM": "Technology",
    "ORCL": "Technology",
    "ADBE": "Technology",
    "NOW": "Technology",
    "AVGO": "Technology",
    "ASML": "Technology",
    "SNOW": "Technology",
    "PANW": "Technology",
    "UBER": "Technology",
    "DASH": "Technology",
    "COIN": "Technology",
    "RIVN": "Technology/Auto",
    "PLTR": "Technology",
    "ARM": "Technology",
    "CRWD": "Technology",
    "NET": "Technology",
    "ZS": "Technology",
    "DDOG": "Technology",
    "TEAM": "Technology",
    "DOCU": "Technology",
    "ZM": "Technology",
    "OKTA": "Technology",
    
    # Finance
    "JPM": "Finance",
    "BAC": "Finance",
    "GS": "Finance",
    "V": "Finance",
    "MA": "Finance",
    
    # Healthcare
    "JNJ": "Healthcare",
    "PFE": "Healthcare",
    "UNH": "Healthcare",
    "MRK": "Healthcare",
    "ABBV": "Healthcare",
    "LLY": "Healthcare",
    
    # Consumer
    "WMT": "Consumer",
    "COST": "Consumer",
    "KO": "Consumer",
    
    # Industrial
    "CAT": "Industrial",
    "HON": "Industrial",
    "DE": "Industrial",
    
    # Energy
    "XOM": "Energy",
    "CVX": "Energy",
    
    # ETF
    "SPY": "ETF",
    "QQQ": "ETF",
}


def get_sector(symbol):
    """Get sector for a symbol"""
    return SECTORS.get(symbol.upper(), "Unknown")


def get_symbols_by_sector(sector):
    """Get all symbols in a sector"""
    return [sym for sym, sec in SECTORS.items() if sec == sector]


def get_all_sectors():
    """Get all unique sectors"""
    return sorted(set(SECTORS.values()))


def sector_report(results):
    """Generate sector analysis report"""
    sectors = {}
    
    for r in results:
        sym = r["symbol"]
        sector = get_sector(sym)
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(r)
    
    report = "# Sector Analysis\n\n"
    
    for sector in sorted(sectors.keys()):
        stocks = sectors[sector]
        avg_score = sum(s["score"] for s in stocks) / len(stocks)
        best = max(stocks, key=lambda x: x["score"])
        
        report += f"## {sector} ({len(stocks)} stocks)\n"
        report += f"- Avg Score: {avg_score:.0f}\n"
        report += f"- Best: {best['symbol']} ({best['score']}/100)\n"
        report += "| Symbol | Price | Score | Upside | Rating |\n"
        report += "|--------|-------|-------|--------|--------|\n"
        for s in sorted(stocks, key=lambda x: x["score"], reverse=True):
            report += f"| {s['symbol']} | ${s['price']:.2f} | {s['score']} | {s['upside']:+.1f}% | {s['rating']} |\n"
        report += "\n"
    
    return report

def sector_rotation():
    """Analyze sector rotation - which sectors to invest in"""
    from .core import analyze_multiple_parallel
    from .data_financial import F
    
    sectors = {}
    for sym in F.keys():
        sec = get_sector(sym)
        if sec not in sectors:
            sectors[sec] = []
        sectors[sec].append(sym)
    
    results = {}
    for sec, syms in sectors.items():
        stocks = analyze_multiple_parallel(syms[:10], max_workers=5)
        valid = [s for s in stocks.values() if s]
        if valid:
            avg_score = sum(s["score"] for s in valid) / len(valid)
            avg_upside = sum(s["upside"] for s in valid) / len(valid)
            top_stock = max(valid, key=lambda x: x["score"])
            results[sec] = {
                "avg_score": avg_score,
                "avg_upside": avg_upside,
                "num_stocks": len(valid),
                "top_stock": top_stock["symbol"],
                "top_score": top_stock["score"]
            }
    
    # Rank by composite score
    ranked = sorted(results.items(), 
                   key=lambda x: x[1]["avg_score"] * 0.6 + x[1]["avg_upside"] * 0.4,
                   reverse=True)
    
    report = "# Sector Rotation Analysis\n\n"
    report += "| Rank | Sector | Avg Score | Avg Upside | Stocks | Top Pick |\n"
    report += "|------|--------|-----------|------------|--------|----------|\n"
    
    for i, (sec, data) in enumerate(ranked[:10], 1):
        report += f"| {i} | {sec} | {data['avg_score']:.0f} | {data['avg_upside']:+.1f}% | {data['num_stocks']} | {data['top_stock']} ({data['top_score']}) |\n"
    
    report += "\n**Recommendation:** "
    if ranked:
        best = ranked[0]
        report += f"Overweight {best[0]} sector"
    
    return report
