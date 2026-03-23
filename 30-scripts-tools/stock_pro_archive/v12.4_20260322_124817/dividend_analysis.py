"""Dividend Analysis Module - Dividend safety and growth analysis"""
from stock_pro.data_financial import F
from stock_pro.data_price import P


def get_dividend_data(symbol):
    """Get dividend metrics for symbol"""
    fcf, div = None, None

    financial = F.get(symbol, (0,0,0,0,0,0,0,0))
    if len(financial) >= 8:
        fcf = financial[6]  # FCF yield
        div = financial[7]   # Dividend yield

    price = P.get(symbol, 0)

    # Mock dividend data for demo
    dividend_data = {
        "AAPL": {"yield": 0.005, "payout": 0.15, "growth": 0.07, "streak": 12},
        "MSFT": {"yield": 0.008, "payout": 0.25, "growth": 0.10, "streak": 18},
        "JNJ": {"yield": 0.030, "payout": 0.45, "growth": 0.06, "streak": 62},
        "KO": {"yield": 0.030, "payout": 0.75, "growth": 0.035, "streak": 60},
        "PG": {"yield": 0.025, "payout": 0.60, "growth": 0.05, "streak": 67},
        "PEP": {"yield": 0.027, "payout": 0.70, "growth": 0.05, "streak": 52},
        "XOM": {"yield": 0.035, "payout": 0.50, "growth": 0.03, "streak": 42},
        "CVX": {"yield": 0.040, "payout": 0.55, "growth": 0.04, "streak": 37},
    }

    return dividend_data.get(symbol, {"yield": 0, "payout": 0, "growth": 0, "streak": 0})


def calc_dividend_score(symbol):
    """Calculate dividend quality score (0-100)"""
    data = get_dividend_data(symbol)

    if data["yield"] == 0:
        return {"symbol": symbol, "score": 0, "grade": "N/A", "reason": "No dividend"}

    # Safety score (40%)
    payout = data["payout"]
    if payout < 0.30:
        safety = 100
    elif payout < 0.50:
        safety = 80
    elif payout < 0.70:
        safety = 60
    elif payout < 1.0:
        safety = 40
    else:
        safety = 20

    # Growth score (30%)
    growth = data["growth"]
    if growth >= 0.10:
        growth_score = 100
    elif growth >= 0.07:
        growth_score = 80
    elif growth >= 0.05:
        growth_score = 60
    elif growth >= 0.03:
        growth_score = 40
    else:
        growth_score = 20

    # Yield score (30%)
    yield_ = data["yield"]
    if yield_ >= 0.05:
        yield_score = 100
    elif yield_ >= 0.03:
        yield_score = 80
    elif yield_ >= 0.02:
        yield_score = 60
    elif yield_ >= 0.01:
        yield_score = 40
    else:
        yield_score = 20

    # Streak bonus
    streak = data["streak"]
    streak_bonus = min(10, streak // 10)

    total = safety * 0.4 + growth_score * 0.3 + yield_score * 0.3 + streak_bonus

    # Grade
    if total >= 85:
        grade = "A+"
    elif total >= 75:
        grade = "A"
    elif total >= 65:
        grade = "B+"
    elif total >= 55:
        grade = "B"
    elif total >= 45:
        grade = "C"
    else:
        grade = "D"

    return {
        "symbol": symbol,
        "score": int(total),
        "grade": grade,
        "safety": safety,
        "growth": growth_score,
        "yield_score": yield_score,
        "streak": streak,
        "yield": data["yield"] * 100,
        "payout": data["payout"] * 100,
        "dgr": data["growth"] * 100
    }


def dividend_report(symbols):
    """Generate dividend report"""
    report = "# Dividend Analysis Report\n\n"
    report += "| Symbol | Yield | Payout | Growth | Streak | Score | Grade |\n"
    report += "|--------|-------|--------|--------|--------|-------|-------|\n"

    results = []
    for symbol in symbols:
        d = get_dividend_data(symbol)
        if d["yield"] > 0:
            score = calc_dividend_score(symbol)
            results.append(score)
            report += f"| {symbol} | {d['yield']*100:.1f}% | {d['payout']*100:.0f}% | {d['growth']*100:.1f}% | {d['streak']}y | {score['score']} | {score['grade']} |\n"

    if not results:
        return report + "\nNo dividend data for selected symbols."

    # Best dividend stocks
    report += "\n## Top Dividend Picks\n\n"
    top = sorted(results, key=lambda x: x["score"], reverse=True)[:5]
    for i, t in enumerate(top, 1):
        report += f"{i}. **{t['symbol']}**: {t['grade']} (Score: {t['score']}, Yield: {t['yield']:.1f}%)\n"

    # Dividend aristocrats
    aristocrats = [r for r in results if r["streak"] >= 25]
    if aristocrats:
        report += "\n## Dividend Aristocrats (25+ years)\n\n"
        for a in sorted(aristocrats, key=lambda x: x["score"], reverse=True):
            report += f"- {a['symbol']}: {a['streak']} years, {a['yield']:.1f}% yield\n"

    return report
