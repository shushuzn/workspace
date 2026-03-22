#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Naming Convention Checker
检查新工具是否符合命名规范，减少重复
"""

import os
import re
from pathlib import Path
from difflib import SequenceMatcher

def check_similar_tools(new_tool_name, tools_dir="D:/OpenClaw/workspace/30-scripts-tools"):
    """检查是否有相似的工具"""
    tools = [f.stem for f in Path(tools_dir).glob("*.py")]
    new_base = re.sub(r'_\d+$', '', new_tool_name)  # 移除 _001 后缀
    
    similar = []
    for tool in tools:
        base = re.sub(r'_\d+$', '', tool)
        # 检查前缀匹配
        if base == new_base:
            similar.append((tool, "SAME BASE"))
        elif new_base.startswith(base) or base.startswith(new_base):
            similar.append((tool, "SIMILAR"))
        # 检查编辑距离
        elif SequenceMatcher(None, base, new_base).ratio() > 0.8:
            similar.append((tool, f"FUZZY ({SequenceMatcher(None, base, new_base).ratio():.0%})"))
    
    return similar

def check_naming_convention(name):
    """检查命名是否符合规范"""
    issues = []
    
    # 检查是否有后缀
    if not re.search(r'_\d+$', name) and name not in ['archive_stock_pro.py', 'release_stock_pro.py']:
        issues.append("Missing _001 suffix")
    
    # 检查是否包含空格
    if ' ' in name:
        issues.append("Contains spaces")
    
    # 检查大小写
    if name != name.lower():
        issues.append("Should be lowercase")
    
    return issues

def suggest_tool_name(base_name, purpose):
    """基于目的推荐工具名"""
    # 标准化名称
    name = base_name.lower().replace(' ', '_')
    
    # 添加 _001 后缀
    if not re.search(r'_\d+$', name):
        name = f"{name}_001"
    
    return name

def main():
    import sys
    
    if len(sys.argv) > 1:
        new_tool = sys.argv[1]
        print(f"Checking: {new_tool}")
        print("-" * 50)
        
        # 检查命名规范
        issues = check_naming_convention(new_tool)
        if issues:
            print("[!] Naming issues:")
            for issue in issues:
                print(f"    - {issue}")
        
        # 检查相似工具
        similar = check_similar_tools(new_tool)
        if similar:
            print("\n[!] Similar tools found:")
            for tool, reason in similar:
                print(f"    - {tool} ({reason})")
            print("\nConsider:")
            print("  1. Using existing tool instead")
            print("  2. Adding to existing tool as new function")
            print("  3. Using different naming")
        else:
            print("\n[OK] No similar tools found")
            print(f"Suggested name: {suggest_tool_name(new_tool.rsplit('.', 1)[0], '')}")
    else:
        print("Usage:")
        print("  python tool_naming_convention.py <tool_name>")
        print("\nExamples:")
        print("  python tool_naming_convention.py my_new_tool.py")
        print("  python tool_naming_convention.py SmartAnalyzer_001.py")

if __name__ == "__main__":
    main()
