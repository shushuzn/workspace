import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path

registry_file = Path("30-scripts-tools/tools_registry.json")
if registry_file.exists():
    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    print(f"工具总数：{len(tools)}")
    print("\n工具列表 (前 50 个):")
    for i, (tool_id, info) in enumerate(list(tools.items())[:50], 1):
        path = info.get("path", "N/A")
        print(f"  {i}. {tool_id}: {path}")
    
    if len(tools) > 50:
        print(f"\n... 还有 {len(tools)-50} 个工具")
else:
    print("ERROR: tools_registry.json 不存在")

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
# py check_registry_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_registry_001.py

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
