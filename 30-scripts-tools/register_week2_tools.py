#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Week 2 Tools - 注册 Week 2 工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOLS = [
    {
        "tool_id": "naming_standard_analyzer",
        "name": "Naming Standard Analyzer",
        "description": "命名规范分析 - 分析工具命名，识别不符合规范的工具",
        "file": "naming_standard_analyzer.py",
        "category": "quality",
        "status": "active"
    },
    {
        "tool_id": "standardize_naming",
        "name": "Standardize Naming",
        "description": "统一命名规范 - 将 kebab-case 工具重命名为 underscore",
        "file": "standardize_naming.py",
        "category": "automation",
        "status": "active"
    },
    {
        "tool_id": "subdivide_general_category",
        "name": "Subdivide General Category",
        "description": "细分 general 类 - 将 222 个 general 工具细分为更具体的分类",
        "file": "subdivide_general_category.py",
        "category": "automation",
        "status": "active"
    }
]

def register_tools():
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    registered = 0
    for tool_data in NEW_TOOLS:
        tool_id = tool_data["tool_id"]
        
        if tool_id not in tools:
            tools[tool_id] = {
                "name": tool_data["name"],
                "description": tool_data["description"],
                "file": tool_data["file"],
                "category": tool_data["category"],
                "parameters": [],
                "examples": [f"py {tool_data['file']}"],
                "added_at": datetime.now().isoformat(),
                "status": tool_data["status"]
            }
            print(f"✅ 已注册：{tool_id}")
            registered += 1
        else:
            print(f"⚠️  已存在：{tool_id}")
    
    registry["tools"] = tools
    registry["version"] = "1.7.9"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：1.7.9")
    print(f"📊 新注册：{registered} 个")
    print(f"📊 总工具数：{len(tools)}")
    
    return True

if __name__ == '__main__':
    register_tools()
