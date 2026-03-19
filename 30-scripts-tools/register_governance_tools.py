#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Tool Governance Tools
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOLS = [
    {
        "tool_id": "tool_governance_analyzer",
        "name": "Tool Governance Analyzer",
        "description": "工具治理分析 - 分析 424 个工具现状，识别问题",
        "file": "tool_governance_analyzer.py",
        "category": "analysis",
        "parameters": [],
        "examples": ["py tool_governance_analyzer.py"]
    },
    {
        "tool_id": "brainstorm_tool_governance",
        "name": "Brainstorm Tool Governance",
        "description": "工具爆炸治理方案 - 5 层治理框架，15 个行动",
        "file": "brainstorm_tool_governance.py",
        "category": "brainstorm",
        "parameters": [],
        "examples": ["py brainstorm_tool_governance.py"]
    }
]

def register_tools():
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.7.1")
    new_version = "1.7.2"
    
    registered = 0
    
    for tool in NEW_TOOLS:
        tool_id = tool["tool_id"]
        
        if tool_id in tools:
            print(f"⚠️  已存在：{tool_id}")
            continue
        
        tools[tool_id] = {
            "name": tool["name"],
            "description": tool["description"],
            "file": tool["file"],
            "category": tool["category"],
            "parameters": tool["parameters"],
            "examples": tool["examples"],
            "added_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        print(f"✅ 已注册：{tool_id}")
        registered += 1
    
    registry["tools"] = tools
    registry["version"] = new_version
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：{new_version}")
    print(f"📊 注册：{registered} 个")
    print(f"📊 总工具数：{len(tools)}")
    
    return True

if __name__ == '__main__':
    register_tools()
