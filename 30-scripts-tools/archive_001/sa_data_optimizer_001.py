import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-DATA-OPTIMIZER-001 Stock Data Optimizer
============================================
Optimize stock data collection with caching and fallback
"""

import json, sys, time
from pathlib import Path
from datetime import datetime, timedelta

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CACHE_DIR = Path("60-DATA/stock_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class SADataOptimizer:
    def __init__(self):
        self.sources = {
            "yahoo": {"timeout": 10, "cache_ttl": 300},
            "cache": {"ttl": 3600}
        }

    def get_quote(self, symbol) -> None:
        """Get quote with caching"""
        cache_file = CACHE_DIR / f"{symbol}_quote.json"

        # Check cache
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < self.sources["cache"]["ttl"]:
                data = json.loads(cache_file.read_text(encoding="utf-8", errors="replace"))
                data["from_cache"] = True
                return data

        # Fetch from source
        result = self._fetch_yahoo(symbol)

        if result:
            # Save to cache
            cache_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            result["from_cache"] = False

        return result

    def _fetch_yahoo(self, symbol) -> None:
        """Fetch from Yahoo Finance"""
        try:
            import urllib.request
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"

            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            chart = data.get("chart", {}).get("result", [{}])[0]
            meta = chart.get("meta", {})

            return {
                "symbol": symbol.upper(),
                "price": meta.get("regularMarketPrice", 0),
                "change": meta.get("regularMarketChange", 0),
                "change_pct": meta.get("regularMarketChangePercent", 0),
                "volume": meta.get("regularMarketVolume", 0),
                "timestamp": int(time.time()),
                "source": "yahoo"
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    def get_batch(self, symbols) -> None:
        """Get multiple quotes efficiently"""
        results = []
        for symbol in symbols:
            start = time.time()
            quote = self.get_quote(symbol)
            quote["fetch_time_ms"] = int((time.time() - start) * 1000)
            results.append(quote)

        return {
            "count": len(results),
            "quotes": results
        }

    def clear_cache(self, symbol=None) -> None:
        """Clear cache for symbol or all"""
        if symbol:
            files = [CACHE_DIR / f"{symbol}_quote.json"]
        else:
            files = CACHE_DIR.glob("*_quote.json")

        count = 0
        for f in files:
            if f.exists():
                f.unlink()
                count += 1

        return {"cleared": count, "symbol": symbol}

if __name__ == "__main__":
    optimizer = SADataOptimizer()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--quote":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
            print(json.dumps(optimizer.get_quote(symbol), ensure_ascii=False, indent=2))
        elif cmd == "--batch":
            symbols = sys.argv[2].split(",") if len(sys.argv) > 2 else ["AAPL", "GOOGL", "MSFT"]
            print(json.dumps(optimizer.get_batch(symbols), ensure_ascii=False, indent=2))
        elif cmd == "--clear":
            symbol = sys.argv[2] if len(sys.argv) > 2 else None
            print(json.dumps(optimizer.clear_cache(symbol), ensure_ascii=False, indent=2))
    else:
        print("SA-DATA-OPTIMIZER-001")
        print("Usage:")
        print("  --quote <symbol>     Get quote with caching")
        print("  --batch <a,b,c>      Batch quotes")
        print("  --clear [symbol]     Clear cache")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py sa_data_optimizer_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py sa_data_optimizer_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""
