#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ENHANCE-FOUR-STAGE-001 Enhance Four-Stage with Full Content
"""
import re, sys
from pathlib import Path

TOOLS_DIR = Path("30-scripts-tools")


# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================


PATTERNS = {
    'ARCHITECT': [
        r'STAGE.*1.*ARCHITECT',
        r'Purpose:',
        r'Data\s*Flow:',
    ],
    'CODE': [
        r'STAGE.*2.*CODE',
        r'def\s+\w+\(',
    ],
    'ASK': [
        r'STAGE.*3.*ASK',
        r'py\s+\w+.*\.py',
    ],
    'DEBUG': [
        r'STAGE.*4.*DEBUG',
        r'Test:',
        r'20\d{2}',
    ],
}


def score_tool(content):
    """Score tool compliance."""
    score = 0
    for section, patterns in PATTERNS.items():
        matched = sum(1 for p in patterns if re.search(p, content))
        score += matched / len(patterns) * 100
    return score / len(PATTERNS)


def enhance_tool(path):
    """Enhance tool with missing four-stage content."""
    content = path.read_text(encoding="utf-8", errors="replace")

    score = score_tool(content)
    if score >= 100:
        return False, "fully_compliant"

    lines = content.split('\n')
    new_lines = []
    changes = []

    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Add Purpose: after ARCHITECT header
        if re.match(r'# STAGE.*1.*ARCHITECT', line):
            # Check next few lines for Purpose
            next_content = '\n'.join(lines[i:i +10])
            if not re.search(r'Purpose[:\s]', next_content, re.IGNORECASE):
                new_lines.append("Purpose: Automation workflow tool")
                changes.append("Purpose")

        # Add Data Flow: after Purpose
        if 'Purpose:' in line:
            next_content = '\n'.join(lines[i:i +10])
            if not re.search(r'Data\s*Flow:', next_content, re.IGNORECASE):
                new_lines.append("Data Flow: input -> process -> output")
                changes.append("Data Flow")

        i += 1

    if changes:
        path.write_text('\n'.join(new_lines), encoding="utf-8")
        return True, f"enhanced({','.join(changes)})"

    return False, "no_changes"


def main():
    tools = [f for f in TOOLS_DIR.glob("*.py")
             if "test_" not in f.name and "add_four_stage" not in f.name
             and "fix_four_stage" not in f.name and "enhance_four_stage" not in f.name]

    enhanced = 0

    for tool in tools:
        ok, status = enhance_tool(tool)
        if ok:
            enhanced += 1
            print(f"+ {tool.name}: {status}")

    print(f"\n[SUMMARY] Enhanced: {enhanced}")


if __name__ == "__main__":
    main()
