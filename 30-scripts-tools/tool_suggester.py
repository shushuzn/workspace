#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Suggester - 工具推荐

功能:
- 根据任务描述推荐工具
- 基于关键词匹配
- 支持使用频率排序
"""

import json
from pathlib import Path

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

def load_tools():
    """加载工具库"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    return registry.get("tools", {})

def suggest_tools(task_description, top_k=5):
    """根据任务描述推荐工具"""
    
    tools = load_tools()
    
    # 关键词提取 (简单分词)
    keywords = task_description.lower().split()
    
    # 计算匹配分数
    scored_tools = []
    for tool_id, tool in tools.items():
        score = 0
        
        # 匹配工具 ID
        for keyword in keywords:
            if keyword in tool_id.lower():
                score += 3
        
        # 匹配工具名称
        name = tool.get("name", "").lower()
        for keyword in keywords:
            if keyword in name:
                score += 2
        
        # 匹配描述
        desc = tool.get("description", "").lower()
        for keyword in keywords:
            if keyword in desc:
                score += 1
        
        if score > 0:
            scored_tools.append({
                "tool_id": tool_id,
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "score": score
            })
    
    # 按分数排序
    scored_tools.sort(key=lambda x: x["score"], reverse=True)
    
    return scored_tools[:top_k]

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: py tool_suggester.py <task_description>")
        print("Example: py tool_suggester.py \"compress session memory\"")
        return
    
    task = " ".join(sys.argv[1:])
    
    print("=" * 70)
    print(f"🔍 工具推荐：{task}")
    print("=" * 70)
    
    suggestions = suggest_tools(task)
    
    if not suggestions:
        print("\n⚠️  未找到匹配的工具")
        return
    
    print(f"\n📊 推荐 {len(suggestions)} 个工具:\n")
    
    for i, tool in enumerate(suggestions, 1):
        print(f"{i}. [{tool['tool_id']}]")
        print(f"   名称：{tool['name']}")
        print(f"   描述：{tool['description']}")
        print(f"   匹配分数：{tool['score']}")
        print()

if __name__ == '__main__':
    main()
