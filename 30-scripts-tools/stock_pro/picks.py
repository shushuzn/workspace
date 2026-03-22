"""Quick stock picks - Fast screening"""
from .core import analyze_multiple_parallel

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

def top_picks(n=10):
    """Get top N overall picks"""
    from .data_financial import F
    symbols = list(F.keys())
    
    results = analyze_multiple_parallel(symbols, max_workers=10)
    
    picks = [data for data in results.values() if data]
    return sorted(picks, key=lambda x: x["score"], reverse=True)[:n]

def quick_picks(n=5):
    """Quick top picks for dashboard"""
    return top_picks(n)

def get_top_picks_report(n=10, category="all"):
    """Generate top picks report"""
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
