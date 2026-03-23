#!/usr/bin/env python
import sys
from pathlib import Path

workspace_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(workspace_root / "30-scripts-tools" / "13-memory"))

from agent_contracts import ContractBuilder


def get_contracts():
    return {
        "safety": ContractBuilder("safety")
        .with_precondition(lambda ctx: ctx.get("input") is not None)
        .build(),
        "memory": ContractBuilder("memory")
        .with_invariant(lambda result: result is not None)
        .build(),
    }


action = sys.argv[1] if len(sys.argv) > 1 else "list"
contracts = get_contracts()

if action == "list":
    print("Available Contracts:")
    for name in contracts:
        print(f"  - {name}")

elif action == "check":
    name = sys.argv[2] if len(sys.argv) > 2 else ""
    if name in contracts:
        print(f"Contract '{name}' exists")
    else:
        print(f"Contract '{name}' not found")

else:
    print(f"Unknown action: {action}")
    print("Available: list, check")
