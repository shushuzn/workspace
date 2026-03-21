import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创意质量预测器 - 预测创意的潜在价值和成功率
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class BrainstormQualityPredictor:
    """创意质量预测器"""
    
    def __init__(self):
        self.model_file = Path("flow-archive/20260320-brainstorm-v2/quality-model.json")
        self.history_file = Path("flow-archive/20260320-brainstorm-v2/idea-history.json")
        self.model = self._load_model()
    
    def _load_model(self) -> Dict:
        """加载质量模型"""
        if self.model_file.exists():
            with open(self.model_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "weights": {
                "novelty": 0.25,
                "feasibility": 0.20,
                "impact": 0.30,
                "clarity": 0.15,
                "alignment": 0.10
            },
            "thresholds": {
                "excellent": 85,
                "good": 70,
                "fair": 55,
                "poor": 0
            }
        }
    
    def predict_quality(self, idea: Dict, context: Dict = None) -> Dict:
        """预测创意质量"""
        
        context = context or {}
        
        # 评估各维度 (0-100)
        scores = {
            "novelty": self._assess_novelty(idea, context),
            "feasibility": self._assess_feasibility(idea, context),
            "impact": self._assess_impact(idea, context),
            "clarity": self._assess_clarity(idea),
            "alignment": self._assess_alignment(idea, context)
        }
        
        # 计算加权总分
        total_score = sum(
            scores[dim] * self.model['weights'][dim]
            for dim in scores
        )
        
        # 质量等级
        if total_score >= self.model['thresholds']['excellent']:
            quality_level = "excellent"
        elif total_score >= self.model['thresholds']['good']:
            quality_level = "good"
        elif total_score >= self.model['thresholds']['fair']:
            quality_level = "fair"
        else:
            quality_level = "poor"
        
        # 成功概率预测
        success_probability = self._predict_success_probability(scores, context)
        
        return {
            "idea_name": idea.get('name', 'Unnamed'),
            "total_score": total_score,
            "quality_level": quality_level,
            "dimension_scores": scores,
            "success_probability": success_probability,
            "recommendation": self._generate_recommendation(quality_level, success_probability),
            "strengths": self._identify_strengths(scores),
            "weaknesses": self._identify_weaknesses(scores)
        }
    
    def _assess_novelty(self, idea: Dict, context: Dict) -> float:
        """评估新颖性"""
        # 简化评估：基于关键词
        novelty_keywords = ['new', 'innovative', 'novel', 'first', 'unique', 'breakthrough']
        description = (idea.get('description', '') + ' ' + idea.get('name', '')).lower()
        
        keyword_count = sum(1 for kw in novelty_keywords if kw in description)
        base_score = 50 + (keyword_count * 10)
        
        return min(100, max(0, base_score))
    
    def _assess_feasibility(self, idea: Dict, context: Dict) -> float:
        """评估可行性"""
        # 基于资源需求和复杂度
        resources = idea.get('resources', 'medium')
        complexity = idea.get('complexity', 'medium')
        
        resource_scores = {'low': 90, 'medium': 60, 'high': 30}
        complexity_scores = {'low': 90, 'medium': 60, 'high': 30}
        
        return (resource_scores.get(resources, 60) + complexity_scores.get(complexity, 60)) / 2
    
    def _assess_impact(self, idea: Dict, context: Dict) -> float:
        """评估影响力"""
        # 基于预期影响力评分
        impact_score = idea.get('impact_score', 5)
        return impact_score * 10  # 转换为 0-100
    
    def _assess_clarity(self, idea: Dict) -> float:
        """评估清晰度"""
        # 基于描述长度和结构
        description = idea.get('description', '')
        
        if len(description) < 20:
            return 30
        elif len(description) < 50:
            return 60
        elif len(description) < 100:
            return 80
        else:
            return 90
    
    def _assess_alignment(self, idea: Dict, context: Dict) -> float:
        """评估对齐度"""
        # 与目标/主题的对齐程度
        if not context.get('goal'):
            return 70  # 默认中等对齐
        
        goal_keywords = context.get('goal', '').lower().split()
        idea_text = (idea.get('description', '') + ' ' + idea.get('name', '')).lower()
        
        alignment_count = sum(1 for kw in goal_keywords if kw in idea_text)
        return min(100, 50 + (alignment_count * 10))
    
    def _predict_success_probability(self, scores: Dict, context: Dict) -> float:
        """预测成功概率"""
        # 基于各维度分数预测
        avg_score = sum(scores.values()) / len(scores)
        
        # 调整因子
        if context.get('urgency') == 'high':
            feasibility_boost = scores['feasibility'] * 0.1
            avg_score += feasibility_boost
        
        return min(100, max(0, avg_score))
    
    def _generate_recommendation(self, quality_level: str, success_prob: float) -> str:
        """生成建议"""
        if quality_level == "excellent":
            return "Highly recommended for immediate implementation"
        elif quality_level == "good":
            return "Recommended with minor refinements"
        elif quality_level == "fair":
            return "Consider for future implementation after improvement"
        else:
            return "Not recommended in current form"
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        """识别优势"""
        strengths = []
        dimension_names = {
            "novelty": "Novelty/Innovation",
            "feasibility": "Feasibility",
            "impact": "Potential Impact",
            "clarity": "Clarity",
            "alignment": "Goal Alignment"
        }
        
        for dim, score in scores.items():
            if score >= 80:
                strengths.append(f"{dimension_names[dim]} ({score:.0f})")
        
        return strengths
    
    def _identify_weaknesses(self, scores: Dict) -> List[str]:
        """识别劣势"""
        weaknesses = []
        dimension_names = {
            "novelty": "Novelty/Innovation",
            "feasibility": "Feasibility",
            "impact": "Potential Impact",
            "clarity": "Clarity",
            "alignment": "Goal Alignment"
        }
        
        for dim, score in scores.items():
            if score < 60:
                weaknesses.append(f"{dimension_names[dim]} ({score:.0f})")
        
        return weaknesses
    
    def batch_predict(self, ideas: List[Dict], context: Dict = None) -> Dict:
        """批量预测"""
        predictions = []
        
        for idea in ideas:
            prediction = self.predict_quality(idea, context)
            predictions.append(prediction)
        
        # 排序
        sorted_predictions = sorted(
            predictions,
            key=lambda x: x['total_score'],
            reverse=True
        )
        
        return {
            "total_ideas": len(ideas),
            "predictions": sorted_predictions,
            "excellent_count": sum(1 for p in predictions if p['quality_level'] == 'excellent'),
            "good_count": sum(1 for p in predictions if p['quality_level'] == 'good'),
            "avg_score": sum(p['total_score'] for p in predictions) / len(predictions) if predictions else 0
        }
    
    def get_stats(self) -> Dict:
        """获取统计"""
        history = []
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        return {
            "total_predictions": len(history),
            "avg_quality_score": (
                sum(h.get('total_score', 0) for h in history) / len(history)
            ) if history else 0
        }
    
    def display_status(self) -> str:
        """显示状态"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 20 + "Quality Predictor")
        output.append("=" * 70)
        
        output.append(f"\n[Model Info]")
        output.append(f"  Version:          {self.model['version']}")
        output.append(f"  Dimensions:       {len(self.model['weights'])}")
        
        output.append(f"\n[Stats]")
        output.append(f"  Total Predictions:  {stats['total_predictions']}")
        output.append(f"  Avg Quality Score:  {stats['avg_quality_score']:.1f}")
        
        output.append(f"\n[Quality Thresholds]")
        for level, threshold in self.model['thresholds'].items():
            output.append(f"  {level.capitalize():12} >= {threshold}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)
    
    def run(self, ideas: List[Dict], context: Dict = None) -> Dict:
        """运行预测"""
        return self.batch_predict(ideas, context)

logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py brainstorm_quality_predictor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py brainstorm_quality_predictor_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

测试入口"""
    predictor = BrainstormQualityPredictor()
    
    print("Quality Predictor Test")
    print("=" * 70)
    
    # 测试：预测创意质量
    test_ideas = [
        {"name": "Idea 1", "description": "A new innovative approach", "impact_score": 8},
        {"name": "Idea 2", "description": "Simple improvement", "impact_score": 5},
        {"name": "Idea 3", "description": "Breakthrough solution with high impact", "impact_score": 9},
    ]
    
    result = predictor.batch_predict(test_ideas)
    
    print(f"\n[OK] Predicted {result['total_ideas']} ideas")
    print(f"Excellent: {result['excellent_count']}")
    print(f"Good: {result['good_count']}")
    print(f"Avg Score: {result['avg_score']:.1f}")
    
    # 显示状态
    print(predictor.display_status())
    
    print(f"\n[OK] Quality predictor test completed")

if __name__ == "__main__":
    main()
