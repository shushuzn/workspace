"""yfinance wrapper for live data"""
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

from .core import P

def get_live_price(symbol):
    """Get live price via yfinance"""
    if not YF_AVAILABLE:
        return None

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        return info.last_price
    except:
        return None

def get_live_data(symbol):
    """Get full live data"""
    if not YF_AVAILABLE:
        return None

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "target": info.get("targetMeanPrice"),
            "pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg": info.get("pegRatio"),
            "roe": info.get("returnOnEquity"),
            "roic": info.get("returnOnAssets"),
            "beta": info.get("beta"),
            "div_yield": info.get("dividendYield"),
            "rev_growth": info.get("revenueGrowth"),
            "fcf_yield": info.get("freeCashflow") / info.get("marketCap") if info.get("marketCap") else None,
            "analyst_count": info.get("numberOfAnalystOpinions"),
            "recommendation": info.get("recommendationKey"),
        }
    except:
        return None

if YF_AVAILABLE:
    __all__ = ['get_live_price', 'get_live_data', 'YF_AVAILABLE']
else:
    __all__ = ['get_live_price', 'get_live_data', 'YF_AVAILABLE']
