"""OpenViking MCP Metrics Tracker.

Tracks tool call counts and latency for health dashboard.
Injected into server.py request handlers.
"""
import time
from typing import Dict
from collections import defaultdict

class MetricsTracker:
    def __init__(self):
        self._calls: Dict[str, int] = defaultdict(int)
        self._latency: Dict[str, float] = defaultdict(float)
        self._total_calls = 0
        self._start = time.time()

    def record(self, tool_name: str, latency_ms: float):
        self._calls[tool_name] += 1
        self._latency[tool_name] += latency_ms
        self._total_calls += 1

    def get_summary(self) -> dict:
        uptime = time.time() - self._start
        tool_stats = []
        for name in self._calls:
            count = self._calls[name]
            avg_lat = self._latency[name] / count if count > 0 else 0
            tool_stats.append({
                "tool": name,
                "calls": count,
                "avg_latency_ms": round(avg_lat, 2),
                "total_latency_ms": round(self._latency[name], 2),
            })
        tool_stats.sort(key=lambda x: x["calls"], reverse=True)
        return {
            "total_calls": self._total_calls,
            "uptime_seconds": round(uptime, 1),
            "tools": tool_stats,
        }

_tracker = MetricsTracker()

def track(tool_name: str, latency_ms: float):
    _tracker.record(tool_name, latency_ms)

def get_summary() -> dict:
    return _tracker.get_summary()
