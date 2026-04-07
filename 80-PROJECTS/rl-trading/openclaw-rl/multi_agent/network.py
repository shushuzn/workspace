"""Multi-Agent Network Coordinator.

Ties PolicyAgent + RiskAgent + ReporterAgent together via SharedMemoryStore.
Run all three agents in parallel coroutines.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from typing import Any

from .interfaces import OrderType, TradingSignal
from .memory_store import get_shared_store, SharedMemoryStore
from .policy_agent import GRPOPolicyAgent
from .reporter_agent import DailyReporterAgent
from .risk_agent import SimpleRiskAgent

logger = logging.getLogger(__name__)


class MultiAgentNetwork:
    """Coordinates Policy + Risk + Reporter agents.

    Usage:
        network = MultiAgentNetwork()
        await network.start()
        # ... agents run ...
        await network.stop()
    """

    def __init__(
        self,
        policy_agent: GRPOPolicyAgent | None = None,
        risk_agent: SimpleRiskAgent | None = None,
        reporter_agent: DailyReporterAgent | None = None,
        store: SharedMemoryStore | None = None,
    ) -> None:
        self._store = store or get_shared_store()
        self._policy = policy_agent or GRPOPolicyAgent()
        self._risk = risk_agent or SimpleRiskAgent()
        self._reporter = reporter_agent or DailyReporterAgent()
        self._tasks: list[asyncio.Task] = []
        self._running = False

    async def start(self) -> None:
        """Start all three agent loops in parallel."""
        if self._running:
            return
        self._running = True
        logger.info("Starting multi-agent network...")

        self._tasks = [
            asyncio.create_task(self._policy.run_loop(self._store)),
            asyncio.create_task(self._risk.run_loop(self._store)),
            asyncio.create_task(self._reporter.run_loop(self._store)),
        ]
        logger.info("All agents started: policy=%s, risk=%s, reporter=%s",
                     self._policy.role.value, self._risk.role.value, self._reporter.role.value)

    async def stop(self) -> None:
        """Gracefully stop all agents."""
        if not self._running:
            return
        self._running = False
        logger.info("Stopping multi-agent network...")

        self._policy.stop()
        self._risk.stop()
        self._reporter.stop()

        # Cancel all tasks
        for t in self._tasks:
            t.cancel()

        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        logger.info("Multi-agent network stopped")

    def get_store(self) -> SharedMemoryStore:
        return self._store

    async def run_until_shutdown(self) -> None:
        """Run the network until SIGINT/SIGTERM."""
        loop = asyncio.get_running_loop()
        shutdown_event = asyncio.Event()

        def _sig_handler() -> None:
            shutdown_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _sig_handler)
            except NotImplementedError:
                # Windows: use keyboard interrupt instead
                pass

        await self.start()
        try:
            await shutdown_event.wait()
        finally:
            await self.stop()


async def demo() -> None:
    """Quick demo: start network, write some fake market data, print results."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    network = MultiAgentNetwork()
    store = network.get_store()

    # Seed some positions
    store.write_position("BTC", 0.5, 65000.0, "init")
    store.write_position("ETH", 5.0, 3500.0, "init")
    store.write_position("SPY", 10.0, 480.0, "init")

    await network.start()

    # Let agents run for 10 seconds
    await asyncio.sleep(10)

    # Print state
    print("\n=== Shared Memory State ===")
    for ns_key in ["positions", "signals", "alerts", "reports"]:
        from .memory_store import MemoryNamespace
        ns = MemoryNamespace(ns_key)
        entries = store.scan(ns)
        print(f"\n[{ns_key}] ({len(entries)} entries)")
        for e in entries[-3:]:
            print(f"  {e.key}: {e.value}")

    await network.stop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(demo())
    else:
        print("Usage: python -m multi_agent.network demo")
        print("  Starts a 3-agent network with 10s demo run.")
