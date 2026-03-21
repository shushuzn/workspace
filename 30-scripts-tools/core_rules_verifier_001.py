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

if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
