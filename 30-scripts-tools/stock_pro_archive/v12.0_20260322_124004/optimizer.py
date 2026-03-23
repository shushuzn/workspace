"""Portfolio Optimizer - Modern Portfolio Theory"""
import json
from pathlib import Path
from stock_pro.core import A, P, analyze_multiple

WORKSPACE = Path("D:/OpenClaw/workspace")
HISTORY_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_history.json"


class PortfolioOptimizer:
    def __init__(self):
        self.history = self._load_history()

    def _load_history(self):
        """Load price history"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_returns(self, symbols, days=30):
        """Calculate historical returns"""
        returns = {}
        for sym in symbols:
            if sym in self.history:
                prices = [p[1] for p in self.history.get(sym, [])[-days:]]
                if len(prices) >= 2:
                    ret = (prices[-1] - prices[0]) / prices[0]
                    returns[sym] = ret
        return returns

    def get_volatility(self, symbols, days=30):
        """Calculate volatility (std dev of returns)"""
        volatilities = {}
        for sym in symbols:
            if sym in self.history:
                prices = [p[1] for p in self.history.get(sym, [])[-days:]]
                if len(prices) >= 5:
                    daily_returns = [(prices[i] - prices[i -1]) / prices[i -1] for i in range(1, len(prices))]
                    mean = sum(daily_returns) / len(daily_returns)
                    variance = sum((r - mean) ** 2 for r in daily_returns) / len(daily_returns)
                    volatilities[sym] = (variance ** 0.5) * (252 ** 0.5)  # Annualized
        return volatilities

    def optimize_min_variance(self, symbols, risk_free_rate=0.04):
        """Find minimum variance portfolio"""
        results = analyze_multiple(symbols)

        # Filter by score
        valid = [r for r in results if r["score"] >= 50]

        if not valid:
            return {"error": "Not enough stocks with score >= 50"}

        # Equal weight as simple optimization
        weights = {r["symbol"]: 1 /len(valid) for r in valid}

        # Calculate portfolio metrics
        returns = self.get_returns(symbols, days=30)
        volatilities = self.get_volatility(symbols, days=30)

        port_return = sum(weights[s] * returns.get(s, 0) for s in weights)
        port_vol = sum(weights[s] ** 2 * (volatilities.get(s, 0.3) ** 2) for s in weights) ** 0.5

        sharpe = (port_return - risk_free_rate / 12) / port_vol if port_vol > 0 else 0

        return {
            "type": "Minimum Variance",
            "weights": weights,
            "expected_return": port_return * 100,
            "volatility": port_vol * 100,
            "sharpe_ratio": sharpe,
            "stocks": len(valid)
        }

    def optimize_max_sharpe(self, symbols, risk_free_rate=0.04):
        """Find maximum Sharpe ratio portfolio"""
        results = analyze_multiple(symbols)

        # Filter top 10 by score
        valid = sorted(results, key=lambda x: x["score"], reverse=True)[:10]

        if not valid:
            return {"error": "No valid stocks"}

        # Score-weighted allocation
        total_score = sum(r["score"] for r in valid)
        weights = {r["symbol"]: r["score"] / total_score for r in valid}

        returns = self.get_returns(symbols, days=30)
        volatilities = self.get_volatility(symbols, days=30)

        port_return = sum(weights[s] * returns.get(s, 0.02) for s in weights)
        port_vol = sum(weights[s] ** 2 * (volatilities.get(s, 0.3) ** 2) for s in weights) ** 0.5

        sharpe = (port_return - risk_free_rate / 12) / port_vol if port_vol > 0 else 0

        return {
            "type": "Maximum Sharpe",
            "weights": weights,
            "expected_return": port_return * 100,
            "volatility": port_vol * 100,
            "sharpe_ratio": sharpe,
            "stocks": len(valid)
        }

    def efficient_frontier(self, symbols, points=5):
        """Calculate efficient frontier points"""
        results = analyze_multiple(symbols)
        valid = sorted(results, key=lambda x: x["score"], reverse=True)[:15]

        frontier = []
        volatilities = self.get_volatility(symbols, days=30)
        returns = self.get_returns(symbols, days=30)

        for i in range(points):
            # Create portfolio with varying risk tolerance
            n_stocks = max(3, len(valid) - i * 2)
            top_n = valid[:n_stocks]

            weights = {r["symbol"]: 1 /n_stocks for r in top_n}

            port_return = sum(weights[s] * returns.get(s, 0.02) for s in weights)
            port_vol = sum(weights[s] ** 2 * (volatilities.get(s, 0.3) ** 2) for s in weights) ** 0.5

            frontier.append({
                "volatility": port_vol * 100,
                "return": port_return * 100,
                "stocks": n_stocks
            })

        return frontier


def optimize_report(symbols=None, method="max_sharpe"):
    """Generate optimization report"""
    from stock_pro.core import A
    if symbols is None:
        symbols = list(A.keys())[:15]

    optimizer = PortfolioOptimizer()

    if method == "min_variance":
        result = optimizer.optimize_min_variance(symbols)
    else:
        result = optimizer.optimize_max_sharpe(symbols)

    if "error" in result:
        return f"[Optimizer] {result['error']}"

    report = f"# Portfolio Optimization: {result['type']}\n\n"
    report += f"**Stocks:** {result['stocks']}\n"
    report += f"**Expected Return:** {result['expected_return']:.1f}%\n"
    report += f"**Volatility:** {result['volatility']:.1f}%\n"
    report += f"**Sharpe Ratio:** {result['sharpe_ratio']:.2f}\n\n"

    report += "## Recommended Allocation\n\n"
    report += "| Symbol | Weight | Score |\n"
    report += "|--------|--------|-------|\n"

    for sym, weight in sorted(result["weights"].items(), key=lambda x: x[1], reverse=True):
        data = analyze_multiple([sym])[0]
        report += f"| {sym} | {weight *100:.1f}% | {data['score']} |\n"

    return report
