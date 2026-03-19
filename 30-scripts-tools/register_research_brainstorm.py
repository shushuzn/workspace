#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Research-Driven Brainstorm Tool
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOL = {
    "tool_id": "brainstorm_research_driven",
    "name": "Brainstorm Research Driven",
    "description": "研究驱动 AI Agent 创新 - GitHub 4 项目+arXiv 4 方向 20 创意",
    "file": "brainstorm_research_driven.py",
    "category": "brainstorm",
    "parameters": [],
    "examples": ["py brainstorm_research_driven.py"]
}

def register_tool():
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.7.0")
    new_version = "1.7.1"
    
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
