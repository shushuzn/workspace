"""Concrete Risk Agent implementation.

Monitors positions, validates signals, and emits risk alerts.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from .interfaces import (
    PolicyAgent,
    Position,
    RiskAlert,
    RiskAgent,
    TradingSignal,
)
from .memory_store import MemoryNamespace, SharedMemoryStore

logger = logging.getLogger(__name__)


class SimpleRiskAgent(RiskAgent):
    """Rule-based risk agent enforcing position size and drawdown limits.

    Checks every signal against:
    - MAX_POSITION_SIZE (20% per position)
    - MAX_SINGLE_SYMBOL_EXPOSURE (25% total per symbol)
    - MIN_CONFIDENCE (signal must be confident enough)
    - Position count limits
    """

    def __init__(
        self,
        max_position_size: float = 0.20,
        max_total_exposure: float = 1.0,
        max_drawdown_pct: float = 0.10,
        max_single_symbol_exposure: float = 0.25,
        min_confidence: float = 0.60,
        max_positions: int = 10,
    ) -> None:
        self.MAX_POSITION_SIZE = max_position_size
        self.MAX_TOTAL_EXPOSURE = max_total_exposure
        self.MAX_DRAWDOWN_PCT = max_drawdown_pct
        self.MAX_SINGLE_SYMBOL_EXPOSURE = max_single_symbol_exposure
        self.MIN_CONFIDENCE = min_confidence
        self.MAX_POSITIONS = max_positions
        self._running = False
        self._peak_equity = 0.0
        self._current_equity = 0.0

    def check_signal(self, signal: TradingSignal, positions: dict[str, Position]) -> tuple[bool, str | None]:
        """Validate a trading signal against risk rules."""

        # 1. Confidence gate
        if signal.confidence < self.MIN_CONFIDENCE:
            return False, f"confidence {signal.confidence:.2f} < {self.MIN_CONFIDENCE:.2f}"

        # 2. Symbol overexposure
        current_qty = positions.get(signal.symbol, Position(signal.symbol, 0, 0, 0)).qty
        portfolio_value = sum(p.qty * p.current_price for p in positions.values()) or 1.0

        # Estimate order size from signal metadata
        est_order_value = portfolio_value * 0.10  # assume 10% of portfolio
        new_position_value = (current_qty * positions.get(signal.symbol, Position(signal.symbol, 0, 0, 0)).current_price) + est_order_value
        symbol_weight = new_position_value / portfolio_value

        if symbol_weight > self.MAX_SINGLE_SYMBOL_EXPOSURE:
            return False, f"symbol {signal.symbol} weight {symbol_weight:.1%} > {self.MAX_SINGLE_SYMBOL_EXPOSURE:.1%}"

        # 3. Total exposure
        total_exposure = sum(p.qty * p.current_price for p in positions.values()) / portfolio_value
        if total_exposure + (est_order_value / portfolio_value) > self.MAX_TOTAL_EXPOSURE:
            return False, f"total exposure {total_exposure:.1%} would exceed {self.MAX_TOTAL_EXPOSURE:.1%}"

        # 4. Max positions
        if len(positions) >= self.MAX_POSITIONS and signal.symbol not in positions:
            return False, f"max positions {self.MAX_POSITIONS} reached"

        return True, None

    def check_portfolio_risk(self, positions: dict[str, Position]) -> list[RiskAlert]:
        alerts: list[RiskAlert] = []
        portfolio_value = sum(p.qty * p.current_price for p in positions.values()) or 1.0

        # Update peak equity
        if portfolio_value > self._peak_equity:
            self._peak_equity = portfolio_value
        self._current_equity = portfolio_value

        # 1. Drawdown check
        if self._peak_equity > 0:
            drawdown = (self._peak_equity - portfolio_value) / self._peak_equity
            if drawdown > self.MAX_DRAWDOWN_PCT:
                alerts.append(RiskAlert(
                    alert_type="drawdown",
                    severity="critical",
                    symbol=None,
                    details={
                        "current_equity": portfolio_value,
                        "peak_equity": self._peak_equity,
                        "drawdown_pct": drawdown,
                    },
                    recommendation=f"Stop trading — drawdown {drawdown:.1%} exceeds {self.MAX_DRAWDOWN_PCT:.1%}",
                ))

        # 2. Per-symbol overexposure
        for symbol, pos in positions.items():
            if pos.current_price > 0:
                weight = (pos.qty * pos.current_price) / portfolio_value
                if weight > self.MAX_SINGLE_SYMBOL_EXPOSURE:
                    alerts.append(RiskAlert(
                        alert_type="overexposure",
                        severity="warning",
                        symbol=symbol,
                        details={"weight": weight, "qty": pos.qty},
                        recommendation=f"Reduce {symbol} — weight {weight:.1%} > {self.MAX_SINGLE_SYMBOL_EXPOSURE:.1%}",
                    ))

        # 3. Loss limit per position
        for symbol, pos in positions.items():
            if pos.entry_price > 0 and pos.pnl_pct < -0.05:  # -5% loss
                alerts.append(RiskAlert(
                    alert_type="loss_limit",
                    severity="warning",
                    symbol=symbol,
                    details={"pnl": pos.pnl, "pnl_pct": pos.pnl_pct},
                    recommendation=f"Take loss on {symbol} — down {pos.pnl_pct:.1%}",
                ))

        return alerts

    async def run_loop(self, store: SharedMemoryStore, interval_seconds: float = 3.0) -> None:
        self._running = True
        logger.info("Risk Agent loop started (interval=%ds)", interval_seconds)

        while self._running:
            try:
                # Check new signals
                signals = store.scan(MemoryNamespace.SIGNALS)
                positions: dict[str, Position] = {}
                for e in store.scan(MemoryNamespace.POSITIONS):
                    v = e.value
                    positions[v["symbol"]] = Position(
                        symbol=v["symbol"],
                        qty=v["qty"],
                        entry_price=v["entry_price"],
                        current_price=v.get("current_price", v["entry_price"]),
                    )

                for sig_entry in signals:
                    sig = sig_entry.value
                    pos_dict = positions.get(sig["symbol"], Position(sig["symbol"], 0, 0, 0))
                    # Quick check
                    allowed, reason = self.check_signal(
                        TradingSignal(
                            signal_id=sig.get("signal_id", ""),
                            symbol=sig["symbol"],
                            action=sig["action"],
                            confidence=sig.get("confidence", 0),
                            reason=sig.get("reason", ""),
                        ),
                        {sig["symbol"]: pos_dict},
                    )
                    if not allowed:
                        logger.warning("Signal blocked: %s — %s", sig.get("signal_id"), reason)
                        store.write_alert(
                            alert_type="signal_blocked",
                            details={"signal": sig, "reason": reason},
                            agent_id=self.role.value,
                            severity="info",
                        )

                # Portfolio risk scan
                alerts = self.check_portfolio_risk(positions)
                for alert in alerts:
                    store.write_alert(
                        alert_type=alert.alert_type,
                        details={
                            "symbol": alert.symbol,
                            "severity": alert.severity,
                            "details": alert.details,
                            "recommendation": alert.recommendation,
                        },
                        agent_id=self.role.value,
                        severity=alert.severity,
                    )

                # Acknowledge normalized alerts
                for entry in store.scan(MemoryNamespace.ALERTS):
                    if entry.value.get("acknowledged"):
                        continue
                    alert_type = entry.value.get("alert_type")
                    # Simple normalization checks
                    if alert_type == "drawdown":
                        pos_vals = [e.value for e in store.scan(MemoryNamespace.POSITIONS)]
                        total_pnl = sum(p.get("current_price", 0) - p.get("entry_price", 0) for p in pos_vals)
                        if total_pnl > -self._peak_equity * self.MAX_DRAWDOWN_PCT:
                            store.acknowledge_alert(entry.key)
                    elif alert_type == "overexposure":
                        pass  # Requires manual review

                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Risk agent loop error: %s", e)
                await asyncio.sleep(interval_seconds)

        logger.info("Risk Agent loop stopped")

    def stop(self) -> None:
        self._running = False
