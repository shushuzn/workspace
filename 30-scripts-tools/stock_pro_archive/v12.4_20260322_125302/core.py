"""Core stock analysis engine"""
import json, urllib.request
from datetime import datetime
from stock_pro.data_target import A
from stock_pro.data_financial import F
from stock_pro.data_price import P, B, E

def fetch(symbol):
    """Get current price from API"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
            return price, "live", datetime.now().isoformat(), datetime.now().isoformat()
    except Exception:
        return P.get(symbol, 0), "cached", datetime.now().isoformat(), datetime.now().isoformat()

def fetch_live(symbols):
    return [{"symbol": s, "price": fetch(s)[0]} for s in symbols]

def calc_dcf(symbol, price, shares=15, wacc=0.10, growth=0.15, de=0):
    """DCF valuation"""
    fcf = F.get(symbol, (0,0,0,0,0,0,0,0))[6] or 0.03
    fcf_y1 = price * shares * fcf
    cash_flows = []
    for y in range(1, 6):
        cf = fcf_y1 * ((1 + growth) ** y) / ((1 + wacc) ** y)
        cash_flows.append(cf)
    tv = cash_flows[-1] * (1 + growth) / (wacc - growth)
    terminal = tv / ((1 + wacc) ** 5)
    equity = sum(cash_flows) + terminal
    intrinsic = equity / shares
    upside = (intrinsic - price) / price * 100 if price else 0
    return {"base": intrinsic, "upside": upside, "bear": intrinsic * 0.7, "bull": intrinsic * 1.3}

def calc_score(symbol, price, data):
    """Calculate composite score"""
    t, r, n = data
    upside = (t - price) / price * 100 if price else 0
    gm, pm, roe, roic, de, rg, fcf, div = F.get(symbol, (0,0,0,0,0,0,0,0))
    beta = B.get(symbol, 1.0)
    eps = E.get(symbol, 0)
    
    pe = price / eps if eps > 0 else 100
    v_score = min(100, max(0, 100 - pe * 2)) if eps > 0 else 50
    g_score = min(100, rg * 4) if rg > 0 else max(0, 50 + rg * 5)
    p_score = min(100, (pm * 100 + gm * 0.5 + roic * 0.5))
    b_score = max(0, 100 - de * 15)
    m_score = max(0, 100 - (beta - 1) * 30)
    
    weights = {"val": 0.25, "growth": 0.25, "prof": 0.25, "bal": 0.15, "mom": 0.10}
    score = v_score * weights["val"] + g_score * weights["growth"] + p_score * weights["prof"] + b_score * weights["bal"] + m_score * weights["mom"]
    
    if r == "Sell": score = min(score, 20)
    elif r == "Underperform": score = min(score, 35)
    elif r == "Neutral": score = min(max(score, 45), 55)
    elif r == "Hold": score = min(max(score, 40), 60)
    elif r in ("Outperform", "Buy"): score = max(score, 60)
    elif r == "Strong Buy": score = max(score, 80)
    
    return int(min(100, max(0, score)))

def analyze(symbol):
    """Full analysis for one symbol"""
    price, source, fetched, expires = fetch(symbol)
    if symbol not in A: return None
    
    t, r, n = A[symbol]
    upside = (t - price) / price * 100 if price else 0
    eps = E.get(symbol, 0)
    pe = price / eps if eps > 0 else 0
    gm, pm, roe, roic, de, rg, fcf, div = F.get(symbol, (0,0,0,0,0,0,0,0))
    beta = B.get(symbol, 1.0)
    dcf = calc_dcf(symbol, price)
    
    score = calc_score(symbol, price, A[symbol])
    fpe = fcf / price * 100 if price else 0
    peg = pe / (rg * 100) if rg > 0 else 0
    
    if score >= 75: rating = "STRONG BUY"
    elif score >= 60: rating = "BUY"
    elif score >= 40: rating = "HOLD"
    else: rating = "UNDERWEIGHT"
    
    recommend = "Expensive" if pe > 40 else "Fair" if pe > 20 else "Cheap"
    
    return {"symbol": symbol, "price": price, "target": t, "upside": upside, "score": score, "rating": rating, "pe": pe, "fpe": fpe, "peg": peg, "dcf_base": dcf["base"], "dcf_bear": dcf["bear"], "dcf_bull": dcf["bull"], "gm": gm * 100, "pm": pm * 100, "roe": roe * 100, "roic": roic * 100, "de": de, "rev_g": rg * 100, "fcf": fcf * 100, "div": div * 100, "beta": beta, "analyst_rating": r, "num_analysts": n, "recommend": recommend, "source": source, "fetched_at": fetched, "expires_at": expires}

def analyze_multiple(symbols):
    return [r for r in (analyze(s) for s in symbols) if r]

def get_top_picks(n=10):
    results = analyze_multiple(list(A.keys()))
    return sorted(results, key=lambda x: x["score"], reverse=True)[:n]

def get_value_picks():
    results = analyze_multiple(list(A.keys()))
    return sorted(results, key=lambda x: x["upside"], reverse=True)[:10]
