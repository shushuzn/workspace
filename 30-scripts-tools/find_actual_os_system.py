#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find ACTUAL os.system usage (not detection patterns)"""

import re
import sys
import codecs
from pathlib import Path

files_to_check = [
    "30-scripts-tools/auto_distill.py",
    "30-scripts-tools/critic_auto_fix.py",
    "30-scripts-tools/dashboard_integration.py",
    "30-scripts-tools/innovation_pattern_matcher.py",
    "30-scripts-tools/memory_engine_ops.py",
    "30-scripts-tools/memory_llm_hypothesis.py",
    "30-scripts-tools/parallel_executor.py",
    "30-scripts-tools/smart_notification.py",
    "30-scripts-tools/task_priority_scorer.py",
]

for file_path in files_to_check:
    path = Path(file_path)
    if not path.exists():
        print(f"NOT FOUND: {file_path}")
        continue
    
    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    print(f"\n{'='*60}")
    print(f"FILE: {file_path}")
    print('='*60)
    
    found = False
    for i, line in enumerate(lines, 1):
        # Look for actual os.system calls (not in strings/comments/regex patterns)
        if 'os.system(' in line and not line.strip().startswith('#'):
            # Check if it's in a regex pattern or string literal
            if r'os\.system' in line or '"os.system' in line or "'os.system" in line:
                continue  # This is a pattern string
            print(f"  Line {i}: {line.strip()[:120]}")
            found = True
    
    if not found:
        print("  (No actual os.system calls found)")
