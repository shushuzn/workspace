#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股票数据抓取器 - 多数据源
"""

import json
import sys
import time
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def get_from_fmp(symbol):
    """Financial Modeling Prep API (免费额度)"""
    print(f"  [FMP] {symbol}...")

    if not HAS_REQUESTS:
        return None

    try:
        # 免费API (需要注册获取key)
        url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}"
        params = {"apikey": "demo"}  # 用demo有额度限制

        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if data:
            d = data[0]
            return {
                "symbol": d.get("symbol"),
                "price": d.get("price"),
                "change": d.get("changesPercentage"),
                "market_cap": d.get("marketCap"),
                "pe": d.get("pe"),
                "high": d.get("yearHigh"),
                "low": d.get("yearLow"),
                "volume": d.get("volume"),
                "source": "fmp"
            }
    except Exception as e:
        print(f"    Error: {e}")

    return None


def get_from_browser(symbol):
    """用浏览器抓取 Yahoo Finance"""
    print(f"  [Browser] {symbol}...")

    if not HAS_PLAYWRIGHT:
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = f"https://finance.yahoo.com/quote/{symbol}"
            page.goto(url, timeout=30000)
            time.sleep(3)

            # 提取数据
            price_elem = page.query_selector('[data-testid="qsp-price"]')
            price = price_elem.inner_text() if price_elem else "0"

            change_elem = page.query_selector('[data-testid="qsp-price-change"]')
            change = change_elem.inner_text() if change_elem else "0"

            data = {
                "symbol": symbol,
                "price": float(price.replace(",", "")) if price.replace(",", "").replace(".", "").isdigit() else 0,
                "change": change,
                "source": "yahoo_browser"
            }

            browser.close()
            return data

    except Exception as e:
        print(f"    Error: {e}")

    return None


def get_from_alpha_vantage(symbol):
    """Alpha Vantage (免费API)"""
    print(f"  [AlphaVantage] {symbol}...")

    if not HAS_REQUESTS:
        return None

    try:
        # 免费key有限制
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": "demo"  # demo key有限制
        }

        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if "Global Quote" in data and data["Global Quote"]:
            q = data["Global Quote"]
            return {
                "symbol": q.get("01. symbol"),
                "price": float(q.get("05. price", 0)),
                "change": float(q.get("10. change percent", "0").replace("%", "")),
                "high": float(q.get("03. high", 0)),
                "low": float(q.get("04. low", 0)),
                "volume": int(q.get("06. volume", 0)),
                "source": "alpha_vantage"
            }
    except Exception as e:
        print(f"    Error: {e}")

    return None


def get_stock_multi_source(symbol):
    """多数据源获取"""
    print(f"\n获取 {symbol} 数据...")

    # 按优先级尝试
    sources = [
        ("FMP", get_from_fmp),
        ("AlphaVantage", get_from_alpha_vantage),
        ("Browser", get_from_browser),
    ]

    for name, func in sources:
        try:
            data = func(symbol)
            if data and data.get("price", 0) > 0:
                print(f"  [OK] 数据来源: {name}")
                return data
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")

    print(f"  [FAIL] 所有数据源都失败")
    return None


def batch_get(symbols):
    """批量获取"""
    print("=" * 60)
    print("多数据源股票获取")
    print("=" * 60)

    results = []

    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}]")
        data = get_stock_multi_source(symbol)

        if data:
            results.append(data)
            print(f"  价格: ${data.get('price', 'N/A')}")
        else:
            print(f"  [FAIL]")

        time.sleep(1)  # 避免限流

    return results


# 测试
if __name__ == "__main__":
    symbols = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL", "GOOGL", "TSLA"]

    results = batch_get(symbols)

    print("\n" + "=" * 60)
    print("结果汇总")
    print("=" * 60)

    for r in results:
        print(f"{r['symbol']}: ${r.get('price', 'N/A')} ({r.get('change', 'N/A')}) [{r.get('source', 'unknown')}]")
