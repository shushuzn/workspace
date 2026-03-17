#!/usr/bin/env python3
"""
Auto Knowledge Graph Builder
自动从 MEMORY.md 构建知识图谱

Usage:
    python auto_kg_builder.py --build
    python auto_kg_builder.py --extract-only
    python auto_kg_builder.py --merge
    python auto_kg_builder.py --stats
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class AutoKGBuilder:
    """自动知识图谱构建器"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.kg_dir = Path("40-50 外部资源/50-web-skills/data")
        
    def extract_from_memory(self) -> Dict:
        """从 MEMORY.md 提取教训"""
        
        print("\n" + "="*80)
        print("阶段 1: 从 MEMORY.md 提取教训")
        print("="*80)
        
        result = subprocess.run(
            ['python', 'memory_kg_extractor.py', '--extract'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # 加载提取结果
        entities_file = self.data_dir / "memory_entities.json"
        relations_file = self.data_dir / "memory_relations.json"
        
        with open(entities_file, 'r', encoding='utf-8') as f:
            entities = json.load(f)
        
        with open(relations_file, 'r', encoding='utf-8') as f:
            relations = json.load(f)
        
        return {
            'entities': entities,
            'relations': relations,
            'count': len(entities)
        }
    
    def merge_with_existing(self, new_entities: List, new_relations: List) -> Dict:
        """合并到现有知识图谱"""
        
        print("\n" + "="*80)
        print("阶段 2: 合并到现有知识图谱")
        print("="*80)
        
        # 加载现有知识图谱
        kg_file = self.kg_dir / "knowledge_graph.json"
        
        if kg_file.exists():
            with open(kg_file, 'r', encoding='utf-8') as f:
                kg_data = json.load(f)
            
            existing_entities = kg_data.get('entities', [])
            existing_relations = kg_data.get('relations', [])
            
            print(f"  现有实体：{len(existing_entities)}")
            print(f"  现有关系：{len(existing_relations)}")
        else:
            existing_entities = []
            existing_relations = []
            print("  ⚠️ 未找到现有知识图谱，创建新的")
        
        # 去重合并
        entity_ids = {e['id'] for e in existing_entities}
        merged_entities = existing_entities.copy()
        
        for entity in new_entities:
            if entity['id'] not in entity_ids:
                merged_entities.append(entity)
                entity_ids.add(entity['id'])
        
        # 关系去重
        relation_keys = {(r['source'], r['target'], r['type']) for r in existing_relations}
        merged_relations = existing_relations.copy()
        
        for relation in new_relations:
            key = (relation['source'], relation['target'], relation['type'])
            if key not in relation_keys:
                merged_relations.append(relation)
                relation_keys.add(key)
        
        # 保存合并后的知识图谱
        kg_data = {
            'entities': merged_entities,
            'relations': merged_relations,
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'total_entities': len(merged_entities),
                'total_relations': len(merged_relations),
                'source': 'MEMORY.md + existing'
            }
        }
        
        self.kg_dir.mkdir(parents=True, exist_ok=True)
        with open(kg_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 合并完成")
        print(f"  新实体：{len(merged_entities) - len(existing_entities)}")
        print(f"  新关系：{len(merged_relations) - len(existing_relations)}")
        
        return {
            'total_entities': len(merged_entities),
            'total_relations': len(merged_relations),
            'new_entities': len(merged_entities) - len(existing_entities),
            'new_relations': len(merged_relations) - len(existing_relations)
        }
    
    def build(self) -> Dict:
        """完整构建流程"""
        
        start_time = datetime.now()
        
        # 阶段 1: 提取
        extraction_result = self.extract_from_memory()
        
        # 阶段 2: 合并
        merge_result = self.merge_with_existing(
            extraction_result['entities'],
            extraction_result['relations']
        )
        
        # 阶段 3: 可视化
        print("\n" + "="*80)
        print("阶段 3: 生成可视化")
        print("="*80)
        
        viz_result = self.generate_visualization()
        
        # 计算时间
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 生成报告
        report = {
            'extraction': extraction_result,
            'merge': merge_result,
            'visualization': viz_result,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        # 保存报告
        report_file = self.data_dir / "auto_kg_build_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        return report
    
    def generate_visualization(self) -> Dict:
        """生成可视化数据"""
        
        # 运行可视化脚本
        result = subprocess.run(
            ['python', 'kg_visualize.py', '--generate-data'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("  ✅ 可视化数据生成成功")
            return {'status': 'success', 'message': result.stdout}
        else:
            print("  ⚠️ 可视化生成失败")
            return {'status': 'failed', 'message': result.stderr}
    
    def show_stats(self):
        """显示统计信息"""
        
        kg_file = self.kg_dir / "knowledge_graph.json"
        
        if not kg_file.exists():
            print("❌ 知识图谱文件不存在")
            return
        
        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)
        
        entities = kg_data.get('entities', [])
        relations = kg_data.get('relations', [])
        
        # 按类型统计实体
        by_type = {}
        for entity in entities:
            entity_type = entity.get('type', 'Unknown')
            by_type[entity_type] = by_type.get(entity_type, 0) + 1
        
        # 按关系类型统计
        by_relation_type = {}
        for relation in relations:
            rel_type = relation.get('type', 'Unknown')
            by_relation_type[rel_type] = by_relation_type.get(rel_type, 0) + 1
        
        print("\n" + "="*80)
        print("📊 知识图谱统计")
        print("="*80)
        print(f"  总实体数：{len(entities)}")
        print(f"  总关系数：{len(relations)}")
        print(f"  实体类型数：{len(by_type)}")
        print(f"  关系类型数：{len(by_relation_type)}")
        
        print("\n  实体类型分布:")
        for entity_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {entity_type}: {count}")
        
        print("\n  关系类型分布:")
        for rel_type, count in sorted(by_relation_type.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {rel_type}: {count}")
        
        print("\n" + "="*80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='自动知识图谱构建器')
    parser.add_argument('--build', action='store_true', help='完整构建流程')
    parser.add_argument('--extract-only', action='store_true', help='仅提取 (不合并)')
    parser.add_argument('--merge', action='store_true', help='仅合并 (不提取)')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    
    builder = AutoKGBuilder()
    
    if args.build:
        report = builder.build()
        
        print("\n" + "="*80)
        print("🎉 自动知识图谱构建完成！")
        print("="*80)
        print(f"  提取实体：{report['extraction']['count']}")
        print(f"  合并后实体：{report['merge']['total_entities']}")
        print(f"  新增实体：{report['merge']['new_entities']}")
        print(f"  总关系：{report['merge']['total_relations']}")
        print(f"  新增关系：{report['merge']['new_relations']}")
        print(f"  耗时：{report['duration_seconds']:.2f}秒")
        print(f"\n  报告保存到：data/auto_kg_build_report.json")
        print("="*80)
    
    elif args.extract_only:
        builder.extract_from_memory()
    
    elif args.merge:
        # 需要加载之前的提取结果
        entities_file = builder.data_dir / "memory_entities.json"
        relations_file = builder.data_dir / "memory_relations.json"
        
        if entities_file.exists() and relations_file.exists():
            with open(entities_file, 'r', encoding='utf-8') as f:
                entities = json.load(f)
            with open(relations_file, 'r', encoding='utf-8') as f:
                relations = json.load(f)
            
            builder.merge_with_existing(entities, relations)
        else:
            print("❌ 未找到提取结果，请先运行 --extract-only")
    
    elif args.stats:
        builder.show_stats()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
