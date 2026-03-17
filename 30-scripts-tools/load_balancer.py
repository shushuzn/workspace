#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
ENH-005: Task Load Balancer
协调者 - 任务负载均衡优化器

功能:
- 大模型调用批量合并
- 文件操作分组对比
- Git 提交累积推送
- API 请求速率控制
- 资源使用优化

使用示例:
    python load_balancer.py --tasks tasks.json --optimize batch
    python load_balancer.py --check --api llm --window 10m
    python load_balancer.py --strategy auto --verbose
"""

import argparse
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
import hashlib


@dataclass
class Task:
    id: str
    type: str  # llm_call/file_operation/git_commit/api_request/other
    description: str
    priority: str = 'P2'  # P0/P1/P2/P3
    estimated_time: float = 1.0  # minutes
    resource_type: str = 'cpu'  # cpu/memory/network/api
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    batch_id: Optional[str] = None


@dataclass
class BatchGroup:
    id: str
    tasks: List[Task]
    strategy: str  # batch/parallel/sequential/rate_limited
    estimated_savings: float = 0.0  # minutes saved
    execution_order: List[str] = field(default_factory=list)


class LoadBalancer:
    """任务负载均衡器"""
    
    # 优化策略配置
    OPTIMIZATION_RULES = {
        'llm_call': {
            'strategy': 'batch',
            'max_batch_size': 10,
            'batch_window_minutes': 5,
            'savings_percentage': 0.7,  # 70% 减少
            'description': '大模型调用批量合并'
        },
        'file_operation': {
            'strategy': 'grouped_compare',
            'max_group_size': 20,
            'require_pre_hook': True,
            'savings_percentage': 0.5,
            'description': '文件操作分组对比验证'
        },
        'git_commit': {
            'strategy': 'accumulate_push',
            'min_commits_before_push': 3,
            'max_wait_minutes': 30,
            'savings_percentage': 0.6,
            'description': 'Git 提交累积后统一推送'
        },
        'api_request': {
            'strategy': 'rate_limit',
            'max_requests_per_minute': 60,
            'max_concurrent': 5,
            'savings_percentage': 0.3,
            'description': 'API 请求速率限制控制'
        }
    }
    
    def __init__(self):
        self.task_queue: List[Task] = []
        self.batch_groups: List[BatchGroup] = []
        self.execution_history: List[Dict] = []
        self.api_call_log: List[datetime] = []
        self.resource_usage: Dict[str, float] = defaultdict(float)
    
    def add_task(self, task: Task):
        """添加任务到队列"""
        self.task_queue.append(task)
    
    def add_tasks(self, tasks: List[Task]):
        """批量添加任务"""
        self.task_queue.extend(tasks)
    
    def analyze_tasks(self) -> Dict:
        """分析当前任务队列"""
        analysis = {
            'total_tasks': len(self.task_queue),
            'by_type': defaultdict(int),
            'by_priority': defaultdict(int),
            'by_resource': defaultdict(int),
            'total_estimated_time': 0.0,
            'optimization_opportunities': []
        }
        
        for task in self.task_queue:
            analysis['by_type'][task.type] += 1
            analysis['by_priority'][task.priority] += 1
            analysis['by_resource'][task.resource_type] += 1
            analysis['total_estimated_time'] += task.estimated_time
        
        # 识别优化机会
        type_counts = analysis['by_type']
        
        if type_counts.get('llm_call', 0) >= 2:
            analysis['optimization_opportunities'].append({
                'type': 'llm_call',
                'count': type_counts['llm_call'],
                'strategy': 'batch',
                'potential_savings': f"{type_counts['llm_call'] * 0.7:.0f} API calls"
            })
        
        if type_counts.get('file_operation', 0) >= 5:
            analysis['optimization_opportunities'].append({
                'type': 'file_operation',
                'count': type_counts['file_operation'],
                'strategy': 'grouped_compare',
                'potential_savings': f"{type_counts['file_operation'] * 0.5:.0f} comparisons"
            })
        
        if type_counts.get('git_commit', 0) >= 3:
            analysis['optimization_opportunities'].append({
                'type': 'git_commit',
                'count': type_counts['git_commit'],
                'strategy': 'accumulate_push',
                'potential_savings': f"{type_counts['git_commit'] * 0.6:.0f} pushes"
            })
        
        return analysis
    
    def optimize_batch(self, tasks: Optional[List[Task]] = None) -> List[BatchGroup]:
        """优化任务批处理"""
        if tasks is None:
            tasks = self.task_queue
        
        # 按类型分组
        grouped = defaultdict(list)
        for task in tasks:
            grouped[task.type].append(task)
        
        batch_groups = []
        
        for task_type, type_tasks in grouped.items():
            if task_type not in self.OPTIMIZATION_RULES:
                # 无优化规则，顺序执行
                batch_groups.append(BatchGroup(
                    id=f"sequential_{task_type}",
                    tasks=type_tasks,
                    strategy='sequential',
                    estimated_savings=0.0
                ))
                continue
            
            rule = self.OPTIMIZATION_RULES[task_type]
            strategy = rule['strategy']
            
            if strategy == 'batch':
                # 批量合并
                max_size = rule.get('max_batch_size', 10)
                for i in range(0, len(type_tasks), max_size):
                    batch = type_tasks[i:i + max_size]
                    batch_id = hashlib.md5(f"{task_type}_{i}".encode()).hexdigest()[:8]
                    
                    for task in batch:
                        task.batch_id = batch_id
                    
                    savings = sum(t.estimated_time for t in batch) * rule['savings_percentage']
                    
                    batch_groups.append(BatchGroup(
                        id=batch_id,
                        tasks=batch,
                        strategy='batch',
                        estimated_savings=savings,
                        execution_order=[t.id for t in batch]
                    ))
            
            elif strategy == 'grouped_compare':
                # 分组对比
                max_group = rule.get('max_group_size', 20)
                for i in range(0, len(type_tasks), max_group):
                    group = type_tasks[i:i + max_group]
                    group_id = hashlib.md5(f"file_group_{i}".encode()).hexdigest()[:8]
                    
                    for task in group:
                        task.batch_id = group_id
                    
                    savings = sum(t.estimated_time for t in group) * rule['savings_percentage']
                    
                    batch_groups.append(BatchGroup(
                        id=group_id,
                        tasks=group,
                        strategy='grouped_compare',
                        estimated_savings=savings,
                        execution_order=[t.id for t in group]
                    ))
            
            elif strategy == 'accumulate_push':
                # 累积推送
                min_commits = rule.get('min_commits_before_push', 3)
                
                if len(type_tasks) >= min_commits:
                    # 达到阈值，合并推送
                    batch_id = hashlib.md5(f"git_push_{datetime.now().minute}".encode()).hexdigest()[:8]
                    
                    for task in type_tasks:
                        task.batch_id = batch_id
                    
                    savings = sum(t.estimated_time for t in type_tasks) * rule['savings_percentage']
                    
                    batch_groups.append(BatchGroup(
                        id=batch_id,
                        tasks=type_tasks,
                        strategy='accumulate_push',
                        estimated_savings=savings,
                        execution_order=[t.id for t in type_tasks]
                    ))
                else:
                    # 未达到阈值，等待或单独执行
                    batch_groups.append(BatchGroup(
                        id='wait_for_more',
                        tasks=type_tasks,
                        strategy='wait',
                        estimated_savings=0.0
                    ))
            
            elif strategy == 'rate_limit':
                # 速率限制
                max_per_min = rule.get('max_requests_per_minute', 60)
                max_concurrent = rule.get('max_concurrent', 5)
                
                for i in range(0, len(type_tasks), max_per_min):
                    batch = type_tasks[i:i + max_per_min]
                    batch_id = hashlib.md5(f"rate_limit_{i}".encode()).hexdigest()[:8]
                    
                    for task in batch:
                        task.batch_id = batch_id
                    
                    batch_groups.append(BatchGroup(
                        id=batch_id,
                        tasks=batch,
                        strategy='rate_limited',
                        estimated_savings=0.0,
                        execution_order=[t.id for t in batch]
                    ))
        
        self.batch_groups = batch_groups
        return batch_groups
    
    def check_api_rate_limit(self, api_type: str = 'llm', window_minutes: int = 10) -> Dict:
        """检查 API 调用速率"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # 清理过期记录
        self.api_call_log = [t for t in self.api_call_log if t > window_start]
        
        recent_calls = len(self.api_call_log)
        calls_per_minute = recent_calls / max(window_minutes, 1)
        
        # 速率限制配置
        limits = {
            'llm': {'max_per_minute': 10, 'max_per_window': 50},
            'feishu': {'max_per_minute': 30, 'max_per_window': 200},
            'github': {'max_per_minute': 60, 'max_per_window': 1000}
        }
        
        limit = limits.get(api_type, {'max_per_minute': 60, 'max_per_window': 1000})
        
        status = 'normal'
        if calls_per_minute > limit['max_per_minute'] * 0.9:
            status = 'warning'
        if calls_per_minute > limit['max_per_minute']:
            status = 'exceeded'
        
        return {
            'api_type': api_type,
            'window_minutes': window_minutes,
            'recent_calls': recent_calls,
            'calls_per_minute': round(calls_per_minute, 2),
            'limit_per_minute': limit['max_per_minute'],
            'limit_per_window': limit['max_per_window'],
            'status': status,
            'recommendation': self._get_rate_limit_recommendation(status, api_type)
        }
    
    def _get_rate_limit_recommendation(self, status: str, api_type: str) -> str:
        """获取速率限制建议"""
        if status == 'normal':
            return "[OK] API 调用正常，可继续"
        elif status == 'warning':
            return f"[WARN] 接近 {api_type} API 限制，建议批量合并调用"
        else:
            return f"🚫 {api_type} API 限制已超出，等待 {5} 分钟后重试"
    
    def log_api_call(self, api_type: str = 'llm'):
        """记录 API 调用"""
        self.api_call_log.append(datetime.now())
    
    def get_optimization_summary(self) -> Dict:
        """获取优化总结"""
        total_tasks = sum(len(bg.tasks) for bg in self.batch_groups)
        total_savings = sum(bg.estimated_savings for bg in self.batch_groups)
        
        original_time = sum(t.estimated_time for t in self.task_queue)
        optimized_time = original_time - total_savings
        
        return {
            'original_tasks': len(self.task_queue),
            'batch_groups': len(self.batch_groups),
            'total_tasks': total_tasks,
            'original_time_minutes': round(original_time, 2),
            'optimized_time_minutes': round(optimized_time, 2),
            'time_saved_minutes': round(total_savings, 2),
            'efficiency_gain_percentage': round((total_savings / max(original_time, 1)) * 100, 2),
            'strategies_used': list(set(bg.strategy for bg in self.batch_groups))
        }
    
    def export_optimized_plan(self, output_file: str):
        """导出优化后的执行计划"""
        plan = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_optimization_summary(),
            'batch_groups': []
        }
        
        for bg in self.batch_groups:
            plan['batch_groups'].append({
                'id': bg.id,
                'strategy': bg.strategy,
                'task_count': len(bg.tasks),
                'tasks': [
                    {
                        'id': t.id,
                        'type': t.type,
                        'description': t.description,
                        'priority': t.priority,
                        'batch_id': t.batch_id
                    }
                    for t in bg.tasks
                ],
                'estimated_savings_minutes': round(bg.estimated_savings, 2),
                'execution_order': bg.execution_order
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        return plan


def load_tasks_from_file(file_path: str) -> List[Task]:
    """从文件加载任务"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tasks = []
    for item in data:
        task = Task(
            id=item.get('id', f"task_{len(tasks)}"),
            type=item.get('type', 'other'),
            description=item.get('description', ''),
            priority=item.get('priority', 'P2'),
            estimated_time=item.get('estimated_time', 1.0),
            resource_type=item.get('resource_type', 'cpu'),
            dependencies=item.get('dependencies', [])
        )
        tasks.append(task)
    
    return tasks


def main():
    parser = argparse.ArgumentParser(description='Load Balancer - ENH-005')
    parser.add_argument('--tasks', type=str, help='任务 JSON 文件')
    parser.add_argument('--optimize', type=str, choices=['batch', 'all', 'check'],
                        default='all', help='优化模式')
    parser.add_argument('--check', action='store_true', help='检查模式')
    parser.add_argument('--api', type=str, default='llm', help='API 类型')
    parser.add_argument('--window', type=str, default='10m', help='时间窗口')
    parser.add_argument('--strategy', type=str, default='auto', help='策略选择')
    parser.add_argument('--output', type=str, help='输出文件')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    
    args = parser.parse_args()
    
    balancer = LoadBalancer()
    
    # 加载任务
    if args.tasks:
        tasks = load_tasks_from_file(args.tasks)
        balancer.add_tasks(tasks)
    
    # 检查模式
    if args.check:
        window_minutes = int(args.window.replace('m', ''))
        result = balancer.check_api_rate_limit(args.api, window_minutes)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[CHART] API 速率检查 ({args.api})")
            print(f"{'='*60}")
            print(f"时间窗口：{window_minutes} 分钟")
            print(f"最近调用：{result['recent_calls']} 次")
            print(f"调用速率：{result['calls_per_minute']} 次/分钟")
            print(f"限制：{result['limit_per_minute']} 次/分钟")
            print(f"状态：{result['status'].upper()}")
            print(f"建议：{result['recommendation']}")
            print(f"{'='*60}\n")
        return
    
    # 分析模式
    if args.optimize == 'check':
        analysis = balancer.analyze_tasks()
        
        if args.json:
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[LIST] 任务队列分析")
            print(f"{'='*60}")
            print(f"总任务数：{analysis['total_tasks']}")
            print(f"预估时间：{analysis['total_estimated_time']:.1f} 分钟")
            print(f"\n按类型:")
            for t, c in analysis['by_type'].items():
                print(f"  - {t}: {c}")
            print(f"\n按优先级:")
            for p, c in analysis['by_priority'].items():
                print(f"  - {p}: {c}")
            print(f"\n优化机会:")
            for opp in analysis['optimization_opportunities']:
                print(f"  - {opp['type']}: {opp['strategy']} ({opp['potential_savings']})")
            print(f"{'='*60}\n")
        return
    
    # 优化模式
    if args.tasks or args.optimize in ['batch', 'all']:
        if not balancer.task_queue:
            # 示例任务
            balancer.add_task(Task('1', 'llm_call', 'Summarize paper 1', 'P1', 2.0))
            balancer.add_task(Task('2', 'llm_call', 'Summarize paper 2', 'P1', 2.0))
            balancer.add_task(Task('3', 'llm_call', 'Summarize paper 3', 'P1', 2.0))
            balancer.add_task(Task('4', 'file_operation', 'Update memory', 'P0', 1.0))
            balancer.add_task(Task('5', 'git_commit', 'Commit changes', 'P2', 0.5))
        
        batch_groups = balancer.optimize_batch()
        summary = balancer.get_optimization_summary()
        
        if args.output:
            plan = balancer.export_optimized_plan(args.output)
            print(f"优化计划已导出到：{args.output}")
        
        if args.json:
            output = {
                'summary': summary,
                'batch_groups': [
                    {
                        'id': bg.id,
                        'strategy': bg.strategy,
                        'task_count': len(bg.tasks),
                        'savings_minutes': round(bg.estimated_savings, 2)
                    }
                    for bg in batch_groups
                ]
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[LOAD BALANCER] Optimization Results")
            print(f"{'='*60}")
            print(f"Original tasks: {summary['original_tasks']}")
            print(f"Batch groups: {summary['batch_groups']}")
            print(f"Original time: {summary['original_time_minutes']:.1f} minutes")
            print(f"Optimized time: {summary['optimized_time_minutes']:.1f} minutes")
            print(f"Time saved: {summary['time_saved_minutes']:.1f} minutes")
            print(f"Efficiency gain: {summary['efficiency_gain_percentage']:.1f}%")
            print(f"\nStrategies used:")
            for strategy in summary['strategies_used']:
                print(f"  - {strategy}")
            print(f"\nBatch group details:")
            for bg in batch_groups:
                print(f"  [{bg.id}] {bg.strategy}: {len(bg.tasks)} tasks (saved {bg.estimated_savings:.1f} min)")
            print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
