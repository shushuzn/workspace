#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Final cleanup - keep only core files"""
import shutil
from pathlib import Path

SRC = Path(__file__).parent
ARCHIVE = SRC / "archive_001"

# Core files to KEEP
KEEP = {
    "workflow.py",
    "archive_old.py",  # keep for reference
}

# Keep entire directories
KEEP_DIRS = {"stock_pro"}

# Move all other .py files to archive
moved = 0
for f in SRC.glob("*.py"):
    if f.name not in KEEP and f.is_file():
        dest = ARCHIVE / f.name
        counter = 1
        while dest.exists():
            dest = ARCHIVE / f"{f.stem}_{counter}{f.suffix}"
            counter += 1
        shutil.move(str(f), str(dest))
        print(f"  Archived: {f.name}")
        moved += 1

print(f"\nArchived {moved} files")
print(f"\nRemaining in 30-scripts-tools/:")
for f in sorted(SRC.glob("*")):
    if f.is_dir() or f.name in KEEP:
        print(f"  📁 {f.name}" if f.is_dir() else f"  📄 {f.name}")
