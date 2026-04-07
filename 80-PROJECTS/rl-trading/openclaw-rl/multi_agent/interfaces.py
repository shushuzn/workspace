"""Agent role interfaces for multi-agent trading network.

Defines PolicyAgent, RiskAgent, and ReporterAgent contracts.
Each agent runs in its own event loop, communicating via SharedMemoryStore.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    pass  # SharedMemoryStore imported at runtime via memory_store module


class AgentRole(str, Enum):
    POLICY = "policy_agent"
    RISK = "risk_agent"
    REPORTER = "reporter_agent"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


@dataclass
class Position:
    symbol: str
    qty: float
    entry_price: float
    current_price: float = 0.0

    @property
    def pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.qty

    @property
    def pnl_pct(self) -> float:
        if self.entry_price == 0:
            return 0.0
        return (self.current_price - self.entry_price) / self.entry_price * 100


@dataclass
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    qty: float
    price: float | None = None  # None = market order
    status: str = "pending"     # pending | filled | cancelled | rejected
    filled_price: float | None = None
    filled_qty: float | None = None
    reason: str | None = None


@dataclass
class TradingSignal:
    signal_id: str
    symbol: str
    action: OrderSide
    confidence: float      # 0.0 - 1.0
    reason: str
    order_type: OrderType = OrderType.MARKET
    limit_price: float | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class RiskAlert:
    alert_type: str       # overexposure | drawdown | loss_limit | price_spike | position_limit
    severity: str         # info | warning | critical
    symbol: str | None
    details: dict[str, Any]
    recommendation: str | None = None


class PolicyAgent(ABC):
    """Policy Agent — executes trades based on model predictions.

    Responsibilities:
    - Evaluate market state and generate trading signals
    - Submit orders via the order executor
    - Read position state from shared memory
    - Write signals to shared memory for Risk Agent to review
    """

    role: AgentRole = AgentRole.POLICY

    @abstractmethod
    def evaluate(self, market_data: dict[str, Any]) -> TradingSignal | None:
        """Evaluate market data and produce a trading signal. Returns None if no action."""

    @abstractmethod
    async def run_loop(self, store: SharedMemoryStore, interval_seconds: float = 5.0) -> None:
        """Main evaluation loop. Runs until stop() is called."""

    @abstractmethod
    def stop(self) -> None:
        """Signal the run loop to stop."""


class RiskAgent(ABC):
    """Risk Agent — enforces position limits, drawdown caps, and exposure rules.

    Responsibilities:
    - Monitor all positions and orders in shared memory
    - Reject or modify signals that breach risk rules
    - Emit alerts when risk thresholds are breached
    - Acknowledge alerts when conditions normalize
    """

    role: AgentRole = AgentRole.RISK

    # Risk thresholds (override in subclass or configure)
    MAX_POSITION_SIZE: float = 0.20          # Max 20% of portfolio per position
    MAX_TOTAL_EXPOSURE: float = 1.0          # Max 100% portfolio long/short
    MAX_DRAWDOWN_PCT: float = 0.10          # Max 10% drawdown from peak
    MAX_SINGLE_SYMBOL_EXPOSURE: float = 0.25 # Max 25% in single symbol
    MIN_CONFIDENCE: float = 0.60             # Min signal confidence to execute

    @abstractmethod
    def check_signal(self, signal: TradingSignal, positions: dict[str, Position]) -> tuple[bool, str | None]:
        """Check if signal passes risk rules. Returns (allowed, reject_reason)."""

    @abstractmethod
    def check_portfolio_risk(self, positions: dict[str, Position]) -> list[RiskAlert]:
        """Scan all positions and return active risk alerts."""

    @abstractmethod
    async def run_loop(self, store: SharedMemoryStore, interval_seconds: float = 3.0) -> None:
        """Main risk monitoring loop."""

    @abstractmethod
    def stop(self) -> None:
        """Signal the run loop to stop."""


class ReporterAgent(ABC):
    """Reporter Agent — generates daily/weekly trading reports.

    Responsibilities:
    - Collect trade history from shared memory
    - Compute performance metrics (P&L, Sharpe, max drawdown)
    - Write formatted reports to shared memory
    - Optionally push to external endpoints (Discord, webhook, etc.)
    """

    role: AgentRole = AgentRole.REPORTER

    @abstractmethod
    def generate_daily_report(self, store: SharedMemoryStore) -> dict[str, Any]:
        """Generate daily P&L and performance summary."""

    @abstractmethod
    def generate_trade_summary(self, store: SharedMemoryStore, limit: int = 50) -> dict[str, Any]:
        """Generate recent trade summary."""

    @abstractmethod
    async def run_loop(self, store: SharedMemoryStore, interval_seconds: float = 3600.0) -> None:
        """Main reporting loop. Default fires every hour."""

    @abstractmethod
    def stop(self) -> None:
        """Signal the run loop to stop."""


class OrderExecutor(Protocol):
    """Protocol for executing orders. Implement this to connect to a broker."""

    async def submit(self, order: Order) -> Order:
        """Submit an order. Returns updated Order with filled status."""

    async def cancel(self, order_id: str) -> bool:
        """Cancel an outstanding order."""

    def get_order(self, order_id: str) -> Order | None:
        """Get current state of an order."""
