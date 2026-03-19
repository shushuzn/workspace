#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Phase3 Speed Tools - 注册第三阶段速度优化工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

NEW_TOOLS = [
    {
        "tool_id": "cpu_multiprocess_optimizer",
        "name": "CPU Multiprocess Optimizer",
        "description": "CPU 密集型任务多进程优化器 - 多进程并行计算，速度提升 2-4x",
        "file": "cpu_multiprocess_optimizer.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py cpu_multiprocess_optimizer.py"]
    },
    {
        "tool_id": "pipeline_processor",
        "name": "Pipeline Processor",
        "description": "流水线处理器 - 多阶段并行处理，吞吐量提升 2-3x",
        "file": "pipeline_processor.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py pipeline_processor.py"]
    },
    {
        "tool_id": "memory_mapped_file",
        "name": "Memory Mapped File",
        "description": "内存映射文件 - mmap 大文件映射，读取速度提升 3-5x",
        "file": "memory_mapped_file.py",
        "category": "optimization",
        "parameters": [],
        "examples": ["py memory_mapped_file.py"]
    }
]

def register_tools():
    """批量注册工具"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.6.8")
    
    # 更新版本号 (1.6.8 → 1.6.9)
    new_version = "1.6.9"
    
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
