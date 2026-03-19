#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyze Low Quality Tools - 分析低分工具

识别评分<40 分的工具，分析原因，制定改进计划
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"
OUTPUT_DIR = Path("flow-archive/20260318-universal-workflow-001/flow-quality-improvement")

def analyze_low_quality_tools():
    """分析低分工具"""
    
    print("=" * 70)
    print("📊 分析低分工具")
    print("=" * 70)
    
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 按评分分类
    categories = {
        "excellent": [],  # 80-100
        "good": [],       # 60-79
        "fair": [],       # 40-59
        "poor": []        # 0-39
    }
    
    for tool_id, tool_data in tools.items():
        score = tool_data.get("quality_score", 0)
        
        if score >= 80:
            categories["excellent"].append((tool_id, score))
        elif score >= 60:
            categories["good"].append((tool_id, score))
        elif score >= 40:
            categories["fair"].append((tool_id, score))
        else:
            categories["poor"].append((tool_id, score))
    
    # 排序
    for cat in categories:
        categories[cat].sort(key=lambda x: x[1])
    
    print(f"\n📊 工具库总览:")
    print(f"  总工具数：{len(tools)}")
    print(f"  平均评分：{registry.get('quality_assessment', {}).get('average_score', 'N/A')}")
    
    print(f"\n📊 评分分布:")
    print(f"  优秀 (80-100): {len(categories['excellent'])} 个")
    print(f"  良好 (60-79):  {len(categories['good'])} 个")
    print(f"  一般 (40-59):  {len(categories['fair'])} 个")
    print(f"  待改进 (0-39): {len(categories['poor'])} 个")
    
    # 分析低分工具原因
    print(f"\n🔍 低分工具分析 (<40 分，共{len(categories['poor'])} 个):\n")
    
    low_quality_analysis = []
    
    for i, (tool_id, score) in enumerate(categories["poor"][:20], 1):
        tool = tools.get(tool_id, {})
        
        # 分析低分原因
        reasons = []
        
        # 检查描述
        desc = tool.get("description", "")
        if len(desc) < 20:
            reasons.append("描述过短")
        
        # 检查参数
        params = tool.get("parameters", [])
        if not params:
            reasons.append("无参数说明")
        
        # 检查示例
        examples = tool.get("examples", [])
        if not examples:
            reasons.append("无使用示例")
        
        # 检查文件
        file_path = tool.get("file", "")
        has_file = Path(file_path).exists() if file_path else False
        if not has_file:
            reasons.append("无文件")
        
        analysis = {
            "rank": i,
            "tool_id": tool_id,
            "score": score,
            "name": tool.get("name", ""),
            "category": tool.get("category", ""),
            "reasons": reasons,
            "improvement_priority": "high" if len(reasons) >= 3 else "medium"
        }
        
        low_quality_analysis.append(analysis)
        
        print(f"  {i}. [{tool_id}] - {score} 分")
        print(f"      类别：{tool.get('category', 'unknown')}")
        print(f"      原因：{', '.join(reasons) if reasons else '未知'}")
        print(f"      优先级：{analysis['improvement_priority']}")
        print()
    
    # 保存分析结果
    result = {
        "analyzed_at": datetime.now().isoformat(),
        "total_tools": len(tools),
        "distribution": {
            "excellent": len(categories["excellent"]),
            "good": len(categories["good"]),
            "fair": len(categories["fair"]),
            "poor": len(categories["poor"])
        },
        "low_quality_analysis": low_quality_analysis,
        "improvement_targets": {
            "current_average": registry.get('quality_assessment', {}).get('average_score', 0),
            "target_average": 55,
            "poor_tools_to_improve": min(20, len(categories["poor"])),
            "expected_gain": "+4.8 分"
        }
    }
    
    result_file = OUTPUT_DIR / "low-quality-analysis.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"📁 分析结果已保存：{result_file}")
    
    # 选择 Top 20 优先改进
    print(f"\n✅ 选择 Top 20 优先改进工具:")
    for item in low_quality_analysis[:20]:
        print(f"  - {item['tool_id']} ({item['score']}分) - {', '.join(item['reasons'])}")
    
    return low_quality_analysis[:20]


if __name__ == '__main__':
    analyze_low_quality_tools()
