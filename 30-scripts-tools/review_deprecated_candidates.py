#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Review Deprecated Candidates - 审查废弃候选

人工审查 88 个废弃候选工具，决定保留或删除
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"
DEPRECATED_CANDIDATES = "flow-archive/20260318-universal-workflow-001/deprecated-candidates.json"

# 自动保留规则
AUTO_KEEP_RULES = {
    # 核心基础设施
    "core_keywords": ["workflow", "memory", "critic", "session", "context", "tool_executor"],
    
    # 最近添加 (<30 天)
    "recent_days": 30,
    
    # 有文档的工具
    "has_docs": True
}

def review_deprecated():
    """审查废弃候选"""
    
    print("=" * 70)
    print("🏷️  审查废弃候选")
    print("=" * 70)
    
    # 加载废弃候选
    with open(DEPRECATED_CANDIDATES, 'r', encoding='utf-8') as f:
        deprecated_data = json.load(f)
    
    candidates = deprecated_data.get("deprecated_candidates", [])
    
    print(f"\n📊 废弃候选总数：{len(candidates)} 个")
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 分类审查
    auto_keep = []
    auto_delete = []
    manual_review = []
    
    for candidate in candidates:
        tool_id = candidate["tool_id"]
        
        if tool_id not in tools:
            continue
        
        tool = tools[tool_id]
        
        # 自动保留检查
        keep_reason = None
        
        # 规则 1: 核心关键词
        for keyword in AUTO_KEEP_RULES["core_keywords"]:
            if keyword in tool_id.lower():
                keep_reason = f"核心关键词：{keyword}"
                break
        
        # 规则 2: 最近添加
        if not keep_reason:
            added_at = tool.get("added_at", "")
            if added_at:
                try:
                    added_date = datetime.fromisoformat(added_at)
                    days_old = (datetime.now() - added_date).days
                    if days_old < AUTO_KEEP_RULES["recent_days"]:
                        keep_reason = f"最近添加：{days_old} 天前"
                except:
                    pass
        
        # 规则 3: 有相关文件
        if not keep_reason:
            file = tool.get("file", "")
            if file:
                file_path = Path("30-scripts-tools") / file
                if file_path.exists():
                    # 检查文件大小 (>1KB 认为是有实际内容)
                    if file_path.stat().st_size > 1024:
                        keep_reason = f"有文件：{file} ({file_path.stat().st_size} bytes)"
        
        # 分类
        if keep_reason:
            auto_keep.append({
                **candidate,
                "keep_reason": keep_reason
            })
        else:
            auto_delete.append(candidate)
    
    # 输出结果
    print("\n" + "=" * 70)
    print("📊 审查结果")
    print("=" * 70)
    
    print(f"\n✅ 自动保留：{len(auto_keep)} 个")
    print(f"❌ 自动删除：{len(auto_delete)} 个")
    print(f"📝 需要人工：{len(manual_review)} 个")
    
    # 显示保留列表
    if auto_keep:
        print("\n" + "=" * 70)
        print("✅ 自动保留工具")
        print("=" * 70)
        
        by_reason = {}
        for tool in auto_keep:
            reason = tool["keep_reason"]
            if reason not in by_reason:
                by_reason[reason] = []
            by_reason[reason].append(tool)
        
        for reason, reason_tools in sorted(by_reason.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n{reason} ({len(reason_tools)} 个):")
            for tool in reason_tools[:10]:
                print(f"  - [{tool['tool_id']}]")
            if len(reason_tools) > 10:
                print(f"  ... 还有 {len(reason_tools) - 10} 个")
    
    # 显示删除列表
    if auto_delete:
        print("\n" + "=" * 70)
        print("❌ 建议删除工具")
        print("=" * 70)
        
        by_category = {}
        for tool in auto_delete:
            cat = tool.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tool)
        
        for cat, cat_tools in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n{cat} ({len(cat_tools)} 个):")
            for tool in cat_tools[:15]:
                print(f"  - [{tool['tool_id']}]")
            if len(cat_tools) > 15:
                print(f"  ... 还有 {len(cat_tools) - 15} 个")
    
    # 保存审查结果
    review_result = {
        "review_date": datetime.now().isoformat(),
        "total_candidates": len(candidates),
        "auto_keep": auto_keep,
        "auto_delete": auto_delete,
        "manual_review": manual_review,
        "summary": {
            "auto_keep_count": len(auto_keep),
            "auto_delete_count": len(auto_delete),
            "manual_review_count": len(manual_review),
            "deletion_reduction": f"{len(auto_delete)}/{len(candidates)} ({len(auto_delete)/len(candidates)*100:.1f}%)"
        }
    }
    
    result_path = Path("flow-archive/20260318-universal-workflow-001/deprecated-review-result.json")
    
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(review_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 审查结果已保存")
    
    print("\n" + "=" * 70)
    print("✅ 审查完成!")
    print("=" * 70)
    
    return review_result

if __name__ == '__main__':
    review_deprecated()
