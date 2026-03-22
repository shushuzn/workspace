#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AAPL 实时分析
使用 yfinance 获取真实数据
"""

import json
import sys
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False
    print("[WARN] yfinance not installed. Using mock data.")


def get_stock_data(symbol):
    """获取股票数据"""
    print(f"[INFO] 获取 {symbol} 数据...")
    
    if not HAS_YF:
        return get_mock_data(symbol)
    
    try:
        stock = yf.Ticker(symbol)
        
        # 实时价格
        info = stock.info
        
        # 最近历史
        hist = stock.history(period="1mo")
        
        # 计算指标
        current_price = info.get('currentPrice', info.get('previousClose', 0))
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0
        
        # MA
        if len(hist) > 20:
            ma20 = hist['Close'].tail(20).mean()
        else:
            ma20 = current_price
            
        if len(hist) > 50:
            ma50 = hist['Close'].tail(50).mean()
        else:
            ma50 = current_price
        
        # RSI (14)
        if len(hist) >= 14:
            delta = hist['Close'].diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
        else:
            rsi = 50
        
        data = {
            "symbol": symbol,
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "prev_close": round(prev_close, 2),
            "open": info.get('open', current_price),
            "high": info.get('dayHigh', current_price),
            "low": info.get('dayLow', current_price),
            "volume": info.get('volume', 0),
            "market_cap": info.get('marketCap', 0),
            "pe": info.get('trailingPE', 0),
            "eps": info.get('trailingEps', 0),
            "dividend_yield": info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            "52w_high": info.get('fiftyTwoWeekHigh', 0),
            "52w_low": info.get('fiftyTwoWeekLow', 0),
            "ma20": round(ma20, 2),
            "ma50": round(ma50, 2),
            "rsi": round(rsi, 2),
            "company": info.get('shortName', symbol),
            "sector": info.get('sector', 'N/A'),
            "recommendation": info.get('recommendationKey', 'N/A'),
            "target_price": info.get('targetMeanPrice', 0),
            "updated_at": datetime.now().isoformat()
        }
        
        print(f"[OK] 价格: ${data['price']} ({data['change_pct']:+.2f}%)")
        return data
        
    except Exception as e:
        print(f"[WARN] {e}")
        return get_mock_data(symbol)


def get_mock_data(symbol):
    """模拟数据"""
    return {
        "symbol": symbol,
        "price": 178.50,
        "change": 2.35,
        "change_pct": 1.33,
        "prev_close": 176.15,
        "open": 176.50,
        "high": 179.20,
        "low": 175.80,
        "volume": 52000000,
        "market_cap": 2800000000000,
        "pe": 28.5,
        "eps": 6.26,
        "dividend_yield": 0.55,
        "52w_high": 199.62,
        "52w_low": 164.08,
        "ma20": 177.30,
        "ma50": 175.80,
        "rsi": 58.5,
        "company": "Apple Inc.",
        "sector": "Technology",
        "recommendation": "buy",
        "target_price": 195.00,
        "updated_at": datetime.now().isoformat()
    }


def analyze(data):
    """分析股票"""
    print(f"\n[2/4] 分析 {data['symbol']}...")
    
    signals = []
    trend = "震荡"
    
    # 趋势判断
    if data['price'] > data['ma20'] > data['ma50']:
        trend = "上涨"
        signals.append("✅ 均线多头排列")
    elif data['price'] < data['ma20'] < data['ma50']:
        trend = "下跌"
        signals.append("⚠️ 均线空头排列")
    
    # RSI 判断
    rsi = data['rsi']
    if rsi > 70:
        signals.append("⚠️ RSI超买")
    elif rsi < 30:
        signals.append("✅ RSI超卖")
    else:
        signals.append("📊 RSI正常")
    
    # 相对位置
    pos = (data['price'] - data['52w_low']) / (data['52w_high'] - data['52w_low']) * 100
    signals.append(f"📍 52周位置: {pos:.1f}%")
    
    # 估值
    pe = data['pe']
    if pe < 20:
        signals.append("💰 市盈率偏低（价值）")
    elif pe > 35:
        signals.append("💎 市盈率偏高（成长）")
    else:
        signals.append("📈 市盈率合理")
    
    result = {
        "trend": trend,
        "signals": signals,
        "score": analyze_score(data)
    }
    
    print(f"[OK] 趋势: {trend}")
    print(f"[OK] 信号: {len(signals)} 条")
    
    return result


def analyze_score(data):
    """综合评分"""
    score = 50  # 基础分
    
    # 趋势加分
    if data['price'] > data['ma20']:
        score += 10
    if data['price'] > data['ma50']:
        score += 10
    
    # RSI 加分
    if 40 < data['rsi'] < 60:
        score += 10
    elif data['rsi'] < 30:
        score += 15
    elif data['rsi'] > 70:
        score -= 10
    
    # 相对位置
    pos = (data['price'] - data['52w_low']) / (data['52w_high'] - data['52w_low']) * 100
    if pos < 30:
        score += 10
    elif pos > 80:
        score -= 10
    
    return max(0, min(100, score))


def recommend(data, analysis):
    """推荐策略"""
    print(f"\n[3/4] 生成策略建议...")
    
    # 自动判断风险偏好
    if analysis['score'] < 40:
        risk_level = "保守"
    elif analysis['score'] > 70:
        risk_level = "激进"
    else:
        risk_level = "稳健"
    
    strategies = {
        "保守": {
            "action": "观望",
            "entry": f"等价格回调至 ${data['ma50']:.2f} 以下入场",
            "stop_loss": f"止损 ${data['price'] * 0.95:.2f} (-5%)",
            "target": f"目标 ${data['target_price']:.2f}",
            "position": "10-20% 仓位",
            "reason": "当前趋势不明，建议轻仓观望"
        },
        "稳健": {
            "action": "分批建仓",
            "entry": f"现价 ${data['price']:.2f} 可入30%，回调入剩余",
            "stop_loss": f"止损 ${data['ma50']:.2f}",
            "target": f"目标 ${data['target_price']:.2f} (+{((data['target_price']/data['price'])-1)*100:.1f}%)",
            "position": "30-50% 仓位",
            "reason": "均线多头，回调是机会"
        },
        "激进": {
            "action": "追涨",
            "entry": f"现价 ${data['price']:.2f} 直接入场",
            "stop_loss": f"止损 ${data['ma20']:.2f}",
            "target": f"目标 ${data['52w_high']:.2f}",
            "position": "50-80% 仓位",
            "reason": "趋势强劲，顺势而为"
        }
    }
    
    strategy = strategies.get(risk_level, strategies["稳健"])
    strategy["risk_level"] = risk_level
    
    print(f"[OK] 推荐策略: {strategy['action']}")
    
    return strategy


def generate_report(symbol, data, analysis, strategy):
    """生成报告"""
    print(f"\n[4/4] 生成报告...")
    
    report = {
        "symbol": symbol,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "company": data['company'],
            "sector": data['sector'],
            "price": f"${data['price']}",
            "change": f"{data['change_pct']:+.2f}%",
            "trend": analysis['trend'],
            "score": analysis['score'],
            "recommendation": strategy['action']
        },
        "data": data,
        "analysis": analysis,
        "strategy": strategy
    }
    
    # 保存
    import os
    report_dir = os.path.dirname(__file__).replace("30-scripts-tools", ".openclaw/stock_analysis/reports")
    os.makedirs(report_dir, exist_ok=True)
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"{report_dir}/{symbol}_{ts}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 报告已保存")
    
    return report


def print_report(report):
    """打印报告"""
    d = report['data']
    a = report['analysis']
    s = report['strategy']
    
    print("\n" + "=" * 60)
    print(f"📊 AAPL 股票分析报告")
    print("=" * 60)
    
    print(f"\n🏢 公司: {d['company']} ({d['sector']})")
    print(f"💰 当前价格: ${d['price']} ({d['change_pct']:+.2f}%)")
    print(f"📈 52周范围: ${d['52w_low']} - ${d['52w_high']}")
    
    print(f"\n📉 技术指标:")
    print(f"   MA20: ${d['ma20']} | MA50: ${d['ma50']}")
    print(f"   RSI(14): {d['rsi']}")
    print(f"   综合评分: {a['score']}/100")
    
    print(f"\n📊 信号:")
    for signal in a['signals']:
        print(f"   {signal}")
    
    print(f"\n🎯 策略建议 ({s['risk_level']}):")
    print(f"   操作: {s['action']}")
    print(f"   入场: {s['entry']}")
    print(f"   止损: {s['stop_loss']}")
    print(f"   目标: {s['target']}")
    print(f"   仓位: {s['position']}")
    print(f"   理由: {s['reason']}")
    
    print("\n" + "=" * 60)


def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    # 1. 获取数据
    data = get_stock_data(symbol)
    
    # 2. 分析
    analysis = analyze(data)
    
    # 3. 推荐策略
    strategy = recommend(data, analysis)
    
    # 4. 生成报告
    report = generate_report(symbol, data, analysis, strategy)
    
    # 打印报告
    print_report(report)


if __name__ == "__main__":
    main()