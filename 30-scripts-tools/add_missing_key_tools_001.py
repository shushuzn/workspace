import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加缺失的关键工具到 registry
"""
import json
from pathlib import Path
from datetime import datetime

def add_missing_tools():
    registry_file = Path("30-scripts-tools/tools_registry.json")
    scripts_dir = Path("30-scripts-tools")
    
    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    # 缺失的关键工具
    missing_tools = [
        "copaw_entry",
        "tool_call_tracker",
        "workflow_guardian_v2",
        "git_commit_helper",
        "git_precommit_check",
        "embedded_critic",
        "workflow_enforcer",
        "performance_analyzer",
        "auto_session_compressor",
        "session_compressor",
        "workflow_auto_executor",
        "workflow_health_dashboard",
        "memory_distiller",
        "auto_memory_distiller"
    ]
    
    added = 0
    for tool_name in missing_tools:
        tool_id = tool_name.replace("_", "-")
        
        # 检查是否已存在
        if tool_id in registry["tools"] or tool_name in registry["tools"]:
            print(f"[SKIP] {tool_id} 已存在")
            continue
        
        # 检查文件是否存在
        filepath = scripts_dir / f"{tool_name}.py"
        if not filepath.exists():
            print(f"[MISSING] {tool_name}.py 不存在")
            continue
        
        # 添加工具定义
        registry["tools"][tool_id] = {
            "tool_id": tool_id,
            "name": tool_id.replace("-", " ").title(),
            "description": f"{tool_id} 工具",
            "version": "1.0.0",
            "file_path": f"30-scripts-tools/{tool_name}.py",
            "category": "core" if "copaw" in tool_name or "workflow" in tool_name or "tool" in tool_name else "general",
            "status": "active",
            "usage_count": 0,
            "created_at": datetime.now().isoformat()
        }
        added += 1
        print(f"[ADD] {tool_id}")
    
    # 更新版本
    registry["version"] = "1.11.39-restored"
    registry["last_updated"] = datetime.now().isoformat()
    
    # 保存
    with open(registry_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print(f"\n添加完成：{added} 个工具")
    print(f"新版本：{registry['version']}")
    
    return {
        "status": "success",
        "added": added,
        "server_time": datetime.now().isoformat()
    }

if __name__ == "__main__":
    result = add_missing_tools()
    print(json.dumps(result, ensure_ascii=False, indent=2))
