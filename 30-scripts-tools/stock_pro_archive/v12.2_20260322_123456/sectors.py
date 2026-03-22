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
