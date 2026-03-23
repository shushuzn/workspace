#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

workspace_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(workspace_root / "30-scripts-tools" / "05-AI-RESEARCH"))
sys.path.insert(0, str(workspace_root / "30-scripts-tools" / "13-memory"))
sys.path.insert(0, str(workspace_root / "ai_memory_system"))

from flare_planner import FLAREPlanner
from harmonic_memory import HarmonicMemoryStore
from autotool_selector import ToolRegistry, AutoTool


def get_research_tool():
    class ResearchTool:
        def __init__(self):
            self.planner = FLAREPlanner(
                lookahead_steps=3, value_propagation=True, commitment_threshold=0.7
            )
            self.memory = HarmonicMemoryStore()
            self.tool_registry = ToolRegistry()
            self._setup_tool_registry()

        def _setup_tool_registry(self):
            self.tool_registry.register("research_scan", "Scan papers", "research")
            self.tool_registry.register(
                "research_analyze", "Analyze content", "analysis"
            )
            self.tool_registry.register("research_write", "Write report", "writing")
            self.tool_registry.register("memory_save", "Save to memory", "memory")
            self.tool_registry.register("memory_search", "Search memory", "memory")
            self.tool_registry.learn_from_trajectory(
                ["research_scan", "research_analyze", "research_write", "memory_save"]
            )

        def research(self, task, use_planner=True):
            if use_planner:
                plan = self.planner.plan(task)
                plan_dict = plan.to_dict()
            else:
                plan_dict = {"actions": [], "metadata": {}}

            tool_sequence = []
            current = None
            for i in range(min(5, len(plan_dict.get("actions", [])))):
                next_tool, method = (
                    self.tool_registry.select_next(current)
                    if current
                    else (None, "start")
                )
                if next_tool:
                    tool_sequence.append({"tool": next_tool, "method": method})
                    current = next_tool
                else:
                    break

            return {
                "task": task,
                "success": True,
                "plan": plan_dict,
                "tool_sequence": tool_sequence,
                "tool_registry_stats": self.tool_registry.get_stats(),
                "memory_stats": self.memory.stats(),
            }

        def add_research_memory(self, content, entities=None, source="research"):
            memory_id = self.memory.add(content, entities=entities or [], source=source)
            return {
                "success": True,
                "memory_id": memory_id,
                "stats": self.memory.stats(),
            }

        def search_research_memory(self, query, mode="harmonic", limit=5):
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

        def get_next_tool(self, current_tool):
            next_tool, method = self.tool_registry.select_next(current_tool)
            return {
                "current": current_tool,
                "next": next_tool,
                "method": method,
                "efficiency": self.tool_registry.autotool.get_efficiency_score(),
            }

    return ResearchTool()


tool = get_research_tool()
action = sys.argv[1] if len(sys.argv) > 1 else "stats"

if action == "stats":
    stats = tool.memory.stats()
    print(f"AI Research System Status:")
    print(f"  Total memories: {stats.get('total_memories', 0)}")
    print(f"  Avg token savings: {stats.get('avg_token_savings', 0):.1%}")
elif action == "research":
    task = sys.argv[2] if len(sys.argv) > 2 else "general research"
    result = tool.research(task)
    print(f"Research Task: {result['task']}")
    print(f"Success: {result['success']}")
    print(f"Plan actions: {len(result['plan']['actions'])}")
elif action == "next":
    current = sys.argv[2] if len(sys.argv) > 2 else "research_scan"
    result = tool.get_next_tool(current)
    print(
        f"{result['current']} -> {result['next']} (via {result['method']}, eff {result['efficiency']:.1%})"
    )
else:
    print(f"Unknown action: {action}")
    print("Available: stats, research, next")
