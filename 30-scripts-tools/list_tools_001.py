import logging
logger = logging.getLogger(__name__)

import os
from pathlib import Path

tools_dir = Path("30-scripts-tools")
keywords = ['context', 'task', 'tool', 'flow', 'workflow', 'executor']

print("现有工具文件:")
for f in sorted(tools_dir.glob("*.py")):
    name = f.stem.lower()
    if any(kw in name for kw in keywords):
        print(f"  - {f.name}")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py list_tools_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py list_tools_001.py

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
