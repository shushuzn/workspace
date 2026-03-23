"""Configuration and caching utilities"""
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/OpenClaw/workspace")
CONFIG_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_config.json"

# Cache
_cache = {}
_cache_ttl = 300  # 5 minutes

DEFAULT_CONFIG = {
    "watchlist": ["NVDA", "META", "JPM", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
    "alert_threshold": 30,
    "default_currency": "USD",
    "cache_duration": 300,
    "theme": "dark"
}

def load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    """Save configuration to file"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def get_cached(key, fetch_func, ttl=None):
    """Get cached data or fetch fresh"""
    global _cache
    ttl = ttl or _cache_ttl

    now = time.time()
    if key in _cache:
        data, timestamp = _cache[key]
        if now - timestamp < ttl:
            return data

    data = fetch_func()
    _cache[key] = (data, now)
    return data

def clear_cache():
    """Clear all cache"""
    global _cache
    _cache = {}

# Time import
import time
