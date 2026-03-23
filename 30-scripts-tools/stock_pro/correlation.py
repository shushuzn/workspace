"""Correlation analysis for Stock PRO"""

def calc_correlation(returns1, returns2):
    """Calculate Pearson correlation between two return series"""
    if len(returns1) != len(returns2) or len(returns1) < 2:
        return None

    n = len(returns1)
    mean1 = sum(returns1) / n
    mean2 = sum(returns2) / n

    numerator = sum((r1 - mean1) * (r2 - mean2) for r1, r2 in zip(returns1, returns2))
    denom1 = sum((r - mean1) ** 2 for r in returns1) ** 0.5
    denom2 = sum((r - mean2) ** 2 for r in returns2) ** 0.5

    if denom1 == 0 or denom2 == 0:
        return None

    return numerator / (denom1 * denom2)


def get_returns_from_history(symbol, days=30):
    """Get returns from history"""
    from stock_pro.history import _history

    prices = _history.get_price_history(symbol, days)
    if len(prices) < 3:
        return []

    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i][1] - prices[i -1][1]) / prices[i -1][1]
        returns.append(ret)

    return returns


def correlation_matrix(symbols, days=30):
    """Generate correlation matrix for symbols"""
    matrix = {}

    # Get returns for all symbols
    all_returns = {}
    for sym in symbols:
        returns = get_returns_from_history(sym, days)
        if returns:
            all_returns[sym] = returns

    # Calculate correlations
    for sym1 in all_returns:
        matrix[sym1] = {}
        for sym2 in all_returns:
            if sym1 == sym2:
                matrix[sym1][sym2] = 1.0
            else:
                corr = calc_correlation(all_returns[sym1], all_returns[sym2])
                matrix[sym1][sym2] = corr if corr is not None else 0

    return matrix


def correlation_report(symbols=None, days=30):
    """Generate correlation report"""
    from stock_pro.core import A

    # Support single symbol string
    if isinstance(symbols, str):
        symbols = [symbols]

    if symbols is None:
        symbols = list(A.keys())[:10]  # Limit to 10 for readability

    matrix = correlation_matrix(symbols, days)

    if not matrix:
        return "[Correlation] Not enough historical data"

    report = f"# Correlation Analysis (last {days} days)\n\n"

    # Header
    report += "| Symbol | " + " | ".join([s[:4] for s in symbols]) + " |\n"
    report += "|--------|" + "|".join(["------" for _ in symbols]) + "|\n"

    # Data
    for sym1 in symbols:
        row = [f"| {sym1[:4]}"]
        for sym2 in symbols:
            corr = matrix.get(sym1, {}).get(sym2, 0)
            if corr is None:
                row.append("-")
            elif corr > 0.7:
                row.append(f"**{corr:.2f}**")
            elif corr > 0.3:
                row.append(f"*{corr:.2f}*")
            else:
                row.append(f"{corr:.2f}")
        report += " ".join(row) + " |\n"

    report += "\n*Bold = Strong positive (>0.7), Italic = Moderate (>0.3)*\n"

    # Find highly correlated pairs
    report += "\n## Highly Correlated Pairs (>0.7)\n\n"
    pairs = []
    for sym1 in matrix:
        for sym2 in matrix[sym1]:
            if sym1 < sym2:
                corr = matrix[sym1][sym2]
                if corr is not None and corr > 0.7:
                    pairs.append((sym1, sym2, corr))

    if pairs:
        pairs.sort(key=lambda x: -x[2])
        for sym1, sym2, corr in pairs[:10]:
            report += f"- {sym1} ↔ {sym2}: {corr:.2f}\n"
    else:
        report += "No highly correlated pairs found.\n"

    return report


def diversification_by_correlation(symbols, threshold=0.7):
    """Suggest portfolio diversification based on correlation"""
    from stock_pro.core import analyze_multiple

    matrix = correlation_matrix(symbols)
    results = analyze_multiple(symbols)

    # Group by correlation
    groups = []
    assigned = set()

    for sym in symbols:
        if sym in assigned:
            continue

        group = [sym]
        assigned.add(sym)

        for other in symbols:
            if other in assigned:
                continue
            corr = matrix.get(sym, {}).get(other, 0)
            if corr is not None and corr < threshold:
                group.append(other)
                assigned.add(other)

        groups.append(group)

    report = "# Diversification Suggestions\n\n"
    report += f"**Correlation threshold:** {threshold}\n"
    report += f"**Clusters found:** {len(groups)}\n\n"

    for i, group in enumerate(groups, 1):
        report += f"## Cluster {i} ({len(group)} stocks)\n"
        report += "| Symbol | Score | Beta | Rating |\n"
        report += "|--------|-------|------|--------|\n"

        for sym in group:
            r = next((x for x in results if x['symbol'] == sym), None)
            if r:
                report += f"| {sym} | {r['score']} | {r.get('beta', 1):.1f} | {r['rating']} |\n"
        report += "\n"

    return report
