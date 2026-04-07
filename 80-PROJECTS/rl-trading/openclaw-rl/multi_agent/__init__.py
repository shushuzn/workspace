"""Multi-Agent Trading Network.

Policy Agent (execution) + Risk Agent (risk control) + Reporter (reporting).
Agents communicate via shared memory (SharedMemoryStore).

Usage:
    from multi_agent import MultiAgentNetwork, get_shared_store

    store = get_shared_store()
    store.write_position("BTC", 0.5, 65000.0, "init")

    network = MultiAgentNetwork(store=store)
    await network.start()
"""

from .interfaces import (
    AgentRole,
    OrderSide,
    OrderType,
    PolicyAgent,
    RiskAgent,
    ReporterAgent,
    Position,
    Order,
    TradingSignal,
    RiskAlert,
    OrderExecutor,
)
from .memory_store import SharedMemoryStore, get_shared_store, MemoryNamespace
from .policy_agent import GRPOPolicyAgent
from .risk_agent import SimpleRiskAgent
from .reporter_agent import DailyReporterAgent
from .network import MultiAgentNetwork

__all__ = [
    # Interfaces
    "AgentRole",
    "OrderSide",
    "OrderType",
    "PolicyAgent",
    "RiskAgent",
    "ReporterAgent",
    "Position",
    "Order",
    "TradingSignal",
    "RiskAlert",
    "OrderExecutor",
    # Memory
    "SharedMemoryStore",
    "get_shared_store",
    "MemoryNamespace",
    # Implementations
    "GRPOPolicyAgent",
    "SimpleRiskAgent",
    "DailyReporterAgent",
    # Network
    "MultiAgentNetwork",
]

