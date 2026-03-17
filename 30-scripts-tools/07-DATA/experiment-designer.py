#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Experiment Designer - 实验设计助手

功能：
1. 基于材料推荐合成方法
2. 推荐实验条件 (温度/时间/气氛)
3. 前驱体推荐
4. 安全性评估

作者：Claw (AI Research OS)
创建时间：2026-03-05 21:35
"""

import json
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExperimentPlan:
    """实验计划"""
    material: str
    method: str
    precursors: List[str]
    temperature: float
    time: float
    atmosphere: str
    safety_level: str
    estimated_cost: float
    
    def to_dict(self) -> Dict:
        return {
            'material': self.material,
            'method': self.method,
            'precursors': self.precursors,
            'temperature': self.temperature,
            'time': self.time,
            'atmosphere': self.atmosphere,
            'safety_level': self.safety_level,
            'estimated_cost': self.estimated_cost
        }


class ExperimentDesigner:
    """实验设计助手"""
    
    def __init__(self):
        self.method_database = {
            'oxide': {
                'method': '固相反应法',
                'precursors': ['氧化物前驱体'],
                'temperature_range': (600, 1000),
                'time_range': (6, 24),
                'atmosphere': '空气或氧气'
            },
            'phosphate': {
                'method': '溶胶 - 凝胶法',
                'precursors': ['磷酸盐', '金属盐'],
                'temperature_range': (500, 800),
                'time_range': (4, 12),
                'atmosphere': '惰性气体'
            },
            'sulfide': {
                'method': '水热法',
                'precursors': ['硫化物前驱体'],
                'temperature_range': (150, 250),
                'time_range': (12, 48),
                'atmosphere': '密闭高压'
            }
        }
    
    def design_experiment(self, material_formula: str) -> ExperimentPlan:
        """设计实验"""
        
        # 判断材料类型
        material_type = self._classify_material(material_formula)
        
        # 获取方法
        method_info = self.method_database.get(material_type, self.method_database['oxide'])
        
        # 生成具体条件
        temp = random.uniform(*method_info['temperature_range'])
        time = random.uniform(*method_info['time_range'])
        
        # 安全性评估
        safety = self._assess_safety(material_formula, temp)
        
        # 成本估算
        cost = self._estimate_cost(method_info['precursors'], time)
        
        return ExperimentPlan(
            material=material_formula,
            method=method_info['method'],
            precursors=method_info['precursors'],
            temperature=round(temp, 0),
            time=round(time, 1),
            atmosphere=method_info['atmosphere'],
            safety_level=safety,
            estimated_cost=round(cost, 2)
        )
    
    def _classify_material(self, formula: str) -> str:
        """分类材料"""
        if 'O' in formula and 'P' in formula:
            return 'phosphate'
        elif 'S' in formula:
            return 'sulfide'
        else:
            return 'oxide'
    
    def _assess_safety(self, formula: str, temperature: float) -> str:
        """安全性评估"""
        if temperature > 900:
            return '高 (高温操作)'
        elif temperature > 600:
            return '中 (标准操作)'
        else:
            return '低 (常规操作)'
    
    def _estimate_cost(self, precursors: List[str], time: float) -> float:
        """成本估算"""
        base_cost = len(precursors) * 50
        time_cost = time * 10
        return base_cost + time_cost


def main():
    """主函数"""
    print("=" * 60)
    print("Experiment Designer - 实验设计助手")
    print("=" * 60)
    
    designer = ExperimentDesigner()
    
    test_materials = ['LiFePO4', 'SiO2', 'TiO2', 'LiCoO2']
    
    for formula in test_materials:
        print(f"\n材料：{formula}")
        plan = designer.design_experiment(formula)
        
        print(f"  方法：{plan.method}")
        print(f"  前驱体：{plan.precursors}")
        print(f"  温度：{plan.temperature}°C")
        print(f"  时间：{plan.time}h")
        print(f"  气氛：{plan.atmosphere}")
        print(f"  安全性：{plan.safety_level}")
        print(f"  成本：${plan.estimated_cost}")
    
    print("\n" + "=" * 60)
    print("实验设计助手准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
