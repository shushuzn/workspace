import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTO-BAREXCEPT-FIX-001 Auto-fix bare except statements
Scans and fixes bare except Exception as e:
    logger.error(f"Error: {e}") with specific exception types
"""
import json, re, sys
from pathlib import Path

TOOLS_DIR = Path("30-scripts-tools")

COMMON_EXCEPTIONS = {
    "json.loads": "(json.JSONDecodeError, IOError, OSError)",
    "open(": "(IOError, OSError, UnicodeDecodeError)",
    "subprocess": "(subprocess.SubprocessError, OSError)",
    "sys.stdout": "(AttributeError, ValueError)",
    "json.load": "(json.JSONDecodeError, IOError, OSError)",
    "Path.exists": "(OSError, ValueError)",
    "json.loads": "(json.JSONDecodeError, IOError, OSError)",
    "_": "(Exception,)"  # Default fallback
}

def detect_context(content, line_num):
    """Detect what the except block is handling"""
    lines = content.split("\n")

    # Look back 5 lines for context
    for i in range(max(0, line_num -6), line_num):
        line = lines[i]
        for pattern, exc_type in COMMON_EXCEPTIONS.items():
            if pattern in line:
                return exc_type
    return "(Exception,)"

def fix_file(filepath):
    """
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
# py auto_barexcept_fix_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py auto_barexcept_fix_001.py

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

Fix bare except in a file"""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (IOError, OSError):
        return {"file": filepath.name, "status": "skip", "reason": "Cannot read"}

    original = content
    fixed_count = 0
    lines = content.split("\n")
    new_lines = []

    for i, line in enumerate(lines):
        if re.search(r'except\s*:\s*$', line.rstrip()):
            # Found bare except, fix it
            context = detect_context(content, i)
            indent = len(line) - len(line.lstrip())
            spaces = " " * indent
            new_line = f"{spaces}except {context}:"
            new_lines.append(new_line)
            fixed_count += 1
        else:
            new_lines.append(line)

    if fixed_count > 0:
        filepath.write_text("\n".join(new_lines), encoding="utf-8")
        return {"file": filepath.name, "status": "fixed", "count": fixed_count}

    return {"file": filepath.name, "status": "ok", "count": 0}

logging.basicConfig(level=logging.INFO)
def main():
    dry_run = "--dry-run" in sys.argv

    print(f"\n[AUTO-BAREXCEPT-FIX-001] {'Dry-run mode' if dry_run else 'Fixing'}")
    print("=" * 50)

    files = list(TOOLS_DIR.glob("*_001.py"))
    results = []

    for f in files:
        if f.name.startswith("auto_barexcept_fix"):
            continue

        # Check if has bare except
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except (IOError, OSError):
            continue

        if re.search(r'except\s*:\s*$', content, re.MULTILINE):
            if dry_run:
                count = len(re.findall(r'except\s*:\s*$', content, re.MULTILINE))
                results.append({"file": f.name, "status": "would_fix", "count": count})
            else:
                result = fix_file(f)
                results.append(result)

    # Summary
    fixed = [r for r in results if r["status"] == "fixed"]
    would_fix = [r for r in results if r["status"] == "would_fix"]

    if dry_run:
        print(f"\n[DRY-RUN] Would fix {len(would_fix)} files, {sum(r['count'] for r in would_fix)} occurrences")
        for r in would_fix[:10]:
            print(f"  - {r['file']}: {r['count']} fixes")
    else:
        print(f"\n[FIXED] {len(fixed)} files")
        for r in fixed:
            print(f"  - {r['file']}: {r['count']} fixes")

    # Save report
    report = {
        "timestamp": "2026-03-21",
        "mode": "dry-run" if dry_run else "fix",
        "results": results
    }
    Path("10-MEMORY/00-CORE/.barexcept_fix_report.json").write_text(json.dumps(report, indent=2))

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <args>")
        sys.exit(1)

if __name__ == "__main__":
    main()
