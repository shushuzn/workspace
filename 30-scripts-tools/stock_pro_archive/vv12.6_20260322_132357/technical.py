"""Technical Analysis Module - Chart patterns and indicators"""
import math
from stock_pro.data_price import P


def calc_ma(prices, period):
    """Calculate Moving Average"""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def calc_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None

    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period

    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema

    return ema


def calc_rsi(prices, period=14):
    """Calculate RSI"""
    if len(prices) < period + 1:
        return None

    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calc_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    if len(prices) < slow:
        return None, None, None

    # Calculate EMAs
    ema_fast = calc_ema(prices, fast)
    ema_slow = calc_ema(prices, slow)

    if ema_fast is None or ema_slow is None:
        return None, None, None

    macd_line = ema_fast - ema_slow

    # Signal line (simplified)
    return macd_line, macd_line * 0.9, macd_line * 1.1


def calc_volatility(prices):
    """Calculate volatility (std dev)"""
    if len(prices) < 2:
        return None

    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    return math.sqrt(variance)


def calc_beta_vs_spy(prices, spy_prices):
    """Calculate beta vs SPY"""
    if len(prices) < 30 or len(spy_prices) < 30:
        return None

    # Calculate returns
    stock_returns = [prices[i] / prices[i-1] - 1 for i in range(1, len(prices))]
    spy_returns = [spy_prices[i] / spy_prices[i-1] - 1 for i in range(1, len(spy_prices))]

    min_len = min(len(stock_returns), len(spy_returns))
    stock_returns = stock_returns[-min_len:]
    spy_returns = spy_returns[-min_len:]

    # Calculate covariance and variance
    stock_mean = sum(stock_returns) / len(stock_returns)
    spy_mean = sum(spy_returns) / len(spy_returns)

    covariance = sum((stock_returns[i] - stock_mean) * (spy_returns[i] - spy_mean) for i in range(len(stock_returns))) / len(stock_returns)
    spy_variance = sum((r - spy_mean) ** 2 for r in spy_returns) / len(spy_returns)

    if spy_variance == 0:
        return None

    return covariance / spy_variance


def detect_pattern(prices):
    """Simple pattern detection"""
    if len(prices) < 50:
        return "Insufficient data"

    recent = prices[-20:]
    first = sum(recent[:10]) / 10
    last = sum(recent[-10:]) / 10

    change = (last - first) / first * 100

    if change > 10:
        return f"Uptrend (+{change:.1f}%)"
    elif change < -10:
        return f"Downtrend ({change:.1f}%)"
    else:
        return f"Consolidation ({change:+.1f}%)"


def get_support_resistance(prices, levels=5):
    """Find support and resistance levels"""
    if len(prices) < 30:
        return {"support": [], "resistance": []}

    current = prices[-1]
    high = max(prices[-30:])
    low = min(prices[-30:])

    # Fibonacci levels
    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]

    support = []
    resistance = []

    for fib in fib_levels:
        res = low + (high - low) * fib
        if res < current:
            support.append(res)
        else:
            resistance.append(res)

    return {
        "support": sorted(support)[-levels:] if support else [low],
        "resistance": sorted(resistance)[:levels] if resistance else [high],
        "current": current,
        "low_30d": low,
        "high_30d": high
    }


def technical_summary(symbol):
    """Get technical analysis summary"""
    if symbol not in P:
        return {"error": "Symbol not found"}

    # Mock price data (in real use, fetch from API)
    price = P[symbol]
    prices = [price * (1 + (i % 10 - 5) * 0.01) for i in range(50)]

    ma20 = calc_ma(prices, 20)
    ma50 = calc_ma(prices, 50) if len(prices) >= 50 else None
    ma200 = calc_ma(prices, 200) if len(prices) >= 200 else None
    rsi = calc_rsi(prices)
    macd, signal, histogram = calc_macd(prices)
    volatility = calc_volatility(prices[-30:])
    pattern = detect_pattern(prices)
    sr_levels = get_support_resistance(prices)

    # Signal
    signals = []

    if rsi:
        if rsi > 70:
            signals.append(("RSI", "Overbought", "sell"))
        elif rsi < 30:
            signals.append(("RSI", "Oversold", "buy"))
        else:
            signals.append(("RSI", f"Neutral ({rsi:.0f})", "hold"))

    if ma20 and ma50:
        if ma20 > ma50:
            signals.append(("MA Cross", "Golden Cross", "buy"))
        else:
            signals.append(("MA Cross", "Death Cross", "sell"))

    if macd and macd > 0:
        signals.append(("MACD", "Bullish", "buy"))
    elif macd:
        signals.append(("MACD", "Bearish", "sell"))

    # Overall signal
    buy_signals = sum(1 for _, _, s in signals if s == "buy")
    sell_signals = sum(1 for _, _, s in signals if s == "sell")

    if buy_signals > sell_signals:
        overall = "BUY"
    elif sell_signals > buy_signals:
        overall = "SELL"
    else:
        overall = "HOLD"

    return {
        "symbol": symbol,
        "price": price,
        "ma20": ma20,
        "ma50": ma50,
        "ma200": ma200,
        "rsi": rsi,
        "macd": macd,
        "volatility": volatility,
        "pattern": pattern,
        "support": sr_levels["support"],
        "resistance": sr_levels["resistance"],
        "signals": signals,
        "overall": overall
    }


def technical_report(symbols):
    """Generate technical analysis report"""
    report = "# Technical Analysis Report\n\n"
    report += "| Symbol | Price | RSI | MA20 | Signal | Trend |\n"
    report += "|--------|-------|-----|------|--------|-------|\n"

    for symbol in symbols:
        data = technical_summary(symbol)
        if "error" in data:
            continue

        ma20_str = f"${data['ma20']:.2f}" if data['ma20'] else "N/A"
        rsi_str = f"{data['rsi']:.0f}" if data['rsi'] else "N/A"

        report += f"| {symbol} | ${data['price']:.2f} | {rsi_str} | {ma20_str} | {data['overall']} | {data['pattern']} |\n"

    return report
