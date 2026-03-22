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
    return {
        "dcf_base": intrinsic, 
        "dcf_bull": intrinsic * 1.3, 
        "dcf_bear": intrinsic * 0.7,
        "upside": upside
    }

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
    elif score >= 20: rating = "SELL"
    else: rating = "STRONG SELL"
    
    if upside >= 30: recommend = "Strong Buy"
    elif upside >= 15: recommend = "Buy"
    elif upside >= 0: recommend = "Hold"
    else: recommend = "Sell"
    
    rev_g = rg * 100
    analyst_rating = r
    num_analysts = 25
    
    return {
        "symbol": symbol, "price": price, "source": source,
        "fetched_at": fetched, "price_source": source,
        "target": t, "rating": r, "name": n,
        "upside": upside, "score": score, "rating_int": rating,
        "recommend": recommend,
        "pe": pe, "eps": eps, "beta": beta,
        "fpe": fpe, "peg": peg,
        "gm": gm, "pm": pm, "roe": roe, "roic": roic,
        "de": de, "rg": rg, "rev_g": rev_g,
        "fcf": fcf, "div": div,
        "analyst_rating": analyst_rating, "num_analysts": num_analysts,
        "dcf_base": dcf["dcf_base"],
        "dcf_bull": dcf["dcf_bull"],
        "dcf_bear": dcf["dcf_bear"],
        "dcf": dcf, "fetched": fetched
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