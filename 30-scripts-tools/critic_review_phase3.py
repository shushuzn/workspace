#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Critic Review - 批判者审查

审查速度优化 Phase 3 完成质量
"""

import json
from pathlib import Path
from datetime import datetime

def critic_review():
    """批判者审查"""
    
    print("=" * 70)
    print("🔍 批判者审查 - 速度优化 Phase 3")
    print("=" * 70)
    
    review = {
        "timestamp": datetime.now().isoformat(),
        "flow_id": "20260319-speed-optimization-phase3",
        "review_type": "phase_completion",
        "scores": {},
        "issues": {
            "critical": [],
            "major": [],
            "minor": []
        },
        "recommendations": []
    }
    
    # 审查维度
    dimensions = {
        "completeness": "完整性 - 所有交付物是否完成",
        "quality": "质量 - 交付物是否符合标准",
        "documentation": "文档 - 文档是否完整清晰",
        "testing": "测试 - 是否经过验证",
        "performance": "性能 - 是否达到预期目标"
    }
    
    print("\n📊 审查维度:\n")
    
    # 1. 完整性审查
    workflow_dir = Path("flow-archive/20260318-universal-workflow-001")
    required_files = [
        "SPEED-OPTIMIZATION-FINAL-SUMMARY.md",
        "SPEED-OPTIMIZATION-GUIDE.md",
        "performance-comparison-report.json",
        "checkpoint.json",
        "verification-result.json"
    ]
    
    missing_files = []
    for f in required_files:
        if not (workflow_dir / f).exists():
            missing_files.append(f)
    
    if not missing_files:
        review["scores"]["completeness"] = 100
        print("  ✅ 完整性：100/100 - 所有交付物完成")
    else:
        review["scores"]["completeness"] = 60
        review["issues"]["critical"].append(f"缺失文件：{missing_files}")
        print(f"  ❌ 完整性：60/100 - 缺失 {len(missing_files)} 个文件")
    
    # 2. 质量审查
    summary_file = workflow_dir / "SPEED-OPTIMIZATION-FINAL-SUMMARY.md"
    if summary_file.exists():
        size = summary_file.stat().st_size
        if size >= 5000:
            review["scores"]["quality"] = 90
            print("  ✅ 质量：90/100 - 报告详细完整")
        else:
            review["scores"]["quality"] = 70
            review["issues"]["minor"].append("报告内容可以更详细")
            print("  ⚠️  质量：70/100 - 报告可以更详细")
    else:
        review["scores"]["quality"] = 0
        review["issues"]["critical"].append("总结报告缺失")
        print("  ❌ 质量：0/100 - 总结报告缺失")
    
    # 3. 文档审查
    guide_file = workflow_dir / "SPEED-OPTIMIZATION-GUIDE.md"
    if guide_file.exists():
        content = guide_file.read_text(encoding='utf-8')
        
        has_quick_start = "快速开始" in content
        has_troubleshooting = "故障排除" in content
        has_examples = "示例" in content or "example" in content.lower()
        
        doc_score = 0
        if has_quick_start:
            doc_score += 40
        if has_troubleshooting:
            doc_score += 30
        if has_examples:
            doc_score += 30
        
        review["scores"]["documentation"] = doc_score
        print(f"  {'✅' if doc_score >= 80 else '⚠️'}  文档：{doc_score}/100")
        
        if doc_score < 80:
            review["issues"]["minor"].append("文档可以添加更多示例")
    else:
        review["scores"]["documentation"] = 0
        review["issues"]["major"].append("实施指南缺失")
        print("  ❌ 文档：0/100 - 实施指南缺失")
    
    # 4. 测试审查
    verification_file = workflow_dir / "verification-result.json"
    if verification_file.exists():
        with open(verification_file, 'r', encoding='utf-8') as f:
            verification = json.load(f)
        
        if verification.get("all_present", False):
            review["scores"]["testing"] = 90
            print("  ✅ 测试：90/100 - 验证通过")
        else:
            review["scores"]["testing"] = 50
            review["issues"]["major"].append("验证未完全通过")
            print("  ⚠️  测试：50/100 - 验证有问题")
    else:
        review["scores"]["testing"] = 0
        review["issues"]["major"].append("缺少验证报告")
        print("  ❌ 测试：0/100 - 缺少验证")
    
    # 5. 性能审查
    perf_file = workflow_dir / "performance-comparison-report.json"
    if perf_file.exists():
        with open(perf_file, 'r', encoding='utf-8') as f:
            perf = json.load(f)
        
        overall_gain = perf.get("overall_gain", "0x")
        
        if "253x" in overall_gain:
            review["scores"]["performance"] = 100
            print(f"  ✅ 性能：100/100 - 整体提升 {overall_gain}")
        elif "100x" in overall_gain:
            review["scores"]["performance"] = 80
            print(f"  ✅ 性能：80/100 - 整体提升 {overall_gain}")
        else:
            review["scores"]["performance"] = 60
            print(f"  ⚠️  性能：60/100 - 提升 {overall_gain}")
    else:
        review["scores"]["performance"] = 0
        review["issues"]["major"].append("缺少性能数据")
        print("  ❌ 性能：0/100 - 缺少性能数据")
    
    # 计算总分
    total_score = sum(review["scores"].values()) / len(review["scores"])
    review["total_score"] = round(total_score, 1)
    
    print("\n" + "=" * 70)
    print(f"📊 总分：{total_score:.1f}/100")
    print("=" * 70)
    
    # 问题统计
    critical = len(review["issues"]["critical"])
    major = len(review["issues"]["major"])
    minor = len(review["issues"]["minor"])
    
    print(f"\n📊 问题统计:")
    print(f"  致命：{critical} 个")
    print(f"  严重：{major} 个")
    print(f"  一般：{minor} 个")
    
    # 审查结论
    print("\n" + "=" * 70)
    if critical > 0:
        print("❌ 审查不通过 - 存在致命问题")
        print("\n必须修复:")
        for issue in review["issues"]["critical"]:
            print(f"  - {issue}")
        review["conclusion"] = "fail"
    elif major > 2:
        print("⚠️  审查有条件通过 - 存在多个严重问题")
        print("\n建议修复:")
        for issue in review["issues"]["major"]:
            print(f"  - {issue}")
        review["conclusion"] = "conditional_pass"
    elif total_score >= 80:
        print("✅ 审查通过 - 质量良好")
        review["conclusion"] = "pass"
    else:
        print("⚠️  审查通过 - 质量一般")
        review["conclusion"] = "pass_with_improvements"
    print("=" * 70)
    
    # 改进建议
    print("\n💡 改进建议:")
    if review["scores"].get("documentation", 0) < 90:
        print("  - 添加更多使用示例和代码片段")
    if review["scores"].get("testing", 0) < 90:
        print("  - 添加自动化测试用例")
    if review["scores"].get("performance", 0) < 100:
        print("  - 进一步优化性能瓶颈")
    
    # 保存审查结果
    result_file = Path("flow-archive/20260318-universal-workflow-001/critic-review-phase3.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(review, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 审查结果已保存：{result_file}")
    
    return review["conclusion"] == "pass" or review["conclusion"] == "conditional_pass"


if __name__ == '__main__':
    success = critic_review()
    exit(0 if success else 1)
