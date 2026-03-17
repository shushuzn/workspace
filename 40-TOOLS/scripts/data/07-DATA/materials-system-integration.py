#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials System Integration v1
材料科学系统集成工具
"""

from pathlib import Path
import json
from datetime import datetime

# 导入所有模块
from materials_project_api import MaterialsProjectClient
from cif_parser import CIFParser
from materials_property_prediction import MaterialsPropertyPredictor
from synthesis_pathway_recommender import SynthesisPathwayRecommender
from materials_knowledge_graph import MaterialsKnowledgeGraph, Entity, Relation

class MaterialsSystemIntegration:
    """材料科学系统集成器"""
    
    def __init__(self):
        self.mp_client = MaterialsProjectClient()
        self.cif_parser = CIFParser()
        self.predictor = MaterialsPropertyPredictor()
        self.recommender = SynthesisPathwayRecommender()
        self.kg = MaterialsKnowledgeGraph()
        
        self.data_dir = Path(r"D:\obsidian\Vault\Materials")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_material(self, formula: str, cif_file: str = None) -> dict:
        """分析材料"""
        result = {
            "formula": formula,
            "timestamp": datetime.now().isoformat(),
            "analysis": {}
        }
        
        # 1. 性能预测
        result["analysis"]["properties"] = self.predictor.predict_all(formula)
        
        # 2. 合成路径推荐
        pathways = self.recommender.recommend(formula)
        result["analysis"]["synthesis"] = [
            {
                "reactants": p.reactants,
                "conditions": {
                    "temperature": p.conditions.temperature,
                    "time": p.conditions.time,
                    "atmosphere": p.conditions.atmosphere
                },
                "cost": p.cost,
                "safety": p.safety_score,
                "yield": p.yield_rate
            }
            for p in pathways
        ]
        
        # 3. 构建知识图谱
        material_id = self.kg.build_from_material(
            formula,
            result["analysis"]["properties"]
        )
        result["analysis"]["knowledge_graph"] = {
            "material_id": material_id,
            "entities": len(self.kg.entities),
            "relations": len(self.kg.relations)
        }
        
        # 4. CIF 解析 (如果提供)
        if cif_file:
            try:
                structure = self.cif_parser.parse_file(cif_file)
                result["analysis"]["structure"] = structure
            except Exception as e:
                result["analysis"]["structure_error"] = str(e)
        
        return result
    
    def save_analysis(self, result: dict):
        """保存分析结果"""
        filename = f"analysis-{result['formula']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_report(self, results: list) -> str:
        """生成分析报告"""
        report = f"# 材料分析报告\n\n"
        report += f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"**分析材料数:** {len(results)}\n\n"
        report += "---\n\n"
        
        for result in results:
            report += f"## {result['formula']}\n\n"
            
            if 'properties' in result.get('analysis', {}):
                props = result['analysis']['properties']
                report += f"### 性能预测\n\n"
                if 'bandgap' in props:
                    report += f"- 带隙：{props['bandgap'].get('prediction', 'N/A')} eV\n"
                if 'formation_energy' in props:
                    report += f"- 形成能：{props['formation_energy'].get('prediction', 'N/A')} eV/atom\n\n"
            
            if 'synthesis' in result.get('analysis', {}):
                report += f"### 合成路径\n\n"
                for i, path in enumerate(result['analysis']['synthesis'], 1):
                    report += f"{i}. {', '.join(path['reactants'])} → {result['formula']}\n"
                    report += f"   条件：{path['conditions']['temperature']}°C, {path['conditions']['time']}h\n\n"
            
            report += "---\n\n"
        
        return report

def demo():
    """演示使用"""
    print("=" * 60)
    print("Materials System Integration v1 Demo")
    print("=" * 60)
    
    integrator = MaterialsSystemIntegration()
    
    # 分析 LiCoO2
    print("\n🔬 分析 LiCoO2:")
    result = integrator.analyze_material("LiCoO2")
    
    print(f"  公式：{result['formula']}")
    print(f"  带隙：{result['analysis']['properties']['bandgap']['prediction']:.2f} eV")
    print(f"  实体数：{result['analysis']['knowledge_graph']['entities']}")
    print(f"  关系数：{result['analysis']['knowledge_graph']['relations']}")
    
    # 保存结果
    filepath = integrator.save_analysis(result)
    print(f"\n✅ 结果已保存：{filepath}")
    
    # 生成报告
    report = integrator.generate_report([result])
    print(f"\n📊 报告生成：{len(report)} 字符")
    
    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    demo()
