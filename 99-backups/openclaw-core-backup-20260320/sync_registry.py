#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
同步 tools_registry.json 与实际存在的工具文件
只保留实际存在的工具
"""
import json
from pathlib import Path
import subprocess

def sync_registry():
    registry_file = Path("30-scripts-tools/tools_registry.json")
    scripts_dir = Path("30-scripts-tools")

    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)

    # 获取所有实际存在的 .py 文件
    existing_files = {f.stem.replace("_", "-"): f.name for f in scripts_dir.glob("*.py")}

    print(f"实际存在的 Python 文件：{len(existing_files)}")

    # 过滤 registry，只保留实际存在的工具
    tools = registry.get("tools", {})
    kept = []
    removed = []

    for tool_id, info in list(tools.items()):
        # 检查工具是否有 command 字段
        command = info.get("command", "")
        if command:
            # 从 command 中提取文件名
            if "py " in command:
                parts = command.split("py ")[1].split(" ")[0]
                filename = parts.split("\\")[-1].split("/")[-1].replace(".py", "").replace("_", "-")
                if filename in existing_files or tool_id.replace("_", "-") in existing_files:
                    kept.append(tool_id)
                else:
                    removed.append(tool_id)
            else:
                removed.append(tool_id)
        else:
            # 没有 command 字段，检查 path 字段
            path = info.get("path", "")
            if path:
                filepath = scripts_dir / path.split("\\")[-1]
                if filepath.exists():
                    kept.append(tool_id)
                else:
                    removed.append(tool_id)
            else:
                removed.append(tool_id)

    print(f"保留的工具：{len(kept)}")
    print(f"移除的工具：{len(removed)}")

    # 更新 registry
    new_tools = {k: tools[k] for k in kept}
    registry["tools"] = new_tools
    registry["version"] = "1.7.0-synced"

    with open(registry_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"\nRegistry 已同步到实际文件")
    print(f"版本：{registry['version']}")

    return {
        "status": "success",
        "kept": len(kept),
        "removed": len(removed),
        "server_time": "2026-03-20T02:45:00+08:00"
    }

if __name__ == "__main__":
    result = sync_registry()
    print(json.dumps(result, ensure_ascii=False, indent=2))
