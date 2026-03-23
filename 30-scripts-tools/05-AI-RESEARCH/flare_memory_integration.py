"""
AI Agent Research Integration Module
Integrates FLARE, MEMORA, ABC, and HiMAC into OpenClaw

Usage:
    from flare_memory_integration import get_flare_planner, get_memory_store

    planner = get_flare_planner()
    store = get_memory_store()
"""

from typing import Optional
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def get_flare_planner():
    """Get FLARE Planner instance for future-aware planning"""
    try:
        sys.path.insert(0, str(SCRIPT_DIR / "05-AI-RESEARCH"))
        from flare_planner import FLAREPlanner

        return FLAREPlanner(
            lookahead_steps=3, value_propagation=True, commitment_threshold=0.7
        )
    except ImportError as e:
        print(f"Warning: Could not import FLARE Planner: {e}")
        return None


def get_harmonic_memory():
    """Get Harmonic Memory Store instance for dual-layer memory"""
    try:
        sys.path.insert(0, str(SCRIPT_DIR / "13-memory"))
        from harmonic_memory import HarmonicMemoryStore

        return HarmonicMemoryStore()
    except ImportError as e:
        print(f"Warning: Could not import Harmonic Memory: {e}")
        return None


def get_agent_contract(name: str = "openclaw"):
    """Get Agent Contract for runtime enforcement"""
    try:
        sys.path.insert(0, str(SCRIPT_DIR / "13-memory"))
        from agent_contracts import ContractBuilder, ViolationType, Severity

        return ContractBuilder(name=name).build()
    except ImportError as e:
        print(f"Warning: Could not import Agent Contracts: {e}")
        return None


def get_himac_executor():
    """Get HiMAC Executor for hierarchical planning"""
    try:
        sys.path.insert(0, str(SCRIPT_DIR / "05-AI-RESEARCH"))
        from himac_executor import HiMACExecutor, MacroPlanner, MicroExecutor

        return HiMACExecutor(planner=MacroPlanner(), executor=MicroExecutor())
    except ImportError as e:
        print(f"Warning: Could not import HiMAC Executor: {e}")
        return None


FLARE_PLANNER = None
HARMONIC_MEMORY = None
AGENT_CONTRACT = None
HIMAC_EXECUTOR = None


def init_agents():
    """Initialize all agent components"""
    global FLARE_PLANNER, HARMONIC_MEMORY, AGENT_CONTRACT, HIMAC_EXECUTOR

    FLARE_PLANNER = get_flare_planner()
    HARMONIC_MEMORY = get_harmonic_memory()
    AGENT_CONTRACT = get_agent_contract()
    HIMAC_EXECUTOR = get_himac_executor()

    return {
        "flare": FLARE_PLANNER is not None,
        "memory": HARMONIC_MEMORY is not None,
        "contract": AGENT_CONTRACT is not None,
        "himac": HIMAC_EXECUTOR is not None,
    }


def demo():
    print("=" * 60)
    print("OpenClaw AI Agent Research Integration Demo")
    print("=" * 60)

    status = init_agents()
    print(f"\nInitialization status:")
    for component, loaded in status.items():
        print(f"  {component}: {'OK' if loaded else 'FAILED'}")

    if FLARE_PLANNER:
        print("\n--- FLARE Planner ---")
        plan = FLARE_PLANNER.plan("Research AI agents and write report")
        print(f"Generated {len(plan.actions)} actions")
        print(f"Committed: {plan.metadata.get('committed_count', 0)}")

    if HARMONIC_MEMORY:
        print("\n--- Harmonic Memory ---")
        HARMONIC_MEMORY.add(
            "Important research finding about LLM planning",
            entities=["LLM", "planning"],
        )
        HARMONIC_MEMORY.add(
            "Memory optimization saves 98% tokens", entities=["memory", "optimization"]
        )
        results = HARMONIC_MEMORY.retrieve("planning", mode="harmonic", limit=2)
        print(f"Retrieved {len(results)} memories")

    if HIMAC_EXECUTOR:
        print("\n--- HiMAC Executor ---")
        blueprint = HIMAC_EXECUTOR.planner.generate_blueprint("Build a research agent")
        print(f"Generated {len(blueprint.subgoals)} subgoals")


if __name__ == "__main__":
    demo()
