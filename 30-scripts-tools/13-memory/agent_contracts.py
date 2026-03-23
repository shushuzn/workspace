"""
Agent Behavioral Contracts (ABC) Implementation
Based on arXiv:2602.22302

Formal framework bringing Design-by-Contract principles to autonomous AI agents.
Contract C = (P, I, G, R):
- P: Preconditions (前置条件)
- I: Invariants (不变量)
- G: Governance (治理策略)
- R: Recovery (恢复机制)

Key theorem: If recovery_rate (γ) > drift_rate (α), then drift is bounded by D* = α/γ
"""

from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum
import json
import traceback


class ViolationType(Enum):
    PRECONDITION = "precondition"
    INVARIANT = "invariant"
    GOVERNANCE = "governance"
    RECOVERY_FAILED = "recovery_failed"


class Severity(Enum):
    SOFT = "soft"  # 警告
    HARD = "hard"  # 硬约束
    CRITICAL = "critical"  # 致命


@dataclass
class Violation:
    type: ViolationType
    severity: Severity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "stack_trace": self.stack_trace,
        }


@dataclass
class Policy:
    name: str
    description: str
    check_fn: Callable[[Any], bool]
    enforcement: str = "log"  # "log", "block", "recover"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryMechanism:
    name: str
    trigger_violation_types: Set[ViolationType]
    execute_fn: Callable[[Violation], Any]
    max_attempts: int = 3
    cooldown_seconds: float = 1.0

    def can_recover(self, violation: Violation) -> bool:
        return violation.type in self.trigger_violation_types


@dataclass
class ContractMetrics:
    total_executions: int = 0
    successful_executions: int = 0
    violations: List[Violation] = field(default_factory=list)
    recoveries: List[Dict] = field(default_factory=list)
    drift_score: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions

    @property
    def violation_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return len(self.violations) / self.total_executions

    def to_dict(self) -> Dict:
        return {
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "success_rate": self.success_rate,
            "violation_rate": self.violation_rate,
            "violations": [v.to_dict() for v in self.violations],
            "recoveries": self.recoveries,
            "drift_score": self.drift_score,
        }


class AgentContract:
    """
    Agent Behavioral Contract with runtime enforcement.

    Contract C = (P, I, G, R):
    - P: Preconditions - actions that must be true before execution
    - I: Invariants - conditions that must hold during execution
    - G: Governance - policies that constrain behavior
    - R: Recovery - mechanisms to restore contract compliance
    """

    def __init__(
        self,
        name: str = "default",
        drift_rate: float = 0.1,
        recovery_rate: float = 0.15,
    ):
        self.name = name
        self.drift_rate = drift_rate
        self.recovery_rate = recovery_rate

        self._preconditions: List[Callable[[], bool]] = []
        self._precondition_messages: List[str] = []

        self._invariants: List[Callable[[Any], bool]] = []
        self._invariant_messages: List[str] = []

        self._governance_policies: List[Policy] = []

        self._recovery_mechanisms: List[RecoveryMechanism] = []

        self.metrics = ContractMetrics()

        self._enabled = True
        self._violation_history: List[Violation] = []

    def add_precondition(
        self, check_fn: Callable[[], bool], message: str = "Precondition not satisfied"
    ) -> "AgentContract":
        self._preconditions.append(check_fn)
        self._precondition_messages.append(message)
        return self

    def add_invariant(
        self, check_fn: Callable[[Any], bool], message: str = "Invariant violated"
    ) -> "AgentContract":
        self._invariants.append(check_fn)
        self._invariant_messages.append(message)
        return self

    def add_governance_policy(self, policy: Policy) -> "AgentContract":
        self._governance_policies.append(policy)
        return self

    def add_recovery_mechanism(self, mechanism: RecoveryMechanism) -> "AgentContract":
        self._recovery_mechanisms.append(mechanism)
        return self

    def execute_action(
        self, action_fn: Callable[[], Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self._enabled:
            return {"success": True, "result": action_fn(), "skipped": True}

        self.metrics.total_executions += 1
        context = context or {}

        if not self._check_preconditions(context):
            violation = self._create_violation(
                ViolationType.PRECONDITION,
                Severity.HARD,
                "Precondition not satisfied",
                context,
            )
            self._handle_violation(violation)
            return {
                "success": False,
                "violation": violation.to_dict(),
                "recovered": False,
            }

        try:
            result = action_fn()
        except Exception as e:
            violation = self._create_violation(
                ViolationType.PRECONDITION,
                Severity.CRITICAL,
                f"Action execution failed: {str(e)}",
                context,
                error=e,
            )
            self._handle_violation(violation)
            return {
                "success": False,
                "violation": violation.to_dict(),
                "recovered": False,
            }

        if not self._check_invariants(result, context):
            violation = self._create_violation(
                ViolationType.INVARIANT,
                Severity.HARD,
                "Invariant violated after execution",
                context,
            )
            self._handle_violation(violation)
            return {
                "success": False,
                "violation": violation.to_dict(),
                "recovered": False,
            }

        policy_violations = self._check_governance(result, context)
        if policy_violations:
            self._enforce_governance(policy_violations, result, context)

        self.metrics.successful_executions += 1
        self._update_drift_score()

        return {"success": True, "result": result, "violations": []}

    def _check_preconditions(self, context: Dict[str, Any]) -> bool:
        for check_fn in self._preconditions:
            try:
                if not check_fn():
                    return False
            except Exception:
                return False
        return True

    def _check_invariants(self, result: Any, context: Dict[str, Any]) -> bool:
        for check_fn in self._invariants:
            try:
                if not check_fn(result):
                    return False
            except Exception:
                return False
        return True

    def _check_governance(self, result: Any, context: Dict[str, Any]) -> List[Policy]:
        violated = []
        for policy in self._governance_policies:
            try:
                if not policy.check_fn(result):
                    violated.append(policy)
            except Exception:
                pass
        return violated

    def _enforce_governance(
        self, policies: List[Policy], result: Any, context: Dict[str, Any]
    ):
        for policy in policies:
            if policy.enforcement == "block":
                violation = self._create_violation(
                    ViolationType.GOVERNANCE,
                    Severity.HARD,
                    f"Governance policy violated: {policy.name}",
                    context,
                )
                self._handle_violation(violation)
            elif policy.enforcement == "log":
                violation = self._create_violation(
                    ViolationType.GOVERNANCE,
                    Severity.SOFT,
                    f"Governance policy warning: {policy.name}",
                    context,
                )
                self.metrics.violations.append(violation)

    def _create_violation(
        self,
        vtype: ViolationType,
        severity: Severity,
        message: str,
        context: Dict[str, Any],
        error: Optional[Exception] = None,
    ) -> Violation:
        stack = None
        if error:
            stack = traceback.format_exc()

        return Violation(
            type=vtype,
            severity=severity,
            message=message,
            context=context,
            stack_trace=stack,
        )

    def _handle_violation(self, violation: Violation):
        self.metrics.violations.append(violation)
        self._violation_history.append(violation)

        for mechanism in self._recovery_mechanisms:
            if mechanism.can_recover(violation):
                self._execute_recovery(mechanism, violation)
                break

    def _execute_recovery(self, mechanism: RecoveryMechanism, violation: Violation):
        try:
            recovery_result = mechanism.execute_fn(violation)
            self.metrics.recoveries.append(
                {
                    "mechanism": mechanism.name,
                    "violation_type": violation.type.value,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "result": str(recovery_result) if recovery_result else None,
                }
            )
        except Exception as e:
            self.metrics.recoveries.append(
                {
                    "mechanism": mechanism.name,
                    "violation_type": violation.type.value,
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error": str(e),
                }
            )

            if violation.severity == Severity.CRITICAL:
                violation_new = self._create_violation(
                    ViolationType.RECOVERY_FAILED,
                    Severity.CRITICAL,
                    f"Recovery mechanism {mechanism.name} failed: {str(e)}",
                    violation.context,
                )
                self.metrics.violations.append(violation_new)

    def _update_drift_score(self):
        alpha = self.drift_rate
        gamma = self.recovery_rate

        if gamma > alpha:
            self.metrics.drift_score = alpha / gamma
        else:
            self.metrics.drift_score = min(1.0, self.metrics.drift_score + alpha)

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.to_dict()

    def get_violation_summary(self) -> Dict[str, int]:
        summary = {vtype.value: 0 for vtype in ViolationType}
        for v in self.metrics.violations:
            summary[v.type.value] += 1
        return summary

    def is_compliant(self) -> bool:
        return (
            self.metrics.success_rate >= 0.95
            and self.metrics.drift_score < 0.3
            and len(
                [v for v in self.metrics.violations if v.severity == Severity.CRITICAL]
            )
            == 0
        )

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def reset_metrics(self):
        self.metrics = ContractMetrics()
        self._violation_history = []


class ContractBuilder:
    """Builder for constructing Agent Contracts"""

    def __init__(self, name: str = "default"):
        self.contract = AgentContract(name=name)

    def with_precondition(
        self, check_fn: Callable[[], bool], message: str = "Precondition not satisfied"
    ) -> "ContractBuilder":
        self.contract.add_precondition(check_fn, message)
        return self

    def with_invariant(
        self, check_fn: Callable[[Any], bool], message: str = "Invariant violated"
    ) -> "ContractBuilder":
        self.contract.add_invariant(check_fn, message)
        return self

    def with_policy(
        self,
        name: str,
        check_fn: Callable[[Any], bool],
        enforcement: str = "log",
        description: str = "",
    ) -> "ContractBuilder":
        policy = Policy(
            name=name,
            description=description,
            check_fn=check_fn,
            enforcement=enforcement,
        )
        self.contract.add_governance_policy(policy)
        return self

    def with_recovery(
        self,
        name: str,
        trigger_types: Set[ViolationType],
        execute_fn: Callable[[Violation], Any],
        max_attempts: int = 3,
    ) -> "ContractBuilder":
        mechanism = RecoveryMechanism(
            name=name,
            trigger_violation_types=trigger_types,
            execute_fn=execute_fn,
            max_attempts=max_attempts,
        )
        self.contract.add_recovery_mechanism(mechanism)
        return self

    def build(self) -> AgentContract:
        return self.contract


def demo():
    print("=" * 60)
    print("Agent Behavioral Contracts (ABC) Demo")
    print("=" * 60)

    def check_memory_available() -> bool:
        import psutil

        return psutil.virtual_memory().percent < 80

    def check_disk_available() -> bool:
        import psutil

        return psutil.disk_usage("/").percent < 90

    def log_violation(v: Violation):
        print(f"  [{v.severity.value.upper()}] {v.message}")

    def recover(violation: Violation):
        print(f"  Recovery triggered for {violation.type.value}")
        return {"recovered": True}

    contract = (
        ContractBuilder("openclaw-research")
        .with_precondition(check_memory_available, "Memory usage too high")
        .with_precondition(check_disk_available, "Disk space too low")
        .with_invariant(lambda r: r is not None, "Result must not be None")
        .with_policy(
            "no-empty-results",
            lambda r: len(str(r)) > 0,
            enforcement="log",
            description="Results must not be empty",
        )
        .with_recovery(
            "log-and-continue",
            {ViolationType.PRECONDITION, ViolationType.INVARIANT},
            recover,
        )
        .build()
    )

    print("\nExecuting with contract enforcement...")

    result = contract.execute_action(lambda: {"status": "success", "data": [1, 2, 3]})

    print(f"\nSuccess: {result['success']}")

    metrics = contract.get_metrics()
    print(f"\nMetrics:")
    print(f"  Total executions: {metrics['total_executions']}")
    print(f"  Success rate: {metrics['success_rate']:.1%}")
    print(f"  Drift score: {metrics['drift_score']:.3f}")

    print(f"\nViolation summary: {contract.get_violation_summary()}")
    print(f"Compliant: {contract.is_compliant()}")


if __name__ == "__main__":
    demo()
