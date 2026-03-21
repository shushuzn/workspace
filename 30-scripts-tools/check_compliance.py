#!/usr/bin/env python
from pathlib import Path
from four_stage_checker_001 import FourStageChecker

checker = FourStageChecker()
TOOLS_DIR = Path("30-scripts-tools")

non_compliant = []
for f in sorted(TOOLS_DIR.glob("*_001.py")):
    if f.name.startswith("__"):
        continue
    result = checker.check_file(f)
    if not result.get("compliant"):
        non_compliant.append((f.name, result.get("score", 0), result.get("missing", [])))

print(f"Non-compliant: {len(non_compliant)}")
for name, score, miss in non_compliant[:30]:
    print(f"  {name}: {score:.0f}% missing {miss}")
