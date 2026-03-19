#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Register Tools - 自动注册工具到 tools_registry.json
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:\\OpenClaw\\workspace")
TOOLS_REGISTRY = WORKSPACE / "30-scripts-tools" / "tools_registry.json"

# 需要注册的工具列表
TOOLS_TO_REGISTER = [
    {
        "tool_id": "long-term-memory",
        "name": "Long Term Memory",
        "description": "跨会话持久化记忆系统 - 搜索、关联、压缩",
        "file": "long_term_memory.py",
        "category": "memory",
        "parameters": ["--search", "--add", "--compress", "--list", "--status"],
        "examples": ["py long_term_memory.py --search '关键词'", "py long_term_memory.py --add '记忆内容'"]
    },
    {
        "tool_id": "task-decomposer",
        "name": "Task Decomposer",
        "description": "任务分解自动化 - 依赖管理、优先级排序、进度追踪",
        "file": "task_decomposer.py",
        "category": "task",
        "parameters": ["--decompose", "--progress", "--execute-next", "--list"],
        "examples": ["py task_decomposer.py --decompose '复杂任务' --template development"]
    },
    {
        "tool_id": "proactive-agent",
        "name": "Proactive Agent",
        "description": "主动式交互系统 - 提醒、建议、预警、上下文感知",
        "file": "proactive_agent.py",
        "category": "interaction",
        "parameters": ["--check", "--remind", "--suggest", "--alert", "--alerts", "--context", "--learn", "--status"],
        "examples": ["py proactive_agent.py --check", "py proactive_agent.py --remind '完成任务'"]
    },
    {
        "tool_id": "multimodal-agent",
        "name": "Multimodal Agent",
        "description": "多模态理解系统 - 图像、OCR、语音、文档、融合",
        "file": "multimodal_agent.py",
        "category": "multimodal",
        "parameters": ["--image", "--ocr", "--audio", "--doc", "--pdf", "--fuse", "--result", "--status"],
        "examples": ["py multimodal_agent.py --image 'photo.jpg'", "py multimodal_agent.py --ocr 'scan.png'"]
    },
    {
        "tool_id": "workflow-recovery",
        "name": "Workflow Recovery",
        "description": "工作流恢复系统 - 检查点恢复、步骤重试",
        "file": "workflow_recovery.py",
        "category": "workflow",
        "parameters": ["--restore", "--retry", "--list-checkpoints", "--status"],
        "examples": ["py workflow_recovery.py --restore 'checkpoint.json'"]
    },
    {
        "tool_id": "integration-validator",
        "name": "Integration Validator",
        "description": "工具集成验证器 - 检查注册、集成、调用场景",
        "file": "integration_validator.py",
        "category": "validation",
        "parameters": ["--tool", "--all"],
        "examples": ["py integration_validator.py --tool 'proactive_agent.py'", "py integration_validator.py --all"]
    }
]

def register_tools():
    """注册工具"""
    if not TOOLS_REGISTRY.exists():
        print("❌ tools_registry.json 不存在")
        return False
    
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "1.6.0")
    
    # 更新版本号
    version_parts = version.split(".")
    version_parts[-1] = str(int(version_parts[-1]) + 1)
    new_version = ".".join(version_parts)
    
    registered_count = 0
    
    for tool in TOOLS_TO_REGISTER:
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
    
    print(f"\n✅ 注册完成：{registered_count} 个工具")
    print(f"📊 新版本：{new_version}")
    
    return True

if __name__ == '__main__':
    register_tools()
