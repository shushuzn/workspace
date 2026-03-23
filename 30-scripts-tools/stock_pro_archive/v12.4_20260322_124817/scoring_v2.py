"""Scoring Engine v2 - Enhanced scoring with multiple models"""
from stock_pro.data_target import A
from stock_pro.data_financial import F
from stock_pro.data_price import P, B, E


def score_model_v1(symbol, price, data):
    """Original scoring model"""
    t, r, n = data
    gm, pm, roe, roic, de, rg, fcf, div = F.get(symbol, (0,0,0,0,0,0,0,0))
    beta = B.get(symbol, 1.0)
    eps = E.get(symbol, 0)

    pe = price / eps if eps > 0 else 100
    v_score = min(100, max(0, 100 - pe * 2)) if eps > 0 else 50
    g_score = min(100, rg * 400) if rg > 0 else max(0, 50 + rg * 200)
    p_score = min(100, (pm * 100 + gm * 0.5 + roic * 0.5))
    b_score = max(0, 100 - de * 15)
    m_score = max(0, 100 - (beta - 1) * 30)

    score = v_score * 0.25 + g_score * 0.25 + p_score * 0.25 + b_score * 0.15 + m_score * 0.10

    if r == "Sell": score = min(score, 20)
    elif r == "Underperform": score = min(score, 35)
    elif r == "Neutral": score = min(max(score, 45), 55)
    elif r == "Hold": score = min(max(score, 40), 60)
    elif r in ("Outperform", "Buy"): score = max(score, 60)
    elif r == "Strong Buy": score = max(score, 80)

    return int(min(100, max(0, score)))


def score_model_v2(symbol, price, data):
    """Enhanced scoring with more factors"""
    t, r, n = data
    gm, pm, roe, roic, de, rg, fcf, div = F.get(symbol, (0,0,0,0,0,0,0,0))
    beta = B.get(symbol, 1.0)
    eps = E.get(symbol, 0)

    # Valuation (30%)
    pe = price / eps if eps > 0 else 100
    if pe <= 15: v_score = 100
    elif pe <= 25: v_score = 80
    elif pe <= 35: v_score = 60
    elif pe <= 50: v_score = 40
    else: v_score = 20

    # Growth (25%)
    if rg >= 0.30: g_score = 100
    elif rg >= 0.20: g_score = 80
    elif rg >= 0.15: g_score = 60
    elif rg >= 0.10: g_score = 40
    else: g_score = 20

    # Profitability (20%)
    p_score = min(100, (pm * 200 + gm * 50 + roic * 100) / 3)

    # Balance Sheet (15%)
    if de <= 0.5: b_score = 100
    elif de <= 1.0: b_score = 80
    elif de <= 2.0: b_score = 60
    elif de <= 3.0: b_score = 40
    else: b_score = 20

    # Momentum/Risk (10%)
    m_score = max(0, 100 - (beta - 1) * 40)

    # Analyst sentiment
    analyst_bonus = 10 if n >= 40 else (5 if n >= 20 else 0)

    score = v_score * 0.30 + g_score * 0.25 + p_score * 0.20 + b_score * 0.15 + m_score * 0.10 + analyst_bonus

    if r == "Sell": score = min(score, 15)
    elif r == "Underperform": score = min(score, 30)
    elif r == "Neutral": score = min(max(score, 45), 55)
    elif r == "Hold": score = min(max(score, 40), 60)
    elif r in ("Outperform", "Buy"): score = max(score, 60)
    elif r == "Strong Buy": score = max(score, 80)

    return int(min(100, max(0, score)))


def score_model_v3(symbol, price, data):
    """Quality-focused scoring"""
    t, r, n = data
    gm, pm, roe, roic, de, rg, fcf, div = F.get(symbol, (0,0,0,0,0,0,0,0))
    beta = B.get(symbol, 1.0)
    eps = E.get(symbol, 0)

    # Quality factors
    roe_score = min(100, roe * 200) if roe > 0 else 0
    pm_score = min(100, pm * 200) if pm > 0 else 0
    gm_score = min(100, gm * 100) if gm > 0 else 0
    roic_score = min(100, roic * 200) if roic > 0 else 0

    if rg >= 0.25 and pm >= 0.15: g_score = 100
    elif rg >= 0.15 and pm >= 0.10: g_score = 80
    elif rg >= 0.10: g_score = 60
    elif rg >= 0.05: g_score = 40
    else: g_score = 20

    pe = price / eps if eps > 0 else 100
    v_score = 100 if pe <= 20 else (75 if pe <= 30 else (50 if pe <= 40 else 25))
    b_score = max(0, 100 - de * 20)
    m_score = max(0, 100 - (beta - 1) * 35)

    score = (roe_score * 0.20 + pm_score * 0.20 + gm_score * 0.10 + roic_score * 0.15 +
             g_score * 0.15 + v_score * 0.10 + b_score * 0.05 + m_score * 0.05)

    if r in ("Outperform", "Buy", "Strong Buy"): score = max(score, 65)
    elif r in ("Hold", "Neutral"): score = min(max(score, 45), 60)
    else: score = min(score, 40)

    return int(min(100, max(0, score)))


def get_all_scores(symbol):
    """Get scores from all models"""
    if symbol not in A:
        return None

    from stock_pro.core import fetch
    price, _, _, _ = fetch(symbol)
    data = A[symbol]

    v1 = score_model_v1(symbol, price, data)
    v2 = score_model_v2(symbol, price, data)
    v3 = score_model_v3(symbol, price, data)

    return {
        "symbol": symbol,
        "price": price,
        "model_v1": v1,
        "model_v2": v2,
        "model_v3": v3,
        "consensus": (v1 + v2 + v3) // 3
    }


def compare_models(symbols=None):
    """Compare scoring models"""
    symbols = symbols or list(A.keys())[:10]

    results = []
    for sym in symbols:
        scores = get_all_scores(sym)
        if scores:
            results.append(scores)

    report = "# Scoring Model Comparison\n\n"
    report += "| Symbol | V1 | V2 | V3 | Consensus |\n"
    report += "|--------|----|----|----|------------|\n"

    for r in sorted(results, key=lambda x: x["consensus"], reverse=True):
        report += f"| {r['symbol']} | {r['model_v1']} | {r['model_v2']} | {r['model_v3']} | {r['consensus']} |\n"

    return report


def get_consensus_top(symbols=None, n=10):
    """Get top stocks by consensus score"""
    symbols = symbols or list(A.keys())

    results = []
    for sym in symbols:
        scores = get_all_scores(sym)
        if scores:
            results.append(scores)

    results.sort(key=lambda x: x["consensus"], reverse=True)
    return results[:n]
