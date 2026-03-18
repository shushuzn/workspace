#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify P1 fixes in target files"""

import sys
import codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import re
from pathlib import Path

# 目标文件（已修复的）
TARGET_FILES = [
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

WORKSPACE = Path(__file__).parent.parent

print("=" * 60)
print("P1 FIX VERIFICATION - TARGET FILES")
print("=" * 60)

all_clean = True

for file_rel in TARGET_FILES:
    file_path = WORKSPACE / file_rel
    if not file_path.exists():
        print(f"NOT FOUND: {file_rel}")
        continue
    
    content = file_path.read_text(encoding='utf-8')
    
    # 检查 os.system（排除注释和字符串）
    os_system_found = False
    for i, line in enumerate(content.split('\n'), 1):
        if 'os.system(' in line and not line.strip().startswith('#'):
            if r'os\.system' not in line and '"os.system' not in line and "'os.system" not in line:
                print(f"  FOUND: {file_rel}:{i} - {line.strip()[:80]}")
                os_system_found = True
                all_clean = False
    
    if not os_system_found:
        print(f"OK: {file_rel}")

print("=" * 60)
if all_clean:
    print("ALL TARGET FILES CLEAN!")
else:
    print("SOME FILES STILL HAVE ISSUES")
print("=" * 60)
