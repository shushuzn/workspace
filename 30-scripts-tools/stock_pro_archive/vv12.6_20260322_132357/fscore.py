"""Piotroski F-Score Module - Financial strength assessment"""
from stock_pro.data_financial import F
from stock_pro.data_price import P, B


def calc_fscore(symbol):
    """Calculate Piotroski F-Score (0-9)"""
    financial = F.get(symbol, (0,0,0,0,0,0,0,0))
    if not financial or len(financial) < 4:
        return {"symbol": symbol, "fscore": 0, "details": [], "grade": "F"}

    gm, pm, roe, roic = financial[:4]
    de = financial[4] if len(financial) > 4 else 0
    fcf = financial[6] if len(financial) > 6 else 0
    roa = roe  # Use ROE as proxy

    score = 0
    details = []

    # Profitability (4 points)
    # ROA > 0
    if roa > 0:
        score += 1
        details.append(("ROA > 0", 1, f"{roa:.1f}%"))
    else:
        details.append(("ROA > 0", 0, f"{roa:.1f}%"))

    # CFO > 0
    if fcf > 0:
        score += 1
        details.append(("FCF > 0", 1, f"{fcf*100:.1f}%"))
    else:
        details.append(("FCF > 0", 0, f"{fcf*100:.1f}%"))

    # ROA improvement
    if roa > 10:
        score += 1
        details.append(("ROA > 10%", 1, f"{roa:.1f}%"))
    else:
        details.append(("ROA > 10%", 0, f"{roa:.1f}%"))

    # Accruals (CFO vs ROA)
    if fcf > roa / 100:
        score += 1
        details.append(("FCF > ROA", 1, "OK"))
    else:
        details.append(("FCF > ROA", 0, "Warning"))

    # Leverage (2 points)
    # Lower debt
    if de < 1.0:
        score += 1
        details.append(("D/E < 1.0", 1, f"{de:.1f}"))
    else:
        details.append(("D/E < 1.0", 0, f"{de:.1f}"))

    # Liquidity
    if de < 1.5:
        score += 1
        details.append(("Low Leverage", 1, "OK"))
    else:
        details.append(("Low Leverage", 0, "High"))

    # Efficiency (3 points)
    # Gross margin improvement
    if gm > 0.40:
        score += 1
        details.append(("GM > 40%", 1, f"{gm*100:.0f}%"))
    else:
        details.append(("GM > 40%", 0, f"{gm*100:.0f}%"))

    # Asset turnover
    if pm > 0.15:
        score += 1
        details.append(("PM > 15%", 1, f"{pm*100:.0f}%"))
    else:
        details.append(("PM > 15%", 0, f"{pm*100:.0f}%"))

    # Operating leverage
    if gm - pm > 0.20:
        score += 1
        details.append(("Op Efficiency", 1, "OK"))
    else:
        details.append(("Op Efficiency", 0, "Low"))

    # Grade
    if score >= 8:
        grade = "A"
    elif score >= 6:
        grade = "B+"
    elif score >= 5:
        grade = "B"
    elif score >= 4:
        grade = "C"
    else:
        grade = "D"

    return {
        "symbol": symbol,
        "fscore": score,
        "details": details,
        "grade": grade
    }


def fscore_report(symbols):
    """Generate F-Score report"""
    report = "# Piotroski F-Score Report\n\n"
    report += "| Symbol | F-Score | Grade | Profitability | Leverage | Efficiency |\n"
    report += "|--------|---------|-------|---------------|---------|------------|\n"

    results = []
    for symbol in symbols:
        fs = calc_fscore(symbol)
        results.append(fs)

        prof = sum(1 for d in fs["details"][:4] if d[1])
        lev = sum(1 for d in fs["details"][4:6] if d[1])
        eff = sum(1 for d in fs["details"][6:] if d[1])

        report += f"| {symbol} | {fs['fscore']} | {fs['grade']} | {prof}/4 | {lev}/2 | {eff}/3 |\n"

    # Best by F-Score
    report += "\n## Top F-Score Stocks\n\n"
    top = sorted(results, key=lambda x: x["fscore"], reverse=True)[:5]
    for i, t in enumerate(top, 1):
        report += f"{i}. **{t['symbol']}**: F-Score {t['fscore']}/9 ({t['grade']})\n"

    # High quality value stocks
    hv = [r for r in results if r["fscore"] >= 6]
    if hv:
        report += "\n## High Quality Value Stocks\n\n"
        for r in sorted(hv, key=lambda x: x["fscore"], reverse=True):
            report += f"- {r['symbol']}: F-Score {r['fscore']}\n"

    return report
