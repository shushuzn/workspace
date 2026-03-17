#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
学习质量评估器 - Learning Quality Assessor
功能：评估学习质量，提供改进建议
"""

from typing import Dict, List

class LearningQualityAssessor:
    """学习质量评估器"""
    
    def __init__(self):
        self.criteria = {
            'clarity': 0.25,       # 清晰度
            'specificity': 0.25,   # 具体性
            'actionability': 0.25, # 可操作性
            'connectivity': 0.25   # 关联性
        }
    
    def assess_lesson(self, lesson: Dict) -> Dict:
        """评估教训质量"""
        scores = {
            'clarity': self._assess_clarity(lesson),
            'specificity': self._assess_specificity(lesson),
            'actionability': self._assess_actionability(lesson),
            'connectivity': self._assess_connectivity(lesson)
        }
        
        # 加权总分
        total_score = sum(scores[k] * self.criteria[k] for k in scores)
        
        # 等级评定
        if total_score >= 0.90:
            grade = 'A+'  # 优秀
        elif total_score >= 0.80:
            grade = 'A'   # 良好
        elif total_score >= 0.70:
            grade = 'B'   # 中等
        elif total_score >= 0.60:
            grade = 'C'   # 需改进
        else:
            grade = 'D'   # 不合格
        
        # 改进建议
        suggestions = self._generate_suggestions(scores, lesson)
        
        # 优点
        strengths = self._identify_strengths(scores)
        
        return {
            'total_score': total_score,
            'grade': grade,
            'scores': scores,
            'suggestions': suggestions,
            'strengths': strengths
        }
    
    def _assess_clarity(self, lesson: Dict) -> float:
        """评估清晰度"""
        score = 0.5
        
        # 有明确标题 → +0.25
        if lesson.get('title') and len(lesson['title']) > 5:
            score += 0.25
        
        # 问题描述清晰 → +0.25
        problem = lesson.get('problem', '')
        if problem and problem != "未明确描述" and len(problem) > 10:
            score += 0.25
        
        return min(1.0, score)
    
    def _assess_specificity(self, lesson: Dict) -> float:
        """评估具体性"""
        score = 0.5
        
        # 有数据支持 → +0.25
        confidence = lesson.get('confidence', 0.5)
        if confidence >= 0.8:
            score += 0.25
        
        # 有关键词 → +0.25
        keywords = lesson.get('keywords', [])
        if len(keywords) >= 3:
            score += 0.25
        
        return min(1.0, score)
    
    def _assess_actionability(self, lesson: Dict) -> float:
        """评估可操作性"""
        score = 0.5
        
        # 解决方案具体 → +0.25
        solution = lesson.get('solution', '')
        if solution and solution != "未明确描述" and len(solution) > 20:
            score += 0.25
        
        # 有验证结果 → +0.25
        if '验证' in str(lesson) or 'test' in str(lesson).lower():
            score += 0.25
        
        return min(1.0, score)
    
    def _assess_connectivity(self, lesson: Dict) -> float:
        """评估关联性"""
        score = 0.5
        
        # 有相关教训 → +0.25
        related = lesson.get('related_lessons', [])
        if len(related) >= 1:
            score += 0.25
        
        # 有多个相关 → +0.25
        if len(related) >= 2:
            score += 0.25
        
        return min(1.0, score)
    
    def _generate_suggestions(self, scores: Dict[str, float], lesson: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if scores['clarity'] < 0.7:
            suggestions.append("明确问题描述和解决方案")
        
        if scores['specificity'] < 0.7:
            suggestions.append("添加具体数据和关键词")
        
        if scores['actionability'] < 0.7:
            suggestions.append("提供可操作的具体步骤")
        
        if scores['connectivity'] < 0.7:
            suggestions.append("建立与其他教训的关联")
        
        return suggestions
    
    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """识别优点"""
        strengths = []
        
        if scores['clarity'] >= 0.8:
            strengths.append("问题描述清晰")
        
        if scores['specificity'] >= 0.8:
            strengths.append("数据支持充分")
        
        if scores['actionability'] >= 0.8:
            strengths.append("解决方案可操作")
        
        if scores['connectivity'] >= 0.8:
            strengths.append("知识关联良好")
        
        return strengths


def demo_learning_assessment():
    """演示学习质量评估"""
    print("=" * 60)
    print("学习质量评估器")
    print("=" * 60)
    
    assessor = LearningQualityAssessor()
    
    # 示例教训
    test_lesson = {
        'id': '[SYS-019]',
        'title': '100% 防护系统',
        'category': 'SYS - 系统配置',
        'problem': '新会话文件创建在 C 盘而非 D 盘',
        'solution': '实施 5 层防护系统 (sitecustomize + 环境变量 + PowerShell Profile + Git 钩子 + 路径拦截)',
        'confidence': 0.95,
        'keywords': ['防护', '路径', 'sitecustomize', '环境变量'],
        'related_lessons': [
            {'id': '[SYS-020]', 'title': '7 人格检测验证'}
        ]
    }
    
    assessment = assessor.assess_lesson(test_lesson)
    
    print(f"\n教训：{test_lesson['id']} - {test_lesson['title']}")
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
    demo_learning_assessment()
