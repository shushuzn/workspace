#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Delete Deprecated Tools - 删除废弃工具

实际删除已确认的废弃工具
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"
REVIEW_RESULT = "flow-archive/20260318-universal-workflow-001/deprecated-review-result.json"
TOOLS_DIR = Path("30-scripts-tools")

def delete_deprecated(confirm=True):
    """删除废弃工具"""
    
    print("=" * 70)
    print("🗑️  删除废弃工具")
    print("=" * 70)
    
    # 加载审查结果
    with open(REVIEW_RESULT, 'r', encoding='utf-8') as f:
        review = json.load(f)
    
    to_delete = review.get("auto_delete", [])
    
    print(f"\n📊 待删除工具：{len(to_delete)} 个")
    
    if not to_delete:
        print("✅ 没有需要删除的工具")
        return True
    
    # 确认
    if confirm:
        print("\n⚠️  即将删除以下工具:")
        for tool in to_delete[:20]:
            print(f"  - [{tool['tool_id']}]")
        if len(to_delete) > 20:
            print(f"  ... 还有 {len(to_delete) - 20} 个")
        
        response = input(f"\n确认删除 {len(to_delete)} 个工具？(yes/no): ")
        if response.lower() != 'yes':
            print("❌ 已取消")
            return False
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 删除工具
    deleted_tools = 0
    deleted_files = 0
    backup_list = []
    
    for tool_data in to_delete:
        tool_id = tool_data["tool_id"]
        
        if tool_id not in tools:
            continue
        
        tool = tools[tool_id]
        
        # 备份信息
        backup_list.append({
            "tool_id": tool_id,
            "name": tool.get("name", ""),
            "file": tool.get("file", ""),
            "deleted_at": datetime.now().isoformat()
        })
        
        # 删除文件 (如果存在)
        file = tool.get("file", "")
        if file:
            file_path = TOOLS_DIR / file
            if file_path.exists():
                # 移动到备份目录
                backup_dir = Path("99-backups/deprecated-tools")
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                try:
                    file_path.rename(backup_dir / file)
                    deleted_files += 1
                except Exception as e:
                    print(f"⚠️  文件删除失败：{file} - {e}")
        
        # 从工具库删除
        del tools[tool_id]
        deleted_tools += 1
    
    # 更新工具库
    registry["tools"] = tools
    registry["version"] = "1.8.0"
    registry["updated_at"] = datetime.now().isoformat()
    registry["total_tools"] = len(tools)
    registry["deletion_record"] = {
        "deleted_at": datetime.now().isoformat(),
        "deleted_count": deleted_tools,
        "files_backed_up": deleted_files,
        "backup_location": "99-backups/deprecated-tools/"
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 保存删除备份
    backup_path = Path("99-backups/deprecated-tools/deleted-tools-backup.json")
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_list, f, indent=2, ensure_ascii=False)
    
    # 输出结果
    print("\n" + "=" * 70)
    print("📊 删除统计")
    print("=" * 70)
    print(f"  工具删除：{deleted_tools} 个")
    print(f"  文件备份：{deleted_files} 个")
    print(f"  备份位置：99-backups/deprecated-tools/")
    
    print(f"\n📊 工具库变化：{review['total_candidates']} → {len(tools)} (-{deleted_tools})")
    
    print("\n" + "=" * 70)
    print("✅ 删除完成!")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    import sys
    confirm = "--no-confirm" not in sys.argv
    delete_deprecated(confirm=confirm)
