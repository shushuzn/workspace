"""Top picks generator for Stock PRO"""

def get_top_picks(results, n=10):
    """Get top N stocks by score"""
    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
    return sorted_results[:n]


def get_best_value(results, n=5):
    """Get best value stocks (high upside + reasonable score)"""
    scored = [(r, r["upside"] * 0.6 + r["score"] * 0.4) for r in results]
    sorted_results = sorted(scored, key=lambda x: x[1], reverse=True)
    return [r for r, _ in sorted_results[:n]]


def get_growth_picks(results, n=5):
    """Get growth picks (high score + growth metrics)"""
    scored = [(r, r["score"] + r.get("rev_g", 0)) for r in results]
    sorted_results = sorted(scored, key=lambda x: x[1], reverse=True)
    return [r for r, _ in sorted_results[:n]]


def get_defensive_picks(results, n=5):
    """Get defensive picks (low beta + dividend)"""
    scored = [(r, (1 - r.get("beta", 1)) + r.get("div", 0) * 10) for r in results]
    sorted_results = sorted(scored, key=lambda x: x[1], reverse=True)
    return [r for r, _ in sorted_results[:n]]


def get_top_picks_report(results):
    """Generate comprehensive top picks report"""
    if not results:
        return "[Picks] No data"
    
    report = "# Top Picks Report\n\n"
    
    # Top 10 by score
    top10 = get_top_picks(results, 10)
    report += "## Top 10 by Score\n\n"
    report += "| # | Symbol | Price | Score | Upside | Rating | P/E |\n"
    report += "|---|--------|-------|-------|--------|--------|-----|\n"
    for i, r in enumerate(top10, 1):
        report += f"| {i} | {r['symbol']} | ${r['price']:.2f} | {r['score']} | {r['upside']:+.1f}% | {r['rating']} | {r['pe']:.1f}x |\n"
    
    # Best value
    best_value = get_best_value(results, 5)
    report += "\n## Best Value\n\n"
    report += "| Symbol | Price | Score | Upside | Rating |\n"
    report += "|--------|-------|-------|--------|--------|\n"
    for r in best_value:
        report += f"| {r['symbol']} | ${r['price']:.2f} | {r['score']} | {r['upside']:+.1f}% | {r['rating']} |\n"
    
    # Growth picks
    growth = get_growth_picks(results, 5)
    report += "\n## Growth Picks\n\n"
    report += "| Symbol | Price | Score | Rev Growth | Rating |\n"
    report += "|--------|-------|-------|------------|--------|\n"
    for r in growth:
        report += f"| {r['symbol']} | ${r['price']:.2f} | {r['score']} | {r.get('rev_g', 0):+.1f}% | {r['rating']} |\n"
    
    # Defensive picks
    defensive = get_defensive_picks(results, 5)
    report += "\n## Defensive Picks (Low Risk)\n\n"
    report += "| Symbol | Price | Beta | Dividend | Rating |\n"
    report += "|--------|-------|------|----------|--------|\n"
    for r in defensive:
        report += f"| {r['symbol']} | ${r['price']:.2f} | {r.get('beta', 1):.1f} | {r.get('div', 0):.2f}% | {r['rating']} |\n"
    
    return report


def quick_picks(results):
    """Show quick picks summary"""
    if not results:
        return "[Picks] No data"
    
    top = get_top_picks(results, 5)
    
    output = "# Quick Picks\n\n"
    output += "| Symbol | Price | Score | Upside | Why |\n"
    output += "|--------|-------|-------|--------|-----|\n"
    
    for r in top:
        # Generate brief reason
        reasons = []
        if r["score"] >= 80:
            reasons.append("Excellent")
        elif r["upside"] >= 50:
            reasons.append("High Upside")
        if r.get("roe", 0) >= 30:
            reasons.append("High ROE")
        if r.get("fcf", 0) >= 3:
            reasons.append("Strong FCF")
        if r.get("peg", 99) < 1:
            reasons.append("Low PEG")
        
        reason = ", ".join(reasons[:2]) if reasons else "-"
        output += f"| {r['symbol']} | ${r['price']:.2f} | {r['score']} | {r['upside']:+.1f}% | {reason} |\n"
    
    return output
