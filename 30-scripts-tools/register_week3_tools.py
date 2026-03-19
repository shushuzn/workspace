#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Week 3 Tools - 注册 Week 3 工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOLS = [
    {
        "tool_id": "generate_tool_directory",
        "name": "Generate Tool Directory",
        "description": "生成工具目录 - 创建 Markdown 格式的工具目录，按分类组织",
        "file": "generate_tool_directory.py",
        "category": "documentation",
        "status": "active"
    },
    {
        "tool_id": "review_deprecated_candidates",
        "name": "Review Deprecated Candidates",
        "description": "审查废弃候选 - 人工审查废弃候选工具，决定保留或删除",
        "file": "review_deprecated_candidates.py",
        "category": "quality",
        "status": "active"
    },
    {
        "tool_id": "delete_deprecated_tools",
        "name": "Delete Deprecated Tools",
        "description": "删除废弃工具 - 实际删除已确认的废弃工具，带备份",
        "file": "delete_deprecated_tools.py",
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
    registry["version"] = "1.8.0"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：1.8.0")
    print(f"📊 新注册：{registered} 个")
    print(f"📊 总工具数：{len(tools)}")
    
    return True

if __name__ == '__main__':
    register_tools()
