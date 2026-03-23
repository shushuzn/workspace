"""Data sync module for Stock PRO"""
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/OpenClaw/workspace")
SYNC_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_sync.json"


class DataSync:
    def __init__(self):
        self.sync_state = self.load()

    def load(self):
        """Load sync state"""
        if SYNC_FILE.exists():
            try:
                with open(SYNC_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_sync": None, "sources": {}, "logs": []}

    def save(self):
        """Save sync state"""
        with open(SYNC_FILE, 'w') as f:
            json.dump(self.sync_state, f, indent=2)

    def sync_yfinance(self, symbols):
        """Sync data from yfinance"""
        try:
            import yfinance as yf

            results = []
            for sym in symbols:
                try:
                    ticker = yf.Ticker(sym)
                    info = ticker.info

                    results.append({
                        "symbol": sym,
                        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                        "pe": info.get("trailingPE"),
                        "forward_pe": info.get("forwardPE"),
                        "market_cap": info.get("marketCap"),
                        "volume": info.get("averageVolume"),
                        "beta": info.get("beta"),
                        "source": "yfinance"
                    })
                except Exception:
                    results.append({"symbol": sym, "error": "Failed to fetch"})

            self.sync_state["last_sync"] = datetime.now().isoformat()
            self.sync_state["sources"]["yfinance"] = {
                "timestamp": datetime.now().isoformat(),
                "symbols": len(results)
            }
            self.sync_state["logs"].append({
                "time": datetime.now().isoformat(),
                "action": "yfinance_sync",
                "symbols": len(symbols)
            })
            self.save()

            return results
        except ImportError:
            return [{"error": "yfinance not installed"}]

    def sync_alpha_vantage(self, symbols, api_key):
        """Sync data from Alpha Vantage"""
        # Placeholder for Alpha Vantage integration
        return [{"error": "Alpha Vantage not implemented"}]

    def get_sync_status(self):
        """Get sync status"""
        report = "# Data Sync Status\n\n"

        last_sync = self.sync_state.get("last_sync")
        if last_sync:
            report += f"**Last Sync:** {last_sync}\n"
        else:
            report += "**Last Sync:** Never\n"

        if self.sync_state.get("sources"):
            report += "\n## Sources\n\n"
            for source, data in self.sync_state["sources"].items():
                report += f"- **{source}:** {data['symbols']} symbols ({data['timestamp']})\n"

        return report


# Global instance
_sync = DataSync()


def sync_yfinance(symbols):
    """Sync data from yfinance"""
    return _sync.sync_yfinance(symbols)


def get_sync_status():
    """Get sync status"""
    return _sync.get_sync_status()


def sync_all(symbols):
    """Sync from all available sources"""
    results = sync_yfinance(symbols)
    return results
