#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Speed Optimization Tools - 注册速度优化工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOL = {
    "tool_id": "speed-optimization-brainstorm",
    "name": "Speed Optimization Brainstorm",
    "description": "速度优化头脑风暴 - 生成在不影响功能情况下提升速度的优化方案",
    "file": "speed_optimization_brainstorm.py",
    "category": "optimization",
    "parameters": ["--output-dir", "--top-n"],
    "examples": ["py speed_optimization_brainstorm.py"]
}

def register_tool():
    """注册工具"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.6.5")
    
    # 更新版本号
    new_version = "1.6.6"
    
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
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 已注册：{tool_id}")
    print(f"📊 新版本：{new_version}")
    
    return True

if __name__ == '__main__':
    register_tool()
