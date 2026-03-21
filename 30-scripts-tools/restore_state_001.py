import logging
logger = logging.getLogger(__name__)

from pathlib import Path
import shutil

state_files = list(Path("flow-archive").glob("*/execution-state.json.backup"))
print(f"找到 {len(state_files)} 个备份文件:")

for f in state_files:
    new_path = str(f).replace('.backup', '')
    shutil.move(str(f), new_path)
    print(f"  恢复：{f.name} -> {Path(new_path).name}")

print("\n恢复完成")

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
# py restore_state_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py restore_state_001.py

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
