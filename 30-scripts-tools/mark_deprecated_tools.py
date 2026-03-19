#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mark Deprecated Tools - 标记废弃工具

基于使用统计标记废弃候选工具
"""

import json
from datetime import datetime, timedelta

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

def mark_deprecated():
    """标记废弃工具"""
    
    print("=" * 70)
    print("🏷️  标记废弃工具")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 加载使用统计
    try:
        with open("flow-archive/20260318-universal-workflow-001/tool-usage-stats.json", 'r', encoding='utf-8') as f:
            usage_report = json.load(f)
        unused_ids = [tid for tid, _ in usage_report.get("unused", [])]
    except:
        print("⚠️  未找到使用统计报告，跳过")
        unused_ids = []
    
    print(f"\n📊 未使用工具：{len(unused_ids)} 个")
    
    # 标记废弃候选
    deprecated_candidates = []
    
    for tool_id in unused_ids:
        if tool_id in tools:
            tool = tools[tool_id]
            
            # 检查是否已经是废弃状态
            if tool.get("status") == "deprecated":
                continue
            
            # 检查是否是核心工具 (根据名称判断)
            core_keywords = ["workflow", "memory", "critic", "session", "tool_executor"]
            is_core = any(kw in tool_id.lower() for kw in core_keywords)
            
            # 标记为废弃候选
            if not is_core:
                tool["status"] = "deprecated_candidate"
                tool["deprecated_reason"] = "unused_in_codebase"
                tool["deprecated_at"] = datetime.now().isoformat()
                tool["review_required"] = True
                
                deprecated_candidates.append({
                    "tool_id": tool_id,
                    "name": tool.get("name", ""),
                    "category": tool.get("category", ""),
                    "reason": "0 次使用"
                })
    
    # 更新工具库
    registry["tools"] = tools
    registry["version"] = "1.7.7"
    registry["updated_at"] = datetime.now().isoformat()
    registry["deprecated_count"] = len(deprecated_candidates)
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 输出结果
    print("\n" + "=" * 70)
    print("🏷️  废弃候选工具")
    print("=" * 70)
    
    if deprecated_candidates:
        print(f"\n标记 {len(deprecated_candidates)} 个工具为废弃候选:\n")
        
        # 按分类分组
        by_category = {}
        for tool in deprecated_candidates:
            cat = tool["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tool)
        
        for cat, cat_tools in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n{cat} ({len(cat_tools)} 个):")
            for tool in cat_tools[:10]:  # 每类显示前 10 个
                print(f"  - [{tool['tool_id']}] - {tool['name'][:40]}")
            if len(cat_tools) > 10:
                print(f"  ... 还有 {len(cat_tools) - 10} 个")
        
        print(f"\n💡 建议:")
        print(f"  1. 人工审查这些工具是否真的不需要")
        print(f"  2. 确认后可以删除或归档")
        print(f"  3. 更新 tools_registry.json")
    else:
        print("\n✅ 没有新的废弃候选工具")
    
    # 保存报告
    report = {
        "review_date": datetime.now().isoformat(),
        "total_unused": len(unused_ids),
        "deprecated_candidates": deprecated_candidates,
        "by_category": {cat: len(tools) for cat, tools in by_category.items()},
        "action_required": "manual_review"
    }
    
    report_path = Path("flow-archive/20260318-universal-workflow-001/deprecated-candidates.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 报告已保存")
    
    print("\n" + "=" * 70)
    print("✅ 完成!")
    print("=" * 70)
    
    return report

if __name__ == '__main__':
    from pathlib import Path
    mark_deprecated()
