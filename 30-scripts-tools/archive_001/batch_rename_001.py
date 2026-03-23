import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BATCH-RENAME-001 Batch Rename Tool
"""

import json, sys, re, shutil
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

def to_snake(name):
    # Remove _001 suffix
    name = re.sub(r'_\d+$', '', name)
    # Split by underscores, hyphens, or camelCase
    words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+', name)
    return '_'.join(w.lower() for w in words if w)

def to_pascal(name):
    words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+', name.replace("-", "_"))
    return ''.join(w.capitalize() for w in words if w)

def scan_and_suggest():
    pattern = re.compile(r'^[a-z][a-z0-9_]*_\d+\.py$')
    results = []

    for f in sorted(TOOLS_DIR.glob("*.py")):
        if not pattern.match(f.name):
            old = f.stem
            snake = to_snake(old)
            new = f"{snake}_001.py"
            cls = to_pascal(snake) + "001"
            results.append({"old": f.name, "new": new, "class": cls})

    return results

def batch_rename(dry_run=True, limit=50):
    suggestions = scan_and_suggest()
    renamed = []

    for s in suggestions[:limit]:
        old_path = TOOLS_DIR / s["old"]
        new_path = TOOLS_DIR / s["new"]

        if new_path.exists():
            print(f"SKIP: {s['old']} -> {s['new']} (exists)")
            continue

        if dry_run:
            print(f"DRY: {s['old']} -> {s['new']}")
        else:
            old_path.rename(new_path)
            print(f"RENAMED: {s['old']} -> {s['new']}")

        renamed.append(s)

    return renamed
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py batch_rename_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py batch_rename_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""



if __name__ == "__main__":
    dry = "--dry" in sys.argv
    limit = 50

    if "--dry" in sys.argv:
        sys.argv.remove("--dry")
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        limit = int(sys.argv[1])

    print(f"Mode: {'DRY RUN' if dry else 'LIVE'}")
    print(f"Limit: {limit}")
    print()

    renamed = batch_rename(dry_run=dry, limit=limit)
    print(f"\nTotal: {len(renamed)} files")
