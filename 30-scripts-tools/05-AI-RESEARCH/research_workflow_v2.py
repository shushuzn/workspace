"""
Research Workflow v2.0 - with FLARE + MEMORA + HiMAC

Integrates:
- FLARE Planner: Future-aware task planning
- MEMORA: Dual-layer memory with 98% token savings
- HiMAC: Hierarchical macro-micro execution
- ABC Contracts: Safety and reliability

Usage:
    from research_workflow_v2 import ResearchWorkflow
    wf = ResearchWorkflow()
    result = wf.run("Research AI agent planning methods")
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
PARENT_DIR = SCRIPT_DIR.parent


class ResearchWorkflow:
    """
    Research workflow with integrated FLARE/MEMORA/HiMAC
    """

    def __init__(self):
        self.planner = None
        self.memory = None
        self.executor = None
        self.contract = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize all components"""
        if self._initialized:
            return True

        try:
            sys.path.insert(0, str(SCRIPT_DIR))
            from flare_planner import FLAREPlanner
            from himac_executor import HiMACExecutor, MacroPlanner, MicroExecutor

            sys.path.insert(0, str(PARENT_DIR / "10-MEMORY/00-CORE"))
            from harmonic_memory import HarmonicMemoryStore

            self.planner = FLAREPlanner(
                lookahead_steps=3, value_propagation=True, commitment_threshold=0.7
            )

            self.memory = HarmonicMemoryStore()

            self.executor = HiMACExecutor(
                planner=MacroPlanner(), executor=MicroExecutor()
            )

            self._initialized = True
            return True

        except ImportError as e:
            print(f"Initialization failed: {e}")
            return False

    def run(self, task: str) -> Dict[str, Any]:
        """Run complete research workflow"""
        if not self.initialize():
            return {"success": False, "error": "Initialization failed"}

        result = {
            "success": True,
            "task": task,
            "started_at": datetime.now().isoformat(),
            "steps": [],
        }

        step = {"name": "plan", "status": "pending"}
        try:
            plan = self.planner.plan(task)
            step["status"] = "completed"
            step["actions_count"] = len(plan.actions)
            step["committed"] = plan.metadata.get("committed_count", 0)
            result["plan"] = plan.to_dict()
        except Exception as e:
            step["status"] = "failed"
            step["error"] = str(e)
        result["steps"].append(step)

        step = {"name": "execute", "status": "pending"}
        try:
            blueprint = self.executor.planner.generate_blueprint(task)
            step["status"] = "completed"
            step["subgoals_count"] = len(blueprint.subgoals)
            result["blueprint"] = blueprint.to_dict()
        except Exception as e:
            step["status"] = "failed"
            step["error"] = str(e)
        result["steps"].append(step)

        step = {"name": "memory_save", "status": "pending"}
        try:
            self.memory.add(
                f"Research task completed: {task}",
                entities=self._extract_entities(task),
                source="research",
            )
            step["status"] = "completed"
        except Exception as e:
            step["status"] = "failed"
            step["error"] = str(e)
        result["steps"].append(step)

        result["completed_at"] = datetime.now().isoformat()
        return result

    def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities from text"""
        keywords = ["AI", "agent", "planning", "memory", "research", "LLM", "model"]
        words = text.upper().split()
        entities = [w for w in words if any(kw.upper() in w for kw in keywords)]
        return list(set(entities))[:5]

    def get_memory(self, query: str, limit: int = 5) -> List[str]:
        """Retrieve relevant memories"""
        if not self.memory:
            return []
        entries = self.memory.retrieve(query, mode="harmonic", limit=limit)
        return [e.primary_abstraction for e in entries]

    def add_research_findings(
        self,
        finding: str,
        paper_id: Optional[str] = None,
        entities: Optional[List[str]] = None,
    ):
        """Add research findings to memory"""
        if not self.memory:
            return
        metadata = {"paper_id": paper_id} if paper_id else {}
        self.memory.add(
            finding, entities=entities or [], source="research", metadata=metadata
        )


def create_research_workflow():
    """Factory function to create research workflow"""
    return ResearchWorkflow()


def demo():
    print("=" * 60)
    print("Research Workflow v2.0 Demo (FLARE + MEMORA + HiMAC)")
    print("=" * 60)

    wf = ResearchWorkflow()

    print("\n--- Initializing ---")
    initialized = wf.initialize()
    print(f"Initialized: {initialized}")

    if not initialized:
        print("Failed to initialize components")
        return

    print("\n--- Running Research Task ---")

    task = "Research recent advances in AI agent planning methods"
    result = wf.run(task)

    print(f"\nSuccess: {result['success']}")
    print(f"Task: {result['task']}")

    print("\n--- Steps ---")
    for step in result.get("steps", []):
        print(f"  {step['name']}: {step['status']}")

    print("\n--- Plan Summary ---")
    if "plan" in result:
        plan = result["plan"]
        print(
            f"  Actions: {plan.get('metadata', {}).get('iterations', 'N/A')} iterations"
        )
        print(f"  Committed: {plan.get('metadata', {}).get('committed_count', 0)}")

    print("\n--- Blueprint Summary ---")
    if "blueprint" in result:
        bp = result["blueprint"]
        print(f"  Subgoals: {len(bp.get('subgoals', []))}")

    print("\n--- Memory Test ---")
    wf.add_research_findings(
        "FLARE planner addresses myopic commitment in LLM agents",
        paper_id="2601.22311",
        entities=["FLARE", "planner", "myopic"],
    )

    memories = wf.get_memory("planning agent", limit=3)
    print(f"Found {len(memories)} relevant memories")
    for m in memories:
        print(f"  - {m[:50]}...")


if __name__ == "__main__":
    demo()
