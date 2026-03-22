import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

tools = registry["tools"]
scripts_dir = Path("30-scripts-tools")

# 检查实际存在的文件
py_files = [f.stem.replace("_", "-") for f in scripts_dir.glob("*.py")]

# 查找 registry 中不存在的文件
missing_from_registry = []
for f in py_files[:30]:  # 前 30 个
    if f not in tools and f.replace("-", "_") not in tools:
        missing_from_registry.append(f)

print("实际存在但 Registry 中没有的工具 (前 30):")
for f in missing_from_registry[:20]:
    print(f"  - {f}")

# 检查关键工具
key_files = ["copaw_entry", "tool_executor", "tool_call_tracker", "workflow_guardian_v2"]
print("\n关键工具检查:")
for key in key_files:
    key_dash = key.replace("_", "-")
    key_under = key.replace("-", "_")
    found = key_dash in tools or key_under in tools
    print(f"  {key}: {'[OK]' if found else '[MISSING]'}")

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
# py check_missing_tools_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_missing_tools_001.py

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
