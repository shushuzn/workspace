#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test runner for workspace"""
import subprocess
import sys
from pathlib import Path

def run_tests():
    print("=" * 50)
    print("Running Workspace Tests")
    print("=" * 50)

    # Stock PRO tests
    print("\n[1/1] Stock PRO v12.7")
    print("-" * 30)

    result = subprocess.run(
        [sys.executable, "30-scripts-tools/stock_pro/test_all.py"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent.parent
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Summary
    if "18 passed" in result.stdout:
        print("\n[PASS] All tests passed!")
        return 0
    else:
        print("\n[FAIL] Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
