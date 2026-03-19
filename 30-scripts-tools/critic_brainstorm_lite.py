#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Critic Brainstorm Lite - 头脑风暴轻量批判者
特色：快速审查、仅检查致命问题、≥60 分通过

区别于主工作流的严格批判者 (≥80 分)
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class CriticBrainstormLite:
    """头脑风暴轻量批判者"""
    
    def __init__(self, brainstorm_result_file):
        """
        初始化批判者
        
        Args:
            brainstorm_result_file: 头脑风暴结果 JSON 文件路径
        """
        with open(brainstorm_result_file, 'r', encoding='utf-8') as f:
            self.result = json.load(f)
        
        self.top_ideas = self.result.get('final_top_ideas', [])
        self.criteria = {
            "originality": {"weight": 0.3, "threshold": 60},
            "relevance": {"weight": 0.3, "threshold": 60},
            "feasibility": {"weight": 0.2, "threshold": 50},
            "impact": {"weight": 0.2, "threshold": 60}
        }
    
    def check_fatal_issues(self, idea):
        """检查致命问题"""
        fatal_issues = []
        idea_text = str(idea).lower()
        
        # 学术诚信检查
        if 'fabricate' in idea_text or 'fake' in idea_text or '伪造' in idea_text:
            fatal_issues.append("学术诚信问题")
        
        # 可行性检查
        if 'impossible' in idea_text or '无法实现' in idea_text:
            fatal_issues.append("不可实现")
        
        # 伦理风险检查
        if 'violate' in idea_text or '违反' in idea_text or 'unethical' in idea_text:
            fatal_issues.append("伦理风险")
        
        # 成本检查
        if 'too expensive' in idea_text or '成本过高' in idea_text:
            fatal_issues.append("成本过高")
        
        return fatal_issues
    
    def score_idea(self, idea):
        """评分单个想法"""
        idea_text = str(idea).lower()
        
        # 原创性评分 (0-100)
        originality_score = 60  # 基础分
        innovation_keywords = ['新', '创新', '首次', '突破', 'novel', 'first', 'breakthrough']
        for kw in innovation_keywords:
            if kw in idea_text:
                originality_score += 10
        originality_score = min(originality_score, 100)
        
        # 相关性评分 (0-100)
        relevance_score = 60  # 基础分
        topic = self.result.get('topic', '').lower()
        if topic in idea_text:
            relevance_score += 20
        relevance_score = min(relevance_score, 100)
        
        # 可行性评分 (0-100)
        feasibility_score = 60  # 基础分
        feasibility_keywords = ['简单', '快速', '自动', 'easy', 'simple', 'quick']
        difficulty_keywords = ['复杂', '困难', '需要', 'complex', 'difficult', 'require']
        for kw in feasibility_keywords:
            if kw in idea_text:
                feasibility_score += 5
        for kw in difficulty_keywords:
            if kw in idea_text:
                feasibility_score -= 10
        feasibility_score = max(min(feasibility_score, 100), 0)
        
        # 影响力评分 (0-100)
        impact_score = 60  # 基础分
        impact_keywords = ['系统', '平台', '框架', '优化', 'system', 'platform', 'optimize']
        for kw in impact_keywords:
            if kw in idea_text:
                impact_score += 10
        impact_score = min(impact_score, 100)
        
        # 加权总分
        total_score = (
            originality_score * self.criteria['originality']['weight'] +
            relevance_score * self.criteria['relevance']['weight'] +
            feasibility_score * self.criteria['feasibility']['weight'] +
            impact_score * self.criteria['impact']['weight']
        )
        
        return {
            'originality': originality_score,
            'relevance': relevance_score,
            'feasibility': feasibility_score,
            'impact': impact_score,
            'total': total_score
        }
    
    def review(self):
        """执行批判者审查"""
        print(f"\n{'='*60}")
        print(f"Critic Brainstorm Lite - 轻量批判者审查")
        print(f"{'='*60}")
        print(f"审查想法数：{len(self.top_ideas)}")
        print(f"通过标准：≥60 分")
        print(f"{'='*60}\n")
        
        review_results = []
        passed_count = 0
        
        for i, idea in enumerate(self.top_ideas, 1):
            print(f"\n想法 {i}:")
            idea_text = idea.get('idea', 'N/A')
            print(f"  内容：{idea_text[:80]}...")
            
            # 检查致命问题
            fatal_issues = self.check_fatal_issues(idea)
            
            # 评分
            scores = self.score_idea(idea)
            
            # 判断是否通过
            passed = scores['total'] >= 60 and len(fatal_issues) == 0
            
            if passed:
                passed_count += 1
                status = "通过"
            else:
                status = "不通过"
            
            print(f"  评分：{scores['total']:.1f}/100")
            print(f"  致命问题：{len(fatal_issues)} 个")
            if fatal_issues:
                print(f"    - {', '.join(fatal_issues)}")
            print(f"  状态：{status}")
            
            review_results.append({
                'idea': idea,
                'scores': scores,
                'fatal_issues': fatal_issues,
                'passed': passed
            })
        
        # 计算总体评分
        overall_score = sum(r['scores']['total'] for r in review_results) / len(review_results) if review_results else 0
        pass_rate = passed_count / len(review_results) * 100 if review_results else 0
        
        print(f"\n{'='*60}")
        print(f"审查总结:")
        print(f"  总体评分：{overall_score:.1f}/100")
        print(f"  通过数量：{passed_count}/{len(review_results)}")
        print(f"  通过率：{pass_rate:.1f}%")
        
        if overall_score >= 60 and pass_rate >= 50:
            print(f"  结果：✅ 通过 (≥60 分)")
        else:
            print(f"  结果：❌ 不通过 (<60 分)")
        print(f"{'='*60}\n")
        
        return {
            'reviewed_at': datetime.now().isoformat(),
            'total_ideas': len(self.top_ideas),
            'passed_ideas': passed_count,
            'failed_ideas': len(self.top_ideas) - passed_count,
            'overall_score': overall_score,
            'pass_rate': pass_rate,
            'results': review_results,
            'passed': overall_score >= 60 and pass_rate >= 50
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python critic_brainstorm_lite.py <brainstorm_result_file>")
        sys.exit(1)
    
    result_file = sys.argv[1]
    
    critic = CriticBrainstormLite(result_file)
    review_result = critic.review()
    
    # 保存审查结果
    output_dir = Path("flow-archive/20260318-universal-workflow-001")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"critic-lite-review-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(review_result, f, indent=2, ensure_ascii=False)
    
    print(f"审查结果已保存：{output_file}")
    
    # 返回退出码
    sys.exit(0 if review_result['passed'] else 1)


if __name__ == "__main__":
    main()
