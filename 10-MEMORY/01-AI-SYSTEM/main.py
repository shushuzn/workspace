"""
AI Memory System - Main entry point.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_memory_system.memory_system import MemorySystem

__version__ = "0.1.0"


def main():
    print(f"AI Memory System v{__version__}")
    print("-" * 40)

    ms = MemorySystem()
    print(f"Initialized: {ms}")

    ms.add("user_name", "Alice", memory_type="short")
    ms.add("user_email", "alice@example.com", memory_type="short")
    ms.add("last_project", "OpenClaw memory system", memory_type="long")
    ms.add("preferred_language", "Chinese", memory_type="long")

    print(f"After adding: {ms}")
    print(f"Stats: {ms.stats()}")

    print("\nSearch 'alice':")
    results = ms.search("alice")
    for r in results:
        print(f"  [{r['source']}] {r['key']}: {r['value']} (score: {r['score']:.2f})")

    print("\nGet context for 'user':")
    context = ms.get_context("user")
    print(context)

    print("\nDistill memories:")
    distilled = ms.distill()
    print(f"  Summary: {distilled['summary']}")
    print(f"  Insights: {distilled['key_insights']}")

    ms.save()
    print("\nMemory saved to disk.")

    ms.clear("short")
    print(f"After clearing short-term: {ms}")

    print("\nDone!")


if __name__ == "__main__":
    main()
