"""Quick stock picks - Fast screening"""
from .core import analyze_multiple_parallel

def dividend_picks(min_div=2.0, min_score=50):
    """Find best dividend stocks"""
    from .data_financial import F
    symbols = list(F.keys())
    
    results = analyze_multiple_parallel(symbols, max_workers=10)
    
    picks = []
    for sym, data in results.items():
        if not data:
            continue
        div_yield = data.get("div", 0)
        if div_yield >= min_div and data["score"] >= min_score:
            picks.append(data)
    
    return sorted(picks, key=lambda x: x["div"], reverse=True)[:10]

def dividend_report():
    """Generate dividend stock report"""
    picks = dividend_picks(min_div=2.0)
    
    report = "# Dividend Stock Picks\n\n"
    report += "| Symbol | Price | Div Yield | Score | P/E | ROE | Risk |\n"
    report += "|--------|-------|-----------|-------|-----|-----|------|\n"
    
    for p in picks:
        report += f"| {p['symbol']} | ${p['price']:.2f} | {p['div']:.2f}% | {p['score']} | {p['pe']:.0f}x | {p['roe']:.0f}% | {p.get('risk_level', 'N/A')} |\n"
    
    return report

def value_picks(min_score=70, min_upside=20):
    """Find best value stocks"""
    from .data_financial import F
    symbols = list(F.keys())
    
    results = analyze_multiple_parallel(symbols, max_workers=10)
    
    picks = []
    for sym, data in results.items():
        if not data:
            continue
        if data["score"] >= min_score and data["upside"] >= min_upside:
            if data["pe"] < 25:  # Value filter
                picks.append(data)
    
    return sorted(picks, key=lambda x: x["score"], reverse=True)[:10]

def growth_picks(min_score=65, min_rg=15):
    """Find fastest growing stocks"""
    from .data_financial import F
    symbols = list(F.keys())
    
    results = analyze_multiple_parallel(symbols, max_workers=10)
    
    picks = []
    for sym, data in results.items():
        if not data:
            continue
        rg = data.get("rg", 0) * 100
        if data["score"] >= min_score and rg >= min_rg:
            picks.append(data)
    
    return sorted(picks, key=lambda x: x.get("rg", 0), reverse=True)[:10]

def dividend_picks(min_div=2.0, min_score=55):
    """Find best dividend stocks"""
    from .data_financial import F
    symbols = list(F.keys())
    
    results = analyze_multiple_parallel(symbols, max_workers=10)
    
    picks = []
    for sym, data in results.items():
        if not data:
            continue
        div = data.get("div", 0)
        if div >= min_div and data["score"] >= min_score:
            picks.append(data)
    
    return sorted(picks, key=lambda x: x.get("div", 0), reverse=True)[:10]

def momentum_picks(min_score=60, min_upside=10):
    """Find stocks with best momentum"""
    from .data_financial import F
    symbols = list(F.keys())
    
    results = analyze_multiple_parallel(symbols, max_workers=10)
    
    picks = []
    for sym, data in results.items():
        if not data:
            continue
        beta = data.get("beta", 1.0)
        if data["score"] >= min_score and data["upside"] >= min_upside:
            if 0.8 <= beta <= 1.5:  # Moderate beta
                picks.append(data)
    
    return sorted(picks, key=lambda x: x["score"], reverse=True)[:10]

def top_picks(n=10, min_upside=15):
    """Get top N overall picks - filtered by upside"""
    n = int(n) if n else 10
    from .data_financial import F
    symbols = list(F.keys())
    
    results = analyze_multiple_parallel(symbols, max_workers=10)
    
    # Filter: positive upside and good score
    picks = [data for data in results.values() if data 
             if data.get("score", 0) >= 50 and data.get("upside", 0) >= min_upside]
    return sorted(picks, key=lambda x: (x.get("score", 0), x.get("upside", 0)), reverse=True)[:n]

def quick_picks(n=5):
    """Quick top picks for dashboard"""
    return top_picks(n)

def get_top_picks_report(n=10, category="all"):
    """Generate top picks report"""
    n = int(n) if n else 10
    picks = top_picks(n)
    
    if category == "value":
        picks = value_picks()
    elif category == "growth":
        picks = growth_picks()
    elif category == "momentum":
        picks = momentum_picks()
    
    report = ["# Top Stock Picks Report\n"]
    report.append(f"## {len(picks)} Top Picks\n")
    
    for i, p in enumerate(picks, 1):
        report.append(f"{i}. **{p['symbol']}** - Score: {p['score']}, Upside: {p.get('upside', 0):.1f}%")
    
    return "\n".join(report)
