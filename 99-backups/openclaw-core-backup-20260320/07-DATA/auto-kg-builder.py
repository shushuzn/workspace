#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Knowledge Graph Builder - 知识图谱自动构建器

功能：
1. 从提取的实体构建材料学知识图谱
2. 自动识别实体关系
3. 图谱存储和查询
4. 可视化输出

作者：Claw (AI Research OS)
创建时间：2026-03-05 20:45
"""

import json
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict


# ============================================================================
# 1. 数据结构定义
# ============================================================================

class EntityType:
    """实体类型"""
    MATERIAL = "material"
    PROPERTY = "property"
    STRUCTURE = "structure"
    METHOD = "method"
    VALUE = "value"
    UNIT = "unit"
    AUTHOR = "author"
    INSTITUTION = "institution"
    PAPER = "paper"


class RelationType:
    """关系类型"""
    HAS_PROPERTY = "has_property"  # 材料 - 性能
    HAS_STRUCTURE = "has_structure"  # 材料 - 结构
    SYNTHESIZED_BY = "synthesized_by"  # 材料 - 方法
    HAS_VALUE = "has_value"  # 性能 - 数值
    MEASURED_IN = "measured_in"  # 性能 - 单位
    WRITES = "writes"  # 作者 - 论文
    AFFILIATED_WITH = "affiliated_with"  # 作者 - 机构
    CITES = "cites"  # 论文 - 论文
    SIMILAR_TO = "similar_to"  # 材料 - 材料


@dataclass
class Entity:
    """图谱实体"""
    id: str
    type: str
    name: str
    name_cn: Optional[str] = None
    properties: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Relation:
    """图谱关系"""
    source: str  # 源实体 ID
    target: str  # 目标实体 ID
    type: str
    properties: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KnowledgeGraph:
    """知识图谱"""
    entities: Dict[str, Entity] = field(default_factory=dict)
    relations: List[Relation] = field(default_factory=list)

    def add_entity(self, entity: Entity):
        """添加实体"""
        self.entities[entity.id] = entity

    def add_relation(self, relation: Relation):
        """添加关系"""
        self.relations.append(relation)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        return self.entities.get(entity_id)

    def get_neighbors(self, entity_id: str, relation_type: Optional[str] = None) -> List[Tuple[str, str]]:
        """获取邻居节点"""
        neighbors = []
        for rel in self.relations:
            if rel.source == entity_id:
                if relation_type is None or rel.type == relation_type:
                    neighbors.append((rel.target, rel.type))
            elif rel.target == entity_id:
                if relation_type is None or rel.type == relation_type:
                    neighbors.append((rel.source, rel.type))
        return neighbors

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'entities': [e.to_dict() for e in self.entities.values()],
            'relations': [r.to_dict() for r in self.relations],
            'stats': self.get_stats()
        }

    def get_stats(self) -> Dict:
        """获取统计信息"""
        entity_types = defaultdict(int)
        relation_types = defaultdict(int)

        for entity in self.entities.values():
            entity_types[entity.type] += 1

        for relation in self.relations:
            relation_types[relation.type] += 1

        return {
            'total_entities': len(self.entities),
            'total_relations': len(self.relations),
            'entity_types': dict(entity_types),
            'relation_types': dict(relation_types)
        }


# ============================================================================
# 2. 知识图谱构建器
# ============================================================================

class AutoKGBuilder:
    """自动知识图谱构建器"""

    def __init__(self):
        self.graph = KnowledgeGraph()
        self.entity_counter = 0

    def generate_entity_id(self, entity_type: str) -> str:
        """生成实体 ID"""
        self.entity_counter += 1
        return f"{entity_type}_{self.entity_counter:04d}"

    def build_from_ner_results(self, ner_results: List[Dict]) -> KnowledgeGraph:
        """从 NER 结果构建图谱"""
        for result in ner_results:
            text = result.get('text', '')
            entities = result.get('entities', [])

            # 1. 创建材料实体
            material_entities = [e for e in entities if e['label'] == 'MATERIAL']
            material_id = None

            for mat in material_entities:
                material_id = self._create_entity(
                    EntityType.MATERIAL,
                    mat['text']
                )

            # 2. 创建性能实体并建立关系
            property_entities = [e for e in entities if e['label'] == 'PROPERTY']
            for prop in property_entities:
                prop_id = self._create_entity(
                    EntityType.PROPERTY,
                    prop['text']
                )
                if material_id:
                    self._create_relation(material_id, prop_id, RelationType.HAS_PROPERTY)

                # 查找关联的数值和单位
                value_entities = [e for e in entities if e['label'] == 'VALUE']
                unit_entities = [e for e in entities if e['label'] == 'UNIT']

                if value_entities:
                    value_id = self._create_entity(
                        EntityType.VALUE,
                        value_entities[0]['text']
                    )
                    self._create_relation(prop_id, value_id, RelationType.HAS_VALUE)

                if unit_entities:
                    unit_id = self._create_entity(
                        EntityType.UNIT,
                        unit_entities[0]['text']
                    )
                    self._create_relation(prop_id, unit_id, RelationType.MEASURED_IN)

            # 3. 创建结构实体并建立关系
            structure_entities = [e for e in entities if e['label'] == 'CRYSTAL_STRUCTURE']
            for struct in structure_entities:
                struct_id = self._create_entity(
                    EntityType.STRUCTURE,
                    struct['text']
                )
                if material_id:
                    self._create_relation(material_id, struct_id, RelationType.HAS_STRUCTURE)

            # 4. 创建方法实体并建立关系
            method_entities = [e for e in entities if e['label'] == 'SYNTHESIS_KEYWORD']
            for method in method_entities:
                method_id = self._create_entity(
                    EntityType.METHOD,
                    method['text']
                )
                if material_id:
                    self._create_relation(material_id, method_id, RelationType.SYNTHESIZED_BY)

        return self.graph

    def _create_entity(self, entity_type: str, name: str) -> str:
        """创建实体"""
        entity_id = self.generate_entity_id(entity_type)
        entity = Entity(
            id=entity_id,
            type=entity_type,
            name=name
        )
        self.graph.add_entity(entity)
        return entity_id

    def _create_relation(self, source_id: str, target_id: str, relation_type: str):
        """创建关系"""
        relation = Relation(
            source=source_id,
            target=target_id,
            type=relation_type
        )
        self.graph.add_relation(relation)

    def build_from_property_data(self, property_data: List[Dict]) -> KnowledgeGraph:
        """从性能数据构建图谱"""
        for data in property_data:
            material_name = data.get('material', 'Unknown')
            property_name = data.get('property_name', 'Unknown')
            value = data.get('value')
            unit = data.get('unit', '')

            # 创建材料实体
            material_id = self._create_entity(EntityType.MATERIAL, material_name)

            # 创建性能实体
            property_id = self._create_entity(
                EntityType.PROPERTY,
                property_name,
                data.get('property_name_cn')
            )

            # 建立关系
            self._create_relation(material_id, property_id, RelationType.HAS_PROPERTY)

            # 创建数值实体
            if value is not None:
                value_id = self._create_entity(
                    EntityType.VALUE,
                    str(value),
                    properties={'numeric_value': value}
                )
                self._create_relation(property_id, value_id, RelationType.HAS_VALUE)

            # 创建单位实体
            if unit:
                unit_id = self._create_entity(EntityType.UNIT, unit)
                self._create_relation(property_id, unit_id, RelationType.MEASURED_IN)

        return self.graph

    def export_json(self, output_path: str):
        """导出为 JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.graph.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"知识图谱已保存到 {output_path}")

    def export_for_visualization(self) -> Dict:
        """导出用于可视化的格式"""
        nodes = []
        links = []

        # 转换节点
        for entity in self.graph.entities.values():
            nodes.append({
                'id': entity.id,
                'label': f"{entity.name}\n({entity.type})",
                'type': entity.type,
                'group': hash(entity.type) % 10
            })

        # 转换边
        for relation in self.graph.relations:
            links.append({
                'source': relation.source,
                'target': relation.target,
                'type': relation.type
            })

        return {
            'nodes': nodes,
            'links': links
        }


# ============================================================================
# 3. 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Auto Knowledge Graph Builder - 知识图谱自动构建器")
    print("=" * 60)

    # 1. 测试构建
    print("\n[1/3] 测试知识图谱构建...")

    builder = AutoKGBuilder()

    # 示例 NER 结果
    ner_results = [
        {
            'text': 'LiFePO4 has a band gap of 3.2 eV',
            'entities': [
                {'text': 'LiFePO4', 'label': 'MATERIAL', 'start': 0, 'end': 7},
                {'text': 'band gap', 'label': 'PROPERTY', 'start': 14, 'end': 22},
                {'text': '3.2', 'label': 'VALUE', 'start': 26, 'end': 29},
                {'text': 'eV', 'label': 'UNIT', 'start': 30, 'end': 32},
            ]
        },
        {
            'text': 'SiO2 crystallizes in the cubic structure',
            'entities': [
                {'text': 'SiO2', 'label': 'MATERIAL', 'start': 0, 'end': 4},
                {'text': 'cubic', 'label': 'CRYSTAL_STRUCTURE', 'start': 27, 'end': 32},
            ]
        },
        {
            'text': 'TiO2 was synthesized by sol-gel method',
            'entities': [
                {'text': 'TiO2', 'label': 'MATERIAL', 'start': 0, 'end': 4},
                {'text': 'sol-gel', 'label': 'SYNTHESIS_KEYWORD', 'start': 24, 'end': 31},
            ]
        },
    ]

    graph = builder.build_from_ner_results(ner_results)

    # 2. 统计信息
    print("\n[2/3] 图谱统计...")
    stats = graph.get_stats()
    print(f"  实体总数：{stats['total_entities']}")
    print(f"  关系总数：{stats['total_relations']}")
    print(f"  实体类型分布：{stats['entity_types']}")
    print(f"  关系类型分布：{stats['relation_types']}")

    # 3. 导出
    print("\n[3/3] 导出图谱...")
    builder.export_json("data/knowledge-graph-example.json")

    # 可视化格式
    viz_data = builder.export_for_visualization()
    print(f"  节点数：{len(viz_data['nodes'])}")
    print(f"  边数：{len(viz_data['links'])}")

    # 显示部分节点
    print("\n  部分节点:")
    for node in viz_data['nodes'][:5]:
        print(f"    - {node['label']}")

    print("\n" + "=" * 60)
    print("知识图谱自动构建器准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
