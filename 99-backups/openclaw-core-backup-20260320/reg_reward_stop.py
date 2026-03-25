#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
注册奖励系统和立即停止机制到 registry
"""
import json
from datetime import datetime

def register_tools():
    with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
        registry = json.load(f)

    new_tools = [
        {
            "tool_id": "reward-system",
            "name": "Reward System",
            "description": "奖励系统 - 只有完整执行工作流才有奖励",
            "file_path": "30-scripts-tools/reward_system.py",
            "category": "protection"
        },
        {
            "tool_id": "emergency-stop",
            "name": "Emergency Stop",
            "description": "立即停止机制 - 出现问题立刻停止所有操作",
            "file_path": "30-scripts-tools/emergency_stop.py",
            "category": "protection"
        }
    ]

    added = 0
    for tool in new_tools:
        tool_id = tool["tool_id"]
        if tool_id not in registry["tools"]:
            registry["tools"][tool_id] = {
                **tool,
                "version": "1.0.0",
                "status": "active",
                "usage_count": 0,
                "created_at": datetime.now().isoformat()
            }
            added += 1
            print(f"[ADD] {tool_id}")
        else:
            print(f"[SKIP] {tool_id} 已存在")

    registry["version"] = "1.11.43-reward-stop-mechanism"
    registry["last_updated"] = datetime.now().isoformat()

    with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"\n注册完成：{added} 个工具")
    print(f"新版本：{registry['version']}")

    return {"status": "success", "added": added}

if __name__ == "__main__":
    result = register_tools()
    print(json.dumps(result, ensure_ascii=False, indent=2))
