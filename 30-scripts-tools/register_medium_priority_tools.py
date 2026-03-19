#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Medium Priority Tools - 注册中优先级工具

注册 6 个中优先级问题修复工具
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 6 个新工具
NEW_TOOLS = [
    {
        "tool_id": "auto-test-runner",
        "name": "Auto Test Runner",
        "description": "自动化测试运行器 - 自动运行项目测试并生成报告",
        "file": "auto_test_runner.py",
        "category": "testing",
        "parameters": ["--test-dir", "--report-dir", "--coverage"],
        "examples": ["py auto_test_runner.py"]
    },
    {
        "tool_id": "rollback-manager",
        "name": "Rollback Manager",
        "description": "回滚管理器 - 管理工作流失败时的回滚操作",
        "file": "rollback_manager.py",
        "category": "workflow",
        "parameters": ["--create", "--list", "--rollback", "--cleanup"],
        "examples": ["py rollback_manager.py --create"]
    },
    {
        "tool_id": "memory-persistence",
        "name": "Memory Persistence",
        "description": "记忆持久化 - 将重要记忆永久保存到 MEMORY.md",
        "file": "memory_persistence.py",
        "category": "memory",
        "parameters": ["--auto", "--persist", "--min-importance"],
        "examples": ["py memory_persistence.py --auto"]
    },
    {
        "tool_id": "config-backup",
        "name": "Config Backup",
        "description": "配置备份 - 自动备份关键配置文件",
        "file": "config_backup.py",
        "category": "backup",
        "parameters": ["--backup-all", "--list", "--restore", "--cleanup"],
        "examples": ["py config_backup.py --backup-all"]
    },
    {
        "tool_id": "parallel-executor",
        "name": "Parallel Executor",
        "description": "并行执行器 - 并行执行独立任务以提高效率",
        "file": "parallel_executor.py",
        "category": "execution",
        "parameters": ["--execute", "--analyze", "--workers"],
        "examples": ["py parallel_executor.py --execute"]
    },
    {
        "tool_id": "result-cache",
        "name": "Result Cache",
        "description": "结果缓存 - 缓存工具执行结果以提高重复任务效率",
        "file": "result_cache.py",
        "category": "cache",
        "parameters": ["--get", "--set", "--clear-expired", "--stats"],
        "examples": ["py result_cache.py --stats"]
    }
]

def register_tools():
    """注册工具"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.6.4")
    
    # 更新版本号
    new_version = "1.6.5"
    
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
