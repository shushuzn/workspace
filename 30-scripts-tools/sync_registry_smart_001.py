import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能同步 tools_registry.json 与实际存在的工具文件
支持命名转换：下划线<->连字符，auto_critic<->auto-critic 等
"""
import json
from pathlib import Path
import re

def normalize_name(name):
    """标准化名称以便比较"""
    # 移除扩展名
    name = name.replace(".py", "")
    # 下划线转连字符
    name = name.replace("_", "-")
    # 转小写
    name = name.lower()
    return name

def sync_registry():
    registry_file = Path("30-scripts-tools/tools_registry.json")
    scripts_dir = Path("30-scripts-tools")
    
    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    # 获取所有实际存在的 .py 文件（标准化名称）
    existing_files = {}
    for f in scripts_dir.glob("*.py"):
        normalized = normalize_name(f.name)
        existing_files[normalized] = f.name
    
    print(f"实际存在的 Python 文件：{len(existing_files)}")
    
    # 过滤 registry，只保留实际存在的工具
    tools = registry.get("tools", {})
    kept = []
    removed = []
    not_found = []
    
    for tool_id, info in list(tools.items()):
        normalized_tool = normalize_name(tool_id)
        
        # 检查工具是否有 command 字段
        command = info.get("command", "")
        if command and "py " in command:
            # 从 command 中提取文件名
            parts = command.split("py ")[1].split(" ")[0]
            filename = parts.split("\\")[-1].split("/")[-1]
            normalized_file = normalize_name(filename)
            
            # 检查文件是否存在
            if normalized_file in existing_files or normalized_tool in existing_files:
                kept.append(tool_id)
            else:
                # 尝试查找相似文件
                found = False
                for existing_norm in existing_files.keys():
                    if normalized_tool in existing_norm or existing_norm in normalized_tool:
                        kept.append(tool_id)
                        found = True
                        break
                if not found:
                    removed.append((tool_id, filename))
                    not_found.append(filename)
        else:
            # 没有 command 字段
            path = info.get("path", "")
            if path:
                filepath = scripts_dir / path.split("\\")[-1]
                if filepath.exists():
                    kept.append(tool_id)
                else:
                    removed.append((tool_id, path))
            else:
                removed.append((tool_id, "N/A"))
    
    print(f"保留的工具：{len(kept)}")
    print(f"移除的工具：{len(removed)}")
    
    if removed:
        print(f"\n移除的工具示例 (前 20 个):")
        for tool_id, filename in removed[:20]:
            print(f"  - {tool_id}: {filename}")
    
    # 更新 registry
    new_tools = {k: tools[k] for k in kept}
    registry["tools"] = new_tools
    registry["version"] = "1.7.0-synced-smart"
    
    with open(registry_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print(f"\nRegistry 已同步到实际文件")
    print(f"版本：{registry['version']}")
    
    return {
        "status": "success",
        "kept": len(kept),
        "removed": len(removed),
        "server_time": "2026-03-20T02:46:00+08:00"
    }

if __name__ == "__main__":
    result = sync_registry()
    print(json.dumps(result, ensure_ascii=False, indent=2))
