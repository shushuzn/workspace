#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find eval/exec/os.system in specific files"""

import re
import sys
import codecs
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

files_to_check = [
    "30-scripts-tools/auto-critic.py",
    "30-scripts-tools/critical_issue_detector.py",
    "30-scripts-tools/issue_scanner.py",
    "30-scripts-tools/quality_gate_check.py",
    "30-scripts-tools/security_auditor.py",
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
        if re.search(r'\b(eval|exec)\s*\(', line) or 'os.system' in line:
            # Skip comments
            if line.strip().startswith('#'):
                continue
            print(f"  Line {i}: {line.strip()[:120]}")
            found = True
    
    if not found:
        print("  (No unsafe calls found)")
