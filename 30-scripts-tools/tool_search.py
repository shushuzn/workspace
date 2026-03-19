#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Search - 工具搜索

功能:
- 按关键词搜索工具
- 按分类筛选
- 支持模糊匹配
- 显示使用统计
"""

import json
import sys
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

def load_tools():
    """加载工具库"""
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    return registry

def search_tools(query=None, category=None, limit=20):
    """搜索工具"""
    
    registry = load_tools()
    tools = registry.get("tools", {})
    
    results = []
    
    for tool_id, tool in tools.items():
        score = 0
        
        # 分类筛选
        if category:
            tool_cat = tool.get("category", "")
            if category.lower() not in tool_cat.lower():
                continue
        
        # 关键词搜索
        if query:
            query_lower = query.lower()
            text = f"{tool_id} {tool.get('name', '')} {tool.get('description', '')}".lower()
            
            # 精确匹配
            if query_lower in tool_id.lower():
                score += 10
            elif query_lower in tool.get("name", "").lower():
                score += 8
            elif query_lower in tool.get("description", "").lower():
                score += 5
            
            # 模糊匹配 (包含关键词)
            for kw in query_lower.split():
                if kw in tool_id.lower():
                    score += 3
                elif kw in text:
                    score += 1
            
            if score == 0:
                continue
        
        results.append({
            "tool_id": tool_id,
            "name": tool.get("name", ""),
            "description": tool.get("description", ""),
            "category": tool.get("category", ""),
            "file": tool.get("file", ""),
            "score": score,
            "status": tool.get("status", "active"),
            "usage_count": tool.get("usage_count", 0)
        })
    
    # 排序 (按分数 + 使用次数)
    results.sort(key=lambda x: (x["score"], x["usage_count"]), reverse=True)
    
    return results[:limit]

def list_categories():
    """列出所有分类"""
    
    registry = load_tools()
    tools = registry.get("tools", {})
    
    category_counts = {}
    for tool in tools.values():
        cat = tool.get("category", "uncategorized")
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return category_counts

def print_results(results, verbose=False):
    """打印搜索结果"""
    
    if not results:
        print("⚠️  未找到匹配的工具")
        return
    
    print(f"\n📊 找到 {len(results)} 个工具:\n")
    
    for i, tool in enumerate(results, 1):
        status_icon = "✅" if tool["status"] == "active" else "⚠️"
        print(f"{i}. {status_icon} [{tool['tool_id']}]")
        print(f"   名称：{tool['name']}")
        print(f"   分类：{tool['category']}")
        print(f"   描述：{tool['description'][:100]}...")
        
        if verbose:
            print(f"   文件：{tool['file']}")
            print(f"   使用次数：{tool['usage_count']}")
            print(f"   状态：{tool['status']}")
        
        print()

def main():
    """主函数"""
    
    if len(sys.argv) < 2:
        print("=" * 70)
        print("🔍 工具搜索")
        print("=" * 70)
        print("\n用法:")
        print("  py tool_search.py <关键词>              - 搜索工具")
        print("  py tool_search.py -c <分类>             - 列出分类下的工具")
        print("  py tool_search.py --categories          - 列出所有分类")
        print("  py tool_search.py -v <关键词>           - 详细模式")
        print("\n示例:")
        print("  py tool_search.py memory                - 搜索 memory 相关工具")
        print("  py tool_search.py -c workflow           - 列出 workflow 分类工具")
        print("  py tool_search.py --categories          - 查看所有分类")
        print("=" * 70)
        return
    
    # 列出分类
    if sys.argv[1] == "--categories":
        categories = list_categories()
        print("=" * 70)
        print("📂 工具分类统计")
        print("=" * 70)
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} 个")
        print(f"\n总工具数：{sum(categories.values())}")
        print("=" * 70)
        return
    
    # 按分类筛选
    if sys.argv[1] == "-c" and len(sys.argv) >= 3:
        category = sys.argv[2]
        results = search_tools(query=None, category=category)
        print(f"\n📂 分类：{category}")
        print_results(results, verbose=True)
        return
    
    # 搜索
    verbose = "-v" in sys.argv
    query_parts = [arg for arg in sys.argv[1:] if arg != "-v"]
    query = " ".join(query_parts)
    
    print("=" * 70)
    print(f"🔍 搜索：{query}")
    print("=" * 70)
    
    results = search_tools(query=query, limit=20)
    print_results(results, verbose=verbose)

if __name__ == '__main__':
    main()
