#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extra Cleanup - 额外清理

进一步清理低频工具，达成 -20% 目标
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

def extra_cleanup(confirm=True):
    """额外清理"""
    
    print("=" * 70)
    print("🧹 额外清理")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 查找低频工具 (使用次数=0 且非核心)
    core_keywords = ["workflow", "memory", "critic", "session", "context", "tool_executor", "task"]
    
    low_usage_tools = []
    
    for tool_id, tool in tools.items():
        usage = tool.get("usage_count", 0)
        
        # 使用次数为 0
        if usage > 0:
            continue
        
        # 检查是否核心工具
        is_core = any(kw in tool_id.lower() for kw in core_keywords)
        if is_core:
            continue
        
        # 检查是否有文件
        file = tool.get("file", "")
        has_file = file and Path("30-scripts-tools").joinpath(file).exists()
        
        # 如果是最近添加 (<14 天)，保留
        added_at = tool.get("added_at", "")
        if added_at:
            try:
                added_date = datetime.fromisoformat(added_at)
                days_old = (datetime.now() - added_date).days
                if days_old < 14:
                    continue
            except:
                pass
        
        low_usage_tools.append({
            "tool_id": tool_id,
            "name": tool.get("name", ""),
            "file": file,
            "has_file": has_file,
            "usage_count": usage
        })
    
    print(f"\n📊 低频工具：{len(low_usage_tools)} 个")
    
    # 选择删除候选 (优先删除无文件的)
    no_file_tools = [t for t in low_usage_tools if not t["has_file"]]
    has_file_tools = [t for t in low_usage_tools if t["has_file"]]
    
    print(f"  无文件：{len(no_file_tools)} 个")
    print(f"  有文件：{len(has_file_tools)} 个")
    
    # 目标：再删除 9 个达成 -20%
    target_deletions = 9
    
    # 优先删除无文件的
    to_delete = no_file_tools[:target_deletions]
    
    if len(to_delete) < target_deletions:
        # 如果无文件不够，从有文件中选使用最少的
        remaining = target_deletions - len(to_delete)
        to_delete.extend(has_file_tools[:remaining])
    
    print(f"\n📊 建议删除：{len(to_delete)} 个")
    
    if not to_delete:
        print("✅ 没有需要删除的工具")
        return True
    
    # 显示删除列表
    print("\n⚠️  建议删除工具:")
    for tool in to_delete[:20]:
        file_status = "✅" if tool["has_file"] else "❌"
        print(f"  {file_status} [{tool['tool_id']}] - 文件：{tool['file'] or '无'}")
    
    # 确认
    if confirm:
        response = input(f"\n确认删除 {len(to_delete)} 个工具？(yes/no): ")
        if response.lower() != 'yes':
            print("❌ 已取消")
            return False
    
    # 执行删除
    deleted = 0
    backup_list = []
    
    for tool_data in to_delete:
        tool_id = tool_data["tool_id"]
        
        if tool_id in tools:
            tool = tools[tool_id]
            
            # 备份
            backup_list.append({
                **tool_data,
                "deleted_at": datetime.now().isoformat(),
                "reason": "extra_cleanup"
            })
            
            # 删除文件 (如果有)
            if tool_data["has_file"]:
                file_path = Path("30-scripts-tools") / tool_data["file"]
                try:
                    backup_dir = Path("99-backups/deprecated-tools")
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    file_path.rename(backup_dir / file_path.name)
                except:
                    pass
            
            # 从工具库删除
            del tools[tool_id]
            deleted += 1
    
    # 更新工具库
    registry["tools"] = tools
    registry["version"] = "1.8.2"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    registry["cleanup_record"] = {
        "cleaned_at": datetime.now().isoformat(),
        "deleted_count": deleted,
        "reason": "extra_cleanup_target_20_percent"
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 保存备份
    backup_path = Path("99-backups/deprecated-tools/extra-cleanup-backup.json")
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_list, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 删除完成：{deleted} 个")
    print(f"📊 工具库：{registry.get('total_tools', 0)} 个")
    
    # 计算 -20% 进度
    original = 424
    current = len(tools)
    reduction = (original - current) / original * 100
    
    print(f"\n📊 -20% 目标进度:")
    print(f"  原始：{original} 个")
    print(f"  当前：{current} 个")
    print(f"  减少：{original - current} 个 ({reduction:.1f}%)")
    
    if reduction >= 20:
        print(f"\n🎉 -20% 目标达成!")
    else:
        print(f"\n📊 还需删除：{int(original * 0.2 - (original - current))} 个")
    
    print("\n" + "=" * 70)
    print("✅ 清理完成!")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    import sys
    confirm = "--no-confirm" not in sys.argv
    extra_cleanup(confirm=confirm)
