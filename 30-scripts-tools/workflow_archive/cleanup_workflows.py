#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cleanup old workflow files - move to archive
"""
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ARCHIVE_DIR = SCRIPT_DIR / "workflow_archive"
ARCHIVE_DIR.mkdir(exist_ok=True)

# Files to keep (new unified workflow)
KEEP_FILES = {"workflow.py"}

# Find old workflow files to archive
pattern_files = [
    "*workflow*.py",
    "*_workflow*.py",
    "*workflow_*.py",
]

moved = set()
total = 0

for pattern in pattern_files:
    for f in SCRIPT_DIR.glob(pattern):
        if f.name not in KEEP_FILES and f.is_file():
            total += 1
            if f.name not in moved:
                dest = ARCHIVE_DIR / f.name
                # Handle duplicate names
                if dest.exists():
                    import time
                    dest = ARCHIVE_DIR / f"{f.stem}_{int(time.time())}{f.suffix}"
                print(f"  Moving: {f.name}")
                try:
                    shutil.move(str(f), str(dest))
                    moved.add(f.name)
                except Exception as e:
                    print(f"  Error: {e}")

print(f"\nMoved {len(moved)} files to {ARCHIVE_DIR}")
print(f"Total found: {total}")

# List what's left
remaining = list(SCRIPT_DIR.glob("*workflow*.py"))
print(f"\nRemaining workflow files: {[f.name for f in remaining]}")
