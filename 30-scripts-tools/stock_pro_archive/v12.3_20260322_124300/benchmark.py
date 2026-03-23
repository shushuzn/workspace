"""Benchmarking module for Stock PRO"""

def benchmark_vs_index(symbols, benchmark="SPY"):
    """Compare stock performance vs benchmark index"""
    from stock_pro.history import _history
    from stock_pro.core import analyze_multiple, P

    results = analyze_multiple(symbols)

    # Get benchmark returns
    bench_prices = _history.get_price_history(benchmark, days=30)
    if len(bench_prices) < 2:
        return "[Benchmark] Not enough benchmark data"

    bench_return = (bench_prices[-1][1] - bench_prices[0][1]) / bench_prices[0][1] * 100

    report = f"# Benchmark vs {benchmark}\n\n"
    report += f"**Benchmark Return:** {bench_return:+.1f}%\n\n"

    report += "| Symbol | Price | Score | Alpha | Outperform |\n"
    report += "|--------|-------|-------|-------|------------|\n"

    outperform = 0
    for r in results:
        sym = r["symbol"]
        prices = _history.get_price_history(sym, days=30)

        if len(prices) >= 2:
            ret = (prices[-1][1] - prices[0][1]) / prices[0][1] * 100
            alpha = ret - bench_return
            out = "Yes" if alpha > 0 else "No"
            if alpha > 0:
                outperform += 1
            report += f"| {sym} | ${r['price']:.2f} | {r['score']} | {alpha:+.1f}% | {out} |\n"
        else:
            report += f"| {sym} | ${r['price']:.2f} | {r['score']} | N/A | N/A |\n"

    report += f"\n**Outperformance Rate:** {outperform}/{len(results)} ({outperform /len(results) *100:.0f}%)\n"

    return report


def sector_benchmark():
    """Compare sector performance"""
    from stock_pro.core import A, analyze_multiple
    from stock_pro.sectors import get_symbols_by_sector, get_all_sectors

    sectors = get_all_sectors()

    report = "# Sector Benchmark\n\n"
    report += "| Sector | Avg Score | Avg Upside | Stocks |\n"
    report += "|--------|-----------|------------|--------|\n"

    sector_data = []
    for sector in sectors:
        symbols = get_symbols_by_sector(sector)
        results = analyze_multiple(symbols)

        if results:
            avg_score = sum(r["score"] for r in results) / len(results)
            avg_upside = sum(r["upside"] for r in results) / len(results)
            sector_data.append((sector, avg_score, avg_upside, len(results)))

    # Sort by score
    sector_data.sort(key=lambda x: x[1], reverse=True)

    for sector, score, upside, count in sector_data:
        report += f"| {sector} | {score:.0f} | {upside:+.1f}% | {count} |\n"

    return report


def score_distribution():
    """Show score distribution"""
    from stock_pro.core import A, analyze_multiple

    results = analyze_multiple(list(A.keys()))

    # Distribution buckets
    buckets = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "50-59": 0, "40-49": 0, "<40": 0}

    for r in results:
        score = r["score"]
        if score >= 90:
            buckets["90-100"] += 1
        elif score >= 80:
            buckets["80-89"] += 1
        elif score >= 70:
            buckets["70-79"] += 1
        elif score >= 60:
            buckets["60-69"] += 1
        elif score >= 50:
            buckets["50-59"] += 1
        elif score >= 40:
            buckets["40-49"] += 1
        else:
            buckets["<40"] += 1

    report = "# Score Distribution\n\n"
    report += "| Score Range | Count | Distribution |\n"
    report += "|-------------|-------|-------------|\n"

    for range_name, count in buckets.items():
        pct = count / len(results) * 100
        bar = "█" * int(pct / 5)
        report += f"| {range_name} | {count} | {bar} {pct:.0f}% |\n"

    avg_score = sum(r["score"] for r in results) / len(results)
    report += f"\n**Average Score:** {avg_score:.0f}\n"

    return report
