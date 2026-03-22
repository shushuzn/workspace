"""Watchlist management for Stock PRO"""
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/OpenClaw/workspace")
WATCHLIST_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_watchlist.json"


class Watchlist:
    def __init__(self):
        self.lists = {}
        self.load()
    
    def load(self):
        """Load watchlists from file"""
        if WATCHLIST_FILE.exists():
            try:
                with open(WATCHLIST_FILE, 'r') as f:
                    self.lists = json.load(f)
            except:
                self.lists = {"default": []}
        else:
            self.lists = {"default": []}
    
    def save(self):
        """Save watchlists to file"""
        with open(WATCHLIST_FILE, 'w') as f:
            json.dump(self.lists, f, indent=2)
    
    def add(self, symbol, list_name="default"):
        """Add symbol to watchlist"""
        if list_name not in self.lists:
            self.lists[list_name] = []
        symbol = symbol.upper()
        if symbol not in self.lists[list_name]:
            self.lists[list_name].append(symbol)
            self.save()
            return f"[Watchlist] Added {symbol} to {list_name}"
        return f"[Watchlist] {symbol} already in {list_name}"
    
    def remove(self, symbol, list_name="default"):
        """Remove symbol from watchlist"""
        if list_name in self.lists and symbol.upper() in self.lists[list_name]:
            self.lists[list_name].remove(symbol.upper())
            self.save()
            return f"[Watchlist] Removed {symbol} from {list_name}"
        return f"[Watchlist] {symbol} not in {list_name}"
    
    def list_lists(self):
        """List all watchlists"""
        if not self.lists:
            return "[Watchlist] No watchlists"
        result = "# Watchlists\n"
        for name, symbols in self.lists.items():
            result += f"\n## {name} ({len(symbols)} stocks)\n"
            if symbols:
                result += ", ".join(symbols)
            else:
                result += "(empty)"
        return result
    
    def get(self, list_name="default"):
        """Get symbols from a watchlist"""
        return self.lists.get(list_name, [])
    
    def create(self, name):
        """Create a new watchlist"""
        if name in self.lists:
            return f"[Watchlist] {name} already exists"
        self.lists[name] = []
        self.save()
        return f"[Watchlist] Created {name}"
    
    def delete(self, name):
        """Delete a watchlist"""
        if name == "default":
            return "[Watchlist] Cannot delete default list"
        if name in self.lists:
            del self.lists[name]
            self.save()
            return f"[Watchlist] Deleted {name}"
        return f"[Watchlist] {name} not found"


# Global instance
_watchlist = Watchlist()


def add_to_watchlist(symbol, list_name="default"):
    """Add symbol to watchlist"""
    return _watchlist.add(symbol, list_name)


def remove_from_watchlist(symbol, list_name="default"):
    """Remove symbol from watchlist"""
    return _watchlist.remove(symbol, list_name)


def get_watchlist(list_name="default"):
    """Get watchlist symbols"""
    return _watchlist.get(list_name)


def list_watchlists():
    """List all watchlists"""
    return _watchlist.list_lists()


def create_watchlist(name):
    """Create a new watchlist"""
    return _watchlist.create(name)


def delete_watchlist(name):
    """Delete a watchlist"""
    return _watchlist.delete(name)
