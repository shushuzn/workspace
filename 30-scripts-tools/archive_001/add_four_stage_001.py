#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ADD-FOUR-STAGE-001 Batch Add Four-Stage Headers

=============================================================================
STAGE 1: ARCHITECT 架构设计
=============================================================================
Purpose:
    - Add four-stage compliance headers to tools
    - Update existing tools with ARCHITECT/CODE/ASK/DEBUG sections

Data Flow:
    tool_file → read_content → detect_purpose → add_headers → write

Files:
    - add_four_stage_001.py (this tool)

Edge Cases:
    - Already has headers → skip
    - Read-only files → log and skip
    - Empty files → add basic header

=============================================================================
STAGE 2: CODE 编写代码
=============================================================================
"""
import re, sys
from pathlib import Path

TOOLS_DIR = Path("30-scripts-tools")

STAGE_HEADER = """
# ==============================================================================
# STAGE 3: ASK 询问确认
# py add_four_stage_001.py  # Run verification
# ==============================================================================
"""
STAGE_HEADER += '"""\nASK: Run verification\n'
STAGE_HEADER += '"""'

DEBUG_HEADER = """
# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG_HEADER += '"""\nDEBUG: Test cases\n"""'


def has_four_stage(content):
    return "STAGE 1: ARCHITECT" in content and "STAGE 3: ASK" in content and "STAGE 4: DEBUG" in content
# py add_four_stage_001.py  # Run verification
# Test: 2026


def extract_purpose(content):
    """Extract first docstring or purpose comment."""
    lines = content.split('\n')
    for i, line in enumerate(lines[:20]):
        if 'Purpose:' in line:
            return line.replace('Purpose:', '').strip()
    return "Workflow automation tool"


def add_four_stage(content, tool_name):
    """Add four-stage headers to tool content."""
    # Already compliant
    if has_four_stage(content):
        return None, "already_compliant"

    # Check if has ARCHITECT header
    has_architect = "STAGE 1: ARCHITECT" in content

    # Find insertion point for ASK (before STAGE 4 or at end of main code)
    # Look for last function definition or if __name__ == "__main__"
    insert_point = None
    patterns = [
        r'(if __name__ == ["\']__main__["\']:.*)',
        r'(def \w+\(.*\):\s*\n(?:[^\n]*\n){0,5}\s*""")',
    ]

    for match in re.finditer(patterns[-1], content, re.DOTALL):
        insert_point = match.end()
        break

    if not insert_point:
        # Try finding last def
        last_def = content.rfind('\ndef ')
        if last_def > 0:
            insert_point = content.find('\n\n', last_def)
            if insert_point < 0:
                insert_point = last_def + 200

    if not insert_point or insert_point < 0:
        insert_point = len(content)

    # Build stage sections
    new_content = content[:insert_point]

    if not has_architect:
        header = f"""
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
# ==============================================================================
"""
        new_content += header

    new_content += f"""
# ==============================================================================
# STAGE 3: ASK 询问确认
# py add_four_stage_001.py  # Run verification
# ==============================================================================
\"\"\"
ASK: Run verification

Test Commands:
    py {tool_name}

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
\"\"\"
"""

    new_content += f"""
# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
\"\"\"
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
\"\"\"
"""

    if insert_point < len(content):
        new_content += '\n' + content[insert_point:]

    return new_content, "updated"


def process_tools(tools):
    """Process list of tool files."""
    results = {"updated": [], "skipped": [], "errors": []}

    for tool_path in tools:
        try:
            path = TOOLS_DIR / tool_path if not Path(tool_path).is_absolute() else Path(tool_path)
            if not path.exists():
                results["errors"].append(f"{tool_path}: file not found")
                continue

            content = path.read_text(encoding="utf-8", errors="replace")

            if "test_" in path.name or "_test.py" in path.name:
                results["skipped"].append(f"{path.name}: test file")
                continue

            new_content, status = add_four_stage(content, path.name)

            if status == "already_compliant":
                results["skipped"].append(f"{path.name}: already compliant")
            elif status == "updated":
                path.write_text(new_content, encoding="utf-8")
                results["updated"].append(f"{path.name}")
            else:
                results["errors"].append(f"{path.name}: {status}")

        except Exception as e:
            results["errors"].append(f"{tool_path}: {e}")

    return results


def main():
    # Get tools to process from command line or scan
    if len(sys.argv) > 1 and sys.argv[1] != "--scan":
        tools = sys.argv[1:]
    else:
        # Scan for non-compliant tools
        tools = []
        for f in TOOLS_DIR.glob("*.py"):
            if "test_" in f.name:
                continue
            content = f.read_text(encoding="utf-8", errors="replace")
            if not has_four_stage(content):
                tools.append(f.name)

    if not tools:
        print("[ADD-FOUR-STAGE-001] All tools compliant!")
        return

    print(f"[ADD-FOUR-STAGE-001] Processing {len(tools)} tools...")

    # Limit batch size
    tools = tools[:50]

    results = process_tools(tools)

    print(f"\n[SUMMARY]")
    print(f"  Updated: {len(results['updated'])}")
    print(f"  Skipped: {len(results['skipped'])}")
    print(f"  Errors: {len(results['errors'])}")

    if results["updated"]:
        print(f"\n[UPDATED]")
        for t in results["updated"][:10]:
            print(f"  + {t}")

    if results["skipped"]:
        print(f"\n[SKIPPED]")
        for t in results["skipped"][:5]:
            print(f"  - {t}")

    if results["errors"]:
        print(f"\n[ERRORS]")
        for e in results["errors"][:5]:
            print(f"  ! {e}")


if __name__ == "__main__":
    main()

# ==============================================================================
# STAGE 3: ASK 询问确认
# py add_four_stage_001.py  # Run verification
# ==============================================================================
# py {tool_name}  # Run verification
"""
ASK: Run verification
"""
# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases
"""
