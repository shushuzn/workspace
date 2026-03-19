#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Week 4 Tools - 注册 Week 4 工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOLS = [
    {
        "tool_id": "detect_duplicate_tools",
        "name": "Detect Duplicate Tools",
        "description": "检测重复工具 - 分析工具库识别功能重复的工具",
        "file": "detect_duplicate_tools.py",
        "category": "analysis",
        "status": "active"
    },
    {
        "tool_id": "merge_duplicate_tools",
        "name": "Merge Duplicate Tools",
        "description": "合并重复工具 - 基于使用次数合并功能重复的工具",
        "file": "merge_duplicate_tools.py",
        "category": "automation",
        "status": "active"
    },
    {
        "tool_id": "extra_cleanup",
        "name": "Extra Cleanup",
        "description": "额外清理 - 进一步清理低频工具达成 -20% 目标",
        "file": "extra_cleanup.py",
        "category": "automation",
        "status": "active"
    },
    {
        "tool_id": "final_cleanup",
        "name": "Final Cleanup",
        "description": "最终清理 - 删除 9 个低频工具达成 -20% 目标",
        "file": "final_cleanup.py",
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
    registry["version"] = "1.9.0"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：1.9.0")
    print(f"📊 新注册：{registered} 个")
    print(f"📊 总工具数：{len(tools)}")
    
    return True

if __name__ == '__main__':
    register_tools()
