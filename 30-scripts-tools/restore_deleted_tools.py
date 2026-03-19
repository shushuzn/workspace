#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Restore Deleted Tools - 恢复被删除工具

立即恢复 Week 3-4 删除的工具，重新评估
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# Week 3 删除的 86 个工具备份
WEEK3_BACKUP = "99-backups/deprecated-tools/deleted-tools-backup.json"

# Week 4 删除的工具备份
WEEK4_MERGE_BACKUP = "99-backups/deprecated-tools/merged-tools-backup.json"
WEEK4_FINAL_BACKUP = "99-backups/deprecated-tools/final-cleanup-backup.json"

def restore_tools():
    """恢复被删除工具"""
    
    print("=" * 70)
    print("🔄 恢复被删除工具")
    print("=" * 70)
    
    # 加载当前工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    original_count = len(tools)
    
    print(f"\n📊 当前工具数：{original_count}")
    
    restored = 0
    
    # 恢复 Week 4 最终清理的 9 个工具
    print("\n📝 恢复 Week 4 最终清理工具 (9 个):")
    try:
        with open(WEEK4_FINAL_BACKUP, 'r', encoding='utf-8') as f:
            week4_final = json.load(f)
        
        for tool_data in week4_final:
            tool_id = tool_data["tool_id"]
            if tool_id not in tools:
                tools[tool_id] = {
                    "name": tool_data.get("name", ""),
                    "description": "待补充",
                    "category": "general",
                    "status": "active",
                    "restored_at": datetime.now().isoformat(),
                    "restored_from": "week4_final_cleanup"
                }
                print(f"  ✅ 恢复：{tool_id}")
                restored += 1
    except FileNotFoundError:
        print("  ⚠️  备份文件未找到")
    
    # 恢复 Week 4 合并的工具
    print("\n📝 恢复 Week 4 合并工具:")
    try:
        with open(WEEK4_MERGE_BACKUP, 'r', encoding='utf-8') as f:
            week4_merge = json.load(f)
        
        for tool_data in week4_merge:
            tool_id = tool_data["tool_id"]
            if tool_id not in tools:
                tools[tool_id] = {
                    "name": tool_data.get("name", ""),
                    "description": "待补充",
                    "category": "general",
                    "status": "active",
                    "restored_at": datetime.now().isoformat(),
                    "restored_from": "week4_merge"
                }
                print(f"  ✅ 恢复：{tool_id}")
                restored += 1
    except FileNotFoundError:
        print("  ⚠️  备份文件未找到")
    
    # 恢复 Week 3 删除的工具 (分批恢复，先恢复核心功能)
    print("\n📝 恢复 Week 3 删除工具 (优先恢复有实际功能的):")
    try:
        with open(WEEK3_BACKUP, 'r', encoding='utf-8') as f:
            week3_deleted = json.load(f)
        
        # 优先恢复有文件、有功能的工具
        priority_keywords = ["workflow", "memory", "critic", "session", "cache", "optimize", "analyze"]
        
        for tool_data in week3_deleted:
            tool_id = tool_data["tool_id"]
            
            # 如果是核心功能相关，优先恢复
            is_priority = any(kw in tool_id.lower() for kw in priority_keywords)
            
            if tool_id not in tools and is_priority:
                tools[tool_id] = {
                    "name": tool_data.get("name", ""),
                    "description": "待补充",
                    "category": "general",
                    "status": "active",
                    "restored_at": datetime.now().isoformat(),
                    "restored_from": "week3_deletion"
                }
                print(f"  ✅ 恢复：{tool_id}")
                restored += 1
        
        print(f"  ... (其余工具待人工审查后恢复)")
    except FileNotFoundError:
        print("  ⚠️  备份文件未找到")
    
    # 更新工具库
    registry["tools"] = tools
    registry["version"] = "1.9.1"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    registry["restoration_record"] = {
        "restored_at": datetime.now().isoformat(),
        "restored_count": restored,
        "reason": "quality_over_quantity - 质量优先于数量"
    }
    
    # 移除错误的 -20% 里程碑标记
    if "milestone_20_percent" in registry:
        del registry["milestone_20_percent"]
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 恢复统计:")
    print(f"  恢复前：{original_count} 个")
    print(f"  恢复后：{len(tools)} 个")
    print(f"  恢复数：{restored} 个")
    
    print("\n" + "=" * 70)
    print("⚠️  反思:")
    print("=" * 70)
    print("""
❌ 错误：为了达成 -20% 数量目标而删除工具
✅ 正确：质量优先于数量，工具价值不应仅由使用次数决定

教训:
1. 使用次数=0 不等于工具无用 (可能是备用/特殊场景)
2. 数量目标不应凌驾于质量之上
3. 删除前需要人工审查和验证
4. 应该建立质量评估体系，而非简单删除

下一步:
1. 人工审查每个工具的实际价值
2. 建立工具质量评分体系
3. 完善工具文档和使用说明
4. 制定合理的治理策略
""")
    
    print("\n" + "=" * 70)
    print("✅ 恢复完成!")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    restore_tools()
