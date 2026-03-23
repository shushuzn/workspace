"""Watchlist Manager v2 - Enhanced watchlist with alerts and tracking"""
import json
from pathlib import Path
from datetime import datetime
from stock_pro.core import analyze_multiple

WORKSPACE = Path("D:/OpenClaw/workspace")
WATCHLIST_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_watchlists.json"


class WatchlistManager:
    """Enhanced watchlist manager with tracking"""

    def __init__(self):
        self.watchlists = self._load()

    def _load(self):
        """Load watchlists"""
        if WATCHLIST_FILE.exists():
            try:
                with open(WATCHLIST_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"default": [], "tracked": {}, "performance": {}}

    def _save(self):
        """Save watchlists"""
        with open(WATCHLIST_FILE, 'w') as f:
            json.dump(self.watchlists, f, indent=2)

    def add(self, symbol, list_name="default"):
        """Add symbol to watchlist"""
        symbol = symbol.upper()
        if list_name not in self.watchlists:
            self.watchlists[list_name] = []

        if symbol not in self.watchlists[list_name]:
            self.watchlists[list_name].append(symbol)
            # Track entry
            if symbol not in self.watchlists["tracked"]:
                self.watchlists["tracked"][symbol] = {}
            self.watchlists["tracked"][symbol][list_name] = {
                "added": datetime.now().isoformat(),
                "added_price": None  # Will be filled when analyzed
            }
            self._save()
            return f"[Watchlist] Added {symbol} to {list_name}"
        return f"[Watchlist] {symbol} already in {list_name}"

    def remove(self, symbol, list_name="default"):
        """Remove symbol from watchlist"""
        symbol = symbol.upper()
        if list_name in self.watchlists and symbol in self.watchlists[list_name]:
            self.watchlists[list_name].remove(symbol)
            self._save()
            return f"[Watchlist] Removed {symbol} from {list_name}"
        return f"[Watchlist] {symbol} not in {list_name}"

    def list_all(self):
        """List all watchlists"""
        report = "# Watchlists\n\n"
        for name, symbols in self.watchlists.items():
            if isinstance(symbols, list):
                report += f"## {name} ({len(symbols)} stocks)\n"
                if symbols:
                    report += ", ".join(symbols) + "\n\n"
        return report

    def get_watchlist(self, list_name="default"):
        """Get symbols from watchlist"""
        return self.watchlists.get(list_name, [])

    def update_prices(self, list_name="default"):
        """Update prices for watchlist symbols"""
        symbols = self.get_watchlist(list_name)
        if not symbols:
            return {}

        results = analyze_multiple(symbols)

        for r in results:
            sym = r["symbol"]
            if sym not in self.watchlists["tracked"]:
                self.watchlists["tracked"][sym] = {}
            if list_name not in self.watchlists["tracked"][sym]:
                self.watchlists["tracked"][sym][list_name] = {}

            # Store current price for tracking
            self.watchlists["tracked"][sym][list_name]["current_price"] = r["price"]
            self.watchlists["tracked"][sym][list_name]["current_score"] = r["score"]
            self.watchlists["tracked"][sym][list_name]["last_updated"] = datetime.now().isoformat()

        self._save()
        return {r["symbol"]: r for r in results}

    def performance_report(self, list_name="default"):
        """Generate performance report for watchlist"""
        symbols = self.get_watchlist(list_name)
        if not symbols:
            return f"[Watchlist] {list_name} is empty"

        results = analyze_multiple(symbols)

        report = f"# Watchlist Performance: {list_name}\n\n"
        report += f"**Stocks:** {len(results)}\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "| Symbol | Price | Score | Upside | Action |\n"
        report += "|--------|-------|-------|--------|--------|\n"

        for r in sorted(results, key=lambda x: x["score"], reverse=True):
            # Determine action based on score and upside
            if r["score"] >= 75 and r["upside"] >= 20:
                action = "Strong Buy"
            elif r["score"] >= 60 and r["upside"] >= 10:
                action = "Buy"
            elif r["score"] >= 50:
                action = "Hold"
            else:
                action = "Review"

            report += f"| {r['symbol']} | ${r['price']:.2f} | {r['score']} | {r['upside']:+.1f}% | {action} |\n"

        return report

    def compare_lists(self, list1="default", list2="growth"):
        """Compare two watchlists"""
        symbols1 = self.get_watchlist(list1)
        symbols2 = self.get_watchlist(list2)

        results1 = analyze_multiple(symbols1) if symbols1 else []
        results2 = analyze_multiple(symbols2) if symbols2 else []

        report = f"# Watchlist Comparison: {list1} vs {list2}\n\n"

        avg1 = sum(r["score"] for r in results1) / len(results1) if results1 else 0
        avg2 = sum(r["score"] for r in results2) / len(results2) if results2 else 0

        avg_upside1 = sum(r["upside"] for r in results1) / len(results1) if results1 else 0
        avg_upside2 = sum(r["upside"] for r in results2) / len(results2) if results2 else 0

        report += "| Metric | " + list1 + " | " + list2 + " |\n"
        report += "|--------|-------|-------|\n"
        report += f"| Stocks | {len(results1)} | {len(results2)} |\n"
        report += f"| Avg Score | {avg1:.0f} | {avg2:.0f} |\n"
        report += f"| Avg Upside | {avg_upside1:+.1f}% | {avg_upside2:+.1f}% |\n"

        return report

    def create_from_screener(self, name, criteria):
        """Create watchlist from screener criteria"""
        from stock_pro.screener_v2 import AdvancedScreener

        screener = AdvancedScreener()
        screener.execute()

        if "min_score" in criteria:
            screener.filter_by_score(criteria["min_score"])
        if "min_upside" in criteria:
            screener.filter_by_upside(criteria["min_upside"])
        if "max_pe" in criteria:
            screener.filter_by_pe(criteria["max_pe"])

        results = screener.top(20)
        symbols = [r["symbol"] for r in results]

        self.watchlists[name] = symbols
        self._save()

        return f"[Watchlist] Created '{name}' with {len(symbols)} stocks"


# Global instance
_watchlist = WatchlistManager()


def add_to_watchlist(symbol, list_name="default"):
    """Add symbol to watchlist"""
    return _watchlist.add(symbol, list_name)


def remove_from_watchlist(symbol, list_name="default"):
    """Remove symbol from watchlist"""
    return _watchlist.remove(symbol, list_name)


def get_watchlist(list_name="default"):
    """Get watchlist symbols"""
    return _watchlist.get_watchlist(list_name)


def list_watchlists():
    """List all watchlists"""
    return _watchlist.list_all()


def watchlist_performance(list_name="default"):
    """Get watchlist performance"""
    return _watchlist.performance_report(list_name)


def compare_watchlists(list1="default", list2="growth"):
    """Compare two watchlists"""
    return _watchlist.compare_lists(list1, list2)
