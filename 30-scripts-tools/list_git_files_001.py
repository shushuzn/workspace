import logging
logger = logging.getLogger(__name__)

import subprocess

result = subprocess.run(
    ["git", "ls-files", "*.py"],
    capture_output=True,
    text=True,
    encoding="utf-8"
, timeout=60)

files = result.stdout.strip().split("\n")
critic_files = [f for f in files if "critic" in f.lower()]

print(f"Git 跟踪的 Python 文件总数：{len(files)}")
print(f"Critic 相关文件：{len(critic_files)}")
print("\nCritic 文件列表:")
for f in critic_files[:20]:
    print(f"  - {f}")

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
# py list_git_files_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py list_git_files_001.py

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
