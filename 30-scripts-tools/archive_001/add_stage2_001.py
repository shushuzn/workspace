#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ADD-STAGE2-001 Add Missing STAGE 2: CODE Headers
"""
from pathlib import Path


def add_stage2(path):
    """Add STAGE 2: CODE header if missing."""
    content = path.read_text(encoding="utf-8", errors="replace")

    if "STAGE 2: CODE" in content:
        return False, "has_stage2"

    # Find insertion point (after STAGE 1, before STAGE 3 or end)
    lines = content.split('\n')
    insert_idx = None

    for i, line in enumerate(lines):
        if 'STAGE 1: ARCHITECT' in line:
            # Find end of STAGE 1 block (next section or blank line after)
            for j in range(i+1, min(i+20, len(lines))):
                if 'STAGE 3' in lines[j] or 'Purpose:' in lines[j]:
                    insert_idx = j
                    break
        if insert_idx:
            break

    if not insert_idx:
        # Put after first few lines of actual code
        insert_idx = 10

    # Build STAGE 2 section
    stage2 = """
# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================
"""

    new_lines = lines[:insert_idx] + [stage2] + lines[insert_idx:]
    path.write_text('\n'.join(new_lines), encoding="utf-8")
    return True, "added"


def main():
    TOOLS_DIR = Path("30-scripts-tools")
    updated = 0

    for f in sorted(TOOLS_DIR.glob("*_001.py")):
        if "test_" in f.name:
            continue
        ok, status = add_stage2(f)
        if ok:
            updated += 1
            print(f"+ {f.name}")

    print(f"\n[SUMMARY] Added STAGE 2 to {updated} tools")


if __name__ == "__main__":
    main()
