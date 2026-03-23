"""Portfolio management"""
import json
from pathlib import Path

WORKSPACE = Path("D:/OpenClaw/workspace")
PORTFOLIO_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_portfolio.json"
from .core import fetch, fetch_live

class PortfolioManager:
    def __init__(self):
        self.positions = {}
        self.load()

    def load(self):
        if PORTFOLIO_FILE.exists():
            try:
                with open(PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                    self.positions = json.load(f)
            except:
                self.positions = {}

    def save(self):
        PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, indent=2)

    def add(self, symbol, shares, avg_cost):
        sym = symbol.upper()
        self.positions[sym] = {"shares": shares, "avg_cost": avg_cost}
        self.save()
        return f"[Portfolio] Added {shares} shares of {sym} @ ${avg_cost:.2f}"

    def remove(self, symbol):
        sym = symbol.upper()
        if sym in self.positions:
            del self.positions[sym]
            self.save()
            return f"[Portfolio] Removed {sym}"
        return f"[Portfolio] {sym} not found"

    def show(self, use_live=False):
        if not self.positions:
            return "[Portfolio] Empty. Add positions with: --portfolio-add NVDA 100 150"

        lines = ["=" * 80, "Stock PRO Portfolio", "=" * 80, "",
                 f"{'Symbol':<10} {'Shares':>10} {'Avg Cost':>12} {'Current':>12} {'Value':>14} {'Gain/Loss':>16}", "-" * 80]

        total_value = 0
        total_cost = 0

        for sym, pos in self.positions.items():
            shares = pos["shares"]
            avg_cost = pos["avg_cost"]
            price, _, _, _ = fetch(sym)
            if use_live:
                p = fetch_live(sym)
                if p > 0: price = p

            value = shares * price
            cost = shares * avg_cost
            gain = value - cost
            gain_pct = (gain / cost * 100) if cost > 0 else 0
            total_value += value
            total_cost += cost
            sign = "+" if gain >= 0 else ""
            lines.append(f"{sym:<10} {shares:>10.1f} ${avg_cost:>10.2f} ${price:>10.2f} ${value:>12,.2f} {sign}${gain:,.2f} ({gain_pct:+.1f}%)")

        lines.append("-" * 80)
        total_gain = total_value - total_cost
        total_gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0
        sign = "+" if total_gain >= 0 else ""
        lines.append(f"{'TOTAL':<10} {'':<10} ${total_cost:>10,.2f} {'':<12} ${total_value:>12,.2f} {sign}${total_gain:,.2f} ({total_gain_pct:+.1f}%)")
        lines.append("=" * 80)
        return "\n".join(lines)
