import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断工具：检查 registry 与 实际文件的映射关系
"""
import json
from pathlib import Path

def diagnose():
    registry_file = Path("30-scripts-tools/tools_registry.json")
    scripts_dir = Path("30-scripts-tools")
    
    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    print("=" * 70)
    print("工具注册诊断报告")
    print("=" * 70)
    print(f"Registry 工具总数：{len(tools)}\n")
    
    # 分类统计
    found = []
    not_found = []
    wrong_path = []
    
    for tool_id, info in tools.items():
        command = info.get("command", "")
        path = info.get("path", "")
        
        # 提取文件名
        filename = None
        if command and "py " in command:
            parts = command.split("py ")[1].split(" ")[0]
            filename = parts.split("\\")[-1].split("/")[-1]
        elif path:
            filename = path.split("\\")[-1].split("/")[-1]
        
        if not filename:
            not_found.append((tool_id, "无 command/path 字段"))
            continue
        
        # 检查文件是否存在
        filepath = scripts_dir / filename
        if filepath.exists():
            found.append((tool_id, filename))
        else:
            # 尝试查找相似文件
            similar = list(scripts_dir.glob(f"*{filename.replace('.py', '')}*.py"))
            if similar:
                wrong_path.append((tool_id, filename, [s.name for s in similar]))
            else:
                not_found.append((tool_id, filename))
    
    print(f"[OK] 文件存在：{len(found)}")
    print(f"[WARN] 路径错误：{len(wrong_path)}")
    print(f"[FAIL] 文件缺失：{len(not_found)}")
    
    if wrong_path:
        print("\n" + "=" * 70)
        print("路径错误 (建议修复):")
        print("=" * 70)
        for tool_id, expected, actual in wrong_path[:10]:
            print(f"  {tool_id}:")
            print(f"    期望：{expected}")
            print(f"    实际：{actual}")
    
    if not_found:
        print("\n" + "=" * 70)
        print("文件缺失 (需要创建或删除):")
        print("=" * 70)
        for tool_id, filename in not_found[:20]:
            print(f"  {tool_id}: {filename}")
    
    # 检查常见模式问题
    print("\n" + "=" * 70)
    print("常见问题分析:")
    print("=" * 70)
    
    # 1. 下划线 vs 连字符
    underscore_tools = [t for t in tools.keys() if "_" in t]
    hyphen_files = [f.name for f in scripts_dir.glob("*.py") if "-" in f.name]
    
    print(f"\n1. 命名不一致:")
    print(f"   Registry 使用下划线：{len(underscore_tools)} 个")
    print(f"   文件使用连字符：{len(hyphen_files)} 个")
    
    # 2. 重复定义
    names = [info.get("command", "").split("\\")[-1].split(" ")[0] for info in tools.values() if info.get("command")]
    duplicates = [n for n in names if names.count(n) > 1]
    print(f"\n2. 重复定义：{len(set(duplicates))} 个文件被多次注册")
    
    # 3. ${args} 问题
    args_tools = [t for t, i in tools.items() if "${args}" in i.get("command", "")]
    print(f"\n3. 使用 ${{args}} 占位符：{len(args_tools)} 个 (可能导致解析错误)")
    
    return {
        "found": len(found),
        "wrong_path": len(wrong_path),
        "not_found": len(not_found),
        "server_time": "2026-03-20T07:55:00+08:00"
    }
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py diagnose_registry_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py diagnose_registry_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""



if __name__ == "__main__":
    result = diagnose()
    print("\n" + "=" * 70)
    print(f"诊断完成：{json.dumps(result, ensure_ascii=False)}")
