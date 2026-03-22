"""Core stock analysis engine - Optimized v12.8"""
import json
import urllib.request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from stock_pro.data_target import A
from stock_pro.data_financial import F
from stock_pro.data_price import P, B, E
from stock_pro.cache import cache

# Cache TTL: 15 minutes
LIVE_CACHE_TTL = 900

def fetch(symbol):
    """Get current price with caching"""
    cache_key = f"price:{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return cached[0], "cached", cached[1], cached[2]
    
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
            now = datetime.now().isoformat()
            cache.set(cache_key, (price, now, now), ttl=LIVE_CACHE_TTL)
            return price, "live", now, now
    except:
        fallback = P.get(symbol, 0), "fallback", datetime.now().isoformat(), datetime.now().isoformat()
        cache.set(cache_key, fallback, ttl=LIVE_CACHE_TTL)
        return fallback

def fetch_batch(symbols):
    """Batch fetch - cache first, then fetch remaining"""
    results = {}
    uncached = []
    
    # Check cache
    for sym in symbols:
        cached = cache.get(f"price:{sym}")
        if cached:
            results[sym] = (cached[0], "cached", cached[1], cached[2])
        else:
            uncached.append(sym)
    
    # Fetch uncached in parallel
    if uncached:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch, s): s for s in uncached}
            for future in as_completed(futures):
                s = futures[future]
                try:
                    results[s] = future.result()
                except:
                    results[s] = (0, "error", datetime.now().isoformat(), datetime.now().isoformat())
    
    return results

def fetch_live(symbols):
    """Get live prices"""
    results = fetch_batch(symbols)
    return [{"symbol": s, "price": results.get(s, (0,))[0]} for s in symbols]

def calc_dcf(symbol, price, wacc=0.09, growth=0.10):
    """Simplified DCF using PE-based valuation"""
    eps = E.get(symbol, 0) or (price / 30)
    _, _, _, _, _, rev_g, fcf_yield, _ = F.get(symbol, (0,0,0,0,0,0,0.05,0))
    
    # Target PE based on growth
    target_pe = 25 + rev_g * 50  # Higher growth = higher PE
    target_pe = min(target_pe, 50)  # Cap at 50x
    
    # Project EPS
    eps_future = eps * ((1 + growth) ** 5)
    
    # Intrinsic = 5yr avg PE * avg EPS
    intrinsic = eps * target_pe * 0.8 + eps_future * target_pe * 0.2
    
    upside = (intrinsic - price) / price * 100 if price > 0 else 0
    
    return {
        "dcf_base": round(intrinsic, 2), 
        "dcf_bull": round(intrinsic * 1.5, 2), 
        "dcf_bear": round(intrinsic * 0.5, 2),
        "upside": round(upside, 1)
    }

def calc_score(symbol, price, data):
    """Calculate composite score (0-100)"""
    t, r, n = data
    upside = (t - price) / price * 100 if price else 0
    gm, pm, roe, roic, de, rg, fcf, div = F.get(symbol, (0,0,0,0,0,0,0,0))
    beta = B.get(symbol, 1.0)
    eps = E.get(symbol, 0)
    
    pe = price / eps if eps > 0 else 100
    
    # Value Score (25%): Lower PE = better, fair PE ~20x
    if pe <= 15: v_score = 90
    elif pe <= 20: v_score = 75
    elif pe <= 25: v_score = 60
    elif pe <= 30: v_score = 45
    elif pe <= 40: v_score = 30
    else: v_score = 15
    
    # Growth Score (25%): Higher revenue growth = better
    if rg >= 0.30: g_score = 90
    elif rg >= 0.20: g_score = 75
    elif rg >= 0.15: g_score = 60
    elif rg >= 0.10: g_score = 45
    elif rg >= 0.05: g_score = 30
    else: g_score = 15
    
    # Profitability Score (25%): ROE + Profit Margin
    prof = (roe * 0.5 + pm * 50)  # ROE already in %, pm in decimal
    if prof >= 40: p_score = 90
    elif prof >= 30: p_score = 75
    elif prof >= 20: p_score = 60
    elif prof >= 10: p_score = 45
    else: p_score = 30
    
    # Balance Sheet Score (15%): Lower debt = better
    if de <= 0.5: b_score = 90
    elif de <= 1.0: b_score = 75
    elif de <= 2.0: b_score = 60
    elif de <= 3.0: b_score = 45
    else: b_score = 30
    
    # Momentum/Beta Score (10%): Lower beta = better
    if beta <= 0.8: m_score = 90
    elif beta <= 1.0: m_score = 75
    elif beta <= 1.2: m_score = 60
    elif beta <= 1.5: m_score = 45
    else: m_score = 30
    
    # Weighted average
    score = v_score * 0.25 + g_score * 0.25 + p_score * 0.25 + b_score * 0.15 + m_score * 0.10
    
    # Analyst adjustment
    if r in ("Outperform", "Buy", "Strong Buy"): score = max(score, 65)
    elif r == "Overweight": score = max(score, 60)
    elif r == "Neutral": score = min(max(score, 45), 55)
    elif r == "Hold": score = min(max(score, 40), 55)
    elif r in ("Underperform", "Sell"): score = min(score, 40)
    
    return int(min(100, max(0, score)))

def calc_risk(symbol, price, data):
    """Calculate risk score (0-100, higher = riskier)"""
    _, _, _, _, de, rg, _, div = F.get(symbol, (0,0,0,0,0,0,0,0))
    beta = B.get(symbol, 1.0)
    eps = E.get(symbol, 0)
    pe = price / eps if eps > 0 else 100
    
    # Risk factors (lower = riskier)
    risks = {}
    
    # Valuation risk: High PE = risky
    if pe >= 50: risks["valuation"] = 30
    elif pe >= 40: risks["valuation"] = 50
    elif pe >= 30: risks["valuation"] = 70
    else: risks["valuation"] = 90
    
    # Debt risk: High debt = risky
    if de >= 3: risks["debt"] = 30
    elif de >= 2: risks["debt"] = 50
    elif de >= 1: risks["debt"] = 70
    else: risks["debt"] = 90
    
    # Volatility risk: High beta = risky
    if beta >= 2.0: risks["volatility"] = 30
    elif beta >= 1.5: risks["volatility"] = 50
    elif beta >= 1.2: risks["volatility"] = 70
    else: risks["volatility"] = 90
    
    # Growth risk: Negative or declining growth
    if rg < 0: risks["growth"] = 30
    elif rg < 0.05: risks["growth"] = 50
    elif rg < 0.10: risks["growth"] = 70
    else: risks["growth"] = 90
    
    risk_score = sum(risks.values()) / len(risks)
    risk_level = "HIGH" if risk_score < 50 else "MEDIUM" if risk_score < 70 else "LOW"
    
    return {"risk_score": round(risk_score, 1), "risk_level": risk_level, "risks": risks}

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
    elif score >= 20: rating = "SELL"
    else: rating = "STRONG SELL"
    
    if upside >= 30: recommend = "Strong Buy"
    elif upside >= 15: recommend = "Buy"
    elif upside >= 0: recommend = "Hold"
    else: recommend = "Sell"
    
    rev_g = rg * 100
    analyst_rating = r
    num_analysts = 25
    risk = calc_risk(symbol, price, A[symbol])
    
    return {
        "symbol": symbol, "price": price, "source": source,
        "fetched_at": fetched, "price_source": source,
        "target": t, "rating": r, "name": n,
        "upside": upside, "score": score, "rating_int": rating,
        "recommend": recommend,
        "pe": pe, "eps": eps, "beta": beta,
        "fpe": fpe, "peg": peg,
        "gm": gm * 100, "pm": pm * 100, "roe": roe * 100, "roic": roic * 100,
        "de": de, "rg": rg * 100, "rev_g": rev_g,
        "fcf": fcf * 100, "div": div * 100,
        "analyst_rating": analyst_rating, "num_analysts": num_analysts,
        "dcf_base": dcf["dcf_base"],
        "dcf_bull": dcf["dcf_bull"],
        "dcf_bear": dcf["dcf_bear"],
        "dcf": dcf, "fetched": fetched,
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
    }

def analyze_multiple(symbols):
    """Analyze multiple symbols"""
    return [analyze(s) for s in symbols]

def analyze_multiple_parallel(symbols, max_workers=10):
    """Parallel analysis - optimized batch fetch"""
    if not symbols:
        return {}
    
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(analyze, s): s for s in symbols}
        for future in as_completed(futures):
            s = futures[future]
            try:
                results[s] = future.result()
            except:
                results[s] = None
    
    return results

# Performance: pre-warm cache with popular stocks
_POPULAR_STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

def prewarm_cache():
    """Pre-warm cache - call manually or after hours"""
    fetch_batch(_POPULAR_STOCKS)
    return len(_POPULAR_STOCKS)