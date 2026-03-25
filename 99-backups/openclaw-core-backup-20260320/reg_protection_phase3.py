#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
注册 Phase 3 强化工具到 registry
"""
import json
from datetime import datetime

def register_tools():
    with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
        registry = json.load(f)

    new_tools = [
        {
            "tool_id": "penalty-system-v2",
            "name": "Penalty System V2",
            "description": "违规惩罚机制 v2.0 - 强化版 (自动封锁 + 连续违规加倍)",
            "file_path": "30-scripts-tools/penalty_system_v2.py",
            "category": "protection"
        },
        {
            "tool_id": "protection-monitor",
            "name": "Protection Monitor",
            "description": "实时防护监控 - 监控所有操作并实时阻断违规",
            "file_path": "30-scripts-tools/protection_monitor.py",
            "category": "protection"
        },
        {
            "tool_id": "git-precommit-v4",
            "name": "Git PreCommit V4",
            "description": "Git Pre-Commit Hook v4.0 - 强化版 (6 项检查 + 惩罚集成)",
            "file_path": "30-scripts-tools/git_precommit_check_v4.py",
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

    registry["version"] = "1.11.42-protection-phase3-enhanced"
    registry["last_updated"] = datetime.now().isoformat()

    with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"\n注册完成：{added} 个工具")
    print(f"新版本：{registry['version']}")

    return {"status": "success", "added": added}

if __name__ == "__main__":
    result = register_tools()
    print(json.dumps(result, ensure_ascii=False, indent=2))
