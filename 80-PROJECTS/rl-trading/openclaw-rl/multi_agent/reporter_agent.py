"""Concrete Reporter Agent implementation.

Generates daily/weekly reports from shared memory.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any

from .interfaces import ReporterAgent
from .memory_store import MemoryNamespace, SharedMemoryStore

logger = logging.getLogger(__name__)


class DailyReporterAgent(ReporterAgent):
    """Daily reporting agent.

    Generates:
    - Daily P&L report (written to shared memory)
    - Trade summary (last N trades)
    - Risk summary (active alerts)
    """

    def __init__(self, portfolio_value: float = 100_000.0) -> None:
        self._running = False
        self._portfolio_value = portfolio_value
        self._last_report_time = 0.0

    def generate_daily_report(self, store: SharedMemoryStore) -> dict[str, Any]:
        """Build daily P&L and performance digest."""
        positions = store.read_all(MemoryNamespace.POSITIONS)
        alerts = store.get_active_alerts(acknowledged=False)

        total_pnl = 0.0
        position_summaries = []
        for key, pos in positions.items():
            qty = pos.get("qty", 0)
            entry = pos.get("entry_price", 0)
            current = pos.get("current_price", entry)
            pnl = (current - entry) * qty
            pnl_pct = (current - entry) / entry * 100 if entry > 0 else 0.0
            total_pnl += pnl
            position_summaries.append({
                "symbol": pos.get("symbol", key),
                "qty": qty,
                "entry_price": entry,
                "current_price": current,
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2),
            })

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "portfolio_value": self._portfolio_value,
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl / self._portfolio_value * 100, 2) if self._portfolio_value else 0,
            "position_count": len(positions),
            "positions": position_summaries,
            "active_alerts": len(alerts),
            "alert_summary": [
                {"type": a.get("alert_type"), "severity": a.get("severity")}
                for a in alerts
            ],
        }

    def generate_trade_summary(self, store: SharedMemoryStore, limit: int = 50) -> dict[str, Any]:
        """Build recent trade summary from signals."""
        signals = store.scan(MemoryNamespace.SIGNALS)
        recent = sorted(signals, key=lambda e: e.timestamp, reverse=True)[:limit]

        trades = []
        for e in recent:
            v = e.value
            trades.append({
                "signal_id": v.get("signal_id"),
                "symbol": v.get("symbol"),
                "action": v.get("action"),
                "confidence": v.get("confidence"),
                "reason": v.get("reason"),
                "timestamp": datetime.fromtimestamp(e.timestamp).isoformat() + "Z",
            })

        buy_count = sum(1 for t in trades if t["action"] == "buy")
        sell_count = sum(1 for t in trades if t["action"] == "sell")
        hold_count = sum(1 for t in trades if t["action"] == "hold")

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "trade_count": len(trades),
            "buy_count": buy_count,
            "sell_count": sell_count,
            "hold_count": hold_count,
            "recent_trades": trades,
        }

    async def run_loop(self, store: SharedMemoryStore, interval_seconds: float = 3600.0) -> None:
        self._running = True
        logger.info("Reporter Agent loop started (interval=%ds)", interval_seconds)

        while self._running:
            try:
                now = time.time()
                if now - self._last_report_time >= interval_seconds:
                    daily = self.generate_daily_report(store)
                    store.write_report(
                        report_type="daily",
                        content=daily,
                        agent_id=self.role.value,
                    )
                    logger.info("Daily report written: P&L=%.2f (%.2f%%), positions=%d",
                                 daily["total_pnl"], daily["total_pnl_pct"], daily["position_count"])

                    summary = self.generate_trade_summary(store)
                    store.write_report(
                        report_type="trade_summary",
                        content=summary,
                        agent_id=self.role.value,
                    )
                    self._last_report_time = now

                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Reporter agent loop error: %s", e)
                await asyncio.sleep(interval_seconds)

        logger.info("Reporter Agent loop stopped")

    def stop(self) -> None:
        self._running = False
