#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
规划质量评估器 - Plan Quality Assessor
功能：评估规划质量，提供改进建议
"""

from typing import Dict, List

class PlanQualityAssessor:
    """规划质量评估器"""
    
    def __init__(self):
        self.criteria = {
            'completeness': 0.20,    # 完整性
            'specificity': 0.20,     # 具体性
            'feasibility': 0.20,     # 可行性
            'risk_awareness': 0.20,  # 风险意识
            'alternatives': 0.20     # 备选方案
        }
    
    def assess_plan(self, plan: Dict) -> Dict:
        """评估规划质量"""
        scores = {
            'completeness': self._assess_completeness(plan),
            'specificity': self._assess_specificity(plan),
            'feasibility': self._assess_feasibility(plan),
            'risk_awareness': self._assess_risk_awareness(plan),
            'alternatives': self._assess_alternatives(plan)
        }
        
        # 加权总分
        total_score = sum(scores[k] * self.criteria[k] for k in scores)
        
        # 等级评定
        if total_score >= 0.9:
            grade = 'A+'  # 优秀
        elif total_score >= 0.8:
            grade = 'A'   # 良好
        elif total_score >= 0.7:
            grade = 'B'   # 中等
        elif total_score >= 0.6:
            grade = 'C'   # 需改进
        else:
            grade = 'D'   # 不合格
        
        # 改进建议
        suggestions = self._generate_suggestions(scores, plan)
        
        return {
            'total_score': total_score,
            'grade': grade,
            'scores': scores,
            'suggestions': suggestions,
            'strengths': self._identify_strengths(scores)
        }
    
    def _assess_completeness(self, plan: Dict) -> float:
        """评估完整性"""
        score = 0.5
        
        # 有任务分解 → +0.25
        if '分解' in plan and len(plan['分解']) >= 4:
            score += 0.25
        
        # 有时间估算 → +0.25
        if '时间估算' in plan:
            score += 0.25
        
        return min(1.0, score)
    
    def _assess_specificity(self, plan: Dict) -> float:
        """评估具体性"""
        score = 0.5
        
        # 有验收标准 → +0.25
        if '验收标准' in plan and len(plan['验收标准']) >= 3:
            score += 0.25
        
        # 有时间估算 → +0.25
        if '时间估算' in plan and '总时间' in plan['时间估算']:
            score += 0.25
        
        return min(1.0, score)
    
    def _assess_feasibility(self, plan: Dict) -> float:
        """评估可行性"""
        score = 0.6
        
        # 任务分解合理 → +0.2
        if '分解' in plan:
            subtasks = plan['分解']
            if all('预计' in s for s in subtasks):
                score += 0.2
        
        # 有缓冲时间 → +0.2
        if '时间估算' in plan and '缓冲时间' in plan['时间估算']:
            score += 0.2
        
        return min(1.0, score)
    
    def _assess_risk_awareness(self, plan: Dict) -> float:
        """评估风险意识"""
        score = 0.5
        
        # 有风险评估 → +0.25
        if '风险评估' in plan and len(plan['风险评估']) >= 1:
            score += 0.25
        
        # 有缓解措施 → +0.25
        if '风险评估' in plan:
            has_mitigation = all('缓解措施' in r for r in plan['风险评估'])
            if has_mitigation:
                score += 0.25
        
        return min(1.0, score)
    
    def _assess_alternatives(self, plan: Dict) -> float:
        """评估备选方案"""
        score = 0.5
        
        # 有备选方案 → +0.25
        if '备选方案' in plan and len(plan['备选方案']) >= 1:
            score += 0.25
        
        # 有多个备选 → +0.25
        if '备选方案' in plan and len(plan['备选方案']) >= 2:
            score += 0.25
        
        return min(1.0, score)
    
    def _generate_suggestions(self, scores: Dict[str, float], plan: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if scores['completeness'] < 0.7:
            suggestions.append("添加更详细的任务分解 (≥4 个子任务)")
        
        if scores['specificity'] < 0.7:
            suggestions.append("明确验收标准和交付物")
        
        if scores['feasibility'] < 0.7:
            suggestions.append("添加缓冲时间，提高可行性")
        
        if scores['risk_awareness'] < 0.7:
            suggestions.append("增加风险评估和缓解措施")
        
        if scores['alternatives'] < 0.7:
            suggestions.append("准备至少 2 个备选方案")
        
        return suggestions
    
    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """识别优点"""
        strengths = []
        
        if scores['completeness'] >= 0.8:
            strengths.append("规划完整，包含所有必要元素")
        
        if scores['specificity'] >= 0.8:
            strengths.append("目标具体，验收标准清晰")
        
        if scores['feasibility'] >= 0.8:
            strengths.append("可行性高，时间估算合理")
        
        if scores['risk_awareness'] >= 0.8:
            strengths.append("风险意识强，有缓解措施")
        
        if scores['alternatives'] >= 0.8:
            strengths.append("备选方案充足")
        
        return strengths


def demo_assessment():
    """演示规划质量评估"""
    print("=" * 60)
    print("规划质量评估器")
    print("=" * 60)
    
    assessor = PlanQualityAssessor()
    
    # 示例规划
    test_plan = {
        'task': '优化记忆系统',
        '分解': [
            {'步骤': 1, '任务': '分析现状', '预计': '30min'},
            {'步骤': 2, '任务': '设计方案', '预计': '1h'},
            {'步骤': 3, '任务': '实施优化', '预计': '2h'},
            {'步骤': 4, '任务': '测试验证', '预计': '1h'},
        ],
        '时间估算': {
            '基础时间': '4.5 小时',
            '缓冲时间': '0.9 小时',
            '总时间': '5.4 小时'
        },
        '风险评估': [
            {'风险': '技术难点', '概率': '中', '影响': '高', '缓解措施': '提前调研'}
        ],
        '备选方案': [
            {'方案': 'A (标准)', '描述': '标准流程', '时间': '正常', '风险': '低'},
            {'方案': 'B (快速)', '描述': '简化流程', '时间': '-30%', '风险': '中'}
        ],
        '验收标准': ['功能完整', '测试通过', '文档完整']
    }
    
    assessment = assessor.assess_plan(test_plan)
    
    print(f"\n规划：{test_plan['task']}")
    print(f"质量评分：{assessment['total_score']:.2f} ({assessment['grade']})")
    print(f"\n维度评分:")
    for dim, score in assessment['scores'].items():
        print(f"  {dim}: {score:.2f}")
    
    print(f"\n优点:")
    for strength in assessment['strengths']:
        print(f"  [OK] {strength}")
    
    print(f"\n改进建议:")
    for suggestion in assessment['suggestions']:
        print(f"  [WARN] {suggestion}")


if __name__ == "__main__":
    demo_assessment()
