#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Low Priority Tools - 注册低优先级工具

注册 6 个低优先级问题修复工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 6 个新工具
NEW_TOOLS = [
    {
        "tool_id": "auto-doc-generator",
        "name": "Auto Doc Generator",
        "description": "自动文档生成器 - 根据代码/项目结构自动生成文档",
        "file": "auto_doc_generator.py",
        "category": "documentation",
        "parameters": ["--output-dir", "--include-tests"],
        "examples": ["py auto_doc_generator.py"]
    },
    {
        "tool_id": "performance-benchmark",
        "name": "Performance Benchmark",
        "description": "性能基准测试 - 测试系统性能并生成报告",
        "file": "performance_benchmark.py",
        "category": "performance",
        "parameters": ["--output-dir", "--iterations"],
        "examples": ["py performance_benchmark.py"]
    },
    {
        "tool_id": "changelog-generator",
        "name": "Changelog Generator",
        "description": "变更日志生成器 - 从 Git 历史自动生成 CHANGELOG.md",
        "file": "changelog_generator.py",
        "category": "documentation",
        "parameters": ["--output", "--max-commits"],
        "examples": ["py changelog_generator.py"]
    },
    {
        "tool_id": "memory-auto-compress",
        "name": "Memory Auto Compress",
        "description": "记忆自动压缩 - 自动压缩过期的记忆文件",
        "file": "memory_auto_compress.py",
        "category": "memory",
        "parameters": ["--days-old", "--cleanup-after"],
        "examples": ["py memory_auto_compress.py"]
    },
    {
        "tool_id": "incremental-executor",
        "name": "Incremental Executor",
        "description": "增量执行支持 - 只执行变更的部分，跳过未变化的内容",
        "file": "incremental_executor.py",
        "category": "execution",
        "parameters": ["--files", "--cache-dir"],
        "examples": ["py incremental_executor.py"]
    },
    {
        "tool_id": "timeout-optimizer",
        "name": "Timeout Optimizer",
        "description": "超时优化器 - 优化工作流步骤超时设置",
        "file": "timeout_optimizer.py",
        "category": "optimization",
        "parameters": ["--workflow", "--optimize"],
        "examples": ["py timeout_optimizer.py --workflow workflow.json"]
    }
]

def register_tools():
    """注册工具"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.6.3")
    
    # 更新版本号
    new_version = "1.6.4"
    
    registered_count = 0
    
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
        registered_count += 1
    
    # 更新 registry
    registry["tools"] = tools
    registry["version"] = new_version
    registry["updated_at"] = datetime.now().isoformat()
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 注册完成：{registered_count}/6 个工具")
    print(f"📊 新版本：{new_version}")
    
    return registered_count

if __name__ == '__main__':
    register_tools()
