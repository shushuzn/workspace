"""History tracking for Stock PRO"""
import json
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("D:/OpenClaw/workspace")
HISTORY_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_history.json"

MAX_HISTORY = 1000  # Keep last 1000 records

class History:
    def __init__(self):
        self.records = []
        self.load()
    
    def load(self):
        """Load history from file"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    self.records = json.load(f)
            except:
                self.records = []
    
    def save(self):
        """Save history to file"""
        # Keep only last MAX_HISTORY records
        if len(self.records) > MAX_HISTORY:
            self.records = self.records[-MAX_HISTORY:]
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.records, f, indent=2)
    
    def add(self, symbol, data):
        """Add a record"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "price": data.get("price"),
            "score": data.get("score"),
            "rating": data.get("rating"),
            "upside": data.get("upside"),
        }
        self.records.append(record)
        self.save()
    
    def get_symbol_history(self, symbol, days=30):
        """Get history for a symbol"""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        return [r for r in self.records 
                if r["symbol"] == symbol and r["timestamp"] >= cutoff_str]
    
    def get_price_history(self, symbol, days=30):
        """Get price history for charting"""
        history = self.get_symbol_history(symbol, days)
        return [(r["timestamp"], r["price"]) for r in history]
    
    def get_score_history(self, symbol, days=30):
        """Get score history for charting"""
        history = self.get_symbol_history(symbol, days)
        return [(r["timestamp"], r["score"]) for r in history]
    
    def get_trends(self, days=7):
        """Get trending stocks"""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        # Group by symbol
        trends = {}
        for r in self.records:
            if r["timestamp"] >= cutoff_str:
                sym = r["symbol"]
                if sym not in trends:
                    trends[sym] = []
                trends[sym].append(r)
        
        # Calculate changes
        result = []
        for sym, records in trends.items():
            if len(records) >= 2:
                first = records[0]["price"]
                last = records[-1]["price"]
                change = (last - first) / first * 100 if first > 0 else 0
                result.append({
                    "symbol": sym,
                    "price_start": first,
                    "price_end": last,
                    "change_pct": change,
                    "records": len(records)
                })
        
        # Sort by change
        result.sort(key=lambda x: x["change_pct"], reverse=True)
        return result
    
    def stats(self):
        """Get history statistics"""
        return f"[History] {len(self.records)} records, {len(set(r['symbol'] for r in self.records))} symbols"
    
    def clear(self):
        """Clear history"""
        self.records = []
        self.save()
        return "[History] Cleared"


# Global history instance
_history = History()


def track(symbol, data):
    """Track a stock analysis"""
    _history.add(symbol, data)


def get_history(symbol, days=30):
    """Get history for symbol (use '*' for all symbols)"""
    if symbol == "*":
        return _history.records[-100:]  # Last 100 records
    return _history.get_symbol_history(symbol, days)


def get_trends(days=7):
    """Get trending stocks"""
    return _history.get_trends(days)


def history_stats():
    """Get history stats"""
    return _history.stats()
