"""Shared Memory Store for multi-agent coordination."""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryNamespace(str, Enum):
    POSITIONS = "positions"       # Current positions, PnL
    ORDERS = "orders"             # Pending/executed orders
    SIGNALS = "signals"           # Policy signals
    ALERTS = "alerts"            # Risk alerts
    REPORTS = "reports"          # Generated reports


@dataclass
class MemoryEntry:
    key: str
    value: Any
    namespace: MemoryNamespace
    agent_id: str
    timestamp: float = field(default_factory=time.time)
    ttl: float | None = None     # Seconds until expiry, None = never

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() > self.timestamp + self.ttl


class SharedMemoryStore:
    """Thread-safe shared memory for inter-agent communication.

    Usage:
        store = SharedMemoryStore()
        store.write("pos:AAPL", {"qty": 100, "entry": 150.0}, MemoryNamespace.POSITIONS, "policy_agent")
        entry = store.read("pos:AAPL", MemoryNamespace.POSITIONS)
        entries = store.scan(MemoryNamespace.POSITIONS)
        store.write_alert("overexposure", {"symbol": "TSLA", "weight": 0.35}, "risk_agent")
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._store: dict[str, dict[str, MemoryEntry]] = {ns.value: {} for ns in MemoryNamespace}
        self._history: dict[str, list[MemoryEntry]] = {ns.value: [] for ns in MemoryNamespace}
        self._subscribers: dict[str, list[callable]] = {}

    def _full_key(self, key: str, namespace: MemoryNamespace) -> str:
        return f"{namespace.value}:{key}"

    def write(
        self,
        key: str,
        value: Any,
        namespace: MemoryNamespace,
        agent_id: str,
        ttl: float | None = None,
    ) -> MemoryEntry:
        entry = MemoryEntry(key=key, value=value, namespace=namespace, agent_id=agent_id, ttl=ttl)
        with self._lock:
            ns_store = self._store[namespace.value]
            ns_history = self._history[namespace.value]
            # Evict expired before write
            ns_store[key] = entry
            ns_history.append(entry)
            # Keep last 1000 per namespace
            if len(ns_history) > 1000:
                ns_history[:] = ns_history[-1000:]
        self._notify(namespace, entry)
        return entry

    def read(self, key: str, namespace: MemoryNamespace) -> MemoryEntry | None:
        with self._lock:
            entry = self._store[namespace.value].get(key)
            if entry and entry.is_expired():
                del self._store[namespace.value][key]
                return None
            return entry

    def scan(
        self,
        namespace: MemoryNamespace,
        include_expired: bool = False,
    ) -> list[MemoryEntry]:
        with self._lock:
            entries = list(self._store[namespace.value].values())
        if not include_expired:
            entries = [e for e in entries if not e.is_expired()]
        return entries

    def read_all(self, namespace: MemoryNamespace) -> dict[str, Any]:
        entries = self.scan(namespace)
        return {e.key: e.value for e in entries}

    def delete(self, key: str, namespace: MemoryNamespace) -> bool:
        with self._lock:
            if key in self._store[namespace.value]:
                del self._store[namespace.value][key]
                return True
            return False

    def clear_expired(self, namespace: MemoryNamespace | None = None) -> int:
        count = 0
        namespaces = [namespace] if namespace else list(MemoryNamespace)
        with self._lock:
            for ns in namespaces:
                ns_store = self._store[ns.value]
                expired = [k for k, e in ns_store.items() if e.is_expired()]
                for k in expired:
                    del ns_store[k]
                    count += 1
        return count

    def write_position(self, symbol: str, qty: float, entry_price: float, agent_id: str) -> MemoryEntry:
        return self.write(
            f"pos:{symbol}",
            {"symbol": symbol, "qty": qty, "entry_price": entry_price, "updated_at": time.time()},
            MemoryNamespace.POSITIONS,
            agent_id,
        )

    def write_signal(
        self,
        symbol: str,
        action: str,      # "buy" | "sell" | "hold"
        confidence: float,
        reason: str,
        agent_id: str,
    ) -> MemoryEntry:
        signal_id = f"sig:{symbol}:{uuid.uuid4().hex[:8]}"
        return self.write(
            signal_id,
            {"symbol": symbol, "action": action, "confidence": confidence, "reason": reason, "signal_id": signal_id},
            MemoryNamespace.SIGNALS,
            agent_id,
            ttl=60.0,   # Signals expire after 60s
        )

    def write_alert(
        self,
        alert_type: str,   # "overexposure" | "drawdown" | "loss_limit" | "price_spike"
        details: dict[str, Any],
        agent_id: str,
        severity: str = "warning",  # "info" | "warning" | "critical"
    ) -> MemoryEntry:
        alert_id = f"alert:{alert_type}:{uuid.uuid4().hex[:8]}"
        return self.write(
            alert_id,
            {
                "alert_type": alert_type,
                "severity": severity,
                "details": details,
                "alert_id": alert_id,
                "acknowledged": False,
            },
            MemoryNamespace.ALERTS,
            agent_id,
            ttl=None,
        )

    def acknowledge_alert(self, alert_id: str) -> bool:
        entry = self.read(alert_id, MemoryNamespace.ALERTS)
        if not entry:
            return False
        entry.value["acknowledged"] = True
        entry.value["acknowledged_at"] = time.time()
        return True

    def write_report(
        self,
        report_type: str,   # "daily" | "weekly" | "trade_summary"
        content: dict[str, Any],
        agent_id: str,
    ) -> MemoryEntry:
        report_id = f"report:{report_type}:{uuid.uuid4().hex[:8]}"
        return self.write(
            report_id,
            {"report_type": report_type, "content": content, "report_id": report_id},
            MemoryNamespace.REPORTS,
            agent_id,
            ttl=None,
        )

    def subscribe(self, namespace: MemoryNamespace, callback: callable) -> None:
        with self._lock:
            if namespace.value not in self._subscribers:
                self._subscribers[namespace.value] = []
            self._subscribers[namespace.value].append(callback)

    def _notify(self, namespace: MemoryNamespace, entry: MemoryEntry) -> None:
        with self._lock:
            cbs = list(self._subscribers.get(namespace.value, []))

        for cb in cbs:
            try:
                cb(entry)
            except Exception:
                pass  # Don't let subscriber errors break the writer

    def get_positions_summary(self) -> dict[str, dict]:
        """Get a summary of all positions."""
        return {e.key: e.value for e in self.scan(MemoryNamespace.POSITIONS)}

    def get_active_alerts(self, acknowledged: bool | None = None) -> list[dict]:
        """Get active alerts, optionally filtered by acknowledged status."""
        alerts = self.scan(MemoryNamespace.ALERTS)
        result = []
        for e in alerts:
            if acknowledged is None or e.value.get("acknowledged") == acknowledged:
                result.append(e.value)
        return result

    def to_dict(self) -> dict[str, Any]:
        """Serialize current state (for debugging/serialization)."""
        with self._lock:
            return {
                ns.value: {
                    k: {"value": e.value, "agent": e.agent_id, "ts": e.timestamp}
                    for k, e in self._store[ns.value].items()
                    if not e.is_expired()
                }
                for ns in MemoryNamespace
            }


# Global singleton
_store: SharedMemoryStore | None = None
_store_lock = threading.Lock()


def get_shared_store() -> SharedMemoryStore:
    global _store
    with _store_lock:
        if _store is None:
            _store = SharedMemoryStore()
        return _store
