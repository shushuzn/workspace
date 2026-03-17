#!/usr/bin/env python3
"""
规划者助手 V2 - Planner Assistant
功能：任务分解 + 时间估算 + 风险评估 + 备选方案
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class PlannerAssistantV2:
    """规划者助手 V2"""
    
    def __init__(self):
        self.task_complexity_weights = {
            '简单': 1.0,
            '中等': 2.0,
            '复杂': 3.0,
            '非常复杂': 4.0
        }
        
        self.risk_factors = {
            '新技术': 0.3,
            '外部依赖': 0.2,
            '时间紧迫': 0.2,
            '资源不足': 0.2,
            '需求变更': 0.1
        }
    
    def create_plan(self, task: str, context: Dict = None) -> Dict:
        """
        创建完整规划
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            完整规划 (包含分解、时间、风险、备选方案)
        """
        plan = {
            'task': task,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '分解': self._decompose_task(task),
            '时间估算': self._estimate_time(task, context),
            '风险评估': self._assess_risks(task, context),
            '备选方案': self._generate_alternatives(task, context),
            '验收标准': self._generate_acceptance_criteria(task),
            '质量评分': 0.0
        }
        
        # 计算质量评分
        plan['质量评分'] = self._calculate_plan_quality(plan)
        
        return plan
    
    def _decompose_task(self, task: str) -> List[Dict]:
        """任务分解"""
        # 基于关键词智能分解
        subtasks = []
        
        # 常见任务模式
        if '优化' in task or 'optimize' in task.lower():
            subtasks = [
                {'步骤': 1, '任务': '分析现状', '预计': '30min'},
                {'步骤': 2, '任务': '识别问题', '预计': '30min'},
                {'步骤': 3, '任务': '设计方案', '预计': '1h'},
                {'步骤': 4, '任务': '实施优化', '预计': '2h'},
                {'步骤': 5, '任务': '测试验证', '预计': '1h'},
            ]
        elif '创建' in task or 'create' in task.lower():
            subtasks = [
                {'步骤': 1, '任务': '需求分析', '预计': '30min'},
                {'步骤': 2, '任务': '设计方案', '预计': '1h'},
                {'步骤': 3, '任务': '实施开发', '预计': '3h'},
                {'步骤': 4, '任务': '测试调试', '预计': '1h'},
                {'步骤': 5, '任务': '文档编写', '预计': '30min'},
            ]
        elif '检测' in task or 'test' in task.lower():
            subtasks = [
                {'步骤': 1, '任务': '设计测试用例', '预计': '30min'},
                {'步骤': 2, '任务': '准备测试环境', '预计': '30min'},
                {'步骤': 3, '任务': '执行测试', '预计': '1h'},
                {'步骤': 4, '任务': '分析结果', '预计': '30min'},
                {'步骤': 5, '任务': '生成报告', '预计': '30min'},
            ]
        else:
            # 通用分解
            subtasks = [
                {'步骤': 1, '任务': '理解任务', '预计': '15min'},
                {'步骤': 2, '任务': '制定计划', '预计': '30min'},
                {'步骤': 3, '任务': '执行任务', '预计': '2h'},
                {'步骤': 4, '任务': '验证结果', '预计': '30min'},
            ]
        
        return subtasks
    
    def _estimate_time(self, task: str, context: Dict = None) -> Dict:
        """时间估算"""
        # 基础时间
        base_time = 2.0  # 小时
        
        # 复杂度调整
        complexity = self._estimate_complexity(task)
        adjusted_time = base_time * self.task_complexity_weights.get(complexity, 1.0)
        
        # 上下文调整
        if context:
            if context.get('urgency') == 'high':
                adjusted_time *= 0.8  # 紧急任务压缩时间
            if context.get('experience') == 'low':
                adjusted_time *= 1.5  # 缺乏经验增加时间
        
        # 缓冲时间 (20%)
        buffer_time = adjusted_time * 0.2
        
        total_time = adjusted_time + buffer_time
        
        return {
            '基础时间': f'{adjusted_time:.1f}小时',
            '缓冲时间': f'{buffer_time:.1f}小时',
            '总时间': f'{total_time:.1f}小时',
            '复杂度': complexity,
            '置信度': '高' if complexity == '简单' else '中' if complexity == '中等' else '低'
        }
    
    def _estimate_complexity(self, task: str) -> str:
        """估算任务复杂度"""
        score = 0
        
        # 长度评分
        if len(task) > 50:
            score += 1
        if len(task) > 100:
            score += 1
        
        # 关键词评分
        complex_keywords = ['系统', '架构', '优化', '集成', '自动化', '多模块']
        for kw in complex_keywords:
            if kw in task.lower():
                score += 1
        
        # 映射到复杂度
        if score <= 1:
            return '简单'
        elif score <= 3:
            return '中等'
        elif score <= 5:
            return '复杂'
        else:
            return '非常复杂'
    
    def _assess_risks(self, task: str, context: Dict = None) -> List[Dict]:
        """风险评估"""
        risks = []
        
        # 自动识别风险
        if '新' in task or 'new' in task.lower():
            risks.append({
                '风险': '新技术/新领域',
                '概率': '中',
                '影响': '高',
                '缓解措施': '提前调研，准备备选方案'
            })
        
        if '外部' in task or 'external' in task.lower():
            risks.append({
                '风险': '外部依赖',
                '概率': '中',
                '影响': '中',
                '缓解措施': '提前沟通，确认接口'
            })
        
        if context and context.get('urgency') == 'high':
            risks.append({
                '风险': '时间紧迫',
                '概率': '高',
                '影响': '高',
                '缓解措施': '优先级排序，必要时削减范围'
            })
        
        # 默认风险
        if not risks:
            risks.append({
                '风险': '需求理解偏差',
                '概率': '低',
                '影响': '中',
                '缓解措施': '确认需求，及时沟通'
            })
        
        return risks
    
    def _generate_alternatives(self, task: str, context: Dict = None) -> List[Dict]:
        """生成备选方案"""
        alternatives = []
        
        # 方案 A: 标准方案
        alternatives.append({
            '方案': 'A (标准)',
            '描述': '按标准流程执行',
            '时间': '正常',
            '风险': '低',
            '推荐': True
        })
        
        # 方案 B: 快速方案
        alternatives.append({
            '方案': 'B (快速)',
            '描述': '简化流程，快速交付',
            '时间': '-30%',
            '风险': '中',
            '推荐': False
        })
        
        # 方案 C: 稳健方案
        alternatives.append({
            '方案': 'C (稳健)',
            '描述': '充分测试，确保质量',
            '时间': '+50%',
            '风险': '低',
            '推荐': False
        })
        
        return alternatives
    
    def _generate_acceptance_criteria(self, task: str) -> List[str]:
        """生成验收标准"""
        criteria = [
            '功能完整，满足需求',
            '测试通过，无重大 bug',
            '文档完整，易于维护',
            '性能达标，响应时间<1s',
            '代码质量，符合规范'
        ]
        return criteria
    
    def _calculate_plan_quality(self, plan: Dict) -> float:
        """计算规划质量"""
        score = 0.5
        
        # 任务分解质量 (0.25)
        if len(plan['分解']) >= 4:
            score += 0.25
        
        # 时间估算质量 (0.25)
        if '缓冲时间' in plan['时间估算']:
            score += 0.25
        
        # 风险评估质量 (0.25)
        if len(plan['风险评估']) >= 2:
            score += 0.25
        
        # 备选方案质量 (0.25)
        if len(plan['备选方案']) >= 2:
            score += 0.25
        
        return min(1.0, score)
    
    def print_plan(self, plan: Dict):
        """打印规划"""
        print("=" * 60)
        print(f"任务：{plan['task']}")
        print(f"创建时间：{plan['created_at']}")
        print(f"质量评分：{plan['质量评分']:.2f}")
        print("=" * 60)
        
        print("\n【任务分解】")
        for subtask in plan['分解']:
            print(f"  {subtask['步骤']}. {subtask['任务']} ({subtask['预计']})")
        
        print("\n【时间估算】")
        for key, value in plan['时间估算'].items():
            print(f"  {key}: {value}")
        
        print("\n【风险评估】")
        for risk in plan['风险评估']:
            print(f"  [WARN] {risk['风险']} (概率:{risk['概率']}, 影响:{risk['影响']})")
            print(f"     缓解：{risk['缓解措施']}")
        
        print("\n【备选方案】")
        for alt in plan['备选方案']:
            recommend = "[REC]" if alt['推荐'] else "     "
            print(f"  {recommend} {alt['方案']}: {alt['描述']} (时间:{alt['时间']}, 风险:{alt['风险']})")
        
        print("\n【验收标准】")
        for i, criteria in enumerate(plan['验收标准'], 1):
            print(f"  {i}. {criteria}")
        
        print("\n" + "=" * 60)


def demo_planner():
    """演示规划者助手"""
    print("=" * 60)
    print("规划者助手 V2")
    print("=" * 60)
    
    assistant = PlannerAssistantV2()
    
    # 演示任务
    tasks = [
        "优化记忆系统检索速度",
        "创建新的知识卡片生成器",
        "检测 7 人格系统运行状态"
    ]
    
    for task in tasks:
        print(f"\n{'='*60}")
        print(f"任务：{task}")
        print('='*60)
        plan = assistant.create_plan(task)
        assistant.print_plan(plan)


if __name__ == "__main__":
    demo_planner()
