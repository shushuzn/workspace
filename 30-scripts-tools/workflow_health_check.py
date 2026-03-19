#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Health Check - 工作流健康度检查

检查工作流执行状态、完成率、待执行步骤
"""

import json
from pathlib import Path
from datetime import datetime

WORKFLOW_DIR = Path("flow-archive/20260318-universal-workflow-001")

def check_workflow_health():
    """检查工作流健康度"""
    
    print("=" * 70)
    print("🏥 工作流健康度检查")
    print("=" * 70)
    
    # 1. 读取工作流配置
    workflow_file = WORKFLOW_DIR / "workflow.json"
    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    print(f"\n📊 工作流信息:")
    print(f"  Flow ID: {workflow['flow_id']}")
    print(f"  名称：{workflow['name']}")
    print(f"  版本：{workflow['version']}")
    print(f"  总步骤：{workflow['total_steps']}")
    
    # 2. 检查 checkpoint
    checkpoint_file = WORKFLOW_DIR / "checkpoint.json"
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        print(f"\n📊 执行状态:")
        print(f"  当前 Flow: {checkpoint.get('flow_id', 'N/A')}")
        print(f"  状态：{checkpoint.get('status', 'unknown')}")
        print(f"  当前步骤：{checkpoint.get('current_step', 0)}")
        print(f"  已完成：{checkpoint.get('completed_steps', [])}")
    else:
        print("\n⚠️  未找到 checkpoint.json")
        checkpoint = None
    
    # 3. 统计报告文件
    reports = list(WORKFLOW_DIR.glob("*.md"))
    report_categories = {
        "brainstorm": [],
        "optimization": [],
        "governance": [],
        "protection": [],
        "reflection": [],
        "other": []
    }
    
    for report in reports:
        name = report.name.lower()
        if "brainstorm" in name:
            report_categories["brainstorm"].append(report.name)
        elif "optimization" in name or "speed" in name:
            report_categories["optimization"].append(report.name)
        elif "governance" in name or "week" in name or "tool" in name:
            report_categories["governance"].append(report.name)
        elif "protection" in name:
            report_categories["protection"].append(report.name)
        elif "reflection" in name:
            report_categories["reflection"].append(report.name)
        else:
            report_categories["other"].append(report.name)
    
    print(f"\n📊 报告文件统计:")
    print(f"  总报告数：{len(reports)}")
    for category, files in report_categories.items():
        if files:
            print(f"  {category.capitalize()}: {len(files)} 个")
    
    # 4. 检查工具库状态
    tools_file = Path("30-scripts-tools/tools_registry.json")
    if tools_file.exists():
        with open(tools_file, 'r', encoding='utf-8') as f:
            tools = json.load(f)
        
        print(f"\n📊 工具库状态:")
        print(f"  版本：{tools.get('version', 'N/A')}")
        print(f"  总工具数：{tools.get('total_tools', len(tools.get('tools', {})))}")
        
        if "quality_assessment" in tools:
            qa = tools["quality_assessment"]
            print(f"  平均质量评分：{qa.get('average_score', 'N/A')}")
            dist = qa.get('distribution', {})
            print(f"  优秀 (80+): {dist.get('excellent', 0)} 个")
            print(f"  良好 (60-79): {dist.get('good', 0)} 个")
            print(f"  一般 (40-59): {dist.get('fair', 0)} 个")
            print(f"  待改进 (<40): {dist.get('poor', 0)} 个")
    
    # 5. 计算健康度评分
    health_score = 100
    issues = []
    
    # 检查点缺失 -10
    if not checkpoint_file.exists():
        health_score -= 10
        issues.append("checkpoint.json 缺失")
    
    # 报告文件过少 -5
    if len(reports) < 10:
        health_score -= 5
        issues.append("报告文件过少")
    
    # 工具质量评分低 -10
    if tools_file.exists() and "quality_assessment" in tools:
        avg_score = tools["quality_assessment"].get("average_score", 0)
        if avg_score < 50:
            health_score -= 10
            issues.append(f"工具平均质量评分过低 ({avg_score})")
    
    print(f"\n🏥 健康度评分：{health_score}/100")
    
    if issues:
        print(f"\n⚠️  发现问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ 无明显问题")
    
    # 6. 建议下一步行动
    print("\n💡 建议下一步行动:")
    
    if checkpoint and checkpoint.get('status') == 'in_progress':
        print(f"  1️⃣  继续执行未完成的 Flow: {checkpoint.get('flow_id')}")
        print(f"     当前步骤：{checkpoint.get('current_step')}/{workflow['total_steps']}")
    
    if tools_file.exists() and "quality_assessment" in tools:
        avg_score = tools["quality_assessment"].get("average_score", 0)
        if avg_score < 60:
            print(f"  2️⃣  提升工具质量 (当前平均 {avg_score} 分)")
            print(f"     - 完善工具文档")
            print(f"     - 添加使用示例")
            print(f"     - 优化代码质量")
    
    if not issues:
        print(f"  3️⃣  执行新任务/工作流")
        print(f"     - 查看待办任务")
        print(f"     - 规划下一阶段目标")
    
    print("\n" + "=" * 70)
    
    return {
        "health_score": health_score,
        "issues": issues,
        "checkpoint": checkpoint,
        "reports_count": len(reports),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == '__main__':
    check_workflow_health()
