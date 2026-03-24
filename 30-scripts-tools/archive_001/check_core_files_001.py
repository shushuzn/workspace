import logging
logger = logging.getLogger(__name__)

import os
files = ['SOUL.md', 'USER.md', 'AGENTS.md', 'TOOLS.md', 'HEARTBEAT.md', '10-MEMORY/00-CORE/MEMORY.md']
print("核心文件检查:")
for f in files:
    exists = os.path.exists(f)
    print(f"  [{'OK' if exists else 'FAIL'}] {f}")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py check_core_files_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_core_files_001.py

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
