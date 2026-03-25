#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
注册 Phase 2 工具到 registry
"""
import json
from datetime import datetime

def register_tools():
    with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
        registry = json.load(f)

    new_tools = [
        {
            "tool_id": "single-step-lock",
            "name": "Single Step Lock",
            "description": "单步锁 - 确保每次只执行一个步骤",
            "file_path": "30-scripts-tools/single_step_lock.py",
            "category": "protection"
        },
        {
            "tool_id": "state-snapshot",
            "name": "State Snapshot",
            "description": "状态快照 - 每步执行后保存状态",
            "file_path": "30-scripts-tools/state_snapshot.py",
            "category": "protection"
        },
        {
            "tool_id": "result-verifier",
            "name": "Result Verifier",
            "description": "结果验证器 - 验证工具执行结果",
            "file_path": "30-scripts-tools/result_verifier.py",
            "category": "protection"
        },
        {
            "tool_id": "penalty-system",
            "name": "Penalty System",
            "description": "违规惩罚机制 - 对违反工作流的行为进行惩罚",
            "file_path": "30-scripts-tools/penalty_system.py",
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

    registry["version"] = "1.11.41-protection-phase2"
    registry["last_updated"] = datetime.now().isoformat()

    with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"\n注册完成：{added} 个工具")
    print(f"新版本：{registry['version']}")

    return {"status": "success", "added": added}

if __name__ == "__main__":
    result = register_tools()
    print(json.dumps(result, ensure_ascii=False, indent=2))
