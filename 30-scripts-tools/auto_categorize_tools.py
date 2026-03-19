#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Categorize Tools - 自动分类工具

应用建议分类到工具库
"""

import json
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 手动修正映射 (针对置信度 0 的工具)
MANUAL_FIXES = {
    "remediation-tracker": "quality",  # 整改跟踪 → 质量
    "brainstorm-define": "automation",  # 头脑风暴 → 自动化
    "brainstorm-diverge": "automation",
    "brainstorm-prioritize": "automation",
    "brainstorm-action": "automation"
}

def auto_categorize():
    """自动分类工具"""
    
    print("=" * 70)
    print("📂 自动分类工具")
    print("=" * 70)
    
    # 加载分析结果
    with open("flow-archive/20260318-universal-workflow-001/uncategorized-tools-analysis.json", 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    suggestions = analysis["suggestions"]
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    categorized = 0
    manual_fixes = 0
    
    for suggestion in suggestions:
        tool_id = suggestion["tool_id"]
        
        # 优先使用手动修正
        if tool_id in MANUAL_FIXES:
            category = MANUAL_FIXES[tool_id]
            manual_fixes += 1
        else:
            category = suggestion["suggested_category"]
        
        # 更新工具分类
        if tool_id in tools:
            tools[tool_id]["category"] = category
            tools[tool_id]["categorized_at"] = datetime.now().isoformat()
            tools[tool_id]["categorized_method"] = "auto"
            print(f"✅ [{tool_id}] → {category}")
            categorized += 1
    
    registry["tools"] = tools
    registry["version"] = "1.7.4"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    registry["categorized_count"] = categorized
    registry["manual_fixes"] = manual_fixes
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 新版本：1.7.4")
    print(f"📊 分类工具：{categorized} 个")
    print(f"📊 手动修正：{manual_fixes} 个")
    print(f"📊 总工具数：{len(tools)}")
    
    # 统计分类分布
    category_counts = {}
    for tool_id, tool in tools.items():
        cat = tool.get("category", "uncategorized")
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print(f"\n📊 分类分布:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {cat}: {count} 个")
    
    print("\n" + "=" * 70)
    print("✅ 自动分类完成!")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    auto_categorize()
