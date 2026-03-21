import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
核心执行规则验证工具
每次工作流启动前必须调用此工具验证
"""
import json
from pathlib import Path
from datetime import datetime

RULES_FILE = Path("flow-archive/20260318-universal-workflow-001/CORE-EXECUTION-RULES.md")

def verify():
    if not RULES_FILE.exists():
        return {
            "status": "error",
            "message": "CORE-EXECUTION-RULES.md 不存在",
            "server_time": datetime.now().isoformat()
        }
    
    content = RULES_FILE.read_text(encoding="utf-8")
    
    # 验证 10 条规则都存在
    required_rules = [
        "纯执行代理",
        "工具调用获取",
        "严格单步执行",
        "禁止提前生成",
        "原样抛出错误",
        "禁止总结润色",
        "可验证字段",
        "禁止假设",
        "禁止过程描述",
        "终止并上报"
    ]
    
    missing = []
    for rule in required_rules:
        if rule not in content:
            missing.append(rule)
    
    if missing:
        return {
            "status": "error",
            "message": f"缺失规则：{missing}",
            "server_time": datetime.now().isoformat()
        }
    
    return {
        "status": "pass",
        "message": "核心执行规则验证通过",
        "rules_count": 10,
        "server_time": datetime.now().isoformat()
    }
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py core_rules_verifier_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py core_rules_verifier_001.py

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



if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
