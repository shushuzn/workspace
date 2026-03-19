#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Standardize Naming - 统一命名规范

将 kebab-case 工具重命名为 underscore
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"
TOOLS_DIR = Path("30-scripts-tools")

def standardize_naming():
    """统一命名规范"""
    
    print("=" * 70)
    print("📝 统一命名规范")
    print("=" * 70)
    
    # 加载分析结果
    with open("flow-archive/20260318-universal-workflow-001/naming-analysis.json", 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    kebab_tools = analysis["kebab_tools"]
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 重命名统计
    renamed_files = 0
    renamed_tools = 0
    skipped = 0
    
    print(f"\n📊 需要重命名：{len(kebab_tools)} 个工具\n")
    
    for old_id in kebab_tools:
        new_id = old_id.replace('-', '_')
        
        if old_id not in tools:
            print(f"⚠️  跳过：{old_id} (不在工具库中)")
            skipped += 1
            continue
        
        # 检查新 ID 是否已存在
        if new_id in tools:
            print(f"⚠️  跳过：{old_id} → {new_id} (已存在)")
            skipped += 1
            continue
        
        # 重命名工具定义
        tool_data = tools[old_id]
        tools[new_id] = tool_data
        del tools[old_id]
        
        # 更新工具 ID 元数据
        tools[new_id]["renamed_from"] = old_id
        tools[new_id]["renamed_at"] = datetime.now().isoformat()
        tools[new_id]["naming_standard"] = "underscore"
        
        # 重命名文件 (如果存在)
        old_file = TOOLS_DIR / f"{old_id}.py"
        new_file = TOOLS_DIR / f"{new_id}.py"
        
        if old_file.exists():
            shutil.move(str(old_file), str(new_file))
            renamed_files += 1
            print(f"✅ {old_id} → {new_id} (文件已重命名)")
        else:
            print(f"✅ {old_id} → {new_id} (仅工具定义)")
        
        renamed_tools += 1
    
    # 更新工具库
    registry["tools"] = tools
    registry["version"] = "1.7.8"
    registry["updated_at"] = datetime.now().isoformat()
    registry["naming_standard"] = {
        "standardized_at": datetime.now().isoformat(),
        "renamed_tools": renamed_tools,
        "renamed_files": renamed_files,
        "skipped": skipped,
        "compliance_rate": len([t for t in tools if '-' not in t]) / len(tools) * 100
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 输出统计
    print("\n" + "=" * 70)
    print("📊 重命名统计")
    print("=" * 70)
    print(f"  工具重命名：{renamed_tools} 个")
    print(f"  文件重命名：{renamed_files} 个")
    print(f"  跳过：{skipped} 个")
    
    # 计算新合规率
    total = len(tools)
    underscore_count = len([t for t in tools if '-' not in t])
    compliance_rate = underscore_count / total * 100
    
    print(f"\n📊 新合规率：{compliance_rate:.1f}% ({underscore_count}/{total})")
    
    print("\n" + "=" * 70)
    print("✅ 命名规范统一完成!")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    standardize_naming()
