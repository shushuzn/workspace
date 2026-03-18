#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scan for eval/exec and os.system usage"""

import os
import re
from pathlib import Path

WORKSPACE = Path("D:/OpenClaw/workspace/30-scripts-tools")

# Patterns
EVAL_EXEC_PATTERN = re.compile(r'\b(eval|exec)\s*\(')
OS_SYSTEM_PATTERN = re.compile(r'\bos\.system\s*\(')

eval_exec_files = []
os_system_files = []

for py_file in WORKSPACE.rglob("*.py"):
    # Skip archive directories
    if '99-archive' in str(py_file) or 'intentkit' in str(py_file):
        continue
    
    try:
        content = py_file.read_text(encoding='utf-8')
        
        if EVAL_EXEC_PATTERN.search(content):
            eval_exec_files.append(str(py_file.relative_to(WORKSPACE.parent.parent)))
        
        if OS_SYSTEM_PATTERN.search(content):
            os_system_files.append(str(py_file.relative_to(WORKSPACE.parent.parent)))
    except:
        continue

print("=" * 60)
print("P1 PRIORITY FIXES - Files to Update")
print("=" * 60)
print(f"\nEval/Exec files: {len(eval_exec_files)}")
for f in eval_exec_files[:10]:
    print(f"  - {f}")

print(f"\nOS.system files: {len(os_system_files)}")
for f in os_system_files[:15]:
    print(f"  - {f}")

print("\n" + "=" * 60)
print(f"Total: {len(eval_exec_files)} eval/exec + {len(os_system_files)} os.system")
print("=" * 60)
