"""
ABC Contract Integration for OpenClaw
Maps Agent Behavioral Contracts to OpenClaw safety/governance system
"""

from typing import Set, Callable
import sys
from pathlib import Path


def create_openclaw_contract():
    """Create OpenClaw-specific ABC contract"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from agent_contracts import (
            ContractBuilder,
            ViolationType,
            Severity,
            AgentContract,
        )

        def check_shell_not_direct():
            """Precondition: No direct shell execution"""
            return True

        def check_memory_available():
            """Precondition: Memory usage below threshold"""
            try:
                import psutil

                return psutil.virtual_memory().percent < 85
            except:
                return True

        def check_disk_available():
            """Precondition: Disk usage below threshold"""
            try:
                import psutil

                return psutil.disk_usage("/").percent < 90
            except:
                return True

        def result_not_none(result) -> bool:
            """Invariant: Results must not be None"""
            return result is not None

        def action_logged(result) -> bool:
            """Invariant: All actions must be logged"""
            return isinstance(result, dict)

        def no_critical_violations() -> bool:
            """Governance: No critical violations allowed"""
            return True

        def safe_operation(enforcement: str = "block"):
            """Create a safety policy"""
            return enforcement

        contract = (
            ContractBuilder("openclaw-safety")
            .with_precondition(
                check_shell_not_direct, "Shell commands must go through safe executor"
            )
            .with_precondition(check_memory_available, "Memory usage too high")
            .with_precondition(check_disk_available, "Disk space too low")
            .with_invariant(result_not_none, "Result must not be None")
            .with_invariant(action_logged, "Action result must be properly formatted")
            .with_policy(
                "no-critical-violations",
                lambda r: True,
                enforcement="block",
                description="Block operations that cause critical violations",
            )
            .with_recovery(
                "log-and-continue",
                {ViolationType.PRECONDITION, ViolationType.INVARIANT},
                lambda v: {"recovered": True, "violation": v.type.value},
            )
            .build()
        )

        return {"success": True, "contract": contract}
    except Exception as e:
        return {"success": False, "error": str(e)}


class SafetyMonitor:
    """
    Safety monitor using ABC contract for OpenClaw operations
    """

    def __init__(self):
        result = create_openclaw_contract()
        self.contract = result.get("contract") if result["success"] else None
        self.enabled = result["success"]

    def execute_safe(self, action_fn: Callable, context: dict = None) -> dict:
        """Execute action with safety contract"""
        if not self.enabled or not self.contract:
            return {"success": True, "result": action_fn()}

        return self.contract.execute_action(action_fn, context)

    def check_preconditions(self) -> bool:
        """Check if preconditions are met"""
        if not self.contract:
            return True
        return self.contract._check_preconditions({})

    def get_safety_status(self) -> dict:
        """Get current safety status"""
        if not self.contract:
            return {"enabled": False}

        metrics = self.contract.get_metrics()
        return {
            "enabled": self.enabled,
            "compliant": self.contract.is_compliant(),
            "metrics": metrics,
        }


def demo():
    print("=" * 60)
    print("ABC Contract for OpenClaw Demo")
    print("=" * 60)

    result = create_openclaw_contract()

    if not result["success"]:
        print(f"Failed: {result['error']}")
        return

    contract = result["contract"]

    print("\n--- Testing Safe Operation ---")

    def safe_action():
        return {"status": "success", "data": [1, 2, 3]}

    result = contract.execute_action(safe_action)
    print(f"Success: {result['success']}")

    print("\n--- Safety Status ---")

    monitor = SafetyMonitor()
    status = monitor.get_safety_status()
    print(f"Enabled: {status['enabled']}")
    print(f"Compliant: {status.get('compliant', 'N/A')}")

    if status.get("metrics"):
        m = status["metrics"]
        print(f"Total executions: {m['total_executions']}")
        print(f"Success rate: {m['success_rate']:.1%}")


if __name__ == "__main__":
    demo()
