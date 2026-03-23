"""
HiMAC Workflow Integration for OpenClaw
Integrates hierarchical macro-micro planning with OpenClaw workflows
"""

from typing import Dict, List, Optional, Callable
import sys
from pathlib import Path


class WorkflowBlueprint:
    """Workflow blueprint from HiMAC planner"""

    def __init__(self, blueprint):
        self.blueprint = blueprint
        self.current_subgoal_index = 0

    @property
    def subgoals(self):
        return self.blueprint.subgoals

    @property
    def progress(self) -> float:
        return self.blueprint.progress()

    def get_current_subgoal(self):
        if self.current_subgoal_index < len(self.subgoals):
            return self.subgoals[self.current_subgoal_index]
        return None

    def advance(self):
        self.current_subgoal_index += 1

    def to_dict(self) -> Dict:
        return self.blueprint.to_dict()


class HiMACWorkflowEngine:
    """
    Workflow engine using HiMAC for hierarchical task execution
    """

    def __init__(self):
        result = create_himac_executor()
        self.executor = result.get("executor") if result["success"] else None
        self.current_blueprint = None
        self.enabled = result["success"]

    def plan_task(self, task: str) -> Optional[WorkflowBlueprint]:
        """Plan a task using HiMAC"""
        if not self.enabled or not self.executor:
            return None

        self.current_blueprint = self.executor.planner.generate_blueprint(task)
        return WorkflowBlueprint(self.current_blueprint)

    def execute_task(self, task: str, action_runner: Callable = None) -> Dict:
        """Execute a task with HiMAC planning"""
        if not self.enabled or not self.executor:
            return {"success": False, "error": "HiMAC not enabled"}

        result = self.executor.execute_task(task)

        return {
            "success": True,
            "blueprint": result.to_dict(),
            "progress": self.executor.get_progress(),
        }

    def get_progress(self) -> Dict:
        """Get current workflow progress"""
        if not self.executor:
            return {"status": "disabled"}
        return self.executor.get_progress()

    def replan_subgoal(self, subgoal_id: str, new_description: str) -> bool:
        """Replan a specific subgoal"""
        if not self.executor:
            return False
        return self.executor.replan_subgoal(subgoal_id, new_description)


def create_himac_executor():
    """Create HiMAC executor instance"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "05-AI-RESEARCH"))
        from himac_executor import HiMACExecutor, MacroPlanner, MicroExecutor

        executor = HiMACExecutor(planner=MacroPlanner(), executor=MicroExecutor())

        return {"success": True, "executor": executor}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_research_workflow():
    """Create a research-specific HiMAC workflow"""
    engine = HiMACWorkflowEngine()

    if not engine.enabled:
        return {"success": False, "error": "HiMAC not available"}

    def run_research_workflow(task: str) -> Dict:
        """Run research workflow with HiMAC planning"""
        plan = engine.plan_task(task)

        if not plan:
            return {"success": False, "error": "Planning failed"}

        results = []
        for subgoal in plan.subgoals:
            results.append(
                {
                    "subgoal_id": subgoal.id,
                    "description": subgoal.description,
                    "status": subgoal.status.value,
                    "goal_conditions": subgoal.goal_conditions,
                }
            )

        return {
            "success": True,
            "blueprint": plan.to_dict(),
            "subgoals": results,
            "progress": plan.progress,
        }

    return {"success": True, "engine": engine, "run_workflow": run_research_workflow}


def demo():
    print("=" * 60)
    print("HiMAC Workflow Integration Demo")
    print("=" * 60)

    engine = HiMACWorkflowEngine()

    if not engine.enabled:
        print("HiMAC not available")
        return

    print("\n--- Planning Research Task ---")

    blueprint = engine.plan_task("Research AI agent planning methods and write report")

    if blueprint:
        print(f"\nGenerated {len(blueprint.subgoals)} subgoals:")
        for i, subgoal in enumerate(blueprint.subgoals):
            print(f"\n{i + 1}. {subgoal.description}")
            print(f"   Conditions: {subgoal.goal_conditions}")

    print("\n--- Executing Task ---")

    result = engine.execute_task("Research AI agents and create summary")
    print(f"\nSuccess: {result['success']}")
    print(f"Progress: {result.get('progress', {})}")


if __name__ == "__main__":
    demo()
