#!/usr/bin/env python3
"""
跨领域类比查询测试
"""

import sys
import importlib.util

# 加载模块
spec = importlib.util.spec_from_file_location("kg_builder", r'D:\npm-global\node_modules\openclaw\skills\knowledge-graph\scripts\kg-builder.py')
kg_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kg_builder)

KnowledgeGraphBuilder = kg_builder.KnowledgeGraphBuilder

# 创建测试图谱
builder = KnowledgeGraphBuilder()

# 手动添加 CS 领域实体
builder.add_entities([
    {
        "id": "cs_adaptive_routing",
        "type": "Concept",
        "properties": {"name": "Adaptive Routing", "domain": "CS"}
    },
    {
        "id": "cs_modular_arch",
        "type": "Concept",
        "properties": {"name": "Modular Architecture", "domain": "CS"}
    },
])

# 手动添加材料科学领域实体
builder.add_entities([
    {
        "id": "mat_triphase_interface",
        "type": "Concept",
        "properties": {"name": "Triphase Interface", "domain": "Materials"}
    },
    {
        "id": "mat_lig",
        "type": "Material",
        "properties": {"name": "Laser-Induced Graphene", "domain": "Materials"}
    },
    {
        "id": "mat_composite",
        "type": "Material",
        "properties": {"name": "Composite Materials", "domain": "Materials"}
    },
])

# 手动添加生物学领域实体
builder.add_entities([
    {
        "id": "bio_synapse",
        "type": "Concept",
        "properties": {"name": "Synaptic Plasticity", "domain": "Biology"}
    },
    {
        "id": "bio_homeostasis",
        "type": "Concept",
        "properties": {"name": "Homeostasis", "domain": "Biology"}
    },
])

# 添加关系
builder.add_relations([
    # CS 领域关系
    {"source": "cs_adaptive_routing", "target": "cs_modular_arch", "type": "uses"},
    
    # 材料领域关系
    {"source": "mat_triphase_interface", "target": "mat_lig", "type": "uses"},
    {"source": "mat_composite", "target": "mat_lig", "type": "is_a"},
    
    # 生物领域关系
    {"source": "bio_synapse", "target": "bio_homeostasis", "type": "regulates"},
])

# 测试跨领域类比查询
print("=" * 60)
print("Cross-Domain Analogy Query Test")
print("=" * 60)

# Test 1: CS -> Materials
print("\n[Test 1] CS Adaptive Routing -> Materials")
analogies = builder.find_analogy("CS", "Adaptive Routing", "Materials")
for a in analogies:
    print(f"  [OK] {a['concept']} ({a['domain']})")
    print(f"    Similarity: {a['similarity_score']:.2f}")
    print(f"    Analogy Type: {a['analogy_type']}")

# Test 2: CS -> Biology
print("\n[Test 2] CS Adaptive Routing -> Biology")
analogies = builder.find_analogy("CS", "Adaptive Routing", "Biology")
for a in analogies:
    print(f"  [OK] {a['concept']} ({a['domain']})")
    print(f"    Similarity: {a['similarity_score']:.2f}")
    print(f"    Analogy Type: {a['analogy_type']}")

# Test 3: No target domain
print("\n[Test 3] CS Modular Architecture -> All domains")
analogies = builder.find_analogy("CS", "Modular Architecture")
for a in analogies:
    print(f"  [OK] {a['concept']} ({a['domain']})")
    print(f"    Similarity: {a['similarity_score']:.2f}")
    print(f"    Analogy Type: {a['analogy_type']}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
