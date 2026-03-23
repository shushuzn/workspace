#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthesis Pathway Recommender v1
材料合成路径推荐系统实现
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ReactionCondition:
    temperature: float  # °C
    time: float  # hours
    atmosphere: str
    pressure: Optional[float] = None  # atm

@dataclass
class SynthesisPathway:
    reactants: List[str]
    products: List[str]
    conditions: ReactionCondition
    cost: float  # ¥/g
    safety_score: int  # 0-100
    yield_rate: float  # 0-1

class SynthesisPathwayRecommender:
    """合成路径推荐器"""

    def __init__(self):
        # 模拟反应数据库
        self.reaction_db = [
            {
                "target": "LiCoO2",
                "reactants": ["Li2CO3", "CoCO3"],
                "conditions": ReactionCondition(900, 12, "air"),
                "cost": 50.0,
                "safety_score": 85,
                "yield_rate": 0.95
            },
            {
                "target": "LiFePO4",
                "reactants": ["LiOH", "FePO4"],
                "conditions": ReactionCondition(700, 8, "argon"),
                "cost": 45.0,
                "safety_score": 90,
                "yield_rate": 0.92
            }
        ]

    def recommend(self, target: str, optimize: str = "cost") -> List[SynthesisPathway]:
        """推荐合成路径"""
        pathways = []

        for reaction in self.reaction_db:
            if reaction["target"].lower() == target.lower():
                pathway = SynthesisPathway(
                    reactants=reaction["reactants"],
                    products=[target],
                    conditions=reaction["conditions"],
                    cost=reaction["cost"],
                    safety_score=reaction["safety_score"],
                    yield_rate=reaction["yield_rate"]
                )
                pathways.append(pathway)

        # 根据优化目标排序
        if optimize == "cost":
            pathways.sort(key=lambda x: x.cost)
        elif optimize == "safety":
            pathways.sort(key=lambda x: x.safety_score, reverse=True)
        elif optimize == "yield":
            pathways.sort(key=lambda x: x.yield_rate, reverse=True)

        return pathways

    def estimate_cost(self, reactants: List[str], conditions: ReactionCondition) -> float:
        """估算成本"""
        # 简化成本估算
        base_cost = len(reactants) * 10
        temp_factor = conditions.temperature / 100
        time_factor = conditions.time / 10

        return base_cost * (1 + temp_factor * 0.1 + time_factor * 0.05)

    def assess_safety(self, conditions: ReactionCondition) -> int:
        """评估安全性"""
        score = 100

        # 高温扣分
        if conditions.temperature > 800:
            score -= 20
        elif conditions.temperature > 500:
            score -= 10

        # 长时间扣分
        if conditions.time > 24:
            score -= 10

        # 特殊气氛扣分
        if conditions.atmosphere in ["hydrogen", "argon"]:
            score -= 5

        return max(0, score)

def demo():
    """演示使用"""
    print("=" * 60)
    print("Synthesis Pathway Recommender v1 Demo")
    print("=" * 60)

    recommender = SynthesisPathwayRecommender()

    # 推荐 LiCoO2 合成路径
    print("\n🧪 推荐 LiCoO2 合成路径:")
    pathways = recommender.recommend("LiCoO2", optimize="cost")

    for i, pathway in enumerate(pathways, 1):
        print(f"\n路径 {i}:")
        print(f"  反应物：{', '.join(pathway.reactants)}")
        print(f"  条件：{pathway.conditions.temperature}°C, {pathway.conditions.time}h, {pathway.conditions.atmosphere}")
        print(f"  成本：¥{pathway.cost}/g")
        print(f"  安全性：{pathway.safety_score}")
        print(f"  产率：{pathway.yield_rate:.2f}")

    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    demo()
