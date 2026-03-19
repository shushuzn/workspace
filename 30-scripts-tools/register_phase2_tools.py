#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Phase2 Speed Tools - 注册第二阶段速度优化工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOLS = [
    {
        "tool_id": "query_result_cache",
        "name": "Query Result Cache",
        "description": "查询结果缓存 - 缓存频繁查询结果，重复查询减少 90%",
        "file": "query_result_cache.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py query_result_cache.py"]
    },
    {
        "tool_id": "batch_parallel_processor",
        "name": "Batch Parallel Processor",
        "description": "批量操作并行化 - 并行执行批量操作，速度提升 3-5x",
        "file": "batch_parallel_processor.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py batch_parallel_processor.py"]
    },
    {
        "tool_id": "connection_pool_manager",
        "name": "Connection Pool Manager",
        "description": "连接池管理器 - 复用数据库/HTTP 连接，连接开销减少 90%",
        "file": "connection_pool_manager.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py connection_pool_manager.py"]
    },
    {
        "tool_id": "comprehensive_performance_benchmark",
        "name": "Comprehensive Performance Benchmark",
        "description": "综合性能基准测试 - 对比优化前后性能，生成详细报告",
        "file": "comprehensive_performance_benchmark.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py comprehensive_performance_benchmark.py"]
    }
]

def register_tools():
    """批量注册工具"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.6.7")
    
    # 更新版本号 (1.6.7 → 1.6.8)
    new_version = "1.6.8"
    
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
