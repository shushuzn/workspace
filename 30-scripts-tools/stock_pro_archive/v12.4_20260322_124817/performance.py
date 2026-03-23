"""Performance metrics for Stock PRO"""

def calc_returns(results, prices_file=None):
    """Calculate returns from history"""
    from stock_pro.history import _history
    from datetime import datetime, timedelta

    returns = {}
    for sym in set(r["symbol"] for r in results):
        history = _history.get_price_history(sym, days=30)
        if len(history) >= 2:
            first_price = history[0][1]
            last_price = history[-1][1]
            pct_return = (last_price - first_price) / first_price * 100
            returns[sym] = {
                "return": pct_return,
                "first_price": first_price,
                "last_price": last_price,
                "days": len(history)
            }
    return returns


def performance_report(results):
    """Generate performance comparison report"""
    from stock_pro.history import _history

    report = "# Performance Analysis\n\n"
    report += "| Symbol | First Price | Last Price | Return | Days |\n"
    report += "|--------|-------------|------------|--------|------|\n"

    all_returns = []
    for r in results:
        sym = r["symbol"]
        history = _history.get_price_history(sym, days=30)

        if len(history) >= 2:
            first = history[0][1]
            last = history[-1][1]
            ret = (last - first) / first * 100
            all_returns.append((sym, ret, first, last, len(history)))
            arrow = "+" if ret > 0 else ""
            report += f"| {sym} | ${first:.2f} | ${last:.2f} | {arrow}{ret:.1f}% | {len(history)} |\n"
        else:
            report += f"| {sym} | - | ${r['price']:.2f} | - | 0 |\n"

    # Summary
    if all_returns:
        avg_return = sum(r[1] for r in all_returns) / len(all_returns)
        best = max(all_returns, key=lambda x: x[1])
        worst = min(all_returns, key=lambda x: x[1])

        report += f"\n**Average Return:** {avg_return:+.1f}%\n"
        report += f"**Best:** {best[0]} ({best[1]:+.1f}%)\n"
        report += f"**Worst:** {worst[0]} ({worst[1]:+.1f}%)\n"

    return report


def rolling_performance(symbol, days=30, window=7):
    """Calculate rolling performance"""
    from stock_pro.history import _history

    prices = _history.get_price_history(symbol, days)
    if len(prices) < window:
        return []

    returns = []
    for i in range(len(prices) - window):
        old_price = prices[i][1]
        new_price = prices[i + window][1]
        pct_return = (new_price - old_price) / old_price * 100
        returns.append((prices[i + window][0], pct_return))

    return returns


def annualized_return(symbol, days=365):
    """Calculate annualized return"""
    from stock_pro.history import _history

    history = _history.get_price_history(symbol, days)
    if len(history) < 2:
        return None

    first = history[0][1]
    last = history[-1][1]
    num_days = len(history)

    if first == 0 or num_days == 0:
        return None

    total_return = (last - first) / first
    years = num_days / 365
    annualized = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    return annualized * 100


def volatility(symbol, days=30):
    """Calculate volatility (standard deviation of returns)"""
    from stock_pro.history import _history
    import statistics

    prices = _history.get_price_history(symbol, days)
    if len(prices) < 3:
        return None

    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i][1] - prices[i-1][1]) / prices[i-1][1]
        returns.append(ret)

    if returns:
        return statistics.stdev(returns) * 100
    return None


def sharpe_ratio(symbol, risk_free_rate=4.0, days=30):
    """Calculate Sharpe ratio (annualized)"""
    ann_return = annualized_return(symbol, days)
    vol = volatility(symbol, days)

    if ann_return is None or vol is None or vol == 0:
        return None

    return (ann_return - risk_free_rate) / vol


def max_drawdown(symbol, days=30):
    """Calculate maximum drawdown"""
    from stock_pro.history import _history

    prices = _history.get_price_history(symbol, days)
    if len(prices) < 2:
        return None

    price_vals = [p[1] for p in prices]
    peak = price_vals[0]
    max_dd = 0

    for price in price_vals:
        if price > peak:
            peak = price
        dd = (peak - price) / peak * 100
        if dd > max_dd:
            max_dd = dd

    return max_dd


def performance_metrics(symbol):
    """Get comprehensive performance metrics"""
    ann_ret = annualized_return(symbol)
    vol = volatility(symbol)
    sharpe = sharpe_ratio(symbol)
    max_dd = max_drawdown(symbol)

    metrics = {
        "symbol": symbol,
        "annualized_return": ann_ret,
        "volatility": vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_dd
    }

    return metrics


def risk_adjusted_report(results):
    """Generate risk-adjusted performance report"""
    report = "# Risk-Adjusted Performance\n\n"
    report += "| Symbol | Ann. Return | Volatility | Sharpe | Max DD |\n"
    report += "|--------|-------------|------------|--------|--------|\n"

    for r in results:
        sym = r["symbol"]
        metrics = performance_metrics(sym)

        ann_ret = f"{metrics['annualized_return']:.1f}%" if metrics['annualized_return'] else "-"
        vol = f"{metrics['volatility']:.1f}%" if metrics['volatility'] else "-"
        sharpe = f"{metrics['sharpe_ratio']:.2f}" if metrics['sharpe_ratio'] else "-"
        max_dd = f"{metrics['max_drawdown']:.1f}%" if metrics['max_drawdown'] else "-"

        report += f"| {sym} | {ann_ret} | {vol} | {sharpe} | {max_dd} |\n"

    return report
