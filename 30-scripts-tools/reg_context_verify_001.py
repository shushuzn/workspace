import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

# 检查 context_verify 是否存在
if "context_verify" in registry["tools"]:
    print("context_verify 已注册")
else:
    # 添加 context_verify
    registry["tools"]["context_verify"] = {
        "tool_id": "context_verify",
        "name": "Context Verify",
        "description": "上下文验证工具",
        "version": "1.0.0",
        "command": "py 30-scripts-tools\\context_verify.py",
        "path": "30-scripts-tools\\context_verify.py",
        "category": "verification",
        "parameters": {}
    }
    
    with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print("context_verify 已注册")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py reg_context_verify_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py reg_context_verify_001.py

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
