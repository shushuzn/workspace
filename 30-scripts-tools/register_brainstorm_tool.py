#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Brainstorm Tool - 注册头脑风暴工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOL = {
    "tool_id": "brainstorm_agent_autonomy",
    "name": "Brainstorm Agent Autonomy",
    "description": "AI Agent 自主性提升头脑风暴 - 6 维度 30 创意",
    "file": "brainstorm_agent_autonomy.py",
    "category": "brainstorm",
    "parameters": [],
    "examples": ["py brainstorm_agent_autonomy.py"]
}

def register_tool():
    """注册工具"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.6.9")
    
    # 更新版本号 (1.6.9 → 1.7.0)
    new_version = "1.7.0"
    
    tool_id = NEW_TOOL["tool_id"]
    
    if tool_id in tools:
        print(f"⚠️  已存在：{tool_id}")
        return False
    
    tools[tool_id] = {
        "name": NEW_TOOL["name"],
        "description": NEW_TOOL["description"],
        "file": NEW_TOOL["file"],
        "category": NEW_TOOL["category"],
        "parameters": NEW_TOOL["parameters"],
        "examples": NEW_TOOL["examples"],
        "added_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    # 更新 registry
    registry["tools"] = tools
    registry["version"] = new_version
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 已注册：{tool_id}")
    print(f"📊 新版本：{new_version}")
    print(f"📊 总工具数：{len(tools)}")
    
    return True

if __name__ == '__main__':
    register_tool()
