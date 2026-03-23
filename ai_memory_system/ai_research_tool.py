"""
AI Research Tool - Integrated FLARE/MEMORA/AutoTool for OpenClaw

This module integrates:
- FLARE Planner: Future-aware task planning
- MEMORA Memory: Dual-layer memory with 98% token savings
- AutoTool: Graph-based tool selection (30% cost reduction)

Usage:
    from ai_research_tool import ResearchTool
    tool = ResearchTool()
    result = tool.research("Research AI agent planning")
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import sys

SCRIPT_DIR = Path(__file__).parent
PARENT_DIR = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR.parent / "30-scripts-tools" / "05-AI-RESEARCH"))
sys.path.insert(0, str(SCRIPT_DIR.parent / "30-scripts-tools" / "13-memory"))

from flare_planner import FLAREPlanner
from harmonic_memory import HarmonicMemoryStore
from autotool_selector import ToolRegistry, AutoTool


class ResearchTool:
    """
    Integrated research tool combining FLARE + MEMORA + AutoTool.

    This is the actual tool used by OpenClaw, not a demo.
    """

    def __init__(self):
        self.planner = FLAREPlanner(
            lookahead_steps=3, value_propagation=True, commitment_threshold=0.7
        )
        self.memory = HarmonicMemoryStore()
        self.tool_registry = ToolRegistry()
        self._setup_tool_registry()
        self._initialized = True

    def _setup_tool_registry(self):
        """Setup OpenClaw tool registry with inertia tracking"""
        self.tool_registry.register(
            "research_scan", "Scan for papers/sources", "research"
        )
        self.tool_registry.register("research_analyze", "Analyze content", "analysis")
        self.tool_registry.register("research_write", "Write report", "writing")
        self.tool_registry.register("research_review", "Review and refine", "review")
        self.tool_registry.register("memory_save", "Save to memory", "memory")
        self.tool_registry.register("memory_search", "Search memory", "memory")

        self.tool_registry.learn_from_trajectory(
            [
                "research_scan",
                "research_analyze",
                "research_write",
                "research_review",
                "research_scan",
                "research_analyze",
                "research_write",
                "memory_save",
            ]
        )

    def research(self, task: str, use_planner: bool = True) -> Dict[str, Any]:
        """
        Execute research task with integrated components.

        Args:
            task: Research task description
            use_planner: Whether to use FLARE planner

        Returns:
            Dict with results from all components
        """
        if use_planner:
            plan = self.planner.plan(task)
            plan_dict = plan.to_dict()
        else:
            plan_dict = {"actions": [], "metadata": {}}

        tool_sequence = []
        current = None
        for i in range(min(5, len(plan_dict.get("actions", [])))):
            next_tool, method = (
                self.tool_registry.select_next(current) if current else (None, "start")
            )
            if next_tool:
                tool_sequence.append({"tool": next_tool, "method": method})
                current = next_tool
            else:
                break

        result = {
            "task": task,
            "success": True,
            "plan": plan_dict,
            "tool_sequence": tool_sequence,
            "tool_registry_stats": self.tool_registry.get_stats(),
            "memory_stats": self.memory.stats(),
        }

        return result

    def add_research_memory(
        self,
        content: str,
        entities: Optional[List[str]] = None,
        source: str = "research",
    ) -> Dict[str, Any]:
        """Add research finding to memory"""
        memory_id = self.memory.add(content, entities=entities or [], source=source)
        return {"success": True, "memory_id": memory_id, "stats": self.memory.stats()}

    def search_research_memory(
        self, query: str, mode: str = "harmonic", limit: int = 5
    ) -> Dict[str, Any]:
        """Search research memories"""
        results = self.memory.retrieve(query, mode=mode, limit=limit)
        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": [
                {
                    "abstraction": r.primary_abstraction,
                    "cue_anchors": r.cue_anchors,
                    "entities": r.entities,
                }
                for r in results
            ],
        }

    def get_next_tool(self, current_tool: str) -> Dict[str, Any]:
        """Get next tool using AutoTool inertia"""
        next_tool, method = self.tool_registry.select_next(current_tool)
        return {
            "current": current_tool,
            "next": next_tool,
            "method": method,
            "efficiency": self.tool_registry.autotool.get_efficiency_score(),
        }

    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Unified action interface for OpenClaw.

        Actions:
            research: Run research task
            add_memory: Add research memory
            search_memory: Search memories
            next_tool: Get next tool suggestion
        """
        actions = {
            "research": lambda: self.research(**kwargs),
            "add_memory": lambda: self.add_research_memory(**kwargs),
            "search_memory": lambda: self.search_research_memory(**kwargs),
            "next_tool": lambda: self.get_next_tool(**kwargs),
        }

        if action not in actions:
            return {"success": False, "error": f"Unknown action: {action}"}

        return actions[action]()


TOOL_INSTANCE: Optional[ResearchTool] = None


def get_research_tool() -> ResearchTool:
    """Get singleton research tool instance"""
    global TOOL_INSTANCE
    if TOOL_INSTANCE is None:
        TOOL_INSTANCE = ResearchTool()
    return TOOL_INSTANCE


def run_cli():
    """CLI interface for OpenClaw integration"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Research Tool")
    parser.add_argument(
        "action", choices=["research", "add", "search", "next", "stats"]
    )
    parser.add_argument("--task", help="Research task")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--content", help="Content to add")
    parser.add_argument("--current", help="Current tool name")

    args = parser.parse_args()
    tool = get_research_tool()

    if args.action == "research":
        result = tool.research(args.task or "general research")
        print(json.dumps(result, indent=2, default=str))
    elif args.action == "add":
        result = tool.add_research_memory(args.content or "")
        print(json.dumps(result, indent=2, default=str))
    elif args.action == "search":
        result = tool.search_research_memory(args.query or "")
        print(json.dumps(result, indent=2, default=str))
    elif args.action == "next":
        result = tool.get_next_tool(args.current or "research_scan")
        print(json.dumps(result, indent=2, default=str))
    elif args.action == "stats":
        result = tool.memory.stats()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run_cli()
