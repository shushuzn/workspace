"""Earnings Analysis Module - Earnings forecast and beat prediction"""
from stock_pro.data_financial import F
from stock_pro.data_target import A
from stock_pro.data_price import P, E


def get_earnings_data(symbol):
    """Get earnings data for symbol"""
    eps = E.get(symbol, 0)
    financial = F.get(symbol, (0,0,0,0,0,0,0,0))

    fcf = financial[6] if len(financial) > 6 else 0
    rg = financial[5] if len(financial) > 5 else 0

    # Calculate forward EPS
    eps_forward = eps * (1 + rg) if eps > 0 else 0

    return {
        "symbol": symbol,
        "eps_current": eps,
        "eps_forward": eps_forward,
        "growth": rg,
        "fcf_per_share": fcf
    }


def calc_earnings_yield(symbol):
    """Calculate earnings yield"""
    eps = E.get(symbol, 0)
    price = P.get(symbol, 0)

    if not eps or not price:
        return 0

    return (eps / price) * 100


def predict_earnings_beat(symbol):
    """Predict if company will beat earnings"""
    data = get_earnings_data(symbol)

    if not data["eps_current"]:
        return {"symbol": symbol, "prediction": "Unknown", "confidence": 0, "factors": []}

    # Get financial data
    gm, pm, roe, roic, de, rg, fcf, div = F.get(symbol, (0,0,0,0,0,0,0,0))

    # Factors that suggest beat
    factors = []

    # Revenue growth
    if rg > 0.20:
        factors.append(("Strong Growth", 1, "+20%"))
    elif rg > 0.10:
        factors.append(("Good Growth", 0.5, f"+{rg *100:.0f}%"))
    elif rg < 0:
        factors.append(("Declining", -1, f"{rg *100:.0f}%"))

    # Profit margins
    if pm > 0.20:
        factors.append(("High Margins", 1, f"{pm *100:.0f}%"))
    elif pm > 0.10:
        factors.append(("Good Margins", 0.5, f"{pm *100:.0f}%"))

    # FCF
    if fcf > 0.03:
        factors.append(("Strong FCF", 1, f"{fcf *100:.1f}%"))

    # Estimate probability
    score = sum(f[1] for f in factors)

    if score >= 2:
        prediction = "Beat"
        confidence = min(90, 50 + score * 15)
    elif score >= 1:
        prediction = "Meet"
        confidence = 50 + score * 10
    else:
        prediction = "Miss"
        confidence = max(30, 50 - abs(score) * 15)

    return {
        "symbol": symbol,
        "prediction": prediction,
        "confidence": confidence,
        "factors": factors,
        "eps_current": data["eps_current"],
        "eps_forward": data["eps_forward"]
    }


def earnings_report(symbols):
    """Generate earnings report"""
    # Support single symbol
    if isinstance(symbols, str):
        symbols = [symbols]

    report = "# Earnings Analysis Report\n\n"
    report += "| Symbol | Current EPS | Forward EPS | Growth | Yield | Beat Prob |\n"
    report += "|--------|-------------|-------------|--------|--------|------------|\n"

    predictions = []
    for symbol in symbols:
        data = get_earnings_data(symbol)
        pred = predict_earnings_beat(symbol)
        price = P.get(symbol, 0)
        yield_ = calc_earnings_yield(symbol)

        report += f"| {symbol} | ${data['eps_current']:.2f} | ${data['eps_forward']:.2f} | {data['growth'] *100:.0f}% | {yield_:.1f}% | {pred['prediction']} ({pred['confidence']:.0f}%) |\n"
        predictions.append(pred)

    # Best bets
    report += "\n## Best Earnings Bets\n\n"
    beats = [p for p in predictions if p["prediction"] == "Beat"]
    if beats:
        for p in sorted(beats, key=lambda x: x["confidence"], reverse=True)[:5]:
            report += f"- **{p['symbol']}**: {p['prediction']} ({p['confidence']:.0f}% confidence)\n"
    else:
        report += "No strong earnings beat predictions.\n"

    return report
