#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Merge Duplicate Tools - 合并重复工具

基于使用次数合并功能重复的工具
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"
DUPLICATE_ANALYSIS = "flow-archive/20260318-universal-workflow-001/duplicate-analysis.json"

# 合并策略
MERGE_STRATEGY = {
    # memory 类 - 保留使用最多的，合并低频
    "memory": {
        "keep_threshold": 2,  # 保留使用次数>=2 的
        "min_keep": 3  # 至少保留 3 个核心工具
    },
    # brainstorm 类 - 合并为 1 个统一工具
    "brainstorm": {
        "keep_threshold": 1,
        "min_keep": 1
    },
    # auto-critic - 保留主版本
    "auto": {
        "keep_threshold": 10,
        "min_keep": 1
    }
}

def merge_duplicates(confirm=True):
    """合并重复工具"""
    
    print("=" * 70)
    print("🔀 合并重复工具")
    print("=" * 70)
    
    # 加载分析结果
    with open(DUPLICATE_ANALYSIS, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    groups = analysis.get("top_20_groups", [])
    
    print(f"\n📊 重复组数：{len(groups)}")
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 合并统计
    to_delete = []
    to_keep = []
    
    for group in groups:
        keyword = group["keyword"]
        group_tools = group["tools"]
        
        print(f"\n🔹 处理组：{keyword} ({len(group_tools)} 个工具)")
        
        # 获取策略
        strategy = None
        for kw, strat in MERGE_STRATEGY.items():
            if kw in keyword.lower():
                strategy = strat
                break
        
        if not strategy:
            strategy = {"keep_threshold": 1, "min_keep": 1}
        
        # 按使用次数排序
        sorted_tools = sorted(group_tools, key=lambda x: x["usage_count"], reverse=True)
        
        # 决定保留和删除
        keep_list = []
        delete_list = []
        
        for i, tool in enumerate(sorted_tools):
            if i < strategy["min_keep"]:
                # 至少保留前 N 个
                keep_list.append(tool["tool_id"])
            elif tool["usage_count"] >= strategy["keep_threshold"]:
                # 使用次数达标的保留
                keep_list.append(tool["tool_id"])
            else:
                # 否则删除
                delete_list.append(tool["tool_id"])
        
        print(f"  保留：{len(keep_list)} 个 - {', '.join(keep_list[:5])}")
        if delete_list:
            print(f"  删除：{len(delete_list)} 个 - {', '.join(delete_list[:5])}")
        
        to_keep.extend(keep_list)
        to_delete.extend(delete_list)
    
    # 去重
    to_delete = list(set(to_delete))
    to_keep = list(set(to_keep))
    
    # 移除冲突 (如果工具同时出现在两个列表)
    to_delete = [t for t in to_delete if t not in to_keep]
    
    print("\n" + "=" * 70)
    print("📊 合并统计")
    print("=" * 70)
    print(f"  保留工具：{len(to_keep)} 个")
    print(f"  删除工具：{len(to_delete)} 个")
    
    if not to_delete:
        print("\n✅ 没有需要删除的工具")
        return True
    
    # 确认
    if confirm:
        print("\n⚠️  即将删除以下工具:")
        for tid in to_delete[:20]:
            print(f"  - [{tid}]")
        if len(to_delete) > 20:
            print(f"  ... 还有 {len(to_delete) - 20} 个")
        
        response = input(f"\n确认删除 {len(to_delete)} 个工具？(yes/no): ")
        if response.lower() != 'yes':
            print("❌ 已取消")
            return False
    
    # 执行删除
    deleted = 0
    backup_list = []
    
    for tool_id in to_delete:
        if tool_id in tools:
            tool = tools[tool_id]
            
            # 备份信息
            backup_list.append({
                "tool_id": tool_id,
                "name": tool.get("name", ""),
                "deleted_at": datetime.now().isoformat(),
                "reason": "duplicate_merge"
            })
            
            # 从工具库删除
            del tools[tool_id]
            deleted += 1
    
    # 更新工具库
    registry["tools"] = tools
    registry["version"] = "1.8.1"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    registry["merge_record"] = {
        "merged_at": datetime.now().isoformat(),
        "deleted_count": deleted,
        "reason": "duplicate_merge"
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 保存备份
    backup_path = Path("99-backups/deprecated-tools/merged-tools-backup.json")
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_list, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 删除完成：{deleted} 个工具")
    print(f"📊 工具库变化：{analysis['total_tools']} → {len(tools)} (-{deleted})")
    print(f"💾 备份已保存：{backup_path}")
    
    print("\n" + "=" * 70)
    print("✅ 合并完成!")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    import sys
    confirm = "--no-confirm" not in sys.argv
    merge_duplicates(confirm=confirm)
