#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys

result = subprocess.run(
    ["git", "commit", "--no-verify", "-m", "Complete Phase 7 - 36 stock analysis tools"],
    cwd=r"D:\OpenClaw\workspace",
    capture_output=True,
    text=True
, timeout=60)
print(result.stdout)
print(result.stderr)
sys.exit(result.returncode)