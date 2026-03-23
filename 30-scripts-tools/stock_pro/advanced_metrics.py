"""Advanced Metrics - Enhanced financial analysis"""
from stock_pro.data_target import A
from stock_pro.data_financial import F
from stock_pro.data_price import P, B, E


def get_advanced_metrics(symbol):
    """Calculate advanced financial metrics"""
    if symbol not in A:
        return None

    price = P.get(symbol, 0)
    eps = E.get(symbol, 0)
    gm, pm, roe, roic, de, rg, fcf, div = F.get(symbol, (0,0,0,0,0,0,0,0))
    beta = B.get(symbol, 1.0)
    target, rating, num_analysts = A[symbol]

    # Basic metrics
    pe = price / eps if eps > 0 else 0
    upside = (target - price) / price * 100 if price else 0

    # Advanced metrics
    roa = roe * (1 - de / 10)  # ROA approximation
    ev_ebitda = (price * 10) / (gm * price * 0.2) if gm > 0 else 0  # Simplified EV/EBITDA
    pb = pe * (1 / roe) if roe > 0 else 0  # P/B approximation
    ps = pm * price if pm > 0 else 0  # P/S approximation
    debt_equity = de
    current_ratio = 2.0 - (de * 0.1)  # Approximation
    quick_ratio = current_ratio * 0.8  # Approximation

    # Growth metrics
    peg = pe / (rg * 100) if rg > 0 else 0
    earnings_yield = (eps / price * 100) if price > 0 else 0
    fcf_yield = (fcf * price / 100) / price * 100 if price > 0 else 0

    # Risk metrics
    sharpe = (rg * 100 - 2) / (beta * 15) if beta > 0 else 0  # Simplified Sharpe
    sortino = sharpe * 1.2  # Approximation

    # Quality scores
    profitability_score = min(100, (pm * 200 + gm * 50 + roic * 100) / 3)
    balance_sheet_score = min(100, max(0, 100 - de * 20))
    growth_score = min(100, rg * 400) if rg > 0 else max(0, 50 + rg * 200)
    valuation_score = min(100, max(0, 100 - pe * 2)) if pe > 0 else 50

    overall_quality = (profitability_score * 0.3 + balance_sheet_score * 0.2 +
                       growth_score * 0.25 + valuation_score * 0.25)

    return {
        "symbol": symbol,
        "price": price,
        "eps": eps,
        "pe": pe,
        "upside": upside,
        # Profitability
        "gm": gm * 100,
        "pm": pm * 100,
        "roe": roe * 100,
        "roic": roic * 100,
        "roa": roa * 100,
        # Valuation
        "pb": pb,
        "ps": ps,
        "ev_ebitda": ev_ebitda,
        # Growth
        "rg": rg * 100,
        "peg": peg,
        "earnings_yield": earnings_yield,
        "fcf_yield": fcf_yield,
        # Balance sheet
        "de": de,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        # Risk
        "beta": beta,
        "sharpe": sharpe,
        "sortino": sortino,
        # Quality
        "profitability_score": profitability_score,
        "balance_sheet_score": balance_sheet_score,
        "growth_score": growth_score,
        "valuation_score": valuation_score,
        "overall_quality": overall_quality,
        # Rating
        "analyst_rating": rating,
        "num_analysts": num_analysts,
        "recommend": "Strong Buy" if overall_quality >= 75 else "Buy" if overall_quality >= 60 else "Hold" if overall_quality >= 40 else "Underweight"
    }


def get_all_advanced_metrics(symbols=None):
    """Get advanced metrics for multiple symbols"""
    # Support single symbol string
    if isinstance(symbols, str):
        symbols = [symbols]
    symbols = symbols or list(A.keys())
    return [m for m in (get_advanced_metrics(s) for s in symbols) if m]


def quality_report(symbols=None):
    """Generate quality-focused report"""
    metrics = get_all_advanced_metrics(symbols)
    metrics.sort(key=lambda x: x["overall_quality"], reverse=True)

    report = "# Quality Analysis Report\n\n"
    report += "| Symbol | Quality | Profit | Growth | Valuation | Balance | Recommend |\n"
    report += "|--------|---------|--------|--------|-----------|---------|----------|\n"

    for m in metrics[:20]:
        report += f"| {m['symbol']} | {m['overall_quality']:.0f} | {m['profitability_score']:.0f} | "
        report += f"{m['growth_score']:.0f} | {m['valuation_score']:.0f} | {m['balance_sheet_score']:.0f} | "
        report += f"{m['recommend']} |\n"

    return report


def risk_return_report(symbols=None):
    """Generate risk-return analysis"""
    metrics = get_all_advanced_metrics(symbols)

    report = "# Risk-Return Analysis\n\n"
    report += "| Symbol | Beta | Sharpe | Upside | Risk Level |\n"
    report += "|--------|------|--------|--------|------------|\n"

    for m in sorted(metrics, key=lambda x: x["sharpe"], reverse=True):
        risk = "High" if m["beta"] > 1.5 else "Medium" if m["beta"] > 1.0 else "Low"
        report += f"| {m['symbol']} | {m['beta']:.1f} | {m['sharpe']:.2f} | {m['upside']:+.1f}% | {risk} |\n"

    return report


def value_vs_growth_report(symbols=None):
    """Compare value vs growth stocks"""
    metrics = get_all_advanced_metrics(symbols)

    value_stocks = [m for m in metrics if m["valuation_score"] > 60]
    growth_stocks = [m for m in metrics if m["growth_score"] > 60]

    report = "# Value vs Growth Analysis\n\n"
    report += "## Value Stocks (Low Valuation)\n\n"
    report += "| Symbol | P/E | P/B | Upside | Quality |\n"
    report += "|--------|-----|-----|--------|---------|\n"
    for m in sorted(value_stocks, key=lambda x: x["pe"])[:10]:
        report += f"| {m['symbol']} | {m['pe']:.1f} | {m['pb']:.1f} | {m['upside']:+.1f}% | {m['overall_quality']:.0f} |\n"

    report += "\n## Growth Stocks (High Growth)\n\n"
    report += "| Symbol | Rev Growth | PEG | Upside | Quality |\n"
    report += "|--------|------------|-----|--------|---------|\n"
    for m in sorted(growth_stocks, key=lambda x: x["rg"], reverse=True)[:10]:
        report += f"| {m['symbol']} | {m['rg']:.1f}% | {m['peg']:.2f} | {m['upside']:+.1f}% | {m['overall_quality']:.0f} |\n"

    return report
