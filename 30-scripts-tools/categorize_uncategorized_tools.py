#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Categorize Uncategorized Tools - 分类未分类工具

分析 27 个 uncategorized 工具，自动建议分类
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 预定义分类关键词
CATEGORY_KEYWORDS = {
    "workflow": ["workflow", "flow", "step", "stage", "pipeline", "enforcer", "scheduler"],
    "memory": ["memory", "remember", "recall", "retrieve", "compress", "distill"],
    "optimization": ["optimize", "performance", "speed", "cache", "accelerate", "enhance"],
    "quality": ["quality", "critic", "review", "validate", "verify", "check"],
    "reporting": ["report", "document", "summary", "changelog", "log"],
    "integration": ["integration", "connect", "sync", "import", "export"],
    "automation": ["auto", "batch", "schedule", "trigger", "cron"],
    "analysis": ["analyze", "scan", "detect", "inspect", "diagnose"],
    "utility": ["util", "helper", "tool", "register", "manage"],
    "deprecated": ["deprecated", "legacy", "old", "obsolete"]
}

def suggest_category(tool_id, tool_data):
    """根据工具 ID 和描述建议分类"""
    
    text = f"{tool_id} {tool_data.get('name', '')} {tool_data.get('description', '')}".lower()
    
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score
    
    if scores:
        best_category = max(scores, key=scores.get)
        return best_category, scores[best_category]
    
    return "uncategorized", 0

def categorize_tools():
    """分类未分类工具"""
    
    print("=" * 70)
    print("📂 分类未分类工具")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 找到未分类工具
    uncategorized = []
    for tool_id, tool in tools.items():
        category = tool.get("category", "")
        if category == "uncategorized" or not category:
            uncategorized.append({
                "tool_id": tool_id,
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "current_category": category
            })
    
    print(f"\n📊 未分类工具：{len(uncategorized)} 个\n")
    
    # 为每个工具建议分类
    suggestions = []
    for tool in uncategorized:
        suggested_cat, confidence = suggest_category(tool["tool_id"], tool)
        
        suggestions.append({
            **tool,
            "suggested_category": suggested_cat,
            "confidence": confidence
        })
        
        print(f"[{tool['tool_id']}]")
        print(f"  名称：{tool['name']}")
        print(f"  描述：{tool['description'][:80]}...")
        print(f"  建议分类：{suggested_cat} (置信度：{confidence})")
        print()
    
    # 按建议分类统计
    category_counts = {}
    for s in suggestions:
        cat = s["suggested_category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("=" * 70)
    print("📊 建议分类统计:")
    print("=" * 70)
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} 个")
    
    # 保存建议
    report = {
        "analysis_date": datetime.now().isoformat(),
        "total_uncategorized": len(uncategorized),
        "suggestions": suggestions,
        "category_counts": category_counts
    }
    
    report_path = Path("flow-archive/20260318-universal-workflow-001/uncategorized-tools-analysis.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 报告已保存：{report_path}")
    
    print("\n" + "=" * 70)
    print("✅ 未分类工具分析完成!")
    print("=" * 70)
    
    return suggestions

if __name__ == '__main__':
    categorize_tools()
