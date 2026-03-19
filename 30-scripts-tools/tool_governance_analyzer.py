#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Governance Analyzer - 工具治理分析

分析 424 个工具现状，提出治理方案
"""

import json
from pathlib import Path
from collections import Counter
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

def analyze_tools():
    """分析工具库"""
    
    print("=" * 70)
    print("🔧 工具库治理分析")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    version = registry.get("version", "unknown")
    
    total_tools = len(tools)
    
    print(f"\n📊 工具库概览:")
    print(f"  版本：{version}")
    print(f"  总工具数：{total_tools}")
    
    # 按类别统计
    categories = Counter()
    for tool_id, tool in tools.items():
        category = tool.get("category", "uncategorized")
        categories[category] += 1
    
    print(f"\n📊 类别分布 (Top 10):")
    for category, count in categories.most_common(10):
        print(f"  {category}: {count} 个工具")
    
    # 按文件分析
    files = [tool.get("file", "") for tool in tools.values()]
    files = [f for f in files if f]
    
    print(f"\n📊 文件统计:")
    print(f"  有文件定义：{len(files)} 个")
    print(f"  无文件定义：{total_tools - len(files)} 个")
    
    # 检查文件是否存在
    existing_files = []
    missing_files = []
    
    for file in files:
        file_path = Path("30-scripts-tools") / file
        if file_path.exists():
            existing_files.append(file)
        else:
            missing_files.append(file)
    
    print(f"  文件存在：{len(existing_files)} 个")
    print(f"  文件缺失：{len(missing_files)} 个")
    
    if missing_files:
        print(f"\n⚠️  缺失文件 (Top 20):")
        for file in missing_files[:20]:
            print(f"    - {file}")
    
    # 工具命名分析
    naming_patterns = {
        "snake_case": 0,
        "kebab_case": 0,
        "camelCase": 0,
        "other": 0
    }
    
    for tool_id in tools.keys():
        if "_" in tool_id:
            naming_patterns["snake_case"] += 1
        elif "-" in tool_id:
            naming_patterns["kebab_case"] += 1
        elif tool_id[0].islower():
            naming_patterns["camelCase"] += 1
        else:
            naming_patterns["other"] += 1
    
    print(f"\n📊 命名规范:")
    for pattern, count in naming_patterns.items():
        print(f"  {pattern}: {count} 个")
    
    # 工具使用频率分析 (基于触发器)
    tools_with_triggers = sum(1 for tool in tools.values() if tool.get("triggers"))
    auto_tools = sum(1 for tool in tools.values() if tool.get("triggers") and "session_end" in tool.get("triggers", []))
    
    print(f"\n📊 自动化程度:")
    print(f"  有触发器：{tools_with_triggers} 个 ({tools_with_triggers/total_tools*100:.1f}%)")
    print(f"  会话结束自动：{auto_tools} 个")
    
    # 工具版本分析
    tools_with_version = sum(1 for tool in tools.values() if tool.get("version"))
    
    print(f"\n📊 版本管理:")
    print(f"  有版本号：{tools_with_version} 个 ({tools_with_version/total_tools*100:.1f}%)")
    print(f"  无版本号：{total_tools - tools_with_version} 个")
    
    # 生成治理建议
    print(f"\n💡 治理建议:")
    
    issues = []
    
    if len(missing_files) > 0:
        issues.append(f"1. 清理缺失文件：{len(missing_files)} 个工具定义但文件不存在")
    
    if categories["uncategorized"] > 0:
        issues.append(f"2. 分类未分类工具：{categories.get('uncategorized', 0)} 个")
    
    if naming_patterns["other"] > 0:
        issues.append(f"3. 统一命名规范：{naming_patterns['other']} 个不符合规范")
    
    if tools_with_version < total_tools * 0.5:
        issues.append(f"4. 添加版本管理：仅 {tools_with_version/total_tools*100:.1f}% 工具有版本号")
    
    if tools_with_triggers < total_tools * 0.2:
        issues.append(f"5. 提升自动化：仅 {tools_with_triggers/total_tools*100:.1f}% 工具有触发器")
    
    for issue in issues:
        print(f"  {issue}")
    
    # 保存分析报告
    report = {
        "analysis_date": datetime.now().isoformat(),
        "version": version,
        "total_tools": total_tools,
        "categories": dict(categories),
        "naming_patterns": naming_patterns,
        "files": {
            "total": len(files),
            "existing": len(existing_files),
            "missing": len(missing_files),
            "missing_files": missing_files
        },
        "automation": {
            "with_triggers": tools_with_triggers,
            "auto_session_end": auto_tools
        },
        "versioning": {
            "with_version": tools_with_version,
            "without_version": total_tools - tools_with_version
        },
        "issues": issues
    }
    
    report_path = Path("flow-archive/20260318-universal-workflow-001/tool-governance-analysis.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 报告已保存：{report_path}")
    
    print("\n" + "=" * 70)
    print("✅ 工具治理分析完成!")
    print("=" * 70)
    
    return report


if __name__ == '__main__':
    analyze_tools()
