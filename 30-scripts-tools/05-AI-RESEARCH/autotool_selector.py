"""
AutoTool: Efficient Tool Selection for LLM Agents
Based on arXiv:2511.14650 (AAAI 2026)

Key insight: Tool Usage Inertia - tools follow predictable sequential patterns
Graph-based approach reduces LLM inference cost by up to 30%
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict
from datetime import datetime
import json


@dataclass
class Tool:
    name: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolTransition:
    from_tool: str
    to_tool: str
    count: int = 1
    probability: float = 0.0


class ToolGraph:
    """
    Directed graph modeling tool transitions based on historical trajectories.

    Nodes = Tools
    Edges = Transition probabilities (capturing "tool usage inertia")
    """

    def __init__(self, inertia_threshold: float = 0.6):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.transitions: List[ToolTransition] = []
        self.inertia_threshold = inertia_threshold
        self.total_transitions: int = 0

    def add_trajectory(self, trajectory: List[str]) -> None:
        """Learn from a tool execution trajectory"""
        if len(trajectory) < 2:
            return

        for i in range(len(trajectory) - 1):
            from_tool = trajectory[i]
            to_tool = trajectory[i + 1]

            self.nodes.add(from_tool)
            self.nodes.add(to_tool)
            self.edges[from_tool][to_tool] += 1
            self.total_transitions += 1

    def add_trajectory_from_results(self, results: List[Dict[str, str]]) -> None:
        """Learn from execution results with tool names"""
        trajectory = [r.get("tool", "") for r in results if r.get("tool")]
        self.add_trajectory(trajectory)

    def calculate_probabilities(self) -> None:
        """Calculate transition probabilities from counts"""
        self.transitions = []

        for from_tool, to_tools in self.edges.items():
            total = sum(to_tools.values())

            for to_tool, count in to_tools.items():
                prob = count / total if total > 0 else 0.0
                self.transitions.append(
                    ToolTransition(
                        from_tool=from_tool,
                        to_tool=to_tool,
                        count=count,
                        probability=prob,
                    )
                )

    def get_next_tool(self, current_tool: str) -> Optional[str]:
        """
        Select next tool based on inertia.
        Returns None if inertia is below threshold (should use LLM).
        """
        if current_tool not in self.edges:
            return None

        to_tools = self.edges[current_tool]
        if not to_tools:
            return None

        total = sum(to_tools.values())
        max_count = max(to_tools.values())
        max_prob = max_count / total if total > 0 else 0.0

        if max_prob >= self.inertia_threshold:
            for to_tool, count in to_tools.items():
                if count == max_count:
                    return to_tool

        return None

    def get_transition_probability(self, from_tool: str, to_tool: str) -> float:
        """Get specific transition probability"""
        if from_tool not in self.edges:
            return 0.0

        to_tools = self.edges[from_tool]
        total = sum(to_tools.values())
        count = to_tools.get(to_tool, 0)

        return count / total if total > 0 else 0.0

    def has_high_inertia(self, from_tool: str, to_tool: str) -> bool:
        """Check if transition has high inertia"""
        return (
            self.get_transition_probability(from_tool, to_tool)
            >= self.inertia_threshold
        )

    def get_likely_sequence(self, start_tool: str, length: int = 5) -> List[str]:
        """Predict likely tool sequence based on inertia"""
        sequence = [start_tool]
        current = start_tool

        for _ in range(length - 1):
            next_tool = self.get_next_tool(current)
            if not next_tool:
                break
            sequence.append(next_tool)
            current = next_tool

        return sequence

    def to_dict(self) -> Dict:
        return {
            "nodes": list(self.nodes),
            "edges": {k: dict(v) for k, v in self.edges.items()},
            "total_transitions": self.total_transitions,
            "inertia_threshold": self.inertia_threshold,
        }


class AutoTool:
    """
    Efficient tool selection using graph-based inertia.

    Reduces LLM inference cost by up to 30% while maintaining
    competitive task completion rates.
    """

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        inertia_threshold: float = 0.6,
        use_graph_fallback: str = "llm",
    ):
        self.tools: Dict[str, Tool] = {t.name: t for t in (tools or [])}
        self.graph = ToolGraph(inertia_threshold=inertia_threshold)
        self.use_graph_fallback = use_graph_fallback
        self.llm_calls_saved: int = 0
        self.total_decisions: int = 0
        self.history: List[Dict[str, Any]] = []

    def register_tool(self, tool: Tool) -> None:
        """Register a tool"""
        self.tools[tool.name] = tool

    def register_tools(self, tools: List[Tool]) -> None:
        """Register multiple tools"""
        for tool in tools:
            self.register_tool(tool)

    def learn_from_trajectory(self, trajectory: List[str]) -> None:
        """Learn tool patterns from trajectory"""
        self.graph.add_trajectory(trajectory)
        self.graph.calculate_probabilities()

    def learn_from_history(self, history: List[Dict[str, Any]]) -> None:
        """Learn from execution history"""
        trajectory = [
            h.get("tool_used", h.get("tool", ""))
            for h in history
            if h.get("tool_used") or h.get("tool")
        ]
        if trajectory:
            self.learn_from_trajectory(trajectory)

    def select_tool(
        self,
        current_tool: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[str], str]:
        """
        Select next tool using graph inertia.

        Returns:
            Tuple of (selected_tool, selection_method)
            - ("tool_name", "graph") if selected via graph
            - (None, "no_inertia") if graph has no suggestion
            - (None, "llm_fallback") if should use LLM
        """
        self.total_decisions += 1

        if not current_tool:
            return None, "start"

        next_tool = self.graph.get_next_tool(current_tool)

        if next_tool:
            self.llm_calls_saved += 1
            return next_tool, "graph"

        return None, "no_inertia"

    def select_and_execute(
        self,
        task: str,
        current_tool: Optional[str] = None,
        executor: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Select and execute tool using AutoTool strategy.

        Args:
            task: Current task description
            current_tool: Currently active tool (or None for first tool)
            executor: Function to execute tool (tool_name, params) -> result

        Returns:
            Execution result with metadata
        """
        selected_tool, method = self.select_tool(current_tool)

        result = {
            "task": task,
            "current_tool": current_tool,
            "selected_tool": selected_tool,
            "selection_method": method,
            "llm_calls_saved": self.llm_calls_saved,
            "total_decisions": self.total_decisions,
        }

        if selected_tool and executor:
            result["execution"] = executor(selected_tool, {})
            self.history.append(
                {
                    "tool": selected_tool,
                    "method": method,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return result

    def get_efficiency_score(self) -> float:
        """Calculate LLM call reduction efficiency"""
        if self.total_decisions == 0:
            return 0.0
        return self.llm_calls_saved / self.total_decisions

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_tools": len(self.tools),
            "graph_nodes": len(self.graph.nodes),
            "graph_edges": sum(len(v) for v in self.graph.edges.values()),
            "total_decisions": self.total_decisions,
            "llm_calls_saved": self.llm_calls_saved,
            "efficiency_score": self.get_efficiency_score(),
        }


class ToolRegistry:
    """
    Tool registry with AutoTool-style inertia tracking.
    Integrates with OpenClaw's 352 tools.
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.autotool = AutoTool()
        self.categories: Dict[str, Set[str]] = defaultdict(set)

    def register(
        self,
        name: str,
        description: str = "",
        category: str = "general",
        parameters: Optional[Dict] = None,
    ) -> None:
        tool = Tool(name=name, description=description, parameters=parameters or {})
        self.tools[name] = tool
        self.categories[category].add(name)
        self.autotool.register_tool(tool)

    def learn_from_trajectory(self, trajectory: List[str]) -> None:
        self.autotool.learn_from_trajectory(trajectory)

    def select_next(self, current_tool: str) -> Tuple[Optional[str], str]:
        return self.autotool.select_tool(current_tool)

    def get_tools_by_category(self, category: str) -> List[Tool]:
        tool_names = self.categories.get(category, set())
        return [self.tools[name] for name in tool_names if name in self.tools]

    def get_stats(self) -> Dict[str, Any]:
        stats = self.autotool.get_stats()
        stats["categories"] = len(self.categories)
        stats["total_tools"] = len(self.tools)
        return stats


def demo():
    print("=" * 60)
    print("AutoTool: Efficient Tool Selection Demo")
    print("=" * 60)

    registry = ToolRegistry()

    registry.register("search", "Search for information", "research")
    registry.register("analyze", "Analyze data", "analysis")
    registry.register("write", "Write content", "writing")
    registry.register("review", "Review and refine", "review")
    registry.register("submit", "Submit result", "final")

    print("\nRegistered tools:")
    for name in registry.tools:
        print(f"  - {name}")

    trajectory = [
        "search",
        "analyze",
        "write",
        "review",
        "search",
        "analyze",
        "write",
        "review",
        "search",
        "analyze",
        "write",
        "submit",
    ]
    registry.learn_from_trajectory(trajectory)

    print(f"\nLearned from {len(trajectory)} tool invocations")
    print(f"Graph nodes: {len(registry.autotool.graph.nodes)}")
    print(f"Graph edges: {sum(len(v) for v in registry.autotool.graph.edges.values())}")

    print("\n--- Tool Selection ---")

    current = "search"
    for i in range(5):
        next_tool, method = registry.select_next(current)
        print(f"  {i + 1}. {current} -> {next_tool} (via {method})")
        if next_tool:
            current = next_tool
        else:
            break

    print(f"\nEfficiency score: {registry.autotool.get_efficiency_score():.1%}")
    print(
        f"LLM calls saved: {registry.autotool.llm_calls_saved}/{registry.autotool.total_decisions}"
    )

    print("\n--- Predicted Sequence ---")

    sequence = registry.autotool.graph.get_likely_sequence("search", length=5)
    print(f"  search -> {' -> '.join(sequence[1:])}")


if __name__ == "__main__":
    demo()
