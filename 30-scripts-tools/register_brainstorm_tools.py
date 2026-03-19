#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Brainstorm Tools - 注册头脑风暴工具到 tools_registry.json
"""

import json
from datetime import datetime
from pathlib import Path

def register_brainstorm_tools():
    """注册头脑风暴工具"""
    
    registry_file = Path("30-scripts-tools/tools_registry.json")
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # 新工具定义
    new_tools = {
        "brainstorm-divergent": {
            "description": "头脑风暴发散工具 - 快速生成大量想法 (双环模式 D1-D5)",
            "category": "brainstorm",
            "automation_enabled": False,
            "usage_count": 0,
            "file": "brainstorm_divergent.py",
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "triggers": ["manual"],
            "review_required": False,
            "blocking": False,
            "timeout_seconds": 1800
        },
        "brainstorm-convergent": {
            "description": "头脑风暴收敛工具 - 筛选高价值想法 (双环模式 C1-C5)",
            "category": "brainstorm",
            "automation_enabled": False,
            "usage_count": 0,
            "file": "brainstorm_convergent.py",
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "triggers": ["manual"],
            "review_required": False,
            "blocking": False,
            "timeout_seconds": 1500
        },
        "brainstorm-facilitator": {
            "description": "头脑风暴引导工具 - 控制双环迭代流程",
            "category": "brainstorm",
            "automation_enabled": False,
            "usage_count": 0,
            "file": "brainstorm_facilitator.py",
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "triggers": ["manual"],
            "review_required": False,
            "blocking": False,
            "timeout_seconds": 5400
        },
        "critic-brainstorm-lite": {
            "description": "头脑风暴轻量批判者 - 快速审查 (≥60 分通过)",
            "category": "quality",
            "automation_enabled": False,
            "usage_count": 0,
            "file": "critic_brainstorm_lite.py",
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "triggers": ["brainstorm_complete"],
            "review_required": False,
            "blocking": False,
            "timeout_seconds": 300
        }
    }
    
    # 添加到 registry
    registry["tools"].update(new_tools)
    
    # 更新版本
    version_parts = registry["version"].split(".")
    registry["version"] = f"{version_parts[0]}.{version_parts[1]}.{int(version_parts[2]) + 1}"
    registry["last_updated"] = datetime.now().isoformat()
    registry["changes"].insert(0, f"v{registry['version']}: Added brainstorm workflow v2.0 tools (divergent, convergent, facilitator, critic-lite)")
    
    # 保存
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"注册完成:")
    print(f"  新工具数：{len(new_tools)}")
    print(f"  版本：{registry['version']}")
    print(f"  总工具数：{len(registry['tools'])}")
    
    return registry

if __name__ == "__main__":
    register_brainstorm_tools()
