#!/usr/bin/env python3
"""
学习者助手 V2 - Learner Assistant
功能：经验提炼 + 知识关联 + 遗忘曲线 + 学习路径
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class LearnerAssistantV2:
    """学习者助手 V2"""
    
    def __init__(self):
        self.knowledge_categories = {
            'SYS': '系统配置',
            'MULTI': '7 人格系统',
            'MEM': '记忆系统',
            'FEISHU': '飞书集成',
            'SEC': '安全相关',
            'PROJ': '项目相关',
            'CR': '批判者发现',
            'TOOL': '工具相关'
        }
        
        self.forgetting_curve = {
            1: 0.90,    # 1 天后保留 90%
            3: 0.70,    # 3 天后保留 70%
            7: 0.50,    # 7 天后保留 50%
            14: 0.35,   # 14 天后保留 35%
            30: 0.25    # 30 天后保留 25%
        }
    
    def extract_lesson(self, experience: str, context: Dict = None) -> Dict:
        """
        从经验中提炼教训
        
        Args:
            experience: 经验描述
            context: 上下文信息
            
        Returns:
            结构化教训
        """
        lesson = {
            'id': self._generate_lesson_id(experience),
            'title': self._extract_title(experience),
            'category': self._categorize_lesson(experience),
            'problem': self._extract_problem(experience),
            'solution': self._extract_solution(experience),
            'confidence': self._calculate_confidence(experience, context),
            'keywords': self._extract_keywords(experience),
            'related_lessons': [],
            'review_schedule': self._generate_review_schedule(),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return lesson
    
    def _generate_lesson_id(self, experience: str) -> str:
        """生成教训编号"""
        # 基于内容自动分类
        if '防护' in experience or '路径' in experience:
            prefix = 'SYS'
        elif '人格' in experience or '规划' in experience:
            prefix = 'MULTI'
        elif '记忆' in experience or '蒸馏' in experience:
            prefix = 'MEM'
        elif '飞书' in experience or '通知' in experience:
            prefix = 'FEISHU'
        elif '安全' in experience or '风险' in experience:
            prefix = 'SEC'
        else:
            prefix = 'LESSON'
        
        # 随机编号 (实际应从数据库获取下一个编号)
        import random
        num = random.randint(100, 999)
        
        return f"[{prefix}-{num}]"
    
    def _extract_title(self, experience: str) -> str:
        """提取标题"""
        # 简单提取第一句作为标题
        lines = experience.strip().split('\n')
        title = lines[0] if lines else "未命名教训"
        
        # 限制长度
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title
    
    def _categorize_lesson(self, experience: str) -> str:
        """分类教训"""
        for prefix, category in self.knowledge_categories.items():
            if prefix in experience or category in experience:
                return f"{prefix} - {category}"
        return "GENERAL - 通用知识"
    
    def _extract_problem(self, experience: str) -> str:
        """提取问题"""
        # 查找问题描述
        problem_keywords = ['问题', '困难', '挑战', '障碍', 'error', 'fail']
        
        for line in experience.split('\n'):
            for kw in problem_keywords:
                if kw.lower() in line.lower():
                    return line.strip()
        
        return "未明确描述"
    
    def _extract_solution(self, experience: str) -> str:
        """提取解决方案"""
        # 查找解决方案
        solution_keywords = ['解决', '方案', '方法', '修复', '优化', 'solution', 'fix']
        
        for line in experience.split('\n'):
            for kw in solution_keywords:
                if kw.lower() in line.lower():
                    return line.strip()
        
        return "未明确描述"
    
    def _calculate_confidence(self, experience: str, context: Dict = None) -> float:
        """计算置信度"""
        score = 0.7  # 基础置信度
        
        # 有具体数据 → +0.1
        if re.search(r'\d+%', experience) or re.search(r'\d+\.\d+', experience):
            score += 0.1
        
        # 有验证结果 → +0.1
        if '验证' in experience or 'test' in experience.lower() or '通过' in experience:
            score += 0.1
        
        # 有批判者评分 → +0.1
        if context and context.get('critic_score'):
            if context['critic_score'] >= 90:
                score += 0.1
            elif context['critic_score'] >= 85:
                score += 0.05
        
        return min(1.0, score)
    
    def _extract_keywords(self, experience: str) -> List[str]:
        """提取关键词"""
        # 简单关键词提取
        keywords = []
        
        # 技术术语
        tech_terms = ['Python', 'Git', 'API', 'JSON', 'HTTP', 'SQL', 'ML', 'AI']
        for term in tech_terms:
            if term in experience:
                keywords.append(term)
        
        # 中文关键词
        cn_terms = ['优化', '系统', '工具', '自动化', '质量', '效率', '安全']
        for term in cn_terms:
            if term in experience:
                keywords.append(term)
        
        return keywords[:5]  # 最多 5 个
    
    def _generate_review_schedule(self) -> List[Dict]:
        """生成复习计划 (基于遗忘曲线)"""
        schedule = []
        today = datetime.now()
        
        for days, retention in self.forgetting_curve.items():
            review_date = today + timedelta(days=days)
            schedule.append({
                'review_date': review_date.strftime('%Y-%m-%d'),
                'days_after': days,
                'expected_retention': f'{retention:.0%}',
                'status': 'pending'
            })
        
        return schedule
    
    def find_related_lessons(self, lesson: Dict, all_lessons: List[Dict]) -> List[Dict]:
        """查找相关教训"""
        related = []
        
        for other in all_lessons:
            # 关键词匹配
            common_keywords = set(lesson['keywords']) & set(other['keywords'])
            if len(common_keywords) >= 2:
                related.append({
                    'id': other['id'],
                    'title': other['title'],
                    'similarity': len(common_keywords) / max(len(lesson['keywords']), 1)
                })
        
        # 按相似度排序
        related.sort(key=lambda x: x['similarity'], reverse=True)
        
        return related[:3]  # 最多 3 个相关
    
    def assess_learning_quality(self, lesson: Dict) -> Dict:
        """评估学习质量"""
        scores = {
            'clarity': 0.5,      # 清晰度
            'specificity': 0.5,  # 具体性
            'actionability': 0.5, # 可操作性
            'connectivity': 0.5   # 关联性
        }
        
        # 清晰度 (有标题 + 问题 + 解决方案)
        if lesson['title'] and lesson['problem'] != "未明确描述":
            scores['clarity'] += 0.25
        if lesson['solution'] != "未明确描述":
            scores['clarity'] += 0.25
        
        # 具体性 (有数据/验证)
        if lesson['confidence'] >= 0.8:
            scores['specificity'] += 0.5
        
        # 可操作性 (有具体步骤)
        if len(lesson['solution']) > 20:
            scores['actionability'] += 0.5
        
        # 关联性 (有相关教训)
        if len(lesson['related_lessons']) > 0:
            scores['connectivity'] += 0.5
        
        # 总分
        total_score = sum(scores.values()) / len(scores)
        
        # 等级
        if total_score >= 0.85:
            grade = 'A+'
        elif total_score >= 0.75:
            grade = 'A'
        elif total_score >= 0.65:
            grade = 'B'
        else:
            grade = 'C'
        
        return {
            'total_score': total_score,
            'grade': grade,
            'scores': scores
        }
    
    def print_lesson(self, lesson: Dict):
        """打印教训"""
        print("=" * 60)
        print(f"教训编号：{lesson['id']}")
        print(f"标题：{lesson['title']}")
        print(f"分类：{lesson['category']}")
        print(f"置信度：{lesson['confidence']:.2f}")
        print("=" * 60)
        
        print(f"\n【问题】{lesson['problem']}")
        print(f"\n【解决方案】{lesson['solution']}")
        
        print(f"\n【关键词】{', '.join(lesson['keywords'])}")
        
        if lesson['related_lessons']:
            print(f"\n【相关教训】")
            for rel in lesson['related_lessons']:
                print(f"  - {rel['id']}: {rel['title']} (相似度:{rel['similarity']:.2f})")
        
        print(f"\n【复习计划】")
        for review in lesson['review_schedule'][:3]:
            print(f"  - {review['review_date']} ({review['days_after']}天后，保留{review['expected_retention']})")
        
        # 学习质量
        quality = self.assess_learning_quality(lesson)
        print(f"\n【学习质量】{quality['total_score']:.2f} ({quality['grade']})")
        
        print("\n" + "=" * 60)


def demo_learner():
    """演示学习者助手"""
    print("=" * 60)
    print("学习者助手 V2")
    print("=" * 60)
    
    assistant = LearnerAssistantV2()
    
    # 示例经验
    experiences = [
        """
        问题：新会话文件创建在 C 盘而非 D 盘
        解决方案：实施 5 层防护系统 (sitecustomize + 环境变量 + PowerShell Profile + Git 钩子 + 路径拦截)
        验证：7 人格检测 5/5 场景通过，批判者评分 95/100
        教训：永远使用绝对路径，使用 Workspace 类管理路径
        """,
        """
        问题：规划者时间估算误差大 (~30%)
        解决方案：实施规划者助手 V2 (自动分解 + 模型估算 +20% 缓冲)
        验证：规划质量从 0.52 提升到 0.91 (+75%)
        教训：时间估算必须包含缓冲，使用模板提高准确性
        """,
        """
        问题：记忆系统检索效率低
        解决方案：实施增强检索 V2 (语义 + 关键词双引擎)
        验证：检索速度提升 60%，准确率提升 40%
        教训：混合检索优于单一检索，缓存提高性能
        """
    ]
    
    for exp in experiences:
        print(f"\n{'='*60}")
        print("经验输入:")
        print(exp.strip())
        print('='*60)
        
        lesson = assistant.extract_lesson(exp)
        assistant.print_lesson(lesson)


if __name__ == "__main__":
    demo_learner()
