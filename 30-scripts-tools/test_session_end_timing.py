#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to measure session_end.py execution time"""

import subprocess
import time
import sys
import codecs

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("="*60)
print("SESSION END SCRIPT - TIMING TEST")
print("="*60)
print()

start_time = time.time()

result = subprocess.run(
    ["py", "30-scripts-tools\\session_end.py", "Test: Timing measurement"],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

end_time = time.time()
elapsed = end_time - start_time

print("\n" + "="*60)
print(f"TOTAL EXECUTION TIME: {elapsed:.2f} seconds")
print("="*60)

print("\nBreakdown by step (estimated):")
print(f"  Step 1: Session Compression     ~5-8 seconds")
print(f"  Step 2: Context Verification    ~2-3 seconds")
print(f"  Step 3: Daily Note Check        ~0.1 seconds")
print(f"  Step 4: Git Status              ~0.5 seconds")
print(f"  Step 5: Git Add                 ~0.5 seconds")
print(f"  Step 6: Git Commit              ~1-2 seconds")
print(f"  Step 7: Git Push                ~3-5 seconds")
print(f"  --------------------------------------------")
print(f"  Total Estimated:                ~12-21 seconds")
print()
print(f"  Actual Time:                    {elapsed:.2f} seconds")
print()

if elapsed < 30:
    print("✅ Performance: EXCELLENT (<30 seconds)")
elif elapsed < 60:
    print("✅ Performance: GOOD (<60 seconds)")
else:
    print("⚠️  Performance: SLOW (>60 seconds)")

print("\nScript output:")
print("-"*60)
print(result.stdout)
if result.stderr:
    print("\nErrors:")
    print(result.stderr)
