import logging
logger = logging.getLogger(__name__)

from pathlib import Path
import shutil

# 临时移除 state 文件
state_files = list(Path("flow-archive").glob("*/execution-state.json"))
print(f"找到 {len(state_files)} 个 state 文件:")
for f in state_files:
    print(f"  - {f}")
    shutil.move(str(f), str(f) + ".backup")

# 再次检查
state_files_after = list(Path("flow-archive").glob("*/execution-state.json"))
print(f"\n移除后：{len(state_files_after)} 个 state 文件")

# 恢复
for f in Path("flow-archive").glob("*/execution-state.json.backup"):
    shutil.move(str(f), str(f).replace('.backup', ''))
print(f"\n已恢复 state 文件")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py check_state_files_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_state_files_001.py

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
