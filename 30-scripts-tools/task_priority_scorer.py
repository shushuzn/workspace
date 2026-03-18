#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
ENH-001: Task Priority Scorer
自动任务优先级评分系统

功能:
- 根据紧迫性、影响力、工作量、依赖关系自动评分
- 输出 P0/P1/P2 优先级分类
- 支持批量任务排序

使用示例:
    python task_priority_scorer.py --task "Complete CNT paper" --deadline 2026-03-20 --impact high --effort 4h
    python task_priority_scorer.py --batch tasks.json
"""

import argparse
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Windows 控制台编码修复
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        os.system('chcp 65001 >nul')


@dataclass
class Task:
    name: str
    deadline: Optional[datetime] = None
    impact_level: str = "medium"  # low/medium/high/critical
    estimated_hours: float = 1.0
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class TaskPriorityScorer:
    """任务优先级评分器"""
    
    # 影响力权重映射
    IMPACT_WEIGHTS = {
        'critical': 100,
        'high': 80,
        'medium': 50,
        'low': 20
    }
    
    def __init__(self):
        self.current_time = datetime.now()
    
    def _calc_urgency(self, deadline: Optional[datetime]) -> float:
        """计算紧迫性分数 (0-100)"""
        if not deadline:
            return 50.0  # 默认中等紧迫
        
        hours_left = (deadline - self.current_time).total_seconds() / 3600
        
        if hours_left <= 0:
            return 100.0  # 已过期
        elif hours_left <= 24:
            return 95.0  # 24 小时内
        elif hours_left <= 72:
            return 80.0  # 3 天内
        elif hours_left <= 168:  # 7 天
            return 60.0
        else:
            return 30.0  # 不紧急
    
    def _calc_impact(self, impact_level: str) -> float:
        """计算影响力分数 (0-100)"""
        return self.IMPACT_WEIGHTS.get(impact_level.lower(), 50.0)
    
    def _calc_effort(self, estimated_hours: float) -> float:
        """计算工作量分数 (0-100) - 工作量越大分数越低"""
        if estimated_hours <= 0.5:
            return 95.0  # 很快完成
        elif estimated_hours <= 2:
            return 80.0
        elif estimated_hours <= 8:
            return 60.0
        elif estimated_hours <= 24:
            return 40.0
        else:
            return 20.0  # 工作量巨大
    
    def _calc_dependency_score(self, dependencies: List[str]) -> float:
        """计算依赖关系分数 (0-100) - 依赖越多越优先"""
        dep_count = len(dependencies)
        
        if dep_count == 0:
            return 50.0  # 无依赖
        elif dep_count <= 2:
            return 70.0  # 少量依赖
        elif dep_count <= 5:
            return 85.0  # 中等依赖
        else:
            return 95.0  # 关键路径
    
    def score(self, task: Task) -> Dict:
        """
        计算任务综合优先级分数
        
        权重分配:
        - 紧迫性 (Urgency): 40%
        - 影响力 (Impact): 30%
        - 工作量 (Effort): -20% (负向，工作量越大优先级越低)
        - 依赖关系 (Dependency): 10%
        """
        urgency = self._calc_urgency(task.deadline)
        impact = self._calc_impact(task.impact_level)
        effort = self._calc_effort(task.estimated_hours)
        dependency = self._calc_dependency_score(task.dependencies)
        
        # 综合评分
        raw_score = (
            urgency * 0.40 +
            impact * 0.30 -
            effort * 0.20 +
            dependency * 0.10
        )
        
        # 归一化到 0-100
        normalized_score = max(0, min(100, raw_score))
        
        # 优先级分类
        if normalized_score >= 80:
            priority = 'P0'
            label = 'Critical - 立即执行'
        elif normalized_score >= 60:
            priority = 'P1'
            label = 'High - 今天完成'
        elif normalized_score >= 40:
            priority = 'P2'
            label = 'Medium - 本周完成'
        else:
            priority = 'P3'
            label = 'Low - 可延后'
        
        return {
            'task_name': task.name,
            'score': round(normalized_score, 2),
            'priority': priority,
            'label': label,
            'breakdown': {
                'urgency': round(urgency, 2),
                'impact': round(impact, 2),
                'effort': round(effort, 2),
                'dependency': round(dependency, 2)
            },
            'recommendation': self._generate_recommendation(normalized_score, task)
        }
    
    def _generate_recommendation(self, score: float, task: Task) -> str:
        """生成执行建议"""
        if score >= 80:
            return "🔥 立即处理！这是关键任务。"
        elif score >= 60:
            return "⚡ 今天优先完成。"
        elif score >= 40:
            return "📅 安排在本周内。"
        else:
            return "[PENDING] 可延后或批量处理。"
    
    def sort_tasks(self, tasks: List[Task]) -> List[Dict]:
        """批量任务排序"""
        scored_tasks = [self.score(task) for task in tasks]
        return sorted(scored_tasks, key=lambda x: x['score'], reverse=True)


def parse_deadline(date_str: str) -> Optional[datetime]:
    """解析截止日期字符串"""
    if not date_str:
        return None
    
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M',
        '%Y/%m/%d',
        '%d-%m-%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # 相对时间解析
    if date_str.endswith('h'):
        hours = int(date_str[:-1])
        return datetime.now() + timedelta(hours=hours)
    elif date_str.endswith('d'):
        days = int(date_str[:-1])
        return datetime.now() + timedelta(days=days)
    
    return None


def main():
    parser = argparse.ArgumentParser(description='Task Priority Scorer - ENH-001')
    parser.add_argument('--task', type=str, help='任务名称')
    parser.add_argument('--deadline', type=str, help='截止日期 (YYYY-MM-DD 或 24h/7d)')
    parser.add_argument('--impact', type=str, default='medium', 
                        choices=['low', 'medium', 'high', 'critical'],
                        help='影响力级别')
    parser.add_argument('--effort', type=str, default='1', help='预估工时 (小时或 2h/8h)')
    parser.add_argument('--deps', type=str, nargs='*', default=[], help='依赖任务列表')
    parser.add_argument('--batch', type=str, help='批量任务 JSON 文件')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    scorer = TaskPriorityScorer()
    
    # 批量模式
    if args.batch:
        with open(args.batch, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        tasks = []
        for data in tasks_data:
            task = Task(
                name=data.get('name', 'Unnamed'),
                deadline=parse_deadline(data.get('deadline')),
                impact_level=data.get('impact', 'medium'),
                estimated_hours=float(data.get('effort', 1)),
                dependencies=data.get('dependencies', [])
            )
            tasks.append(task)
        
        results = scorer.sort_tasks(tasks)
        
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[CHART] 批量任务优先级排序 (共 {len(results)} 个任务)")
            print(f"{'='*60}\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. [{result['priority']}] {result['task_name']}")
                print(f"   分数：{result['score']}/100 | {result['label']}")
                print(f"   建议：{result['recommendation']}")
                print()
        
        return
    
    # 单任务模式
    if not args.task:
        parser.print_help()
        return
    
    # 解析工时
    effort_str = args.effort
    if effort_str.endswith('h'):
        estimated_hours = float(effort_str[:-1])
    else:
        estimated_hours = float(effort_str)
    
    task = Task(
        name=args.task,
        deadline=parse_deadline(args.deadline),
        impact_level=args.impact,
        estimated_hours=estimated_hours,
        dependencies=args.deps
    )
    
    result = scorer.score(task)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"[LIST] 任务优先级评估")
        print(f"{'='*60}")
        print(f"任务：{result['task_name']}")
        print(f"优先级：[{result['priority']}] {result['label']}")
        print(f"综合分数：{result['score']}/100")
        print(f"\n维度分解:")
        print(f"  - 紧迫性：{result['breakdown']['urgency']}")
        print(f"  - 影响力：{result['breakdown']['impact']}")
        print(f"  - 工作量：{result['breakdown']['effort']} (负向)")
        print(f"  - 依赖关系：{result['breakdown']['dependency']}")
        print(f"\n[IDEA] 建议：{result['recommendation']}")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
