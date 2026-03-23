"""Risk analysis for Stock PRO"""

def calc_var(returns, confidence=0.95):
    """Calculate Value at Risk"""
    if not returns:
        return 0
    sorted_returns = sorted(returns)
    index = int((1 - confidence) * len(sorted_returns))
    return abs(sorted_returns[index]) if index < len(sorted_returns) else 0


def risk_profile(result):
    """Generate risk profile for a stock"""
    sym = result["symbol"]
    beta = result.get("beta", 1.0)
    pe = result.get("pe", 0)
    score = result["score"]

    # Risk score components
    factors = []

    # Beta risk
    if beta > 1.5:
        factors.append(("High Volatility", beta, "red"))
    elif beta > 1.0:
        factors.append(("Moderate Volatility", beta, "yellow"))
    elif beta < 0.8:
        factors.append(("Defensive", beta, "green"))
    else:
        factors.append(("Normal Volatility", beta, "white"))

    # P/E risk
    if pe > 40:
        factors.append(("High Valuation", f"{pe:.1f}x", "red"))
    elif pe > 25:
        factors.append(("Moderate Valuation", f"{pe:.1f}x", "yellow"))
    elif pe < 15:
        factors.append(("Value", f"{pe:.1f}x", "green"))
    else:
        factors.append(("Fair Valuation", f"{pe:.1f}x", "white"))

    # Overall risk level
    if beta > 1.5 and pe > 40:
        risk_level = "HIGH"
        risk_color = "red"
    elif beta > 1.2 or pe > 35:
        risk_level = "MEDIUM"
        risk_color = "yellow"
    else:
        risk_level = "LOW"
        risk_color = "green"

    return {
        "symbol": sym,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "beta": beta,
        "pe": pe,
        "factors": factors
    }


def risk_report(results):
    """Generate risk comparison report"""
    if not results:
        return "[Risk] No data"

    profiles = [risk_profile(r) for r in results]

    report = "# Risk Analysis\n\n"
    report += "| Symbol | Risk | Beta | P/E | Factors |\n"
    report += "|--------|------|------|-----|--------|\n"

    for p in sorted(profiles, key=lambda x: x["beta"], reverse=True):
        factors_str = ", ".join([f[0] for f in p["factors"]])
        report += f"| {p['symbol']} | {p['risk_level']} | {p['beta']:.1f} | {p['pe']:.1f}x | {factors_str} |\n"

    return report


def diversification_check(portfolio_results):
    """Check portfolio diversification"""
    sectors = {}
    for r in portfolio_results:
        sym = r["symbol"]
        # Simple sector mapping based on symbol patterns
        if sym in ["NVDA", "AMD", "INTC", "QCOM", "AVGO", "ASML"]:
            sector = "Semiconductors"
        elif sym in ["META", "GOOGL", "AMZN", "NFLX", "CRM", "ADBE", "NOW", "SNOW", "PANW"]:
            sector = "Software/Internet"
        elif sym in ["AAPL", "MSFT"]:
            sector = "Mega Tech"
        elif sym in ["JPM", "BAC", "GS", "V", "MA"]:
            sector = "Finance"
        elif sym in ["JNJ", "PFE", "UNH", "MRK", "ABBV", "LLY"]:
            sector = "Healthcare"
        elif sym in ["WMT", "COST", "KO"]:
            sector = "Consumer"
        elif sym in ["CAT", "HON", "DE"]:
            sector = "Industrial"
        elif sym in ["XOM", "CVX"]:
            sector = "Energy"
        elif sym in ["TSLA"]:
            sector = "Auto/Tech"
        elif sym in ["SPY", "QQQ"]:
            sector = "ETF"
        else:
            sector = "Other"

        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(r)

    recommendations = []

    if len(sectors) < 3:
        recommendations.append(f"[!] Only {len(sectors)} sectors - consider diversifying")
    else:
        recommendations.append(f"[+] Good sector diversification ({len(sectors)} sectors)")

    # Check concentration
    for sector, stocks in sectors.items():
        weight = len(stocks) / len(portfolio_results) * 100
        if weight > 40:
            recommendations.append(f"[!] {sector} is {weight:.0f}% of portfolio - high concentration")

    # Check Beta balance
    high_beta = sum(1 for r in portfolio_results if r.get("beta", 1) > 1.3)
    low_beta = sum(1 for r in portfolio_results if r.get("beta", 1) < 0.8)

    if high_beta > len(portfolio_results) * 0.6:
        recommendations.append("[!] Portfolio is heavily weighted toward high-volatility stocks")
    elif low_beta > len(portfolio_results) * 0.6:
        recommendations.append("[!] Portfolio may be too defensive - missing growth opportunities")
    else:
        recommendations.append("[+] Good balance of growth and defensive stocks")

    return {
        "sectors": {k: len(v) for k, v in sectors.items()},
        "recommendations": recommendations
    }
