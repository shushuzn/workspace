"""
MEMORA Memory Integration for OpenClaw
Integrates HarmonicMemoryStore with existing memory system
"""

from typing import Dict, List, Optional
from pathlib import Path
import json


class MemoryBridge:
    """
    Bridge between HarmonicMemory and existing OpenClaw memory
    """

    def __init__(self, memory_store):
        self.store = memory_store
        self.openclow_memory_file = Path("13-memory/MEMORY.md")
        self.daily_dir = Path("13-memory")

    def add_from_memory_file(self, content: str, source: str = "memory_file") -> str:
        """Add content from existing MEMORY.md"""
        return self.store.add(content, source=source)

    def add_research_insight(
        self, insight: str, entities: List[str], paper_id: Optional[str] = None
    ) -> str:
        """Add research insight with entity tracking"""
        metadata = {"paper_id": paper_id} if paper_id else {}
        return self.store.add(
            insight, entities=entities, source="research", metadata=metadata
        )

    def retrieve_for_task(self, task: str, limit: int = 5) -> List[str]:
        """Retrieve memories relevant to current task"""
        entries = self.store.retrieve(task, mode="harmonic", limit=limit)
        return [e.primary_abstraction for e in entries]

    def get_detailed_memory(self, query: str, limit: int = 3) -> List[Dict]:
        """Get detailed memory values for a query"""
        entries = self.store.retrieve(query, mode="detailed", limit=limit)
        results = []
        for entry in entries:
            results.append(
                {
                    "memory_id": entry.memory_id,
                    "abstraction": entry.primary_abstraction,
                    "cue_anchors": entry.cue_anchors,
                    "concrete_values": [
                        v.to_dict() for v in entry.concrete_values[-3:]
                    ],
                }
            )
        return results

    def export_to_openclaw_format(self) -> Dict:
        """Export memories in OpenClaw format"""
        return self.store.to_dict()

    def import_from_openclaw(self, data: Dict) -> bool:
        """Import from OpenClaw format"""
        try:
            for memory_id, entry_data in data.get("abstractions", {}).items():
                self.store.abstractions[memory_id] = entry_data
            return True
        except Exception:
            return False


def create_memora_integration():
    """Create MEMORA integration with OpenClaw memory system"""
    try:
        import sys
        from pathlib import Path

        script_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(script_dir / "13-memory"))
        from harmonic_memory import HarmonicMemoryStore

        store = HarmonicMemoryStore()
        bridge = MemoryBridge(store)

        return {"success": True, "store": store, "bridge": bridge}
    except Exception as e:
        return {"success": False, "error": str(e)}


def demo():
    print("=" * 60)
    print("MEMORA Memory Integration Demo")
    print("=" * 60)

    result = create_memora_integration()

    if not result["success"]:
        print(f"Failed to initialize: {result['error']}")
        return

    bridge = result["bridge"]
    store = result["store"]

    print("\n--- Adding Research Memories ---")

    bridge.add_research_insight(
        "FLARE planner solves myopic commitment by future-aware lookahead",
        entities=["FLARE", "planner", "myopic"],
        paper_id="2601.22311",
    )

    bridge.add_research_insight(
        "MEMORA achieves 98% token reduction through dual-layer memory",
        entities=["MEMORA", "memory", "token"],
        paper_id="2602.03315",
    )

    bridge.add_research_insight(
        "HiMAC uses hierarchical macro-micro learning for long-horizon tasks",
        entities=["HiMAC", "hierarchical", "planning"],
        paper_id="2603.00977",
    )

    print(f"Added 3 research insights")
    print(f"Store stats: {store.stats()}")

    print("\n--- Retrieving for Task: 'planning agent' ---")

    results = bridge.retrieve_for_task("planning agent", limit=3)
    for i, r in enumerate(results):
        print(f"{i + 1}. {r[:60]}...")

    print("\n--- Getting Detailed Memory ---")

    details = bridge.get_detailed_memory("FLARE", limit=2)
    for d in details:
        print(f"\n{d['abstraction'][:50]}...")
        print(f"  Cue anchors: {d['cue_anchors']}")


if __name__ == "__main__":
    demo()
