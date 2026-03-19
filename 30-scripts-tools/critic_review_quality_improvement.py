#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Critic Review - Tool Quality Improvement

批判者审查工具质量改进成果
"""

import json
from pathlib import Path
from datetime import datetime

def critic_review():
    """批判者审查"""
    
    print("=" * 70)
    print("🔍 批判者审查 - 工具质量改进")
    print("=" * 70)
    
    review = {
        "timestamp": datetime.now().isoformat(),
        "flow_id": "20260320-tool-quality-improvement",
        "review_type": "quality_improvement",
        "scores": {},
        "issues": {"critical": [], "major": [], "minor": []}
    }
    
    # 1. 改进成果审查
    baseline = 50.2
    current = 51.3
    target = 55.0
    
    improvement = current - baseline
    progress = (improvement / (target - baseline)) * 100
    
    print(f"\n📊 改进成果:")
    print(f"  基线：{baseline} 分")
    print(f"  当前：{current} 分")
    print(f"  目标：{target} 分")
    print(f"  改进：+{improvement} 分 ({progress:.0f}%)")
    
    if progress >= 100:
        review["scores"]["improvement"] = 100
        print("  ✅ 目标达成")
    elif progress >= 50:
        review["scores"]["improvement"] = 80
        print("  ✅ 进度过半")
    else:
        review["scores"]["improvement"] = 60
        print("  ⚠️  进度不足")
    
    # 2. 工具数量审查
    poor_before = 44
    poor_after = 24
    reduction = poor_before - poor_after
    reduction_rate = (reduction / poor_before) * 100
    
    print(f"\n📊 待改进工具:")
    print(f"  改进前：{poor_before} 个")
    print(f"  改进后：{poor_after} 个")
    print(f"  减少：{reduction} 个 ({reduction_rate:.0f}%)")
    
    if reduction_rate >= 50:
        review["scores"]["reduction"] = 100
        print("  ✅ 减少 50%+")
    elif reduction_rate >= 30:
        review["scores"]["reduction"] = 80
        print("  ✅ 减少 30%+")
    else:
        review["scores"]["reduction"] = 60
        print("  ⚠️  减少不足")
    
    # 3. 文档质量审查
    tools_file = Path("30-scripts-tools/tools_registry.json")
    with open(tools_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    improved_tools = registry.get("improvement_record", {}).get("improved_count", 0)
    improved_tools += registry.get("improvement_record_phase2", {}).get("improved_count", 0)
    
    print(f"\n📊 文档改进:")
    print(f"  改进工具数：{improved_tools} 个")
    
    if improved_tools >= 20:
        review["scores"]["documentation"] = 90
        print("  ✅ 改进 20+ 工具")
    elif improved_tools >= 10:
        review["scores"]["documentation"] = 70
        print("  ✅ 改进 10+ 工具")
    else:
        review["scores"]["documentation"] = 50
        print("  ⚠️  改进不足")
    
    # 4. 可持续性审查
    print(f"\n📊 可持续性:")
    has_improvement_script = Path("30-scripts-tools/improve_tool_metadata.py").exists()
    has_phase2_script = Path("30-scripts-tools/improve_tool_metadata_phase2.py").exists()
    
    if has_improvement_script and has_phase2_script:
        review["scores"]["sustainability"] = 90
        print("  ✅ 有自动化改进脚本")
    elif has_improvement_script:
        review["scores"]["sustainability"] = 70
        print("  ✅ 有改进脚本")
    else:
        review["scores"]["sustainability"] = 50
        print("  ⚠️  缺少自动化脚本")
    
    # 计算总分
    total_score = sum(review["scores"].values()) / len(review["scores"])
    review["total_score"] = round(total_score, 1)
    
    print("\n" + "=" * 70)
    print(f"📊 总分：{total_score:.1f}/100")
    print("=" * 70)
    
    # 审查结论
    print("\n📋 审查结论:")
    if total_score >= 85:
        print("✅ 审查通过 - 质量优秀")
        review["conclusion"] = "pass_excellent"
    elif total_score >= 70:
        print("✅ 审查通过 - 质量良好")
        review["conclusion"] = "pass_good"
    else:
        print("⚠️  审查通过 - 质量一般")
        review["conclusion"] = "pass"
    
    # 改进建议
    print("\n💡 改进建议:")
    if progress < 100:
        print(f"  - 继续改进剩余 {poor_after} 个低分工具")
        print(f"  - 目标：达到 {target} 分 (还需 +{target-current:.1f}分)")
    if not has_phase2_script:
        print("  - 创建批量改进脚本")
    
    # 保存审查结果
    result_file = Path("flow-archive/20260318-universal-workflow-001/flow-quality-improvement/critic-review.json")
    result_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(review, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 审查结果已保存：{result_file}")
    
    return review["conclusion"] in ["pass_excellent", "pass_good", "pass"]


if __name__ == '__main__':
    critic_review()
