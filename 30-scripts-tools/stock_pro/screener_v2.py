"""Advanced Screener - Multi-factor stock screening"""
from stock_pro.core import A, F, P, analyze_multiple_parallel


class AdvancedScreener:
    """Multi-factor stock screener"""
    
    def __init__(self):
        self.results = []
    
    def filter_by_score(self, min_score=60, max_score=100):
        """Filter by score range"""
        self.results = [r for r in self.results if min_score <= r["score"] <= max_score]
        return self
    
    def filter_by_upside(self, min_upside=10):
        """Filter by minimum upside"""
        self.results = [r for r in self.results if r["upside"] >= min_upside]
        return self
    
    def filter_by_pe(self, max_pe=30):
        """Filter by max P/E ratio"""
        self.results = [r for r in self.results if r.get("pe", 999) <= max_pe]
        return self
    
    def filter_by_peg(self, max_peg=1.5):
        """Filter by max PEG ratio"""
        self.results = [r for r in self.results if r.get("peg", 999) <= max_peg]
        return self
    
    def filter_by_roe(self, min_roe=15):
        """Filter by minimum ROE"""
        self.results = [r for r in self.results if r.get("roe", 0) >= min_roe]
        return self
    
    def filter_by_sector(self, sector):
        """Filter by sector"""
        from stock_pro.sectors import get_sector
        self.results = [r for r in self.results if get_sector(r["symbol"]) == sector]
        return self
    
    def filter_by_market_cap(self, min_cap=None, max_cap=None):
        """Filter by market cap (in billions)"""
        # Placeholder - would need real market cap data
        return self
    
    def filter_by_volume(self, min_volume=1000000):
        """Filter by minimum trading volume"""
        return self
    
    def sort_by(self, key="score", reverse=True):
        """Sort results"""
        self.results.sort(key=lambda x: x.get(key, 0), reverse=reverse)
        return self
    
    def execute(self, symbols=None):
        """Execute screener with parallel analysis"""
        from stock_pro.core import A
        if symbols is None:
            symbols = list(A.keys())
        
        self.results = analyze_multiple_parallel(symbols, max_workers=10)
        return self
    
    def top(self, n=10):
        """Return top N results"""
        return self.results[:n]


def advanced_screener_report(criteria=None):
    """Generate advanced screener report"""
    screener = AdvancedScreener()
    screener.execute()
    
    if criteria:
        # Apply filters
        if "min_score" in criteria:
            screener.filter_by_score(criteria["min_score"])
        if "min_upside" in criteria:
            screener.filter_by_upside(criteria["min_upside"])
        if "max_pe" in criteria:
            screener.filter_by_pe(criteria["max_pe"])
        if "max_peg" in criteria:
            screener.filter_by_peg(criteria["max_peg"])
        if "min_roe" in criteria:
            screener.filter_by_roe(criteria["min_roe"])
        if "sector" in criteria:
            screener.filter_by_sector(criteria["sector"])
    
    screener.sort_by("score", reverse=True)
    results = screener.top(20)
    
    if not results:
        return "[Screener] No stocks match criteria"
    
    report = "# Advanced Screener Results\n\n"
    
    if criteria:
        report += "## Criteria\n\n"
        for k, v in criteria.items():
            report += f"- **{k}:** {v}\n"
        report += "\n"
    
    report += f"**Matches:** {len(results)}\n\n"
    
    report += "| Rank | Symbol | Score | Upside | P/E | PEG | ROE | Sector |\n"
    report += "|------|--------|-------|--------|-----|-----|-----|--------|\n"
    
    for i, r in enumerate(results, 1):
        from stock_pro.sectors import get_sector
        sector = get_sector(r["symbol"])
        report += f"| {i} | {r['symbol']} | {r['score']} | {r['upside']:+.1f}% | {r.get('pe', 'N/A')} | {r.get('peg', 'N/A')} | {r.get('roe', 'N/A')} | {sector} |\n"
    
    return report


def value_picks():
    """Find value stocks (low PE, high ROE)"""
    screener = AdvancedScreener()
    screener.execute()
    
    # Value criteria
    screener.filter_by_pe(25)
    screener.filter_by_roe(15)
    screener.filter_by_upside(10)
    screener.sort_by("upside", reverse=True)
    
    results = screener.top(10)
    
    report = "# Value Stock Picks\n\n"
    report += "| Symbol | P/E | ROE | Upside | Score |\n"
    report += "|--------|-----|-----|--------|-------|\n"
    
    for r in results:
        report += f"| {r['symbol']} | {r.get('pe', 'N/A')} | {r.get('roe', 'N/A')} | {r['upside']:+.1f}% | {r['score']} |\n"
    
    return report


def growth_picks():
    """Find growth stocks (high PEG momentum)"""
    screener = AdvancedScreener()
    screener.execute()
    
    # Growth criteria
    screener.filter_by_peg(1.0)
    screener.filter_by_score(60)
    screener.sort_by("upside", reverse=True)
    
    results = screener.top(10)
    
    report = "# Growth Stock Picks\n\n"
    report += "| Symbol | PEG | Upside | Score | Sector |\n"
    report += "|--------|-----|--------|-------|--------|\n"
    
    from stock_pro.sectors import get_sector
    for r in results:
        sector = get_sector(r["symbol"])
        report += f"| {r['symbol']} | {r.get('peg', 'N/A')} | {r['upside']:+.1f}% | {r['score']} | {sector} |\n"
    
    return report


def dividend_picks():
    """Find dividend stocks"""
    from stock_pro.core import F
    
    results = []
    for sym, data in F.items():
        div_yield = data[7] if len(data) > 7 else 0
        if div_yield > 0.02:  # >2% yield
            results.append({
                "symbol": sym,
                "dividend_yield": div_yield * 100
            })
    
    results.sort(key=lambda x: x["dividend_yield"], reverse=True)
    
    report = "# Dividend Stock Picks\n\n"
    report += "| Symbol | Dividend Yield |\n"
    report += "|--------|----------------|\n"
    
    for r in results[:15]:
        report += f"| {r['symbol']} | {r['dividend_yield']:.1f}% |\n"
    
    return report
