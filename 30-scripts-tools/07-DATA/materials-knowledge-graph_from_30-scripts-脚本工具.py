#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials Knowledge Graph Builder v1
材料知识图谱构建器实现
"""

from typing import Dict, List, Set
from dataclasses import dataclass, field

@dataclass
class Entity:
    id: str
    type: str  # Material, Element, Property, etc.
    name: str
    properties: Dict = field(default_factory=dict)

@dataclass
class Relation:
    source: str
    target: str
    type: str  # contains, has_property, used_for, etc.

class MaterialsKnowledgeGraph:
    """材料知识图谱"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
    
    def add_entity(self, entity: Entity):
        """添加实体"""
        self.entities[entity.id] = entity
    
    def add_relation(self, relation: Relation):
        """添加关系"""
        self.relations.append(relation)
    
    def get_material_relations(self, material_id: str) -> List[Relation]:
        """获取材料相关关系"""
        return [r for r in self.relations 
                if r.source == material_id or r.target == material_id]
    
    def get_neighbors(self, entity_id: str) -> List[Entity]:
        """获取邻居实体"""
        neighbors = []
        for relation in self.relations:
            if relation.source == entity_id:
                if relation.target in self.entities:
                    neighbors.append(self.entities[relation.target])
            elif relation.target == entity_id:
                if relation.source in self.entities:
                    neighbors.append(self.entities[relation.source])
        return neighbors
    
    def build_from_material(self, formula: str, properties: Dict) -> str:
        """从材料构建知识图谱"""
        # 添加材料实体
        material_id = f"mat_{formula}"
        material = Entity(
            id=material_id,
            type="Material",
            name=formula,
            properties=properties
        )
        self.add_entity(material)
        
        # 添加元素实体
        elements = self._extract_elements(formula)
        for element in elements:
            element_id = f"elem_{element}"
            if element_id not in self.entities:
                self.add_entity(Entity(
                    id=element_id,
                    type="Element",
                    name=element
                ))
            # 添加包含关系
            self.add_relation(Relation(
                source=material_id,
                target=element_id,
                type="contains"
            ))
        
        # 添加性能实体
        for prop_name, prop_value in properties.items():
            prop_id = f"prop_{prop_name}_{material_id}"
            self.add_entity(Entity(
                id=prop_id,
                type="Property",
                name=f"{formula} {prop_name}",
                properties={"value": prop_value}
            ))
            self.add_relation(Relation(
                source=material_id,
                target=prop_id,
                type="has_property"
            ))
        
        return material_id
    
    def _extract_elements(self, formula: str) -> List[str]:
        """从化学式提取元素"""
        import re
        # 简化元素提取
        elements = re.findall(r'([A-Z][a-z]?)', formula)
        return list(set(elements))
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "entities": [
                {"id": e.id, "type": e.type, "name": e.name, "properties": e.properties}
                for e in self.entities.values()
            ],
            "relations": [
                {"source": r.source, "target": r.target, "type": r.type}
                for r in self.relations
            ]
        }

def demo():
    """演示使用"""
    print("=" * 60)
    print("Materials Knowledge Graph Builder v1 Demo")
    print("=" * 60)
    
    kg = MaterialsKnowledgeGraph()
    
    # 构建 LiCoO2 知识图谱
    print("\n🕸️ 构建 LiCoO2 知识图谱:")
    material_id = kg.build_from_material("LiCoO2", {
        "band_gap": 2.5,
        "formation_energy": -2.1,
        "bulk_modulus": 150.0
    })
    
    print(f"材料 ID: {material_id}")
    print(f"实体数：{len(kg.entities)}")
    print(f"关系数：{len(kg.relations)}")
    
    # 获取邻居
    neighbors = kg.get_neighbors(material_id)
    print(f"\n邻居实体:")
    for n in neighbors[:5]:
        print(f"  - {n.name} ({n.type})")
    
    # 导出图谱
    graph_dict = kg.to_dict()
    print(f"\n图谱导出:")
    print(f"  实体：{len(graph_dict['entities'])} 个")
    print(f"  关系：{len(graph_dict['relations'])} 条")
    
    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    demo()
