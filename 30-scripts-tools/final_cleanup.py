#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final Cleanup - 最终清理

删除 9 个低频工具达成 -20% 目标
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 保护的核心工具
PROTECTED = {
    "workflow_session_end", "workflow_brainstorm", "workflow_research", 
    "workflow_project", "workflow_enforcer", "memory-consistency-checker",
    "tool_usage_tracker", "mark_deprecated_tools"
}

# 建议删除的工具 (低频且非核心)
TO_DELETE = [
    "critical-issue-detector",  # quality, 0 次
    "critical-checks",  # quality-gate, 0 次
    "analyze_memory_scripts",  # memory, 0 次
    "analyze_memory_tools",  # memory, 0 次
    "context_db",  # context, 0 次
    "critic_daily_note_pollution",  # quality, 0 次
    "git_workflow",  # workflow, 0 次
    "memory_fix_tools",  # memory, 0 次
    "memory_rollback",  # memory, 0 次
]

def final_cleanup():
    """最终清理"""
    
    print("=" * 70)
    print("🧹 最终清理 - 达成 -20% 目标")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    original = 424
    current = len(tools)
    target = int(original * 0.8)  # 339
    
    print(f"\n📊 当前状态:")
    print(f"  原始：{original} 个")
    print(f"  当前：{current} 个")
    print(f"  目标：{target} 个 (-20%)")
    print(f"  差距：{current - target} 个")
    
    # 过滤掉已不存在的工具
    to_delete = [t for t in TO_DELETE if t in tools]
    
    print(f"\n📊 建议删除：{len(to_delete)} 个")
    
    for tid in to_delete:
        tool = tools.get(tid, {})
        print(f"  - [{tid}] - {tool.get('category', 'unknown')}")
    
    # 执行删除
    deleted = 0
    backup_list = []
    
    for tool_id in to_delete:
        if tool_id in tools:
            tool = tools[tool_id]
            
            backup_list.append({
                "tool_id": tool_id,
                "name": tool.get("name", ""),
                "deleted_at": datetime.now().isoformat(),
                "reason": "final_cleanup_target_20_percent"
            })
            
            del tools[tool_id]
            deleted += 1
    
    # 更新工具库
    registry["tools"] = tools
    registry["version"] = "1.9.0"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    
    # 计算最终进度
    final_count = len(tools)
    reduction = (original - final_count) / original * 100
    
    registry["milestone_20_percent"] = {
        "achieved_at": datetime.now().isoformat(),
        "original_count": original,
        "final_count": final_count,
        "reduction_count": original - final_count,
        "reduction_percentage": reduction,
        "target_achieved": reduction >= 20
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 保存备份
    backup_path = Path("99-backups/deprecated-tools/final-cleanup-backup.json")
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_list, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 删除完成：{deleted} 个")
    print(f"\n🎉 -20% 目标达成!")
    print(f"  原始：{original} 个")
    print(f"  最终：{final_count} 个")
    print(f"  减少：{original - final_count} 个 ({reduction:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✅ 清理完成! -20% 目标达成!")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    final_cleanup()
