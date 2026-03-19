#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Missing File Tools - 补全缺失文件工具注册
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

RECOVERED_TOOLS = [
    {
        "tool_id": "git_commit_push",
        "name": "Git Commit Push",
        "description": "Git 提交和推送 - 自动 commit + push",
        "file": "git_commit_push.py",
        "category": "git",
        "status": "recovered"
    },
    {
        "tool_id": "execution_logger",
        "name": "Execution Logger",
        "description": "执行日志记录 - 记录工具调用和执行结果",
        "file": "execution_logger.py",
        "category": "logging",
        "status": "recovered"
    },
    {
        "tool_id": "tool_suggester",
        "name": "Tool Suggester",
        "description": "工具推荐 - 根据任务描述推荐工具",
        "file": "tool_suggester.py",
        "category": "assistant",
        "status": "recovered"
    },
    {
        "tool_id": "task_analyzer",
        "name": "Task Analyzer",
        "description": "任务分析 - 分析复杂度/估算时间/识别依赖",
        "file": "task_analyzer.py",
        "category": "analysis",
        "status": "recovered"
    },
    {
        "tool_id": "checkpoint_saver",
        "name": "Checkpoint Saver",
        "description": "检查点保存 - 保存任务进度，支持恢复",
        "file": "checkpoint_saver.py",
        "category": "utility",
        "status": "recovered"
    },
    {
        "tool_id": "timeout_optimizer",
        "name": "Timeout Optimizer",
        "description": "超时优化 - 根据任务类型优化超时设置",
        "file": "timeout_optimizer.py",
        "category": "optimization",
        "status": "recovered"
    }
]

def register_tools():
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.7.2")
    new_version = "1.7.3"
    
    recovered = 0
    updated = 0
    
    for tool_data in RECOVERED_TOOLS:
        tool_id = tool_data["tool_id"]
        
        if tool_id in tools:
            # 更新现有工具
            tools[tool_id]["file"] = tool_data["file"]
            tools[tool_id]["status"] = "recovered"
            tools[tool_id]["recovered_at"] = datetime.now().isoformat()
            print(f"✅ 已更新：{tool_id}")
            updated += 1
        else:
            # 新工具
            tools[tool_id] = {
                "name": tool_data["name"],
                "description": tool_data["description"],
                "file": tool_data["file"],
                "category": tool_data["category"],
                "parameters": [],
                "examples": [f"py {tool_data['file']}"],
                "added_at": datetime.now().isoformat(),
                "status": "recovered"
            }
            print(f"✅ 已注册：{tool_id}")
            recovered += 1
    
    registry["tools"] = tools
    registry["version"] = new_version
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    registry["recovery_note"] = f"Recovered {len(RECOVERED_TOOLS)} missing file tools"
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：{new_version}")
    print(f"📊 更新：{updated} 个，恢复：{recovered} 个")
    print(f"📊 总工具数：{len(tools)}")
    
    return True

if __name__ == '__main__':
    register_tools()
