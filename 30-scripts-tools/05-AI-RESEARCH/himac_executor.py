"""
HiMAC: Hierarchical Macro-Micro Learning Executor
Based on arXiv:2603.00977

Hierarchical agentic RL framework that decomposes long-horizon decision-making:
- Macro-Level: Structured blueprint generation (planning)
- Micro-Level: Goal-conditioned action execution

Key innovation: Critic-free hierarchical policy optimization
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import json


class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REPLANNED = "replanned"


@dataclass
class Subgoal:
    id: str
    description: str
    goal_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    status: GoalStatus = GoalStatus.PENDING
    execution_history: List[Dict] = field(default_factory=list)
    replan_count: int = 0
    value_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "goal_conditions": self.goal_conditions,
            "status": self.status.value,
            "replan_count": self.replan_count,
            "value_score": self.value_score,
            "metadata": self.metadata,
        }


@dataclass
class Blueprint:
    task: str
    subgoals: List[Subgoal]
    macro_plan: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "task": self.task,
            "subgoals": [s.to_dict() for s in self.subgoals],
            "macro_plan": self.macro_plan,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    def get_completed_count(self) -> int:
        return sum(1 for s in self.subgoals if s.status == GoalStatus.COMPLETED)

    def get_total_count(self) -> int:
        return len(self.subgoals)

    def progress(self) -> float:
        if not self.subgoals:
            return 0.0
        return self.get_completed_count() / self.get_total_count()


@dataclass
class ExecutionContext:
    current_subgoal_index: int = 0
    execution_log: List[Dict] = field(default_factory=list)
    failed_actions: List[Dict] = field(default_factory=list)
    replan_history: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MacroPlanner:
    """Macro-level planner: generates structured blueprint"""

    def __init__(
        self,
        lookahead_enabled: bool = True,
        value_propagation: bool = True,
        llm_generator: Optional[Callable] = None,
    ):
        self.lookahead_enabled = lookahead_enabled
        self.value_propagation = value_propagation
        self.llm_generator = llm_generator

    def generate_blueprint(self, task: str) -> Blueprint:
        if self.llm_generator:
            return self._llm_blueprint(task)
        return self._rule_based_blueprint(task)

    def _llm_blueprint(self, task: str) -> Blueprint:
        prompt = f"""Decompose this task into structured subgoals:
Task: {task}

For each subgoal provide:
1. description
2. goal_conditions (what must be true after completion)
3. suggested actions

Return as JSON array."""

        response = self.llm_generator(prompt)
        subgoal_data = json.loads(response)

        subgoals = []
        for i, data in enumerate(subgoal_data):
            subgoal = Subgoal(
                id=f"sg_{i}",
                description=data["description"],
                goal_conditions=data.get("goal_conditions", {}),
                actions=data.get("actions", []),
            )
            subgoals.append(subgoal)

        return Blueprint(task=task, subgoals=subgoals, macro_plan=response)

    def _rule_based_blueprint(self, task: str) -> Blueprint:
        task_lower = task.lower()

        subgoals = []
        subgoal_id = 0

        if any(kw in task_lower for kw in ["research", "研究", "论文", "paper"]):
            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Gather and scan relevant sources",
                    goal_conditions={"sources_found": True, "count": ">0"},
                    actions=[{"type": "research", "tool": "arxiv_scanner"}],
                )
            )
            subgoal_id += 1

            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Analyze and extract key insights",
                    goal_conditions={"insights_extracted": True, "count": ">0"},
                    actions=[{"type": "analyze", "tool": "llm_analysis"}],
                )
            )
            subgoal_id += 1

            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Synthesize into structured report",
                    goal_conditions={"report_created": True},
                    actions=[{"type": "write", "tool": "report_generator"}],
                )
            )
            subgoal_id += 1

            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Review and refine output",
                    goal_conditions={"review_completed": True},
                    actions=[{"type": "review", "tool": "critic"}],
                )
            )

        elif any(kw in task_lower for kw in ["implement", "实现", "build", "开发"]):
            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Design system architecture",
                    goal_conditions={"design_approved": True},
                    actions=[{"type": "design", "tool": "architecture"}],
                )
            )
            subgoal_id += 1

            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Implement core components",
                    goal_conditions={"components_ready": True},
                    actions=[{"type": "implement", "tool": "code_generator"}],
                )
            )
            subgoal_id += 1

            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Test and debug",
                    goal_conditions={"tests_passed": True},
                    actions=[{"type": "test", "tool": "test_runner"}],
                )
            )
            subgoal_id += 1

            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Deploy and verify",
                    goal_conditions={"deployment_successful": True},
                    actions=[{"type": "deploy", "tool": "deployer"}],
                )
            )

        else:
            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Understand and analyze task",
                    goal_conditions={"analysis_complete": True},
                    actions=[{"type": "analyze"}],
                )
            )
            subgoal_id += 1

            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Execute main task",
                    goal_conditions={"execution_complete": True},
                    actions=[{"type": "execute"}],
                )
            )
            subgoal_id += 1

            subgoals.append(
                Subgoal(
                    id=f"sg_{subgoal_id}",
                    description="Verify and refine results",
                    goal_conditions={"verification_complete": True},
                    actions=[{"type": "verify"}],
                )
            )

        return Blueprint(
            task=task,
            subgoals=subgoals,
            macro_plan=f"Generated {len(subgoals)} subgoals for: {task}",
        )


class MicroExecutor:
    """Micro-level executor: goal-conditioned action execution"""

    def __init__(
        self,
        action_runner: Optional[Callable] = None,
        condition_checker: Optional[Callable] = None,
    ):
        self.action_runner = action_runner or self._default_action_runner
        self.condition_checker = condition_checker or self._default_condition_checker

    def execute_subgoal(self, subgoal: Subgoal) -> bool:
        subgoal.status = GoalStatus.IN_PROGRESS

        for action in subgoal.actions:
            result = self.action_runner(action)

            subgoal.execution_history.append(
                {
                    "action": action,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            if result.get("success", False) is False:
                subgoal.status = GoalStatus.FAILED
                return False

        conditions_met = self.condition_checker(
            subgoal.goal_conditions, subgoal.execution_history
        )

        if conditions_met:
            subgoal.status = GoalStatus.COMPLETED
            return True
        else:
            subgoal.status = GoalStatus.FAILED
            return False

    def _default_action_runner(self, action: Dict) -> Dict:
        return {"success": True, "action": action}

    def _default_condition_checker(
        self, conditions: Dict[str, Any], history: List[Dict]
    ) -> bool:
        return True


class HiMACExecutor:
    """
    Hierarchical Macro-Micro Learning Executor

    Workflow:
    1. Macro-Level: Generate blueprint (structured plan)
    2. Micro-Level: Execute subgoals with goal conditions
    3. Iterative co-evolution: Adapt based on feedback
    """

    def __init__(
        self,
        planner: Optional[MacroPlanner] = None,
        executor: Optional[MicroExecutor] = None,
        max_replan_per_subgoal: int = 3,
    ):
        self.planner = planner or MacroPlanner()
        self.executor = executor or MicroExecutor()
        self.max_replan_per_subgoal = max_replan_per_subgoal

        self.current_blueprint: Optional[Blueprint] = None
        self.context = ExecutionContext()

    def execute_task(self, task: str) -> Blueprint:
        self.context = ExecutionContext()
        self.current_blueprint = self.planner.generate_blueprint(task)

        for i, subgoal in enumerate(self.current_blueprint.subgoals):
            self.context.current_subgoal_index = i

            success = self.executor.execute_subgoal(subgoal)

            if not success:
                if subgoal.replan_count < self.max_replan_per_subgoal:
                    subgoal.replan_count += 1
                    subgoal.status = GoalStatus.REPLANNED

                    self.context.replan_history.append(
                        {
                            "subgoal_id": subgoal.id,
                            "attempt": subgoal.replan_count,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    self._adapt_and_retry(subgoal)
                else:
                    subgoal.status = GoalStatus.FAILED

            self.context.execution_log.append(
                {
                    "subgoal_id": subgoal.id,
                    "status": subgoal.status.value,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return self.current_blueprint

    def _adapt_and_retry(self, subgoal: Subgoal):
        """Adapt and retry failed subgoal"""
        subgoal.status = GoalStatus.PENDING
        subgoal.execution_history.clear()

        if subgoal.goal_conditions:
            simplified_conditions = {
                k: v
                for k, v in subgoal.goal_conditions.items()
                if subgoal.replan_count > 1
            }
            subgoal.goal_conditions = simplified_conditions

    def get_progress(self) -> Dict[str, Any]:
        if not self.current_blueprint:
            return {"status": "not_started"}

        completed = self.current_blueprint.get_completed_count()
        total = self.current_blueprint.get_total_count()

        return {
            "status": "in_progress" if completed < total else "completed",
            "completed": completed,
            "total": total,
            "progress_percent": self.current_blueprint.progress() * 100,
            "failed_subgoals": [
                s.id
                for s in self.current_blueprint.subgoals
                if s.status == GoalStatus.FAILED
            ],
            "replanned_count": sum(
                s.replan_count for s in self.current_blueprint.subgoals
            ),
        }

    def replan_subgoal(self, subgoal_id: str, new_description: str) -> bool:
        if not self.current_blueprint:
            return False

        for subgoal in self.current_blueprint.subgoals:
            if subgoal.id == subgoal_id:
                subgoal.description = new_description
                subgoal.status = GoalStatus.PENDING
                subgoal.execution_history.clear()
                return True

        return False


def demo():
    print("=" * 60)
    print("HiMAC: Hierarchical Macro-Micro Learning Demo")
    print("=" * 60)

    executor = HiMACExecutor()

    task = "Research recent advances in AI agents and write a summary report"

    print(f"\nTask: {task}")
    print("\n--- Generating Blueprint ---")

    blueprint = executor.planner.generate_blueprint(task)

    print(f"\nGenerated {len(blueprint.subgoals)} subgoals:")
    for i, subgoal in enumerate(blueprint.subgoals):
        print(f"\n{i + 1}. {subgoal.description}")
        print(f"   Goal conditions: {subgoal.goal_conditions}")
        print(f"   Actions: {len(subgoal.actions)}")

    print("\n--- Executing Task ---")

    result = executor.execute_task(task)

    print(f"\nProgress: {executor.get_progress()}")
    print(f"\nFinal Blueprint Status:")
    for subgoal in result.subgoals:
        print(
            f"  {subgoal.id}: {subgoal.status.value} (replans: {subgoal.replan_count})"
        )


if __name__ == "__main__":
    demo()
