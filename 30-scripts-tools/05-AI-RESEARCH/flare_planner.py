"""
FLARE Planner: Future-Aware Lookahead with Reward Estimation
Based on arXiv:2601.22311 - "Why Reasoning Fails to Plan"

A minimal instantiation of future-aware planning that enforces:
1. Explicit lookahead
2. Value propagation
3. Limited commitment

This prevents the "myopic commitment" problem where step-wise greedy
policies lead to locally optimal choices that compound over time.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import json


class CommitmentLevel(Enum):
    FULL = "full"  # 完全承诺，不易变更
    SOFT = "soft"  # 柔性承诺，可调整
    FLEXIBLE = "flexible"  # 灵活保留


@dataclass
class Action:
    """行动计划"""

    id: str
    description: str
    action_type: str  # "research", "analyze", "write", "execute", etc.
    expected_outcome: Optional[str] = None
    enabling_conditions: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    commitment_level: CommitmentLevel = CommitmentLevel.FLEXIBLE
    locked: bool = False
    value_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "action_type": self.action_type,
            "expected_outcome": self.expected_outcome,
            "enabling_conditions": self.enabling_conditions,
            "risk_factors": self.risk_factors,
            "commitment_level": self.commitment_level.value,
            "locked": self.locked,
            "value_score": self.value_score,
            "metadata": self.metadata,
        }


@dataclass
class Plan:
    """执行计划"""

    task: str
    actions: List[Action]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "task": self.task,
            "actions": [a.to_dict() for a in self.actions],
            "metadata": self.metadata,
        }

    def get_committed_actions(self) -> List[Action]:
        """获取已承诺的行动"""
        return [a for a in self.actions if a.commitment_level == CommitmentLevel.FULL]

    def get_flexible_actions(self) -> List[Action]:
        """获取灵活的行动"""
        return [
            a for a in self.actions if a.commitment_level == CommitmentLevel.FLEXIBLE
        ]


@dataclass
class ExecutionResult:
    """执行结果"""

    action_id: str
    success: bool
    actual_outcome: Optional[str] = None
    deviation: float = 0.0  # 与预期的偏差
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class FLAREPlanner:
    """
    FLARE Planner - Future-aware Lookahead with Reward Estimation

    Core principles:
    1. Lookahead: Consider future consequences of current actions
    2. Value Propagation: Downstream outcomes influence early decisions
    3. Limited Commitment: Avoid premature locking of uncertain actions
    """

    def __init__(
        self,
        lookahead_steps: int = 3,
        value_propagation: bool = True,
        commitment_threshold: float = 0.7,
        discount_factor: float = 0.7,
        enabling_action_bonus: float = 0.9,
        routine_action_factor: float = 0.5,
        exploration_action_factor: float = 0.3,
    ):
        self.lookahead_steps = lookahead_steps
        self.value_propagation = value_propagation
        self.commitment_threshold = commitment_threshold
        self.discount_factor = discount_factor
        self.enabling_action_bonus = enabling_action_bonus
        self.routine_action_factor = routine_action_factor
        self.exploration_action_factor = exploration_action_factor

        self.action_history: List[Action] = []
        self.future_value_cache: Dict[str, float] = {}
        self.planning_iterations = 0

    def plan(
        self,
        task: str,
        max_iterations: int = 10,
        initial_actions: Optional[List[Action]] = None,
    ) -> Plan:
        """
        主规划函数

        Args:
            task: 任务描述
            max_iterations: 最大迭代次数
            initial_actions: 可选的初始行动序列

        Returns:
            Plan: 优化后的执行计划
        """
        self.planning_iterations = 0
        self.action_history = []

        # 1. 生成或使用初始行动序列
        if initial_actions:
            # 兼容 str 和 Action 两种输入
            actions = []
            for i, item in enumerate(initial_actions):
                if isinstance(item, str):
                    actions.append(
                        Action(
                            id=f"a{i}",
                            description=item,
                            action_type=self._infer_action_type(item),
                        )
                    )
                else:
                    actions.append(item)
        else:
            actions = self._generate_initial_actions(task)

        # 2. 迭代优化
        for i in range(max_iterations):
            self.planning_iterations += 1

            # 3. 评估未来影响
            future_impacts = self._evaluate_future_impacts(actions)

            # 4. 价值传播
            if self.value_propagation:
                propagated_values = self._propagate_values(actions, future_impacts)
            else:
                propagated_values = future_impacts

            # 5. 更新行动价值
            for j, action in enumerate(actions):
                action.value_score = propagated_values.get(j, 0.0)

            # 6. 应用有限承诺
            actions = self._apply_limited_commitment(actions)

            # 7. 检查是否收敛
            if self._is_converged(actions, i):
                break

        # 构建元数据
        metadata = {
            "iterations": self.planning_iterations,
            "final_value_scores": {a.id: a.value_score for a in actions},
            "committed_count": len(
                [a for a in actions if a.commitment_level == CommitmentLevel.FULL]
            ),
            "flexible_count": len(
                [a for a in actions if a.commitment_level == CommitmentLevel.FLEXIBLE]
            ),
        }

        return Plan(task=task, actions=actions, metadata=metadata)

    def replan(
        self, failed_action: Action, remaining_task: str, context: Optional[Dict] = None
    ) -> Plan:
        """
        重新规划：当某个行动失败时触发

        Args:
            failed_action: 失败的行动
            remaining_task: 剩余任务描述
            context: 额外上下文信息

        Returns:
            Plan: 重新规划后的计划
        """
        # 记录失败信息
        self.action_history.append(failed_action)
        self.future_value_cache[failed_action.id] = 0.0

        # 只对未锁定的行动进行重规划
        if not self._is_locked_action(failed_action):
            return self.plan(remaining_task)

        # 如果是锁定行动，需要更激进的重新规划
        locked_action: Optional[List[Action]] = (
            [a for a in self.action_history if not a.locked]
            if self.action_history
            else None
        )
        return self.plan(
            remaining_task,
            max_iterations=5,
            initial_actions=locked_action,
        )

    def should_replan(self, action: Action, execution_result: ExecutionResult) -> bool:
        """
        检查是否需要重新规划

        Args:
            action: 执行的行动
            execution_result: 执行结果

        Returns:
            bool: 是否需要重新规划
        """
        # 已承诺的行动不轻易重规划
        if action.locked and action.commitment_level == CommitmentLevel.FULL:
            return False

        # 明显失败需要重规划
        if not execution_result.success:
            return True

        # 偏差超过阈值
        if execution_result.deviation > 0.3:
            return True

        return False

    def _generate_initial_actions(self, task: str) -> List[Action]:
        """
        生成初始行动序列 - 简单版本
        实际使用时应该调用 LLM 来生成
        """
        # 简单的基于关键词的行动生成
        actions = []
        task_lower = task.lower()

        if any(kw in task_lower for kw in ["research", "研究", "论文", "paper"]):
            actions.append(
                Action(
                    id="a0",
                    description="Scan and gather relevant papers/sources",
                    action_type="research",
                )
            )
            actions.append(
                Action(
                    id="a1",
                    description="Analyze and extract key insights",
                    action_type="analyze",
                )
            )
            actions.append(
                Action(
                    id="a2",
                    description="Synthesize findings into structured report",
                    action_type="write",
                )
            )
            actions.append(
                Action(
                    id="a3",
                    description="Review and refine the report",
                    action_type="review",
                )
            )
        elif any(kw in task_lower for kw in ["implement", "实现", "build", "开发"]):
            actions.append(
                Action(
                    id="a0",
                    description="Design system architecture",
                    action_type="design",
                )
            )
            actions.append(
                Action(
                    id="a1",
                    description="Implement core components",
                    action_type="implement",
                )
            )
            actions.append(
                Action(id="a2", description="Test and debug", action_type="test")
            )
            actions.append(
                Action(id="a3", description="Deploy and verify", action_type="deploy")
            )
        else:
            # 通用任务分解
            actions.append(
                Action(
                    id="a0",
                    description="Understand task requirements",
                    action_type="analyze",
                )
            )
            actions.append(
                Action(id="a1", description="Execute main task", action_type="execute")
            )
            actions.append(
                Action(
                    id="a2",
                    description="Verify and refine results",
                    action_type="verify",
                )
            )

        return actions

    def _infer_action_type(self, description: str) -> str:
        """根据描述推断行动类型"""
        desc_lower = description.lower()
        if "research" in desc_lower or "scan" in desc_lower or "gather" in desc_lower:
            return "research"
        if "analyze" in desc_lower or "extract" in desc_lower:
            return "analyze"
        if "write" in desc_lower or "synthesize" in desc_lower:
            return "write"
        if "design" in desc_lower:
            return "design"
        if "implement" in desc_lower or "build" in desc_lower:
            return "implement"
        if "test" in desc_lower or "debug" in desc_lower:
            return "test"
        if "review" in desc_lower or "refine" in desc_lower:
            return "review"
        if "deploy" in desc_lower or "verify" in desc_lower:
            return "deploy"
        return "execute"

    def _evaluate_future_impacts(self, actions: List[Action]) -> Dict[int, float]:
        """
        评估每个行动的未来影响
        """
        impacts = {}
        n = len(actions)

        for i, action in enumerate(actions):
            # 考虑从当前行动到 lookahead_steps 步之后
            future_actions = actions[i + 1 : min(i + self.lookahead_steps + 1, n)]

            # 评估影响
            impact = self._estimate_impact(action, future_actions)
            impacts[i] = impact

        return impacts

    def _estimate_impact(self, current: Action, future: List[Action]) -> float:
        """
        估算当前行动对未来的影响
        """
        if not future:
            return self._estimate_direct_value(current)

        # 促进分数：当前行动为未来行动创造的条件
        enabling_score = self._check_enabling_conditions(current, future)

        # 风险分数：当前行动可能带来的风险
        risk_score = self._assess_risk(current, future)

        # 不可逆性
        irreversibility = self._check_irreversibility(current)

        # 综合影响 = 促进分数 * (1 - 风险) * (1 - 不可逆性 * 0.5)
        impact = enabling_score * (1 - risk_score) * (1 - irreversibility * 0.5)

        return max(0.0, min(1.0, impact))

    def _estimate_direct_value(self, action: Action) -> float:
        """估计行动的直接价值"""
        # 基于行动类型的基础价值
        type_values = {
            "research": 0.8,
            "analyze": 0.7,
            "design": 0.9,
            "implement": 0.8,
            "write": 0.6,
            "review": 0.5,
            "test": 0.6,
            "deploy": 0.4,
            "execute": 0.5,
        }
        return type_values.get(action.action_type, 0.5)

    def _check_enabling_conditions(
        self, current: Action, future: List[Action]
    ) -> float:
        """
        检查当前行动是否为未来行动创造条件
        """
        if not future:
            return 0.5

        # 研究行动为分析和写作创造条件
        if current.action_type == "research":
            future_types = [a.action_type for a in future]
            if "analyze" in future_types or "write" in future_types:
                return 0.9

        # 设计行动为实现创造条件
        if current.action_type == "design":
            if "implement" in [a.action_type for a in future]:
                return 0.9

        # 实现行动为测试创造条件
        if current.action_type == "implement":
            if "test" in [a.action_type for a in future]:
                return 0.85

        # 分析行动为写作创造条件
        if current.action_type == "analyze":
            if "write" in [a.action_type for a in future]:
                return 0.8

        return 0.5  # 默认中等促进

    def _assess_risk(self, current: Action, future: List[Action]) -> float:
        """
        评估当前行动的风险
        """
        # 基于行动类型的风险
        type_risks = {
            "research": 0.2,
            "analyze": 0.3,
            "design": 0.4,
            "implement": 0.5,
            "write": 0.2,
            "review": 0.1,
            "test": 0.4,
            "deploy": 0.6,
            "execute": 0.3,
        }

        base_risk = type_risks.get(current.action_type, 0.3)

        # 如果有显式的风险因素，增加风险
        if current.risk_factors:
            base_risk = min(1.0, base_risk + 0.2)

        return base_risk

    def _check_irreversibility(self, action: Action) -> float:
        """
        检查行动的不可逆性
        高不可逆性行动应该更谨慎
        """
        irreversible_keywords = ["delete", "remove", "deploy", "submit", "send"]

        for keyword in irreversible_keywords:
            if keyword in action.description.lower():
                return 0.7

        # 某些行动类型天然不可逆
        if action.action_type == "deploy":
            return 0.6
        if action.action_type == "write":
            # 写入文件可以恢复，所以不是完全不可逆
            return 0.2

        return 0.1

    def _propagate_values(
        self, actions: List[Action], future_impacts: Dict[int, float]
    ) -> Dict[int, float]:
        """
        反向传播未来价值到早期行动
        """
        n = len(actions)
        propagated = {}

        for i in range(n - 1, -1, -1):
            if i == n - 1:
                # 最后一个行动的价值 = 直接影响
                propagated[i] = future_impacts.get(i, 0.0)
            else:
                # 当前行动价值 = 直接影响 + 未来价值的一部分
                direct = future_impacts.get(i, 0.0)
                future_value = propagated[i + 1] * self.discount_factor

                # 当前行动对下游的影响系数
                downstream_coefficient = self._calculate_downstream_coefficient(
                    actions[i], actions[i + 1 :]
                )

                propagated[i] = direct + downstream_coefficient * future_value

        return propagated

    def _calculate_downstream_coefficient(
        self, current: Action, downstream: List[Action]
    ) -> float:
        """
        计算当前行动对下游行动的影响系数
        """
        if not downstream:
            return 0.0

        # 关键行动 (为下游创造条件) 系数高
        if self._is_enabling_action(current, downstream):
            return self.enabling_action_bonus

        # 例行行动系数中等
        if self._is_routine_action(current):
            return self.routine_action_factor

        # 探索行动系数低但正值
        if self._is_exploration_action(current):
            return self.exploration_action_factor

        return 0.5

    def _is_enabling_action(self, current: Action, downstream: List[Action]) -> bool:
        """判断是否为赋能行动"""
        future_types = [a.action_type for a in downstream]

        enabling_pairs = {
            "research": ["analyze", "write"],
            "design": ["implement"],
            "analyze": ["write"],
            "implement": ["test"],
        }

        enabling_for = enabling_pairs.get(current.action_type, [])
        return any(ft in enabling_for for ft in future_types)

    def _is_routine_action(self, action: Action) -> bool:
        """判断是否为例行行动"""
        return action.action_type in ["review", "verify", "test"]

    def _is_exploration_action(self, action: Action) -> bool:
        """判断是否为探索行动"""
        return action.action_type in ["research", "analyze"]

    def _apply_limited_commitment(self, actions: List[Action]) -> List[Action]:
        """
        有限承诺机制：避免过早锁定某些行动
        """
        committed = []

        for action in actions:
            value = action.value_score

            if value >= self.commitment_threshold:
                # 高价值行动 → 完全承诺
                action.commitment_level = CommitmentLevel.FULL
                action.locked = True
            elif value >= self.commitment_threshold * 0.6:
                # 中等价值行动 → 柔性承诺
                action.commitment_level = CommitmentLevel.SOFT
                action.locked = False
            else:
                # 低价值行动 → 保持灵活
                action.commitment_level = CommitmentLevel.FLEXIBLE
                action.locked = False

            committed.append(action)

        return committed

    def _is_converged(self, actions: List[Action], iteration: int) -> bool:
        """检查是否收敛"""
        if iteration == 0:
            return False

        # 检查价值分数是否稳定
        if len(actions) >= 2:
            score_diff = abs(actions[-1].value_score - actions[-2].value_score)
            if score_diff < 0.01:
                return True

        return False

    def _is_locked_action(self, action: Action) -> bool:
        """检查行动是否被锁定"""
        return getattr(action, "locked", False)


def demo():
    """演示 FLARE Planner 的使用"""
    print("=" * 60)
    print("FLARE Planner Demo - Future-Aware Planning")
    print("=" * 60)

    # 创建规划器
    planner = FLAREPlanner(
        lookahead_steps=3, value_propagation=True, commitment_threshold=0.7
    )

    # 示例任务
    task = "Research recent advances in AI agents and write a summary report"

    print(f"\nTask: {task}")
    print("\n--- Planning ---")

    # 执行规划
    plan = planner.plan(task, max_iterations=5)

    # 输出结果
    print(f"\nIterations: {plan.metadata['iterations']}")
    print(f"Committed actions: {plan.metadata['committed_count']}")
    print(f"Flexible actions: {plan.metadata['flexible_count']}")

    print("\n--- Action Plan ---")
    for i, action in enumerate(plan.actions):
        commitment_icon = {
            CommitmentLevel.FULL: "🔒",
            CommitmentLevel.SOFT: "⏳",
            CommitmentLevel.FLEXIBLE: "🔓",
        }.get(action.commitment_level, "?")

        print(f"\n{i + 1}. {action.description}")
        print(f"   Type: {action.action_type}")
        print(f"   Value Score: {action.value_score:.3f}")
        print(f"   Commitment: {commitment_icon} {action.commitment_level.value}")
        print(f"   Locked: {action.locked}")

    print("\n--- JSON Output ---")
    print(json.dumps(plan.to_dict(), indent=2))


if __name__ == "__main__":
    demo()
