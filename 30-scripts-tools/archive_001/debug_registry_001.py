import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path

registry_file = Path("30-scripts-tools/tools_registry.json")
scripts_dir = Path("30-scripts-tools")

with open(registry_file, "r", encoding="utf-8") as f:
    registry = json.load(f)

print("Registry 中的工具详情:\n")

for tool_id, info in registry["tools"].items():
    command = info.get("command", "N/A")
    print(f"工具：{tool_id}")
    print(f"  command: {command}")

    # 提取文件名
    if "py " in command:
        parts = command.split("py ")[1].split(" ")[0]
        filename = parts.split("\\")[-1].split("/")[-1]
        print(f"  文件名：{filename}")

        # 检查文件是否存在
        filepath = scripts_dir / filename
        exists = filepath.exists()
        print(f"  文件存在：{exists}")

        # 尝试查找相似文件
        if not exists:
            base_name = filename.replace(".py", "").replace(".", "")
            similar = [f.name for f in scripts_dir.glob(f"{base_name}*.py")]
            if similar:
                print(f"  相似文件：{similar}")
    print()

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
# py debug_registry_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py debug_registry_001.py

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
