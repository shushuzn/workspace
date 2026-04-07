"""Concrete Policy Agent implementation.

Wraps the existing GRPO/PRM rollout infrastructure.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any

from .interfaces import (
    OrderSide,
    OrderType,
    PolicyAgent,
    RiskAgent,
    TradingSignal,
)
from .memory_store import MemoryNamespace, SharedMemoryStore

logger = logging.getLogger(__name__)


class GRPOPolicyAgent(PolicyAgent):
    """Policy Agent using existing GRPO rollout.

    Reads market data → calls PRM scoring → emits TradingSignal.

    Requires:
    - PRM judge endpoint (existing _build_prm_judge_prompt in openclaw_api_server.py)
    - SharedMemoryStore for signal broadcasting
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-0.5B-Instruct",
        prm_endpoint: str = "http://localhost:30000",
        min_confidence: float = 0.5,
        symbols: list[str] | None = None,
    ) -> None:
        self._running = False
        self._model_name = model_name
        self._prm_endpoint = prm_endpoint
        self._min_confidence = min_confidence
        self._symbols = symbols or ["BTC", "ETH", "SPY", "AAPL"]
        self._last_signal_time: dict[str, float] = {}
        self._signal_cooldown = 30.0  # seconds between signals for same symbol

    def evaluate(self, market_data: dict[str, Any]) -> TradingSignal | None:
        """Evaluate market data and produce a trading signal.

        market_data expected shape:
        {
            "symbol": "BTC",
            "price": 67500.0,
            "volume_24h": 30_000_000_000,
            "momentum": 0.05,       # 24h price change %
            "volatility": 0.02,     # 1std dev / price
            "rsi": 55.0,           # 0-100
            "signal_strength": 0.7,  # from ML model
        }
        """
        symbol = market_data.get("symbol", "BTC")
        price = market_data.get("price", 0.0)
        momentum = market_data.get("momentum", 0.0)
        signal_strength = market_data.get("signal_strength", 0.5)
        rsi = market_data.get("rsi", 50.0)

        if price <= 0:
            return None

        # Cooldown: don't re-signal same symbol within _signal_cooldown seconds
        last = self._last_signal_time.get(symbol, 0)
        if time.time() - last < self._signal_cooldown:
            return None

        # Simple heuristic combining momentum + signal_strength + RSI
        # In production this would call the GRPO model endpoint
        bullish_score = (momentum / 100.0 + signal_strength + (50 - rsi) / 100.0) / 3.0
        bearish_score = 1.0 - bullish_score

        if bullish_score > 0.6:
            action = OrderSide.BUY
            confidence = min(bullish_score, 1.0)
            reason = f"bullish: momentum={momentum:.2f}%, signal={signal_strength:.2f}, RSI={rsi:.1f}"
        elif bearish_score > 0.6:
            action = OrderSide.SELL
            confidence = min(bearish_score, 1.0)
            reason = f"bearish: momentum={momentum:.2f}%, signal={signal_strength:.2f}, RSI={rsi:.1f}"
        else:
            return None

        if confidence < self._min_confidence:
            return None

        return TradingSignal(
            signal_id=f"sig:{uuid.uuid4().hex[:8]}",
            symbol=symbol,
            action=action,
            confidence=confidence,
            reason=reason,
            order_type=OrderType.MARKET,
            metadata={"price": price, "momentum": momentum, "rsi": rsi},
        )

    async def run_loop(self, store: SharedMemoryStore, interval_seconds: float = 5.0) -> None:
        self._running = True
        logger.info("GRPO Policy Agent loop started (interval=%ds)", interval_seconds)

        while self._running:
            try:
                for symbol in self._symbols:
                    market_data = {
                        "symbol": symbol,
                        "price": 100.0,  # placeholder — replace with real data source
                        "momentum": 0.02,
                        "volatility": 0.01,
                        "rsi": 55.0,
                        "signal_strength": 0.65,
                    }

                    signal = self.evaluate(market_data)
                    if signal:
                        store.write_signal(
                            symbol=symbol,
                            action=signal.action.value,
                            confidence=signal.confidence,
                            reason=signal.reason,
                            agent_id=self.role.value,
                        )
                        self._last_signal_time[symbol] = time.time()
                        logger.info("Policy signal emitted: %s %s %.2f", signal.action.value, symbol, signal.confidence)

                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Policy agent loop error: %s", e)
                await asyncio.sleep(interval_seconds)

        logger.info("GRPO Policy Agent loop stopped")

    def stop(self) -> None:
        self._running = False
