#!/usr/bin/env python3
"""
知识图谱推理路径验证测试
测试 LIG 生物医学领域的关系推理能力
"""

import sys
import importlib.util

# 加载模块
spec = importlib.util.spec_from_file_location("kg_builder", r'D:\npm-global\node_modules\openclaw\skills\knowledge-graph\scripts\kg-builder.py')
kg_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kg_builder)

KnowledgeGraphBuilder = kg_builder.KnowledgeGraphBuilder

print("=" * 70)
print("知识图谱推理路径验证测试")
print("=" * 70)

# 创建测试图谱
builder = KnowledgeGraphBuilder()

# 添加 LIG 生物医学领域实体
entities = [
    # 材料
    {"id": "lig", "type": "Material", "properties": {"name": "Laser-Induced Graphene", "domain": "Materials"}},
    {"id": "cuo", "type": "Material", "properties": {"name": "Copper Oxide", "domain": "Materials"}},
    {"id": "pdms", "type": "Material", "properties": {"name": "PDMS", "domain": "Materials"}},
    
    # 设备
    {"id": "tumor_patch", "type": "Device", "properties": {"name": "LIG-CuO/PDMS Patch", "domain": "Materials"}},
    {"id": "neural_probe", "type": "Device", "properties": {"name": "LIG Neural Probe", "domain": "Materials"}},
    {"id": "biosensor", "type": "Device", "properties": {"name": "LIG Biosensor", "domain": "Materials"}},
    
    # 信号分子
    {"id": "cu_ion", "type": "Signal", "properties": {"name": "Cu2+", "domain": "Biology"}},
    {"id": "ros", "type": "Signal", "properties": {"name": "ROS", "domain": "Biology"}},
    {"id": "glucose", "type": "Signal", "properties": {"name": "Glucose", "domain": "Biology"}},
    
    # 生物通路
    {"id": "cuproptosis", "type": "BiologicalPathway", "properties": {"name": "Cuproptosis", "domain": "Biology"}},
    {"id": "ferroptosis", "type": "BiologicalPathway", "properties": {"name": "Ferroptosis", "domain": "Biology"}},
    {"id": "apoptosis", "type": "BiologicalPathway", "properties": {"name": "Apoptosis", "domain": "Biology"}},
    
    # 疾病
    {"id": "melanoma", "type": "Disease", "properties": {"name": "Melanoma", "domain": "Medicine"}},
    {"id": "alzheimers", "type": "Disease", "properties": {"name": "Alzheimers Disease", "domain": "Medicine"}},
    
    # 工艺
    {"id": "laser_write", "type": "FabricationProcess", "properties": {"name": "CO2 Laser Direct Write", "domain": "Materials"}},
]

builder.add_entities(entities)
print(f"[OK] Added {len(entities)} entities")

# Add relations
relations = [
    # 制造关系
    {"source": "lig", "target": "laser_write", "type": "fabricated_by"},
    {"source": "tumor_patch", "target": "lig", "type": "fabricated_from"},
    {"source": "tumor_patch", "target": "cuo", "type": "loaded_with"},
    {"source": "tumor_patch", "target": "pdms", "type": "embedded_in"},
    
    # 神经探针
    {"source": "neural_probe", "target": "lig", "type": "fabricated_from"},
    
    # 生物传感器
    {"source": "biosensor", "target": "lig", "type": "fabricated_from"},
    
    # 释放/检测关系
    {"source": "cuo", "target": "cu_ion", "type": "releases"},
    {"source": "cu_ion", "target": "ros", "type": "induces"},
    
    # 细胞死亡通路
    {"source": "ros", "target": "cuproptosis", "type": "induces"},
    {"source": "ros", "target": "ferroptosis", "type": "induces"},
    {"source": "ros", "target": "apoptosis", "type": "induces"},
    
    # 治疗关系
    {"source": "tumor_patch", "target": "melanoma", "type": "treats"},
    
    # 检测关系
    {"source": "neural_probe", "target": "glucose", "type": "detects"},
    {"source": "biosensor", "target": "glucose", "type": "detects"},
]

builder.add_relations(relations)
print(f"[OK] Added {len(relations)} relations")

print("\n" + "=" * 70)
print("Test 1: Tumor Treatment Path Reasoning")
print("=" * 70)

# Test path: LIG -> CuO -> Cu2+ -> ROS -> Cuproptosis -> Melanoma
print("\n[Test Path] LIG -> CuO -> Cu2+ -> ROS -> Cuproptosis -> Melanoma")
print("Expected: Complete tumor treatment mechanism chain\n")

# Manual path verification
def find_path(builder, start_id, end_id, max_depth=5):
    """BFS path finding"""
    from collections import deque
    
    queue = deque([(start_id, [start_id])])
    visited = {start_id}
    
    while queue:
        current, path = queue.popleft()
        
        if len(path) > max_depth:
            continue
        
        # Find all relations from current
        for rel in builder.relations:
            if rel["source"] == current:
                next_node = rel["target"]
                rel_type = rel["type"]
                
                if next_node == end_id:
                    return path + [next_node], [rel_type]
                
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
    
    return None, None

# Test sub-paths
print("Sub-path 1: LIG -> Tumor Patch")
path, rels = find_path(builder, "lig", "tumor_patch")
if path:
    path_names = [builder.entities[p]["properties"]["name"] for p in path]
    print(f"  [OK] Path found: {' -> '.join(path_names)}")
else:
    print(f"  [FAIL] Path not found")

print("\nSub-path 2: Tumor Patch -> CuO -> Cu2+")
path, rels = find_path(builder, "tumor_patch", "cu_ion")
if path:
    path_names = [builder.entities[p]["properties"]["name"] for p in path]
    print(f"  [OK] Path found: {' -> '.join(path_names)}")
else:
    print(f"  [FAIL] Path not found")

print("\nSub-path 3: Cu2+ -> ROS -> Cuproptosis")
path, rels = find_path(builder, "cu_ion", "cuproptosis")
if path:
    path_names = [builder.entities[p]["properties"]["name"] for p in path]
    print(f"  [OK] Path found: {' -> '.join(path_names)}")
else:
    print(f"  [FAIL] Path not found")

print("\nSub-path 4: Tumor Patch -> Melanoma (treatment)")
path, rels = find_path(builder, "tumor_patch", "melanoma")
if path:
    path_names = [builder.entities[p]["properties"]["name"] for p in path]
    print(f"  [OK] Path found: {' -> '.join(path_names)}")
else:
    print(f"  [FAIL] Path not found")

print("\n" + "=" * 70)
print("Test 2: Cross-Domain Analogy Query")
print("=" * 70)

# Test cross-domain analogy
print("\n[Test] CS Adaptive Routing -> Materials Science Analogy")
analogies = builder.find_analogy("CS", "Adaptive Routing", "Materials")
if analogies:
    for a in analogies[:3]:
        print(f"  [OK] {a['concept']} ({a['domain']})")
        print(f"       Similarity: {a['similarity_score']:.2f}, Type: {a['analogy_type']}")
else:
    print("  [WARN] No analogies found (limited test data)")

print("\n" + "=" * 70)
print("Test 3: Entity Relation Query")
print("=" * 70)

# Query all LIG-related relations
print("\n[Query] All LIG-related relations")
lig_relations = [r for r in builder.relations if r["source"] == "lig" or r["target"] == "lig"]
for r in lig_relations:
    source_name = builder.entities[r["source"]]["properties"]["name"]
    target_name = builder.entities[r["target"]]["properties"]["name"]
    print(f"  {source_name} --[{r['type']}]--> {target_name}")

print("\n" + "=" * 70)
print("Test Complete!")
print("=" * 70)
