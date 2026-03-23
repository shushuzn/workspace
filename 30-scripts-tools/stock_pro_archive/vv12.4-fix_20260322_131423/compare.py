"""Stock Comparison Tool - Compare multiple stocks side by side"""
from stock_pro.core import analyze_multiple
from stock_pro.data_target import A
from stock_pro.data_financial import F
from stock_pro.data_price import P, B, E


def compare_stocks(symbols):
    """Compare multiple stocks side by side"""
    if not symbols:
        return "[ERROR] No symbols provided"

    # Get analysis for all symbols
    results = analyze_multiple(symbols)

    if not results:
        return f"[ERROR] No data for {symbols}"

    # Build comparison table
    report = "# Stock Comparison\n\n"

    # Basic metrics
    report += "## Overview\n\n"
    report += "| Symbol | Price | Target | Upside | Score | Rating | P/E | Beta |\n"
    report += "|--------|-------|--------|--------|-------|--------|-----|------|\n"
    for r in results:
        report += f"| {r['symbol']} | ${r['price']:.2f} | ${r['target']:.2f} | {r['upside']:+.1f}% | {r['score']} | {r['rating']} | {r['pe']:.1f}x | {r['beta']:.1f} |\n"

    # Financial metrics
    report += "\n## Financial Metrics\n\n"
    report += "| Symbol | ROE | Profit Margin | Gross Margin | Rev Growth | FCF | Debt/Equity |\n"
    report += "|--------|-----|--------------|--------------|------------|-----|-------------|\n"
    for r in results:
        report += f"| {r['symbol']} | {r['roe']:.1f}% | {r['pm']:.1f}% | {r['gm']:.1f}% | {r['rev_g']:.1f}% | {r['fcf']:.2f}% | {r['de']:.1f} |\n"

    # DCF Valuation
    report += "\n## DCF Valuation\n\n"
    report += "| Symbol | Base | Bull | Bear | vs Price |\n"
    report += "|--------|------|------|------|----------|\n"
    for r in results:
        vs_base = (r['dcf_base'] / r['price'] - 1) * 100
        vs_bull = (r['dcf_bull'] / r['price'] - 1) * 100
        vs_bear = (r['dcf_bear'] / r['price'] - 1) * 100
        report += f"| {r['symbol']} | ${r['dcf_base']:.2f} | ${r['dcf_bull']:.2f} | ${r['dcf_bear']:.2f} | {vs_base:+.1f}% |\n"

    # Rankings
    report += "\n## Rankings\n\n"

    # By score
    by_score = sorted(results, key=lambda x: x['score'], reverse=True)
    report += "**By Score:** " + " > ".join([f"{r['symbol']}({r['score']})" for r in by_score]) + "\n\n"

    # By upside
    by_upside = sorted(results, key=lambda x: x['upside'], reverse=True)
    report += "**By Upside:** " + " > ".join([f"{r['symbol']}({r['upside']:+.1f}%)" for r in by_upside]) + "\n\n"

    # By valuation (lowest P/E)
    by_pe = sorted(results, key=lambda x: x['pe'])
    report += "**By P/E:** " + " < ".join([f"{r['symbol']}({r['pe']:.1f}x)" for r in by_pe[:5]]) + "\n\n"

    # Winner
    report += "## Best Choice\n\n"
    best = max(results, key=lambda x: x['score'])
    report += f"**Overall:** {best['symbol']} (Score: {best['score']}, Upside: {best['upside']:+.1f}%)\n\n"

    best_upside = max(results, key=lambda x: x['upside'])
    report += f"**Highest Upside:** {best_upside['symbol']} ({best_upside['upside']:+.1f}%)\n\n"

    return report


def compare_sectors(symbols):
    """Compare stocks by sector"""
    from stock_pro.sectors import get_sector

    results = analyze_multiple(symbols)

    # Group by sector
    sectors = {}
    for r in results:
        sector = get_sector(r['symbol'])
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(r)

    report = "# Sector Comparison\n\n"

    for sector, stocks in sorted(sectors.items(), key=lambda x: sum(r['score'] for r in x[1]) / len(x[1]) if x[1] else 0, reverse=True):
        avg_score = sum(s['score'] for s in stocks) / len(stocks)
        avg_upside = sum(s['upside'] for s in stocks) / len(stocks)

        report += f"## {sector}\n\n"
        report += f"Average Score: {avg_score:.0f} | Average Upside: {avg_upside:+.1f}%\n\n"
        report += "| Symbol | Score | Upside | P/E | ROE |\n"
        report += "|--------|-------|--------|-----|-----|\n"
        for s in sorted(stocks, key=lambda x: x['score'], reverse=True):
            report += f"| {s['symbol']} | {s['score']} | {s['upside']:+.1f}% | {s['pe']:.1f}x | {s['roe']:.1f}% |\n"
        report += "\n"

    return report


def compare_risk(symbols):
    """Compare risk metrics"""
    results = analyze_multiple(symbols)

    report = "# Risk Comparison\n\n"
    report += "| Symbol | Beta | Debt/Eq | P/E | Score | Risk Level |\n"
    report += "|--------|------|---------|-----|-------|------------|\n"

    for r in sorted(results, key=lambda x: x['beta'], reverse=True):
        if r['beta'] > 1.5:
            risk = "High"
        elif r['beta'] > 1.0:
            risk = "Medium"
        else:
            risk = "Low"

        report += f"| {r['symbol']} | {r['beta']:.1f} | {r['de']:.1f} | {r['pe']:.1f}x | {r['score']} | {risk} |\n"

    # Low risk winners
    low_beta = [r for r in results if r['beta'] <= 1.0]
    if low_beta:
        report += "\n## Low Risk Options (Beta <= 1.0)\n\n"
        for r in sorted(low_beta, key=lambda x: x['score'], reverse=True):
            report += f"- {r['symbol']}: Score {r['score']}, Upside {r['upside']:+.1f}%\n"

    return report


def find_winners(symbols, criteria='score'):
    """Find best stocks by criteria"""
    results = analyze_multiple(symbols)

    if criteria == 'score':
        results.sort(key=lambda x: x['score'], reverse=True)
        label = "Score"
    elif criteria == 'upside':
        results.sort(key=lambda x: x['upside'], reverse=True)
        label = "Upside"
    elif criteria == 'pe':
        results.sort(key=lambda x: x['pe'])
        label = "P/E (lowest)"
    elif criteria == 'roe':
        results.sort(key=lambda x: x['roe'], reverse=True)
        label = "ROE"
    elif criteria == 'beta':
        results.sort(key=lambda x: x['beta'])
        label = "Beta (lowest)"
    else:
        return "[ERROR] Unknown criteria"

    report = f"# Winners by {label}\n\n"
    for i, r in enumerate(results[:10], 1):
        report += f"{i}. **{r['symbol']}** - {label}: "
        if criteria == 'score':
            report += f"{r['score']}"
        elif criteria == 'upside':
            report += f"{r['upside']:+.1f}%"
        elif criteria == 'pe':
            report += f"{r['pe']:.1f}x"
        elif criteria == 'roe':
            report += f"{r['roe']:.1f}%"
        elif criteria == 'beta':
            report += f"{r['beta']:.1f}"
        report += f" | Price: ${r['price']:.2f}\n"

    return report
