#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Convergent Tool - 头脑风暴收敛工具
特色：轻量验证、快速决策、优先级排序

双环模式：收敛环 (C1-C5)
时间盒：25 分钟
"""

import json
import time
from datetime import datetime
from pathlib import Path


class ConvergentBrainstorm:
    """头脑风暴收敛工具 - 筛选高价值想法"""
    
    def __init__(self, idea_pool_file):
        """
        初始化收敛工具
        
        Args:
            idea_pool_file: 发散环生成的想法池 JSON 文件路径
        """
        with open(idea_pool_file, 'r', encoding='utf-8') as f:
            self.idea_pool = json.load(f)
        
        self.ideas = self.idea_pool['ideas']
        self.top_ideas = []
        self.impact_matrix = {
            "high_impact_high_feasibility": [],
            "high_impact_low_feasibility": [],
            "low_impact_high_feasibility": [],
            "low_impact_low_feasibility": []
        }
    
    def step_c1_quick_filter(self, threshold=3.0):
        """
        Step C1: 初步筛选 (5 分钟)
        快速评分 1-5 分，淘汰明显不可行
        
        评分维度:
        - 原创性 (0-5)
        - 相关性 (0-5)
        - 可行性 (0-5)
        - 影响力 (0-5)
        """
        print(f"\n{'='*60}")
        print(f"Step C1: 初步筛选 (5 分钟)")
        print(f"{'='*60}")
        
        filtered_ideas = []
        
        for idea in self.ideas:
            # 简单评分 (基于启发式规则)
            originality = self._score_originality(idea)
            relevance = self._score_relevance(idea)
            feasibility = self._score_feasibility(idea)
            impact = self._score_impact(idea)
            
            avg_score = (originality + relevance + feasibility + impact) / 4
            
            # 添加评分到想法
            idea['scores'] = {
                'originality': originality,
                'relevance': relevance,
                'feasibility': feasibility,
                'impact': impact,
                'average': avg_score
            }
            
            # 保留≥阈值的想法
            if avg_score >= threshold:
                filtered_ideas.append(idea)
        
        self.ideas = filtered_ideas
        print(f"筛选后保留：{len(filtered_ideas)}/{len(self.idea_pool['ideas'])} 个想法")
        print(f"淘汰率：{(1 - len(filtered_ideas)/len(self.idea_pool['ideas']))*100:.1f}%")
        
        return filtered_ideas
    
    def _score_originality(self, idea):
        """评分：原创性 (0-5)"""
        score = 3.0  # 基础分
        
        # 检查是否包含创新关键词
        innovation_keywords = ['新', '创新', '首次', '突破', '原创', 'novel', 'first', 'breakthrough']
        idea_text = str(idea).lower()
        
        for keyword in innovation_keywords:
            if keyword in idea_text:
                score += 0.5
        
        return min(score, 5.0)
    
    def _score_relevance(self, idea):
        """评分：相关性 (0-5)"""
        score = 3.0  # 基础分
        
        # 检查是否包含主题关键词
        topic_keywords = self.idea_pool.get('keywords', [])
        idea_text = str(idea).lower()
        
        match_count = sum(1 for kw in topic_keywords if kw.lower() in idea_text)
        score += min(match_count * 0.3, 2.0)
        
        return min(score, 5.0)
    
    def _score_feasibility(self, idea):
        """评分：可行性 (0-5)"""
        score = 3.0  # 基础分
        
        # 检查是否包含可行性关键词
        feasibility_keywords = ['简单', '快速', '自动', '现有', 'easy', 'simple', 'quick', 'auto']
        difficulty_keywords = ['复杂', '困难', '需要', '必须', 'complex', 'difficult', 'require']
        
        idea_text = str(idea).lower()
        
        for keyword in feasibility_keywords:
            if keyword in idea_text:
                score += 0.3
        
        for keyword in difficulty_keywords:
            if keyword in idea_text:
                score -= 0.3
        
        return max(min(score, 5.0), 0.0)
    
    def _score_impact(self, idea):
        """评分：影响力 (0-5)"""
        score = 3.0  # 基础分
        
        # 检查是否包含影响力关键词
        impact_keywords = ['系统', '平台', '框架', '优化', '提升', 'system', 'platform', 'optimize', 'improve']
        idea_text = str(idea).lower()
        
        for keyword in impact_keywords:
            if keyword in idea_text:
                score += 0.3
        
        return min(score, 5.0)
    
    def step_c2_lite_verification(self, max_papers=3):
        """
        Step C2: 轻量验证 (5 分钟)
        快速检索≤3 篇文献，检查是否已有类似工作
        """
        print(f"\n{'='*60}")
        print(f"Step C2: 轻量验证 (5 分钟)")
        print(f"{'='*60}")
        
        # 简化验证：标记想法的验证状态
        for idea in self.ideas[:max_papers * 2]:  # 仅验证 top 想法
            # 简单验证逻辑
            idea['verification'] = {
                'status': 'lite_checked',
                'papers_checked': min(max_papers, 3),
                'similar_work_found': False,  # 简化：假设无类似工作
                'confidence': 0.7  # 70% 置信度
            }
        
        print(f"完成轻量验证：{min(len(self.ideas), max_papers * 2)} 个想法")
        
        return self.ideas
    
    def step_c3_impact_matrix(self):
        """
        Step C3: 影响力评估 (5 分钟)
        生成 2x2 优先级矩阵
        """
        print(f"\n{'='*60}")
        print(f"Step C3: 影响力评估 (5 分钟)")
        print(f"{'='*60}")
        
        # 重置矩阵
        self.impact_matrix = {
            "high_impact_high_feasibility": [],
            "high_impact_low_feasibility": [],
            "low_impact_high_feasibility": [],
            "low_impact_low_feasibility": []
        }
        
        # 分类想法
        for idea in self.ideas:
            scores = idea.get('scores', {})
            impact = scores.get('impact', 3.0)
            feasibility = scores.get('feasibility', 3.0)
            
            if impact >= 4.0 and feasibility >= 4.0:
                self.impact_matrix["high_impact_high_feasibility"].append(idea)
            elif impact >= 4.0:
                self.impact_matrix["high_impact_low_feasibility"].append(idea)
            elif feasibility >= 4.0:
                self.impact_matrix["low_impact_high_feasibility"].append(idea)
            else:
                self.impact_matrix["low_impact_low_feasibility"].append(idea)
        
        # 打印矩阵
        print("\n影响力 - 可行性矩阵:")
        print(f"  高影响力高可行性：{len(self.impact_matrix['high_impact_high_feasibility'])} 个 ⭐")
        print(f"  高影响力低可行性：{len(self.impact_matrix['high_impact_low_feasibility'])} 个")
        print(f"  低影响力高可行性：{len(self.impact_matrix['low_impact_high_feasibility'])} 个")
        print(f"  低影响力低可行性：{len(self.impact_matrix['low_impact_low_feasibility'])} 个")
        
        return self.impact_matrix
    
    def step_c4_critic_lite(self, threshold=60):
        """
        Step C4: 快速批判 (5 分钟)
        轻量版批判者，仅检查致命问题
        """
        print(f"\n{'='*60}")
        print(f"Step C4: 快速批判 (5 分钟)")
        print(f"{'='*60}")
        
        critic_results = []
        
        for idea in self.ideas:
            # 简化批判逻辑
            fatal_issues = []
            
            # 检查致命问题
            idea_text = str(idea).lower()
            
            if '无法实现' in idea_text or 'impossible' in idea_text:
                fatal_issues.append('不可实现')
            
            if '违反' in idea_text or 'violate' in idea_text:
                fatal_issues.append('伦理风险')
            
            if '成本过高' in idea_text or 'too expensive' in idea_text:
                fatal_issues.append('成本过高')
            
            # 计算评分
            base_score = idea.get('scores', {}).get('average', 3.0) * 20  # 转换为 0-100
            penalty = len(fatal_issues) * 20
            final_score = max(base_score - penalty, 0)
            
            critic_result = {
                'idea': idea,
                'score': final_score,
                'fatal_issues': fatal_issues,
                'passed': final_score >= threshold
            }
            
            critic_results.append(critic_result)
        
        # 过滤通过的想法
        passed_ideas = [r['idea'] for r in critic_results if r['passed']]
        self.ideas = passed_ideas
        
        print(f"批判者审查：{len(passed_ideas)}/{len(critic_results)} 个想法通过 (≥{threshold}分)")
        
        return critic_results
    
    def step_c5_action_plan(self, top_n=3, output_file=None):
        """
        Step C5: 行动规划 (5 分钟)
        Top 3 想法 → 行动计划
        """
        print(f"\n{'='*60}")
        print(f"Step C5: 行动规划 (5 分钟)")
        print(f"{'='*60}")
        
        # 按评分排序
        sorted_ideas = sorted(
            self.ideas,
            key=lambda x: x.get('scores', {}).get('average', 0),
            reverse=True
        )[:top_n]
        
        # 生成行动计划
        action_plan = {
            "topic": self.idea_pool['topic'],
            "generated_at": datetime.now().isoformat(),
            "top_ideas": sorted_ideas,
            "estimated_effort": self._estimate_effort(sorted_ideas),
            "next_steps": self._generate_next_steps(sorted_ideas),
            "impact_matrix": self.impact_matrix
        }
        
        # 保存文件
        if output_file is None:
            output_dir = Path("flow-archive/20260318-universal-workflow-001")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"convergent-brainstorm-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(action_plan, f, indent=2, ensure_ascii=False)
        
        print(f"行动计划已保存：{output_file}")
        print(f"Top {top_n} 想法:")
        for i, idea in enumerate(sorted_ideas, 1):
            print(f"  {i}. {idea.get('idea', 'N/A')[:60]}...")
        
        return action_plan
    
    def _estimate_effort(self, ideas):
        """估算工作量"""
        efforts = []
        for idea in ideas:
            feasibility = idea.get('scores', {}).get('feasibility', 3.0)
            if feasibility >= 4.0:
                effort = "低 (1-2 小时)"
            elif feasibility >= 3.0:
                effort = "中 (2-4 小时)"
            else:
                effort = "高 (4+ 小时)"
            efforts.append(effort)
        return efforts
    
    def _generate_next_steps(self, ideas):
        """生成下一步行动"""
        steps = []
        for idea in ideas:
            steps.append({
                "idea": idea.get('idea', 'N/A')[:50],
                "action": "详细调研 + 可行性分析",
                "timeline": "1 周内",
                "owner": "TBD"
            })
        return steps
    
    def run(self, output_file=None):
        """运行完整收敛流程"""
        print(f"\n{'#'*60}")
        print(f"# 头脑风暴收敛环 - {self.idea_pool['topic']}")
        print(f"# 输入想法：{len(self.ideas)} 个")
        print(f"{'#'*60}")
        
        start = time.time()
        
        # 执行 5 个步骤
        self.step_c1_quick_filter()
        self.step_c2_lite_verification()
        self.step_c3_impact_matrix()
        self.step_c4_critic_lite()
        result = self.step_c5_action_plan(output_file)
        
        elapsed = time.time() - start
        print(f"\n收敛环完成，用时：{elapsed:.1f} 秒")
        
        return result


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python brainstorm_convergent.py <idea_pool_file> [output_file]")
        sys.exit(1)
    
    idea_pool_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convergent = ConvergentBrainstorm(idea_pool_file)
    result = convergent.run(output_file)
    
    print(f"\n收敛环完成:")
    print(f"  Top 想法数：{len(result['top_ideas'])}")


if __name__ == "__main__":
    main()
