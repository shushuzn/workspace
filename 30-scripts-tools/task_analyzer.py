#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Task Analyzer - 任务分析

功能:
- 分析任务复杂度
- 估算所需时间
- 识别依赖关系
"""

import re
from datetime import datetime

def analyze_task(task_description):
    """分析任务"""
    
    analysis = {
        "task": task_description,
        "timestamp": datetime.now().isoformat(),
        "complexity": "medium",
        "estimated_time_minutes": 30,
        "risk_level": "low",
        "dependencies": [],
        "suggested_steps": []
    }
    
    # 关键词分析
    task_lower = task_description.lower()
    
    # 复杂度判断
    high_complexity_keywords = ["multi", "complex", "full", "complete", "end-to-end", "system"]
    medium_complexity_keywords = ["create", "build", "implement", "update", "modify"]
    low_complexity_keywords = ["fix", "check", "list", "show", "read"]
    
    complexity_score = 0
    
    for keyword in high_complexity_keywords:
        if keyword in task_lower:
            complexity_score += 3
    
    for keyword in medium_complexity_keywords:
        if keyword in task_lower:
            complexity_score += 2
    
    for keyword in low_complexity_keywords:
        if keyword in task_lower:
            complexity_score += 1
    
    if complexity_score >= 8:
        analysis["complexity"] = "high"
        analysis["estimated_time_minutes"] = 120
        analysis["risk_level"] = "high"
    elif complexity_score >= 4:
        analysis["complexity"] = "medium"
        analysis["estimated_time_minutes"] = 30
        analysis["risk_level"] = "medium"
    else:
        analysis["complexity"] = "low"
        analysis["estimated_time_minutes"] = 10
        analysis["risk_level"] = "low"
    
    # 识别依赖
    if "git" in task_lower or "commit" in task_lower:
        analysis["dependencies"].append("git_repository")
    
    if "file" in task_lower or "read" in task_lower or "write" in task_lower:
        analysis["dependencies"].append("file_system_access")
    
    if "web" in task_lower or "http" in task_lower or "api" in task_lower:
        analysis["dependencies"].append("network_access")
    
    # 建议步骤
    if analysis["complexity"] == "high":
        analysis["suggested_steps"] = [
            "1. 任务分解",
            "2. 风险评估",
            "3. 制定方案",
            "4. 分步执行",
            "5. 验证测试",
            "6. 提交总结"
        ]
    elif analysis["complexity"] == "medium":
        analysis["suggested_steps"] = [
            "1. 确认需求",
            "2. 执行任务",
            "3. 验证结果",
            "4. 提交总结"
        ]
    else:
        analysis["suggested_steps"] = [
            "1. 执行任务",
            "2. 验证结果"
        ]
    
    return analysis

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: py task_analyzer.py <task_description>")
        print("Example: py task_analyzer.py \"Create new tool for session compression\"")
        return
    
    task = " ".join(sys.argv[1:])
    
    analysis = analyze_task(task)
    
    print("=" * 70)
    print("📊 任务分析报告")
    print("=" * 70)
    
    print(f"\n📝 任务：{analysis['task']}")
    print(f"⏰ 时间：{analysis['timestamp']}")
    print(f"\n📈 复杂度：{analysis['complexity']}")
    print(f"⏱️  预估时间：{analysis['estimated_time_minutes']} 分钟")
    print(f"⚠️  风险等级：{analysis['risk_level']}")
    
    if analysis['dependencies']:
        print(f"\n🔗 依赖:")
        for dep in analysis['dependencies']:
            print(f"    - {dep}")
    
    print(f"\n📋 建议步骤:")
    for step in analysis['suggested_steps']:
        print(f"    {step}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
