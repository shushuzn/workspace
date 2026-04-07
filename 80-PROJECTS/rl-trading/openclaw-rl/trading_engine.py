"""
trading_engine.py — Paper Trading Engine for rl-trading

Connects Alpha Vantage free-tier API to the SLIME RL pipeline.
Returns trading signals in Result schema for PRM reward integration.

Usage:
  python trading_engine.py                    # demo: fetch WTI crude oil price
  python trading_engine.py --symbol CL       # fetch specific commodity
  python trading_engine.py --symbol AAPL --backtest  # run backtest
"""

import argparse
import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Literal

# ─── Result Schema (mirrors shared-types/Result) ────────────────────────────

@dataclass
class Result:
    """
    Unified result schema for rl-trading signals.

    Field layout mirrors shared-types/index.ts Result interface.
    Extended with trading-specific fields: signal, price, symbol.
    """
    success: bool = False
    output: str = ""
    logs: str = ""                       # shared-types field
    artifacts: list = field(default_factory=list)
    error: str | None = None             # shared-types field
    code: str | None = None              # shared-types ErrorCode
    fatal: bool = False
    retryMs: int | None = None           # shared-types field
    attempts: int | None = None         # shared-types field
    cached: bool = False                  # shared-types field
    durationMs: int = 0
    # shared-types causality tracking
    causalityChain: list = field(default_factory=list)
    parentTaskId: str | None = None
    # Arbitrary metadata from the adapter
    metadata: dict = field(default_factory=dict)
    # Trading-specific fields
    signal: Literal["buy", "sell", "hold"] | None = None
    price: float | None = None
    symbol: str | None = None
    timestamp: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

# ─── Alpha Vantage API ───────────────────────────────────────────────────────

ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
FREE_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "demo")

# Commodity/Index mappings (free tier supports these)
COMMODITY_SYMBOLS = {
    "CL": "Crude Oil (WTI)",      # West Texas Intermediate
    "BG": "Brent Crude",           # Europe
    "NG": "Natural Gas",
    "HG": "Copper",
    "ZC": "Corn",
    "ZW": "Wheat",
    "ZS": "Soybeans",
}

STOCK_SYMBOLS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "IBM": "IBM",
    "TSLA": "Tesla",
}

def fetch_quote_alpha_vantage(symbol: str, api_key: str = FREE_KEY) -> Result:
    """Fetch real-time quote from Alpha Vantage (free tier: 25 req/day)."""
    start = time.time()
    url = ALPHA_VANTAGE_BASE
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": api_key,
    }
    try:
        import urllib.request
        req = urllib.request.Request(f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        duration = int((time.time() - start) * 1000)

        # Alpha Vantage "Global Quote" response
        gq = data.get("Global Quote", {})
        if not gq:
            # Try commodity if no stock quote
            params["function"] = "COMMODITY_QUOTE"
            req2 = urllib.request.Request(f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
            with urllib.request.urlopen(req2, timeout=10) as resp2:
                data2 = json.loads(resp2.read().decode())
            commodity = data2.get("data", [{}])[0] if data2.get("data") else {}
            if not commodity:
                return Result(
                    success=False,
                    fatal=False,
                    error=f"No quote data for {symbol}: {data}",
                    durationMs=duration,
                )
            price = float(commodity.get("value", 0))
            return Result(
                success=True,
                output=f"{symbol} = ${price}",
                signal="hold",
                price=price,
                symbol=symbol,
                timestamp=commodity.get("date", ""),
                durationMs=duration,
            )

        price = float(gq.get("05. price", 0) or 0)
        change = float(gq.get("09. change", 0) or 0)
        change_pct = float(gq.get("10. change percent", "0%").replace("%", "") or 0)

        # Simple signal logic: if change > 1% → buy, < -1% → sell, else hold
        if change_pct > 1.0:
            signal = "buy"
        elif change_pct < -1.0:
            signal = "sell"
        else:
            signal = "hold"

        return Result(
            success=True,
            output=f"{symbol} ${price} ({change:+.2f} / {change_pct:+.2f}%)",
            signal=signal,
            price=price,
            symbol=symbol,
            timestamp=gq.get("07. latest trading day", ""),
            durationMs=duration,
            artifacts=[{
                "type": "market_data",
                "change": change,
                "changePercent": change_pct,
                "open": gq.get("02. open", ""),
                "high": gq.get("03. high", ""),
                "low": gq.get("04. low", ""),
                "volume": gq.get("06. volume", ""),
            }],
        )
    except Exception as e:
        return Result(
            success=False,
            fatal=False,
            error=str(e),
            durationMs=int((time.time() - start) * 1000),
        )

# ─── Backtest Module ────────────────────────────────────────────────────────

def backtest(symbol: str, days: int = 30, api_key: str = FREE_KEY) -> Result:
    """
    Fetch historical daily data and compute simple moving average crossover signals.
    Returns Result with backtest artifacts.
    """
    start = time.time()
    url = ALPHA_VANTAGE_BASE
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact" if days <= 100 else "full",
    }
    try:
        import urllib.request
        req = urllib.request.Request(f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        ts = data.get("Time Series (Daily)", {})
        if not ts:
            return Result(success=False, fatal=False, error=f"No historical data: {data}", durationMs=int((time.time()-start)*1000))

        dates = sorted(ts.keys(), reverse=True)[:days]
        closes = [float(ts[d]["4. close"]) for d in dates[::-1]]

        # SMA crossover: SMA_20 vs SMA_50
        sma20 = sum(closes[:20]) / 20 if len(closes) >= 20 else sum(closes[:len(closes)//2]) / (len(closes)//2)
        sma50 = sum(closes[:50]) / 50 if len(closes) >= 50 else sma20
        current_price = closes[0]
        sma20_now = sum(closes[:20]) / 20
        sma50_now = sum(closes[:50]) / 50

        # Signal: price above both SMAs → buy, below → sell
        if sma20_now > sma50_now:
            signal = "buy"
        elif sma20_now < sma50_now:
            signal = "sell"
        else:
            signal = "hold"

        trades = []
        position = 0
        for i in range(1, len(closes)):
            short = sum(closes[max(0, i-20):i]) / min(20, i)
            long = sum(closes[max(0, i-50):i]) / min(50, i)
            prev_short = sum(closes[max(0, i-21):i-1]) / min(20, i-1)
            prev_long = sum(closes[max(0, i-51):i-1]) / min(50, i-1)
            if short > long and prev_short <= prev_long and position == 0:
                trades.append({"date": dates[len(dates)-1-i], "action": "buy", "price": closes[i]})
                position = 1
            elif short < long and prev_short >= prev_long and position == 1:
                trades.append({"date": dates[len(dates)-1-i], "action": "sell", "price": closes[i]})
                position = 0

        pnl = 0.0
        for t in trades:
            if t["action"] == "sell":
                prev = trades[trades.index(t)-1]["price"] if trades.index(t) > 0 else current_price
                pnl += (t["price"] - prev) / prev

        return Result(
            success=True,
            output=f"Backtest {symbol}: {len(trades)} trades, PnL={pnl*100:+.1f}%",
            signal=signal,
            price=current_price,
            symbol=symbol,
            timestamp=dates[0],
            durationMs=int((time.time()-start)*1000),
            artifacts=[{
                "type": "backtest",
                "trades": trades,
                "pnl": pnl,
                "sma20": sma20_now,
                "sma50": sma50_now,
                "days": days,
            }],
        )
    except Exception as e:
        return Result(success=False, fatal=False, error=str(e), durationMs=int((time.time()-start)*1000))

# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Paper Trading Engine for rl-trading")
    parser.add_argument("--symbol", default="CL", help="Symbol (CL/WTI, AAPL, etc.)")
    parser.add_argument("--backtest", action="store_true", help="Run backtest instead of live quote")
    parser.add_argument("--days", type=int, default=30, help="Backtest days")
    parser.add_argument("--api-key", default=FREE_KEY, help="Alpha Vantage API key")
    args = parser.parse_args()

    if args.backtest:
        result = backtest(args.symbol.upper(), args.days, args.api_key)
    else:
        result = fetch_quote_alpha_vantage(args.symbol.upper(), args.api_key)

    print(json.dumps(result.to_dict(), indent=2))

if __name__ == "__main__":
    main()
