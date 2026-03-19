#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Speed Optimization Tools - 批量注册速度优化工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOLS = [
    {
        "tool_id": "db_index_optimizer",
        "name": "Database Index Optimizer",
        "description": "数据库索引优化器 - 为 SQLite 添加索引，提升查询速度 10-100x",
        "file": "db_index_optimizer.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py db_index_optimizer.py"]
    },
    {
        "tool_id": "data_structure_optimizer",
        "name": "Data Structure Optimizer",
        "description": "数据结构优化器 - 将 list 查找改为 set/dict，提升查找速度 10-1000x",
        "file": "data_structure_optimizer.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py data_structure_optimizer.py"]
    },
    {
        "tool_id": "lru_cache_manager",
        "name": "LRU Cache Manager",
        "description": "LRU 缓存管理器 - 实现 LRU 缓存淘汰策略，提升读取速度 30-50%",
        "file": "lru_cache_manager.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py lru_cache_manager.py"]
    },
    {
        "tool_id": "async_io_manager",
        "name": "Async I/O Manager",
        "description": "I/O 异步化管理器 - 将 I/O 操作改为异步执行，减少 I/O 等待时间 60%",
        "file": "async_io_manager.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py async_io_manager.py"]
    },
    {
        "tool_id": "multi_level_cache",
        "name": "Multi-Level Cache",
        "description": "多级缓存架构 - 实现 L1→L2→L3 三级缓存，整体速度提升 50-70%",
        "file": "multi_level_cache.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py multi_level_cache.py"]
    }
]

def register_tools():
    """批量注册工具"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.6.6")
    
    # 更新版本号 (1.6.6 → 1.6.7)
    new_version = "1.6.7"
    
    registered = 0
    skipped = 0
    
    for tool in NEW_TOOLS:
        tool_id = tool["tool_id"]
        
        if tool_id in tools:
            print(f"⚠️  已存在：{tool_id}")
            skipped += 1
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
    
    # 更新 registry
    registry["tools"] = tools
    registry["version"] = new_version
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：{new_version}")
    print(f"📊 注册：{registered} 个，跳过：{skipped} 个")
    print(f"📊 总工具数：{len(tools)}")
    
    return True

if __name__ == '__main__':
    register_tools()
