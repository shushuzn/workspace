#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Archive old numbered scripts"""
import shutil
from pathlib import Path

SRC = Path(__file__).parent
ARCHIVE = SRC / "archive_001"

# Keep these core files
KEEP = {
    "workflow.py",
    "archive_old.py",
    "fast_load.py",
}

# Pattern: *_001.py, *_002.py, etc.
old_files = list(SRC.glob("*_[0-9][0-9][0-9].py"))

# Also archive these patterns
extra_patterns = ["*brainstorm*", "*auto_*", "*add_*"]
for p in extra_patterns:
    old_files.extend(SRC.glob(p))

# Remove duplicates and keep files
old_files = [f for f in set(old_files) if f.name not in KEEP]

print(f"Found {len(old_files)} files to archive\n")
archived = 0

for f in sorted(old_files):
    dest = ARCHIVE / f.name
    counter = 1
    while dest.exists():
        dest = ARCHIVE / f"{f.stem}_{counter}{f.suffix}"
        counter += 1
    print(f"  {f.name}")
    shutil.move(str(f), str(dest))
    archived += 1

print(f"\nArchived {archived} files to archive_001/")

# Show remaining
remaining = [f.name for f in SRC.glob("*.py") if f.name not in KEEP]
print(f"Remaining .py files: {len(remaining)}")
for f in sorted(remaining)[:20]:
    print(f"  {f}")
if len(remaining) > 20:
    print(f"  ... and {len(remaining) -20} more")
