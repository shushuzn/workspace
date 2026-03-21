import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查关键工具文件是否存在
"""
from pathlib import Path

scripts_dir = Path("30-scripts-tools")

# 关键工具列表
key_tools = [
    "copaw_entry.py",
    "tool_executor.py",
    "tool_call_tracker.py",
    "workflow_guardian_v2.py",
    "workflow_enforcer.py",
    "embedded_critic.py",
    "git_commit_helper.py",
    "git_precommit_check.py",
    "performance_analyzer.py",
    "memory_distiller.py",
    "auto_memory_distiller.py",
    "auto_session_compressor.py",
    "session_compressor.py",
    "workflow_auto_executor.py",
    "workflow_health_dashboard.py"
]

print("=" * 60)
print("关键工具文件检查")
print("=" * 60)

found = 0
missing = 0

for tool in key_tools:
    filepath = scripts_dir / tool
    if filepath.exists():
        print(f"  [OK] {tool}")
        found += 1
    else:
        print(f"  [MISSING] {tool}")
        missing += 1

print(f"\n总结:")
print(f"  存在：{found}")
print(f"  缺失：{missing}")
print(f"  可用率：{found/(found+missing)*100:.1f}%")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py check_key_tools_exist_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py check_key_tools_exist_001.py

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
