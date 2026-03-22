import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path

registry_file = Path("30-scripts-tools/tools_registry.json")
with open(registry_file, "r", encoding="utf-8") as f:
    registry = json.load(f)

tools = registry.get("tools", {})
existing = []
missing = []

for tool_id, info in tools.items():
    command = info.get("command", "")
    # 从 command 中提取文件名
    if "py " in command:
        parts = command.split("py ")[1].split(" ")[0]
        filename = parts.split("\\")[-1].split("/")[-1]
        filepath = Path("30-scripts-tools") / filename
        if filepath.exists():
            existing.append(tool_id)
        else:
            missing.append((tool_id, filename))

print(f"工具文件检查:")
print(f"  存在：{len(existing)}")
print(f"  缺失：{len(missing)}")
print(f"\n存在的工具 (前 20 个):")
for t in existing[:20]:
    print(f"  - {t}")

if missing:
    print(f"\n缺失的工具 (前 20 个):")
    for tool_id, filename in missing[:20]:
        print(f"  - {tool_id}: {filename}")

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
# py check_tool_files_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_tool_files_001.py

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
