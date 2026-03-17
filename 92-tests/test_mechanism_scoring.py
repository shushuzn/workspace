#!/usr/bin/env python3
"""
机制深度评分测试
测试 arxiv-daily 的机制深度评分功能
"""

import sys
import importlib.util

# 加载模块
spec = importlib.util.spec_from_file_location("arxiv_daily", r'D:\npm-global\node_modules\openclaw\skills\arxiv-daily\scripts\arxiv-daily.py')
arxiv_daily = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arxiv_daily)

calculate_priority_score = arxiv_daily.calculate_priority_score

print("=" * 70)
print("机制深度评分测试")
print("=" * 70)

# 测试论文 1: 三重细胞死亡 (肿瘤贴片)
paper1 = {
    "source": "PubMed",
    "title": "A Stretchable, Transparent, Photothermally Stimulated Laser-Induced Graphene Patch for Noninvasive Skin Tumor Treatment",
    "abstract": """Melanoma causes over 80% of skin cancer-related deaths. Herein, we developed 
    a soft, stretchable laser-induced graphene (LIG)-Cu/PDMS patch. Upon photothermal 
    activation, it releases Cu2+ that accumulates in melanoma tissue. The patch enhances 
    reactive oxygen species production, inducing apoptosis, cuproptosis, and ferroptosis. 
    It also inhibits tumor invasion/metastasis and boosts antitumor immunity. In a mouse 
    model, two 1-h phototherapy sessions achieved effective tumor suppression within 10 days.""",
    "journal": "ACS Nano"
}

# 测试论文 2: 单一机制
paper2 = {
    "source": "PubMed",
    "title": "LIG-based glucose sensor",
    "abstract": """We developed a laser-induced graphene biosensor for glucose detection. 
    The sensor shows good sensitivity and selectivity in vitro.""",
    "journal": "Biosensors and Bioelectronics"
}

# 测试论文 3: 中等机制深度
paper3 = {
    "source": "PubMed",
    "title": "LIG neural probe for simultaneous recording",
    "abstract": """We present a multimodal neural probe integrating chemical-sensing and 
    neural-recording electrodes. Using laser-induced graphene process, we achieve 
    simultaneous glucose detection and neural spike acquisition in mouse hippocampus. 
    The probe shows ROS-mediated signaling and immune response modulation.""",
    "journal": "ACS Chemical Neuroscience"
}

print("\n[论文 1] 肿瘤贴片 (三重细胞死亡)")
print(f"  标题：{paper1['title'][:60]}...")
score1 = calculate_priority_score(paper1)
print(f"  评分：{score1:.1f}/5.0")
print(f"  预期：高分 (体内验证 +2, 高影响力期刊 +0.5, 多模态 +1.0, 机制深度 +2.0)")

print("\n[论文 2] 葡萄糖传感器 (单一机制)")
print(f"  标题：{paper2['title'][:60]}...")
score2 = calculate_priority_score(paper2)
print(f"  评分：{score2:.1f}/5.0")
print(f"  预期：中等分数 (体外验证 +1.0, 高影响力期刊 +0.5)")

print("\n[论文 3] 神经探针 (中等机制深度)")
print(f"  标题：{paper3['title'][:60]}...")
score3 = calculate_priority_score(paper3)
print(f"  评分：{score3:.1f}/5.0")
print(f"  预期：高分 (体内验证 +2, 高影响力期刊 +0.5, 多模态 +1.0, 机制深度 +1.0~1.5)")

print("\n" + "=" * 70)
print("测试结果分析")
print("=" * 70)

# 分析机制关键词检测
mechanism_keywords = [
    "apoptosis", "cuproptosis", "ferroptosis", "necrosis", "pyroptosis",
    "ROS", "reactive oxygen", "NF-kappaB", "MAPK", "PI3K-AKT",
    "immune", "inflammation", "cytokine", "T cell", "macrophage",
    "synergistic", "synergy", "multi-pathway", "dual", "triple", "multiple mechanism"
]

for i, paper in enumerate([paper1, paper2, paper3], 1):
    abstract_lower = paper["abstract"].lower()
    matched = [kw for kw in mechanism_keywords if kw in abstract_lower]
    print(f"\n论文 {i} 机制关键词匹配：{len(matched)} 个")
    if matched:
        print(f"  匹配词：{', '.join(matched[:5])}{'...' if len(matched) > 5 else ''}")

print("\n" + "=" * 70)
print("测试完成!")
print("=" * 70)
