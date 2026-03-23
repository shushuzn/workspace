"""Cache system for Stock PRO v12.5 - Optimized"""
import json, time, threading
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/OpenClaw/workspace")
CACHE_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_cache.json"

DEFAULT_TTL = 900  # 15 minutes (optimized)

class Cache:
    def __init__(self, ttl=DEFAULT_TTL):
        self.ttl = ttl
        self._memory = {}
        self._lock = threading.Lock()
        self._pending_save = False
        self._save_timer = None
        self.load()

    def load(self):
        """Load cache from file"""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    self._memory = json.load(f)
            except:
                self._memory = {}

    def _schedule_save(self):
        """Schedule delayed save (batch writes)"""
        if not self._pending_save:
            self._pending_save = True
            threading.Timer(0.5, self._delayed_save).start()

    def _delayed_save(self):
        """Delayed save to reduce disk I/O"""
        with self._lock:
            try:
                with open(CACHE_FILE, 'w') as f:
                    json.dump(self._memory, f, indent=2)
            except:
                pass
            finally:
                self._pending_save = False

    def save(self):
        """Force immediate save"""
        with self._lock:
            with open(CACHE_FILE, 'w') as f:
                json.dump(self._memory, f, indent=2)

    def get(self, key, default=None):
        """Get cached value"""
        with self._lock:
            if key in self._memory:
                data, timestamp, ttl = self._memory[key]
                if time.time() - timestamp < ttl:
                    return data
                del self._memory[key]
            return default

    def set(self, key, value, ttl=None):
        """Set cache value with optional custom TTL"""
        if ttl is None:
            ttl = self.ttl
        with self._lock:
            self._memory[key] = (value, time.time(), ttl)
            self._schedule_save()

    def set_many(self, items, ttl=None):
        """Batch set multiple values (optimized)"""
        if ttl is None:
            ttl = self.ttl
        with self._lock:
            now = time.time()
            for key, value in items:
                self._memory[key] = (value, now, ttl)
            self._schedule_save()

    def delete(self, key):
        """Delete cache entry"""
        with self._lock:
            if key in self._memory:
                del self._memory[key]
                self._schedule_save()

    def clear(self):
        """Clear all cache"""
        with self._lock:
            self._memory = {}
            self.save()
        return "[Cache] Cleared"

    def stats(self):
        """Get cache statistics"""
        with self._lock:
            now = time.time()
            valid = sum(1 for _, ts, ttl in self._memory.values() if now - ts < ttl)
            expired = len(self._memory) - valid
            return {"valid": valid, "expired": expired, "total": len(self._memory)}

    def cleanup(self):
        """Remove expired entries"""
        with self._lock:
            before = len(self._memory)
            now = time.time()
            self._memory = {k: v for k, v in self._memory.items()
                          if now - v[1] < v[2]}
            removed = before - len(self._memory)
            if removed > 0:
                self._schedule_save()
        return f"[Cache] Removed {removed} expired entries"


# Global cache instance
cache = Cache()


def get_cached(key, fetch_func, ttl=None):
    """Get from cache or fetch"""
    data = cache.get(key)
    if data is not None:
        return data, True
    data = fetch_func()
    cache.set(key, data, ttl)
    return data, False


def clear_cache():
    """Clear all cache"""
    return cache.clear()


def cache_stats():
    """Get cache stats"""
    stats = cache.stats()
    return f"[Cache] {stats['valid']} valid, {stats['expired']} expired, {stats['total']} total"
