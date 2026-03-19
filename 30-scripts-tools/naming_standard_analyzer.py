#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Naming Standard Analyzer - 命名规范分析

分析工具命名，识别不符合规范的工具
"""

import json
import re
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

# 命名规范
NAMING_PATTERNS = {
    "underscore": r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$',  # snake_case
    "kebab": r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$',  # kebab-case
    "camel": r'^[a-z][a-zA-Z0-9]*$',  # camelCase
    "pascal": r'^[A-Z][a-zA-Z0-9]*$',  # PascalCase
}

def analyze_naming():
    """分析工具命名规范"""
    
    print("=" * 70)
    print("📝 命名规范分析")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 分类统计
    naming_stats = {
        "underscore": [],
        "kebab": [],
        "camel": [],
        "pascal": [],
        "other": []
    }
    
    for tool_id in tools:
        classified = False
        
        for pattern_name, pattern in NAMING_PATTERNS.items():
            if re.match(pattern, tool_id):
                naming_stats[pattern_name].append(tool_id)
                classified = True
                break
        
        if not classified:
            naming_stats["other"].append(tool_id)
    
    # 输出统计
    print("\n📊 命名规范分布:")
    print("=" * 70)
    
    total = len(tools)
    for pattern_name, tool_list in sorted(naming_stats.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(tool_list)
        percentage = count / total * 100
        print(f"  {pattern_name:12s}: {count:3d} 个 ({percentage:5.1f}%)")
        
        # 显示前 5 个示例
        if tool_list[:5]:
            print(f"    示例：{', '.join(tool_list[:5])}")
    
    # 识别需要重命名的工具 (kebab-case → underscore)
    kebab_tools = naming_stats["kebab"]
    
    print("\n" + "=" * 70)
    print("🔄 需要重命名的工具 (kebab → underscore)")
    print("=" * 70)
    
    if kebab_tools:
        print(f"\n共 {len(kebab_tools)} 个工具需要重命名:\n")
        
        rename_mapping = {}
        for tool_id in kebab_tools[:30]:  # 显示前 30 个
            new_id = tool_id.replace('-', '_')
            rename_mapping[tool_id] = new_id
            print(f"  [{tool_id}] → [{new_id}]")
        
        if len(kebab_tools) > 30:
            print(f"  ... 还有 {len(kebab_tools) - 30} 个")
        
        # 保存映射
        mapping_path = Path("flow-archive/20260318-universal-workflow-001/naming-rename-mapping.json")
        mapping_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump({
                "analysis_date": datetime.now().isoformat(),
                "total_kebab": len(kebab_tools),
                "rename_mapping": rename_mapping
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 映射已保存")
    else:
        print("\n✅ 所有工具已符合 underscore 命名规范!")
    
    # 保存分析报告
    report = {
        "analysis_date": datetime.now().isoformat(),
        "total_tools": total,
        "naming_distribution": {
            name: len(tools) for name, tools in naming_stats.items()
        },
        "kebab_tools": kebab_tools,
        "compliance_rate": len(naming_stats["underscore"]) / total * 100
    }
    
    report_path = Path("flow-archive/20260318-universal-workflow-001/naming-analysis.json")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 合规率：{report['compliance_rate']:.1f}%")
    print("\n" + "=" * 70)
    print("✅ 分析完成!")
    print("=" * 70)
    
    return report

if __name__ == '__main__':
    analyze_naming()
