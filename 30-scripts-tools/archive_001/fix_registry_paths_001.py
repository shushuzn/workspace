#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIX-REGISTRY-PATHS-001 修复注册表路径字段
"""
import json
from pathlib import Path

TOOLS_DIR = Path("30-scripts-tools")
REGISTRY_FILE = Path("30-scripts-tools/tools_registry.json")


def fix_registry_paths():
    """修复注册表中的 file_path 字段"""
    if not REGISTRY_FILE.exists():
        print("[ERROR] Registry file not found")
        return

    registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))

    fixed = 0
    missing = 0

    tools = registry.get("tools", {})
    for tool_id, tool in tools.items():
        # Convert tool_id to snake_case filename
        filename = tool_id.lower().replace("-", "_") + ".py"
        file_path = f"30-scripts-tools/{filename}"

        if Path(file_path).exists():
            tool["file_path"] = file_path
            fixed += 1
        else:
            missing += 1
            print(f"  [MISSING] {tool_id} -> {filename}")

    # Save updated registry
    registry["version"] = "2.0.1"
    registry["last_updated"] = "2026-03-21"
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n[SUMMARY]")
    print(f"  Fixed: {fixed}")
    print(f"  Missing files: {missing}")
    print(f"  Registry updated to v2.0.1")


if __name__ == "__main__":
    fix_registry_paths()
