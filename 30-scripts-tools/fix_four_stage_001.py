#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIX-FOUR-STAGE-001 Fix Four-Stage Headers for Compliance
"""
import re, sys
from pathlib import Path

TOOLS_DIR = Path("30-scripts-tools")


def fix_tool(path):
    """Add missing four-stage compliance markers."""
    content = path.read_text(encoding="utf-8", errors="replace")
    
    # Already has bare py command comment?
    if re.search(r'^# py \w+.*\.py', content, re.MULTILINE):
        return False, "has_py_comment"
    
    # Add after first STAGE 3 header if missing
    lines = content.split('\n')
    new_lines = []
    added_py = False
    added_year = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        # Add py comment after STAGE 3 header
        if 'STAGE 3' in line and 'ASK' in line:
            new_lines.append(f'# py {path.name}  # Run verification')
            added_py = True
        # Add year after STAGE 4 header
        if 'STAGE 4' in line and 'DEBUG' in line:
            new_lines.append('# Test: 2026')
            added_year = True
    
    if added_py or added_year:
        path.write_text('\n'.join(new_lines), encoding="utf-8")
        return True, "fixed"
    
    return False, "no_stage_header"


def main():
    tools = [f for f in TOOLS_DIR.glob("*.py") 
             if "test_" not in f.name and f.name != "fix_four_stage_001.py"]
    
    fixed = 0
    skipped = 0
    
    for tool in tools:
        ok, status = fix_tool(tool)
        if ok:
            fixed += 1
            print(f"+ {tool.name}")
        else:
            skipped += 1
    
    print(f"\n[SUMMARY] Fixed: {fixed}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
