#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AAPL 完整分析报告"""

import json
from datetime import datetime
import os

# AAPL 真实数据
AAPL_DATA = {
    "symbol": "AAPL",
    "price": 247.99,
    "change": -0.39,
    "open": 248.96,
    "high": 249.20,
    "low": 246.00,
    "volume": 87981315,
    "market_cap": "3.645T",
    "pe": 31.35,
    "eps": 7.91,
    "dividend": 1.04,
    "dividend_yield": 0.42,
    "52w_high": 288.62,
    "52w_low": 169.21,
    "analyst_rating": "Outperform",
    "analyst_target": 295.44,
    "ytd": -8.69,
    "sector": "Technology",
    "company": "Apple Inc."
}

SAVE_DIR = r"D:\OpenClaw\workspace\.openclaw\stock_analysis\reports"


def analyze():
    data = AAPL_DATA
    pos = (data['price'] - data['52w_low']) / (data['52w_high'] - data['52w_low']) * 100
    upside = (data['analyst_target'] - data['price']) / data['price'] * 100

    score = 50
    if pos < 40:
        score += 20
    elif pos > 70:
        score -= 10
    else:
        score += 10

    if data['pe'] < 30:
        score += 15
    elif data['pe'] > 40:
        score -= 10

    if upside > 15:
        score += 10
    if data['ytd'] < -5:
        score += 10

    score = min(100, max(0, score))

    signals = []
    if pos < 30:
        signals.append(("[+]", "价格低位"))
    elif pos > 70:
        signals.append(("[-]", "价格高位"))
    else:
        signals.append(("[=]", "价格中部"))

    if upside > 15:
        signals.append(("[^]", f"上涨{upside:.0f}%"))
    if data['pe'] < 30:
        signals.append(("[$]", "估值低"))

    return {"score": score, "position": pos, "upside": upside, "signals": signals}


def recommend(analysis):
    s = analysis['score']
    if s >= 70:
        return {"level": "激进", "action": "买入", "position": "50-80%", "entry": f"${AAPL_DATA['price']}", "stop": f"${AAPL_DATA['52w_low']}", "target": f"${AAPL_DATA['analyst_target']}"}
    elif s >= 50:
        return {"level": "稳健", "action": "分批买入", "position": "30-50%", "entry": "分批入场", "stop": f"${AAPL_DATA['52w_low']}", "target": f"${AAPL_DATA['analyst_target'] * 0.95:.2f}"}
    else:
        return {"level": "保守", "action": "观望", "position": "10-20%", "entry": "等回调", "stop": f"${AAPL_DATA['52w_low']}", "target": f"${AAPL_DATA['analyst_target'] * 0.9:.2f}"}


def main():
    analysis = analyze()
    strategy = recommend(analysis)

    report = {
        "generated_at": datetime.now().isoformat(),
        "data": AAPL_DATA,
        "analysis": analysis,
        "strategy": strategy
    }

    # 保存
    os.makedirs(SAVE_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"{SAVE_DIR}/AAPL_{ts}.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 打印
    print("=" * 60)
    print("AAPL 分析报告")
    print("=" * 60)
    print(f"价格: ${AAPL_DATA['price']} ({AAPL_DATA['change']:+.2f}%)")
    print(f"52周范围: ${AAPL_DATA['52w_low']} - ${AAPL_DATA['52w_high']}")
    print(f"52周位置: {analysis['position']:.0f}%")
    print(f"目标价: ${AAPL_DATA['analyst_target']} (上涨{analysis['upside']:.0f}%)")
    print(f"PE: {AAPL_DATA['pe']}")
    print("-" * 60)
    print(f"综合评分: {analysis['score']}/100")
    for emoji, text in analysis['signals']:
        print(f"  {emoji} {text}")
    print("-" * 60)
    print(f"策略: {strategy['level']} - {strategy['action']}")
    print(f"仓位: {strategy['position']}")
    print(f"入场: {strategy['entry']}")
    print(f"止损: {strategy['stop']}")
    print(f"目标: {strategy['target']}")
    print("=" * 60)
    print(f"报告已保存")


if __name__ == "__main__":
    main()
