#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面检查实际存在的工具文件 - 修复 GBK 编码问题
"""
import json
from pathlib import Path

def check_existing_tools():
    scripts_dir = Path("30-scripts-tools")
    registry_file = Path("30-scripts-tools/tools_registry.json")
    
    # 获取所有实际存在的 .py 文件
    py_files = list(scripts_dir.glob("*.py"))
    py_files = [f for f in py_files if not f.name.startswith("_") and f.parent == scripts_dir]
    
    print("=" * 60)
    print("30-scripts-tools 目录中的 Python 文件")
    print("=" * 60)
    print(f"总数：{len(py_files)}\n")
    
    # 关键工具检查
    key_tools = [
        "embedded_critic.py",
        "workflow_enforcer.py",
        "tool_executor.py",
        "copaw_entry.py",
        "tool_call_tracker.py",
        "workflow_guardian_v2.py",
        "git_commit_helper.py",
        "fast_load.py",
        "post_session_compress.py",
        "performance_analyzer.py"
    ]
    
    print("[关键工具检查]")
    for tool in key_tools:
        exists = (scripts_dir / tool).exists()
        status = "[OK]" if exists else "[MISSING]"
        print(f"  {status} {tool}")
    
    # 加载 registry
    print(f"\n{'=' * 60}")
    print("Registry 工具 vs 实际文件匹配")
    print("=" * 60)
    
    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    print(f"Registry 工具总数：{len(tools)}\n")
    
    matched = []
    unmatched = []
    
    for tool_id, info in tools.items():
        command = info.get("command", "")
        if command and "py " in command:
            parts = command.split("py ")[1].split(" ")[0]
            filename = parts.split("\\")[-1].split("/")[-1]
            filepath = scripts_dir / filename
            if filepath.exists():
                matched.append((tool_id, filename))
            else:
                unmatched.append((tool_id, filename))
    
    print(f"匹配的工具：{len(matched)}")
    for tool_id, filename in sorted(matched):
        print(f"  [OK] {tool_id} -> {filename}")
    
    print(f"\n不匹配的工具：{len(unmatched)}")
    if unmatched:
        print(f"前 20 个示例:")
        for tool_id, filename in sorted(unmatched)[:20]:
            print(f"  [MISSING] {tool_id} -> {filename}")
    
    # 按前缀分类统计实际文件
    print(f"\n{'=' * 60}")
    print("实际文件分类统计")
    print("=" * 60)
    
    categories = {}
    for f in py_files:
        prefix = f.name.split("_")[0] if "_" in f.name else f.name.split("-")[0] if "-" in f.name else f.name[:3]
        if prefix not in categories:
            categories[prefix] = []
        categories[prefix].append(f.name)
    
    for prefix, files in sorted(categories.items(), key=lambda x: -len(x[1])):
        if len(files) >= 2:
            print(f"\n{prefix}* - {len(files)} 个文件:")
            for f in sorted(files)[:5]:
                print(f"  - {f}")
            if len(files) > 5:
                print(f"  ... 还有 {len(files)-5} 个")
    
    return {
        "total_py_files": len(py_files),
        "matched_tools": len(matched),
        "unmatched_tools": len(unmatched),
        "matched_list": matched
    }

if __name__ == "__main__":
    result = check_existing_tools()
    print(f"\n{'=' * 60}")
    print(f"总结:")
    print(f"  实际 Python 文件：{result['total_py_files']}")
    print(f"  Registry 匹配：{result['matched_tools']}")
    print(f"  Registry 不匹配：{result['unmatched_tools']}")
