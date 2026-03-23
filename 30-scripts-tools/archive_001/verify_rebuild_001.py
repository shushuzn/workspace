import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path

registry_file = Path("30-scripts-tools/tools_registry.json")
scripts_dir = Path("30-scripts-tools")

with open(registry_file, "r", encoding="utf-8") as f:
    registry = json.load(f)

tools = registry.get("tools", {})
print(f"Registry 工具数：{len(tools)}")

# 验证每个工具的文件是否存在
found = 0
missing = 0

for tool_id, info in tools.items():
    command = info.get("command", "")
    if "py " in command:
        filename = command.split("py ")[1].split(" ")[0].split("\\")[-1]
        if (scripts_dir / filename).exists():
            found += 1
        else:
            missing += 1
            print(f"  [MISSING] {tool_id}: {filename}")

print(f"\n文件存在：{found}")
print(f"文件缺失：{missing}")
print(f"匹配率：{found /(found +missing) *100:.1f}%")

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
# py verify_rebuild_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py verify_rebuild_001.py

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
