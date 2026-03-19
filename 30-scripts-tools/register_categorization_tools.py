#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Categorization Tools - 注册分类工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOLS = [
    {
        "tool_id": "categorize_uncategorized_tools",
        "name": "Categorize Uncategorized Tools",
        "description": "分类未分类工具 - 分析并建议分类",
        "file": "categorize_uncategorized_tools.py",
        "category": "automation",
        "status": "active"
    },
    {
        "tool_id": "auto_categorize_tools",
        "name": "Auto Categorize Tools",
        "description": "自动分类工具 - 应用建议分类到工具库",
        "file": "auto_categorize_tools.py",
        "category": "automation",
        "status": "active"
    },
    {
        "tool_id": "tool_search",
        "name": "Tool Search",
        "description": "工具搜索 - 按关键词/分类搜索，支持模糊匹配",
        "file": "tool_search.py",
        "category": "utility",
        "status": "active"
    }
]

def register_tools():
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.7.4")
    new_version = "1.7.5"
    
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
    registry["version"] = new_version
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：{new_version}")
    print(f"📊 新注册：{registered} 个")
    print(f"📊 总工具数：{len(tools)}")
    
    return True

if __name__ == '__main__':
    register_tools()
