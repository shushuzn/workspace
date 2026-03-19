#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Deprecated Marker - 注册废弃标记工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOL = {
    "tool_id": "mark_deprecated_tools",
    "name": "Mark Deprecated Tools",
    "description": "标记废弃工具 - 基于使用统计标记废弃候选",
    "file": "mark_deprecated_tools.py",
    "category": "automation",
    "status": "active"
}

def register_tool():
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    if NEW_TOOL["tool_id"] not in tools:
        tools[NEW_TOOL["tool_id"]] = {
            "name": NEW_TOOL["name"],
            "description": NEW_TOOL["description"],
            "file": NEW_TOOL["file"],
            "category": NEW_TOOL["category"],
            "parameters": [],
            "examples": ["py mark_deprecated_tools.py"],
            "added_at": datetime.now().isoformat(),
            "status": NEW_TOOL["status"]
        }
        print(f"✅ 已注册：{NEW_TOOL['tool_id']}")
    
    registry["tools"] = tools
    registry["version"] = "1.7.7"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：1.7.7")
    print(f"📊 总工具数：{len(tools)}")
    print(f"📊 废弃候选：{registry.get('deprecated_count', 0)} 个")
    
    return True

if __name__ == '__main__':
    register_tool()
