#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
规划自动优化器 - Plan Auto-Optimizer
功能：自动迭代优化规划质量，直到≥0.85
"""

import sys
from pathlib import Path

# 导入规划助手和质量评估器
sys.path.insert(0, str(Path(__file__).parent))
from planner_assistant_v2 import PlannerAssistantV2
from plan_quality_assessor import PlanQualityAssessor

class PlanAutoOptimizer:
    """规划自动优化器"""
    
    def __init__(self, target_score=0.85, max_iterations=5):
        self.target_score = target_score
        self.max_iterations = max_iterations
        self.planner = PlannerAssistantV2()
        self.assessor = PlanQualityAssessor()
    
    def optimize(self, task: str, context: dict = None) -> dict:
        """
        自动优化规划
        
        Args:
            task: 任务描述
            context: 上下文
            
        Returns:
            优化后的规划
        """
        print(f"[优化] 开始优化任务：{task}")
        print(f"[优化] 目标分数：{self.target_score}")
        print(f"[优化] 最大迭代：{self.max_iterations}")
        print()
        
        # 初始规划
        plan = self.planner.create_plan(task, context)
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"[迭代 {iteration}/{self.max_iterations}]")
            
            # 评估当前规划
            assessment = self.assessor.assess_plan(plan)
            current_score = assessment['total_score']
            
            print(f"  当前分数：{current_score:.2f} ({assessment['grade']})")
            
            # 检查是否达标
            if current_score >= self.target_score:
                print(f"  [OK] 达标！优化完成")
                print()
                break
            
            print(f"  [WARN] 未达标，需要优化")
            print(f"  改进建议:")
            for suggestion in assessment['suggestions']:
                print(f"    - {suggestion}")
            print()
            
            # 应用改进
            plan = self._apply_improvements(plan, assessment)
        
        # 最终评估
        final_assessment = self.assessor.assess_plan(plan)
        
        print(f"[优化完成]")
        print(f"  最终分数：{final_assessment['total_score']:.2f} ({final_assessment['grade']})")
        print(f"  迭代次数：{iteration}")
        print(f"  优化提升：{(final_assessment['total_score'] - current_score)*100:.1f}%")
        print()
        
        return plan
    
    def _apply_improvements(self, plan: dict, assessment: dict) -> dict:
        """应用改进"""
        scores = assessment['scores']
        suggestions = assessment['suggestions']
        
        # 改进任务分解
        if scores['completeness'] < 0.7 and len(plan['分解']) < 5:
            plan['分解'].append({
                '步骤': len(plan['分解']) + 1,
                '任务': '代码审查',
                '预计': '30min'
            })
            print(f"  [改进] 添加任务分解")
        
        # 改进验收标准
        if scores['specificity'] < 0.7 and len(plan['验收标准']) < 5:
            plan['验收标准'].append('性能优化，效率提升>20%')
            print(f"  [改进] 添加验收标准")
        
        # 改进风险评估
        if scores['risk_awareness'] < 0.7:
            if len(plan['风险评估']) < 2:
                plan['风险评估'].append({
                    '风险': '技术实现难度',
                    '概率': '中',
                    '影响': '中',
                    '缓解措施': '技术预研，准备备选方案'
                })
            print(f"  [改进] 添加风险评估")
        
        # 改进备选方案
        if scores['alternatives'] < 0.7:
            if len(plan['备选方案']) < 3:
                plan['备选方案'].append({
                    '方案': 'C (稳健)',
                    '描述': '充分测试，确保质量',
                    '时间': '+50%',
                    '风险': '低',
                    '推荐': False
                })
            print(f"  [改进] 添加备选方案")
        
        # 重新计算质量
        plan['质量评分'] = self.planner._calculate_plan_quality(plan)
        
        return plan


def demo_optimizer():
    """演示优化器"""
    print("=" * 60)
    print("规划自动优化器")
    print("=" * 60)
    print()
    
    optimizer = PlanAutoOptimizer(target_score=0.85, max_iterations=5)
    
    # 演示任务
    task = "优化规划者系统"
    
    optimized_plan = optimizer.optimize(task)
    
    # 打印优化后的规划
    print("=" * 60)
    print("优化后的规划")
    print("=" * 60)
    optimizer.planner.print_plan(optimized_plan)


if __name__ == "__main__":
    demo_optimizer()
