"""Backtesting Module - Historical strategy testing"""
import random


def mock_historical_data(symbol, days=365):
    """Generate mock historical data"""
    from stock_pro.data_price import P

    current = P.get(symbol, 100)
    data = []
    price = current * 0.7  # Start lower

    for i in range(days):
        daily_return = random.gauss(0.0005, 0.02)
        price *= (1 + daily_return)
        data.append(price)

    return data


def backtest_moving_average(symbol, fast_ma=50, slow_ma=200, days=365):
    """Backtest moving average crossover strategy"""
    prices = mock_historical_data(symbol, days)

    trades = []
    position = None
    capital = 10000
    shares = 0

    for i in range(slow_ma, len(prices)):
        ma_fast = sum(prices[i -fast_ma:i]) / fast_ma
        ma_slow = sum(prices[i -slow_ma:i]) / slow_ma
        ma_fast_prev = sum(prices[i -fast_ma -1:i -1]) / fast_ma
        ma_slow_prev = sum(prices[i -slow_ma -1:i -1]) / slow_ma

        # Golden cross
        if ma_fast_prev < ma_slow_prev and ma_fast > ma_slow and position is None:
            shares = capital / prices[i]
            position = prices[i]
            trades.append(("BUY", prices[i], capital))
            capital = 0

        # Death cross
        elif ma_fast_prev > ma_slow_prev and ma_fast < ma_slow and position is not None:
            capital = shares * prices[i]
            trades.append(("SELL", prices[i], capital))
            shares = 0
            position = None

    # Close position if still open
    if position is not None:
        capital = shares * prices[-1]
        trades.append(("CLOSE", prices[-1], capital))

    if len(trades) < 2:
        return {"symbol": symbol, "trades": 0, "return": 0, "message": "No trades generated"}

    total_return = (capital - 10000) / 10000 * 100

    return {
        "symbol": symbol,
        "strategy": f"MA {fast_ma}/{slow_ma}",
        "initial": 10000,
        "final": capital,
        "return": total_return,
        "trades": len(trades),
        "win_rate": 50  # Simplified
    }


def backtest_rsi_strategy(symbol, oversold=30, overbought=70, days=365):
    """Backtest RSI mean reversion strategy"""
    prices = mock_historical_data(symbol, days)

    trades = []
    capital = 10000
    shares = 0
    position = None

    for i in range(20, len(prices)):
        recent = prices[i -14:i]
        gains = [recent[j] - recent[j -1] for j in range(1, len(recent)) if recent[j] > recent[j -1]]
        losses = [recent[j -1] - recent[j] for j in range(1, len(recent)) if recent[j] < recent[j -1]]

        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0.001

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Buy when oversold
        if rsi < oversold and position is None:
            shares = capital / prices[i]
            position = prices[i]
            trades.append(("BUY", prices[i], capital))
            capital = 0

        # Sell when overbought
        elif rsi > overbought and position is not None:
            capital = shares * prices[i]
            trades.append(("SELL", prices[i], capital))
            shares = 0
            position = None

    if position is not None:
        capital = shares * prices[-1]
        trades.append(("CLOSE", prices[-1], capital))

    if len(trades) < 2:
        return {"symbol": symbol, "trades": 0, "return": 0, "message": "No trades generated"}

    total_return = (capital - 10000) / 10000 * 100
    wins = sum(1 for i in range(1, len(trades), 2) if trades[i][2] > trades[i -1][2])

    return {
        "symbol": symbol,
        "strategy": f"RSI {oversold}/{overbought}",
        "initial": 10000,
        "final": capital,
        "return": total_return,
        "trades": len(trades) // 2,
        "win_rate": wins / (len(trades) // 2) * 100 if trades else 0
    }


def backtest_all(symbols, strategies=None):
    """Run all backtests"""
    if strategies is None:
        strategies = ["ma_cross", "rsi"]

    results = []

    for symbol in symbols:
        if "ma_cross" in strategies:
            result = backtest_moving_average(symbol)
            result["type"] = "MA Cross"
            results.append(result)

        if "rsi" in strategies:
            result = backtest_rsi_strategy(symbol)
            result["type"] = "RSI"
            results.append(result)

    return results


def backtest_report(symbols):
    """Generate backtest report"""
    results = backtest_all(symbols)

    if not results:
        return "[ERROR] No backtest results"

    report = "# Backtest Report\n\n"
    report += "| Symbol | Strategy | Return | Trades | Win Rate |\n"
    report += "|--------|----------|--------|--------|----------|\n"

    for r in sorted(results, key=lambda x: x['return'], reverse=True):
        report += f"| {r['symbol']} | {r['type']} | {r['return']:+.1f}% | {r.get('trades', 0)} | {r.get('win_rate', 0):.0f}% |\n"

    # Best performers
    report += "\n## Best Performers\n\n"
    best = sorted(results, key=lambda x: x['return'], reverse=True)[:3]
    for i, r in enumerate(best, 1):
        report += f"{i}. **{r['symbol']}** ({r['type']}): {r['return']:+.1f}%\n"

    return report
