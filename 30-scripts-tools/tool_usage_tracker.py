#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Usage Tracker (Fast) - 工具使用跟踪 (快速版)

只扫描 30-scripts-tools 目录，加快速度
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TOOLS_DIR = Path("D:\\OpenClaw\\workspace\\30-scripts-tools")
TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

def scan_for_tool_usage():
    """扫描工具目录统计使用"""
    
    print("=" * 70)
    print("📊 工具使用统计 (快速版)")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    tool_ids = list(tools.keys())
    
    # 使用统计
    usage_stats = defaultdict(lambda: {"count": 0, "files": []})
    
    # 扫描文件
    files_scanned = 0
    
    print("\n🔍 扫描 30-scripts-tools 目录...")
    
    for file_path in TOOLS_DIR.glob("*.py"):
        files_scanned += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 查找工具 ID
            for tool_id in tool_ids:
                pattern = r'\b' + re.escape(tool_id) + r'\b'
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                if matches:
                    usage_stats[tool_id]["count"] += len(matches)
                    
                    rel_path = file_path.name
                    if len(usage_stats[tool_id]["files"]) < 5:
                        usage_stats[tool_id]["files"].append(rel_path)
        
        except Exception as e:
            pass
    
    print(f"✅ 扫描完成：{files_scanned} 个文件")
    
    # 更新工具库
    print("\n📝 更新工具库...")
    
    updated = 0
    for tool_id, stats in usage_stats.items():
        if tool_id in tools:
            tools[tool_id]["usage_count"] = stats["count"]
            tools[tool_id]["usage_files"] = stats["files"]
            tools[tool_id]["usage_tracked_at"] = datetime.now().isoformat()
            updated += 1
    
    registry["tools"] = tools
    registry["version"] = "1.7.6"
    registry["updated_at"] = datetime.now().isoformat()
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 统计结果
    print("\n" + "=" * 70)
    print("📊 使用统计结果")
    print("=" * 70)
    
    # 按使用次数排序
    sorted_tools = sorted(
        [(tid, tools[tid].get("usage_count", 0)) for tid in tools],
        key=lambda x: x[1],
        reverse=True
    )
    
    # 热门工具 (Top 15)
    print("\n🔥 热门工具 (Top 15):")
    for i, (tool_id, count) in enumerate(sorted_tools[:15], 1):
        tool_name = tools[tool_id].get("name", "")[:40]
        print(f"  {i:2d}. [{tool_id}] - {count} 次")
    
    # 冷门工具 (0 次)
    unused = [(tid, cnt) for tid, cnt in sorted_tools if cnt == 0]
    print(f"\n❄️  冷门工具 (0 次使用): {len(unused)} 个 ({len(unused)/len(sorted_tools)*100:.1f}%)")
    if unused[:15]:
        print("  前 15 个:")
        for tool_id, count in unused[:15]:
            tool_name = tools[tool_id].get("name", "")[:30]
            print(f"    - [{tool_id}]")
    
    # 使用分布
    high = len([t for t in sorted_tools if t[1] > 10])
    medium = len([t for t in sorted_tools if 5 <= t[1] <= 10])
    low = len([t for t in sorted_tools if 1 <= t[1] <= 4])
    
    print(f"\n📊 分布:")
    print(f"  高频 (>10 次): {high} 个")
    print(f"  中频 (5-10 次): {medium} 个")
    print(f"  低频 (1-4 次): {low} 个")
    print(f"  未使用 (0 次): {len(unused)} 个")
    
    # 保存报告
    report = {
        "tracking_date": datetime.now().isoformat(),
        "files_scanned": files_scanned,
        "total_tools": len(tools),
        "tools_tracked": updated,
        "top_15": sorted_tools[:15],
        "unused": unused,
        "usage_distribution": {
            "high": high,
            "medium": medium,
            "low": low,
            "unused": len(unused)
        }
    }
    
    report_path = Path("flow-archive/20260318-universal-workflow-001/tool-usage-stats.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 报告已保存")
    
    print("\n" + "=" * 70)
    print("✅ 完成!")
    print("=" * 70)
    
    return report

if __name__ == '__main__':
    scan_for_tool_usage()
