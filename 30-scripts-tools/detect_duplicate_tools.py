#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Detect Duplicate Tools - 检测重复工具

分析工具库，识别功能重复的工具
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

def detect_duplicates():
    """检测重复工具"""
    
    print("=" * 70)
    print("🔍 检测重复工具")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    print(f"\n📊 总工具数：{len(tools)}")
    
    # 按关键词分组
    keyword_groups = defaultdict(list)
    
    for tool_id, tool in tools.items():
        name = tool.get("name", "").lower()
        desc = tool.get("description", "").lower()
        text = f"{tool_id} {name} {desc}"
        
        # 提取核心关键词
        keywords = extract_keywords(text)
        
        for kw in keywords:
            keyword_groups[kw].append(tool_id)
    
    # 识别重复组 (3 个以上工具共享关键词)
    duplicate_groups = {}
    for kw, tool_ids in keyword_groups.items():
        if len(tool_ids) >= 3:
            duplicate_groups[kw] = tool_ids
    
    print(f"\n📊 发现 {len(duplicate_groups)} 个潜在重复组")
    
    # 详细分析
    print("\n" + "=" * 70)
    print("📋 重复工具组 (Top 20)")
    print("=" * 70)
    
    sorted_groups = sorted(duplicate_groups.items(), key=lambda x: len(x[1]), reverse=True)
    
    analysis_results = []
    
    for kw, tool_ids in sorted_groups[:20]:
        print(f"\n🔹 关键词：{kw} ({len(tool_ids)} 个工具)")
        
        group_tools = []
        for tid in tool_ids[:10]:  # 显示前 10 个
            tool = tools.get(tid, {})
            usage = tool.get("usage_count", 0)
            print(f"    [{tid}] - 使用：{usage} 次")
            group_tools.append({
                "tool_id": tid,
                "usage_count": usage,
                "name": tool.get("name", ""),
                "description": tool.get("description", "")[:80]
            })
        
        if len(tool_ids) > 10:
            print(f"    ... 还有 {len(tool_ids) - 10} 个")
        
        analysis_results.append({
            "keyword": kw,
            "tool_count": len(tool_ids),
            "tools": group_tools,
            "recommendation": generate_recommendation(group_tools)
        })
    
    # 保存分析结果
    report_path = Path("flow-archive/20260318-universal-workflow-001/duplicate-analysis.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "analysis_date": datetime.now().isoformat(),
            "total_tools": len(tools),
            "duplicate_groups": len(duplicate_groups),
            "top_20_groups": analysis_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 报告已保存")
    
    # 估算可删除数量
    potential_deletions = sum(len(g["tools"]) - 1 for g in analysis_results if len(g["tools"]) > 1)
    print(f"\n📊 估算可删除：~{potential_deletions} 个工具")
    
    print("\n" + "=" * 70)
    print("✅ 检测完成!")
    print("=" * 70)
    
    return analysis_results

def extract_keywords(text):
    """提取核心关键词"""
    
    # 移除常见停用词
    stopwords = {"the", "a", "an", "for", "with", "to", "of", "and", "or", "in", "on"}
    
    # 提取单词
    words = re.findall(r'\b[a-z_]+\b', text.lower())
    
    # 过滤短词和停用词
    keywords = [w for w in words if len(w) >= 4 and w not in stopwords]
    
    # 统计频率
    from collections import Counter
    freq = Counter(keywords)
    
    # 返回高频词
    return [kw for kw, count in freq.items() if count >= 2]

def generate_recommendation(tools):
    """生成合并建议"""
    
    if not tools:
        return "无建议"
    
    # 按使用次数排序
    sorted_tools = sorted(tools, key=lambda x: x["usage_count"], reverse=True)
    
    # 保留使用最多的
    keep = sorted_tools[0]["tool_id"] if sorted_tools else "unknown"
    
    # 建议删除的
    to_merge = [t["tool_id"] for t in sorted_tools[1:]]
    
    return {
        "keep": keep,
        "merge": to_merge[:5],  # 最多建议合并 5 个
        "reason": f"保留使用最多的工具 ({sorted_tools[0]['usage_count']} 次)"
    }

if __name__ == '__main__':
    detect_duplicates()
