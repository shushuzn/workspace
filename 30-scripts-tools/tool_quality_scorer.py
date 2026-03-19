#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Quality Scorer - 工具质量评分器

为每个工具计算质量评分 (0-100)
维度：功能独特性 (30%) + 代码质量 (25%) + 文档完整 (20%) + 使用频率 (15%) + 维护状态 (10%)
"""

import json
from pathlib import Path
from datetime import datetime

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

def calculate_quality_score(tool_id: str, tool_data: dict) -> dict:
    """计算单个工具的质量评分"""
    
    scores = {
        "functionality": 0,  # 功能独特性 (30%)
        "code_quality": 0,   # 代码质量 (25%)
        "documentation": 0,  # 文档完整 (20%)
        "usage": 0,          # 使用频率 (15%)
        "maintenance": 0     # 维护状态 (10%)
    }
    
    details = {
        "functionality": "",
        "code_quality": "",
        "documentation": "",
        "usage": "",
        "maintenance": ""
    }
    
    # 1. 功能独特性 (30%)
    # 检查是否有独特功能描述
    desc = tool_data.get("description", "").lower()
    name = tool_data.get("name", "").lower()
    
    unique_keywords = ["unique", "special", "advanced", "auto", "smart", "optimize", "analyze"]
    has_unique = any(kw in desc or kw in name for kw in unique_keywords)
    
    if has_unique:
        scores["functionality"] = 80
        details["functionality"] = "有独特功能描述"
    else:
        scores["functionality"] = 50
        details["functionality"] = "功能描述一般"
    
    # 2. 代码质量 (25%)
    # 检查文件是否存在、大小是否合理
    file_path = tool_data.get("file", "")
    
    if file_path and Path(file_path).exists():
        file_size = Path(file_path).stat().st_size
        
        if 1000 <= file_size <= 50000:  # 1KB-50KB 合理范围
            scores["code_quality"] = 90
            details["code_quality"] = f"文件存在且大小合理 ({file_size} bytes)"
        elif file_size < 1000:
            scores["code_quality"] = 60
            details["code_quality"] = f"文件过小 ({file_size} bytes)"
        else:
            scores["code_quality"] = 70
            details["code_quality"] = f"文件较大 ({file_size} bytes)"
    else:
        scores["code_quality"] = 40
        details["code_quality"] = "文件不存在或无文件"
    
    # 3. 文档完整 (20%)
    # 检查描述、参数、示例
    has_description = len(tool_data.get("description", "")) > 20
    has_parameters = len(tool_data.get("parameters", [])) > 0
    has_examples = len(tool_data.get("examples", [])) > 0
    
    doc_score = 0
    if has_description:
        doc_score += 50
    if has_parameters:
        doc_score += 30
    if has_examples:
        doc_score += 20
    
    scores["documentation"] = doc_score
    details["documentation"] = f"描述:{has_description}, 参数:{has_parameters}, 示例:{has_examples}"
    
    # 4. 使用频率 (15%)
    usage_count = tool_data.get("usage_count", 0)
    
    if usage_count >= 100:
        scores["usage"] = 100
        details["usage"] = f"高频使用 ({usage_count} 次)"
    elif usage_count >= 10:
        scores["usage"] = 70
        details["usage"] = f"中频使用 ({usage_count} 次)"
    elif usage_count >= 1:
        scores["usage"] = 50
        details["usage"] = f"低频使用 ({usage_count} 次)"
    else:
        scores["usage"] = 30
        details["usage"] = "未使用 (0 次)"
    
    # 5. 维护状态 (10%)
    # 检查最近是否更新
    added_at = tool_data.get("added_at", "")
    updated_at = tool_data.get("updated_at", "")
    restored_at = tool_data.get("restored_at", "")
    
    # 简单判断：如果有 updated_at 或 restored_at，认为在维护
    if updated_at or restored_at:
        scores["maintenance"] = 80
        details["maintenance"] = "最近有更新或恢复"
    elif added_at:
        scores["maintenance"] = 60
        details["maintenance"] = "已添加但未更新"
    else:
        scores["maintenance"] = 40
        details["maintenance"] = "无时间戳"
    
    # 计算加权总分
    weights = {
        "functionality": 0.30,
        "code_quality": 0.25,
        "documentation": 0.20,
        "usage": 0.15,
        "maintenance": 0.10
    }
    
    total_score = sum(scores[dim] * weights[dim] for dim in scores)
    
    return {
        "tool_id": tool_id,
        "total_score": round(total_score, 1),
        "dimension_scores": scores,
        "dimension_details": details,
        "calculated_at": datetime.now().isoformat()
    }


def score_all_tools():
    """为所有工具计算质量评分"""
    
    print("=" * 70)
    print("Tool Quality Scoring")
    print("=" * 70)
    
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    print(f"\nTotal tools: {len(tools)}")
    
    results = []
    score_distribution = {
        "excellent": 0,  # 80-100
        "good": 0,       # 60-79
        "fair": 0,       # 40-59
        "poor": 0        # 0-39
    }
    
    for tool_id, tool_data in tools.items():
        result = calculate_quality_score(tool_id, tool_data)
        results.append(result)
        
        # 更新工具数据
        tools[tool_id]["quality_score"] = result["total_score"]
        tools[tool_id]["quality_details"] = result["dimension_details"]
        
        # 统计分布
        score = result["total_score"]
        if score >= 80:
            score_distribution["excellent"] += 1
        elif score >= 60:
            score_distribution["good"] += 1
        elif score >= 40:
            score_distribution["fair"] += 1
        else:
            score_distribution["poor"] += 1
    
    # 更新工具库
    registry["tools"] = tools
    registry["quality_assessment"] = {
        "assessed_at": datetime.now().isoformat(),
        "total_tools": len(tools),
        "average_score": round(sum(r["total_score"] for r in results) / len(results), 1),
        "distribution": score_distribution
    }
    
    with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # 输出结果
    print(f"\nAverage quality score: {registry['quality_assessment']['average_score']}")
    
    print(f"\nScore Distribution:")
    print(f"  Excellent (80-100): {score_distribution['excellent']} tools")
    print(f"  Good (60-79):       {score_distribution['good']} tools")
    print(f"  Fair (40-59):       {score_distribution['fair']} tools")
    print(f"  Poor (0-39):        {score_distribution['poor']} tools")
    
    # 输出 Top 10 和 Bottom 10
    results.sort(key=lambda x: x["total_score"], reverse=True)
    
    print(f"\nTop 10 Tools:")
    for i, r in enumerate(results[:10], 1):
        print(f"  {i}. [{r['tool_id']}] - {r['total_score']} pts")
    
    print(f"\nBottom 10 Tools:")
    for i, r in enumerate(results[-10:], 1):
        print(f"  {i}. [{r['tool_id']}] - {r['total_score']} pts")
    
    # 保存详细报告
    report_file = Path("21-reports/tool-quality-assessment-report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "assessed_at": datetime.now().isoformat(),
            "total_tools": len(results),
            "average_score": registry['quality_assessment']['average_score'],
            "distribution": score_distribution,
            "top_10": results[:10],
            "bottom_10": results[-10:]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport saved to: {report_file}")
    
    print("\n" + "=" * 70)
    print("Quality scoring complete!")
    print("=" * 70)
    
    return results


if __name__ == '__main__':
    score_all_tools()
