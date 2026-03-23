#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量股票分析
"""

import json
import sys
import time
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False


# 默认股票池
DEFAULT_STOCKS = [
    "AAPL",   # 苹果
    "MSFT",   # 微软
    "GOOGL",  # 谷歌
    "AMZN",   # 亚马逊
    "TSLA",   # 特斯拉
    "NVDA",   # 英伟达
    "META",   # Meta
    "BRK-B",  # 伯克希尔
]


def get_stock(symbol):
    """获取单只股票"""
    print(f"  {symbol}...", end=" ")

    if not HAS_YF:
        return get_mock(symbol)

    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        price = info.get('currentPrice', info.get('previousClose', 0))
        prev = info.get('previousClose', price)
        change = ((price - prev) / prev * 100) if prev else 0

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "change": round(change, 2),
            "market_cap": info.get('marketCap', 0),
            "pe": info.get('trailingPE', 0),
            "52w_high": info.get('fiftyTwoWeekHigh', 0),
            "52w_low": info.get('fiftyTwoWeekLow', 0),
            "recommendation": info.get('recommendationKey', 'N/A'),
            "company": info.get('shortName', symbol),
            "sector": info.get('sector', 'N/A'),
            "status": "success"
        }
    except Exception as e:
        print(f"Error: {e}")
        return get_mock(symbol)


def get_mock(symbol):
    """模拟数据"""
    import random
    return {
        "symbol": symbol,
        "price": round(random.uniform(50, 500), 2),
        "change": round(random.uniform(-5, 5), 2),
        "market_cap": random.randint(100, 3000) * 1e9,
        "pe": round(random.uniform(10, 50), 1),
        "52w_high": 200,
        "52w_low": 100,
        "recommendation": random.choice(["buy", "hold", "sell"]),
        "company": f"{symbol} Inc.",
        "sector": "Technology",
        "status": "mock"
    }


def analyze(stock):
    """分析股票"""
    # 计算评分
    score = 50

    # 趋势评分
    price = stock['price']
    high = stock['52w_high']
    low = stock['52w_low']
    if high > low:
        pos = (price - low) / (high - low) * 100
        if pos < 30:
            score += 20  # 低位
        elif pos > 70:
            score -= 10  # 高位

    # PE 评分
    pe = stock['pe']
    if 15 < pe < 25:
        score += 10  # 合理估值
    elif pe > 40:
        score -= 10  # 高估值
    elif pe < 15:
        score += 15  # 低估值

    # 涨跌评分
    change = stock['change']
    if change > 2:
        score += 10
    elif change < -2:
        score -= 10

    score = max(0, min(100, score))

    # 信号
    signals = []
    if score >= 70:
        signals.append("🟢 强势")
        recommendation = "买入"
    elif score >= 50:
        signals.append("🟡 中性")
        recommendation = "持有"
    else:
        signals.append("🔴 弱势")
        recommendation = "观望"

    # 52周位置
    pos = (price - low) / (high - low) * 100 if high > low else 50
    signals.append(f"📍 {pos:.0f}%分位")

    return {
        "score": score,
        "signals": signals,
        "recommendation": recommendation
    }


def batch_analyze(symbols=None):
    """批量分析"""
    if symbols is None:
        symbols = DEFAULT_STOCKS

    print("=" * 70)
    print("批量股票分析")
    print("=" * 70)
    print(f"股票数量: {len(symbols)}")
    print()

    results = []

    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{len(symbols)}] {symbol}")

        # 获取数据
        stock = get_stock(symbol)
        time.sleep(0.5)  # 避免请求过快

        if not stock:
            continue

        # 分析
        analysis = analyze(stock)

        # 合并结果
        result = {**stock, **analysis}
        results.append(result)

        # 打印
        change_str = f"{stock['change']:+.2f}%"
        score_str = f"{analysis['score']}"
        rec = analysis['recommendation']

        print(f"  价格: ${stock['price']} ({change_str}) | 评分: {score_str} | {rec}")
        print()

    # 排序
    results.sort(key=lambda x: x['score'], reverse=True)

    return results


def print_summary(results):
    """打印汇总"""
    print("\n" + "=" * 70)
    print("汇总排名")
    print("=" * 70)

    print(f"{'排名':<4} {'代码':<8} {'价格':<10} {'涨跌':<10} {'评分':<6} {'建议':<6}")
    print("-" * 70)

    for i, r in enumerate(results, 1):
        print(f"{i:<4} {r['symbol']:<8} ${r['price']:<9} {r['change']:+.2f}%{'':<4} {r['score']:<6} {r['recommendation']}")

    # 统计
    print("\n" + "-" * 70)
    print("统计:")
    print(f"  总数: {len(results)}")
    print(f"  买入: {sum(1 for r in results if r['recommendation'] == '买入')}")
    print(f"  持有: {sum(1 for r in results if r['recommendation'] == '持有')}")
    print(f"  观望: {sum(1 for r in results if r['recommendation'] == '观望')}")

    avg_score = sum(r['score'] for r in results) / len(results)
    print(f"  平均评分: {avg_score:.1f}")


def save_results(results):
    """保存结果"""
    import os
    save_dir = r"D:\OpenClaw\workspace\.openclaw\stock_analysis\reports"
    os.makedirs(save_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file = f"{save_dir}/batch_{ts}.json"

    with open(file, 'w', encoding='utf-8') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 保存: {file}")
    return file


def main():
    # 解析参数
    symbols = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_STOCKS

    # 批量分析
    results = batch_analyze(symbols)

    # 打印汇总
    print_summary(results)

    # 保存
    save_results(results)


if __name__ == "__main__":
    main()
