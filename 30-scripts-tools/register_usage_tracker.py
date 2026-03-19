#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Usage Tracker - 注册使用跟踪工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOL = {
    "tool_id": "tool_usage_tracker",
    "name": "Tool Usage Tracker",
    "description": "工具使用跟踪 - 扫描代码库统计使用频率，识别热门/冷门工具",
    "file": "tool_usage_tracker.py",
    "category": "monitoring",
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
            "examples": ["py tool_usage_tracker.py"],
            "added_at": datetime.now().isoformat(),
            "status": NEW_TOOL["status"]
        }
        print(f"✅ 已注册：{NEW_TOOL['tool_id']}")
    else:
        print(f"⚠️  已存在：{NEW_TOOL['tool_id']}")
    
    registry["tools"] = tools
    registry["version"] = "1.7.6"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：1.7.6")
    print(f"📊 总工具数：{len(tools)}")
    
    return True

if __name__ == '__main__':
    register_tool()
