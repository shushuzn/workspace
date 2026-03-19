#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Missing Tools - 注册缺失的工具

注册 7 个未注册工具到 tools_registry.json
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 7 个未注册的工具
MISSING_TOOLS = [
    {
        "tool_id": "git-commit-push",
        "name": "Git Commit Push",
        "description": "Git 提交和推送 - 自动 commit + push",
        "file": "git_commit_push.py",
        "category": "git",
        "parameters": ["--message", "--push", "--all"],
        "examples": ["py git_commit_push.py --message 'fix: update'"]
    },
    {
        "tool_id": "execution-logger",
        "name": "Execution Logger",
        "description": "执行日志记录 - 记录工具调用和执行结果",
        "file": "execution_logger.py",
        "category": "logging",
        "parameters": ["--log", "--get-logs", "--clear-logs"],
        "examples": ["py execution_logger.py --log 'tool executed'"]
    },
    {
        "tool_id": "workflow-scheduler",
        "name": "Workflow Scheduler",
        "description": "工作流调度器 - 调度和管理工作流执行",
        "file": "workflow_scheduler.py",
        "category": "workflow",
        "parameters": ["--schedule", "--list", "--cancel"],
        "examples": ["py workflow_scheduler.py --schedule 'task'"]
    },
    {
        "tool_id": "tool-suggester",
        "name": "Tool Suggester",
        "description": "工具推荐器 - 根据任务推荐合适的工具",
        "file": "tool_suggester.py",
        "category": "assistant",
        "parameters": ["--suggest", "--task"],
        "examples": ["py tool_suggester.py --task 'analyze image'"]
    },
    {
        "tool_id": "integration-validator",
        "name": "Integration Validator",
        "description": "集成验证器 - 验证工具注册和集成状态",
        "file": "integration_validator.py",
        "category": "validation",
        "parameters": ["--tool", "--all"],
        "examples": ["py integration_validator.py --all"]
    },
    {
        "tool_id": "task-analyzer",
        "name": "Task Analyzer",
        "description": "任务分析器 - 分析任务复杂度和类型",
        "file": "task_analyzer.py",
        "category": "analysis",
        "parameters": ["--analyze", "--complexity", "--type"],
        "examples": ["py task_analyzer.py --analyze 'complex task'"]
    },
    {
        "tool_id": "checkpoint-saver",
        "name": "Checkpoint Saver",
        "description": "检查点保存器 - 保存工作流执行状态",
        "file": "checkpoint_saver.py",
        "category": "workflow",
        "parameters": ["--save", "--load", "--list"],
        "examples": ["py checkpoint_saver.py --save 'step6'"]
    }
]

def register_tools():
    """注册工具"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.6.2")
    
    # 更新版本号
    new_version = "1.6.3"
    
    registered_count = 0
    
    for tool in MISSING_TOOLS:
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
    
    print(f"\n✅ 注册完成：{registered_count}/7 个工具")
    print(f"📊 新版本：{new_version}")
    
    return registered_count

if __name__ == '__main__':
    register_tools()
