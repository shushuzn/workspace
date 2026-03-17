#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow Optimizer AI - AI-powered workflow optimization

Features:
- AI-based optimization suggestions
- Performance analysis
- Bottleneck detection
- Parallel execution opportunities
- Resource optimization
- Cost estimation
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
WORKFLOWS_DIR = WORKSPACE / 'workflows'
TOOLS_DIR = WORKSPACE / '30-scripts-tools'

class PerformanceAnalyzer:
    """Analyze workflow performance"""
    
    def __init__(self):
        # Estimated execution times for common tools (seconds)
        self.tool_times = {
            'data_collector.py': 30,
            'data_transformer.py': 60,
            'analyzer.py': 120,
            'report_generator.py': 30,
            'auto_deployer.py': 180,
            'test_runner.py': 300,
            'backup_tool.py': 600,
            'compressor.py': 120,
            'feishu_notification.py': 5,
            'metrics_collector.py': 10,
            'anomaly_detector.py': 30,
        }
    
    def analyze(self, workflow: Dict) -> Dict:
        """Analyze performance"""
        steps = workflow.get('steps', [])
        
        if not steps:
            return {'status': 'no_steps'}
        
        # Estimate execution time
        total_time = 0
        step_times = []
        
        for step in steps:
            tool_name = step.get('tool', '')
            estimated_time = self.tool_times.get(tool_name, 60)  # Default 60s
            
            step_times.append({
                'step': step.get('name', 'unknown'),
                'tool': tool_name,
                'estimated_time': estimated_time,
            })
            
            total_time += estimated_time
        
        # Identify bottlenecks
        bottlenecks = [
            st for st in step_times
            if st['estimated_time'] > total_time * 0.3  # >30% of total
        ]
        
        # Parallel opportunities
        parallel_opportunities = self._find_parallel_opportunities(steps)
        
        return {
            'status': 'success',
            'total_estimated_time': total_time,
            'total_estimated_time_formatted': self._format_time(total_time),
            'step_times': step_times,
            'bottlenecks': bottlenecks,
            'parallel_opportunities': parallel_opportunities,
            'potential_speedup': self._calculate_speedup(total_time, parallel_opportunities),
        }
    
    def _find_parallel_opportunities(self, steps: List[Dict]) -> List[Dict]:
        """Find steps that can run in parallel"""
        # Simple heuristic: steps without dependencies can run in parallel
        opportunities = []
        
        # Group steps by estimated time
        long_steps = [
            s for s in steps
            if self.tool_times.get(s.get('tool', ''), 60) > 60
        ]
        
        if len(long_steps) >= 2:
            opportunities.append({
                'type': 'parallel_long_steps',
                'steps': [s.get('name') for s in long_steps],
                'potential_savings': sum(
                    self.tool_times.get(s.get('tool', ''), 60)
                    for s in long_steps[1:]
                ),
                'description': 'Long-running steps could run in parallel',
            })
        
        return opportunities
    
    def _calculate_speedup(self, sequential_time: int, opportunities: List[Dict]) -> Dict:
        """Calculate potential speedup"""
        if not opportunities:
            return {'speedup': 1.0, 'time_saved': 0}
        
        total_savings = sum(opp.get('potential_savings', 0) for opp in opportunities)
        parallel_time = sequential_time - total_savings
        
        speedup = sequential_time / max(parallel_time, 1)
        
        return {
            'speedup': round(speedup, 2),
            'time_saved': total_savings,
            'time_saved_formatted': self._format_time(total_savings),
            'parallel_time': parallel_time,
            'parallel_time_formatted': self._format_time(parallel_time),
        }
    
    def _format_time(self, seconds: int) -> str:
        """Format time in human-readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"


class ResourceOptimizer:
    """Optimize resource usage"""
    
    def optimize(self, workflow: Dict) -> List[Dict]:
        """Generate optimization suggestions"""
        suggestions = []
        
        steps = workflow.get('steps', [])
        
        # Suggestion 1: Caching opportunities
        caching_suggestions = self._find_caching_opportunities(steps)
        suggestions.extend(caching_suggestions)
        
        # Suggestion 2: Resource pooling
        pooling_suggestions = self._find_pooling_opportunities(steps)
        suggestions.extend(pooling_suggestions)
        
        # Suggestion 3: Lazy evaluation
        lazy_suggestions = self._find_lazy_evaluation_opportunities(steps)
        suggestions.extend(lazy_suggestions)
        
        # Suggestion 4: Batch processing
        batch_suggestions = self._find_batch_opportunities(steps)
        suggestions.extend(batch_suggestions)
        
        return suggestions
    
    def _find_caching_opportunities(self, steps: List[Dict]) -> List[Dict]:
        """Find caching opportunities"""
        suggestions = []
        
        # Look for repeated data access
        data_tools = ['data_collector.py', 'data_loader.py', 'data_fetcher.py']
        data_steps = [s for s in steps if s.get('tool') in data_tools]
        
        if len(data_steps) > 1:
            suggestions.append({
                'type': 'caching',
                'priority': 'high',
                'title': 'Add data caching',
                'description': f'{len(data_steps)} steps access data - consider caching',
                'impact': 'Reduce data access time by 50-80%',
                'effort': 'medium',
                'steps_affected': [s.get('name') for s in data_steps],
            })
        
        return suggestions
    
    def _find_pooling_opportunities(self, steps: List[Dict]) -> List[Dict]:
        """Find resource pooling opportunities"""
        suggestions = []
        
        # Look for repeated tool usage
        tool_counts = defaultdict(list)
        for step in steps:
            tool = step.get('tool', '')
            tool_counts[tool].append(step.get('name'))
        
        for tool, step_names in tool_counts.items():
            if len(step_names) > 1:
                suggestions.append({
                    'type': 'pooling',
                    'priority': 'medium',
                    'title': f'Use connection pooling for {tool}',
                    'description': f'Tool used {len(step_names)} times - pool resources',
                    'impact': 'Reduce initialization overhead',
                    'effort': 'low',
                    'steps_affected': step_names,
                })
        
        return suggestions
    
    def _find_lazy_evaluation_opportunities(self, steps: List[Dict]) -> List[Dict]:
        """Find lazy evaluation opportunities"""
        suggestions = []
        
        # Look for expensive operations that might not always be needed
        expensive_tools = ['analyzer.py', 'ml_model.py', 'complex_transform.py']
        
        for step in steps:
            if step.get('tool') in expensive_tools:
                suggestions.append({
                    'type': 'lazy_evaluation',
                    'priority': 'medium',
                    'title': f'Consider lazy evaluation for {step.get("name")}',
                    'description': 'Expensive operation - only run if needed',
                    'impact': 'Skip unnecessary computation',
                    'effort': 'medium',
                    'steps_affected': [step.get('name')],
                })
        
        return suggestions
    
    def _find_batch_opportunities(self, steps: List[Dict]) -> List[Dict]:
        """Find batch processing opportunities"""
        suggestions = []
        
        # Look for repetitive operations on different data
        # (Simplified heuristic)
        similar_steps = defaultdict(list)
        
        for step in steps:
            tool = step.get('tool', '')
            similar_steps[tool].append(step)
        
        for tool, tool_steps in similar_steps.items():
            if len(tool_steps) > 2:
                suggestions.append({
                    'type': 'batch_processing',
                    'priority': 'high',
                    'title': f'Batch {tool} operations',
                    'description': f'{len(tool_steps)} similar steps - consider batching',
                    'impact': 'Reduce overhead by 60-90%',
                    'effort': 'high',
                    'steps_affected': [s.get('name') for s in tool_steps],
                })
        
        return suggestions


class CostEstimator:
    """Estimate workflow execution cost"""
    
    def __init__(self):
        # Cost per minute for different resources (simplified)
        self.costs = {
            'cpu_minute': 0.001,  # $0.001 per CPU minute
            'memory_gb_minute': 0.0005,  # $0.0005 per GB-minute
            'api_call': 0.01,  # $0.01 per API call
            'storage_gb': 0.02,  # $0.02 per GB storage
        }
    
    def estimate(self, workflow: Dict) -> Dict:
        """Estimate execution cost"""
        steps = workflow.get('steps', [])
        
        total_cpu_time = 0
        total_memory = 0
        api_calls = 0
        
        for step in steps:
            tool = step.get('tool', '')
            
            # Estimate resource usage
            cpu_time = self._estimate_cpu_time(tool)
            memory = self._estimate_memory(tool)
            apis = self._estimate_api_calls(tool)
            
            total_cpu_time += cpu_time
            total_memory += memory
            api_calls += apis
        
        # Calculate cost
        cpu_cost = (total_cpu_time / 60) * self.costs['cpu_minute']
        memory_cost = (total_memory / 1024) * self.costs['memory_gb_minute']
        api_cost = api_calls * self.costs['api_call']
        
        total_cost = cpu_cost + memory_cost + api_cost
        
        return {
            'cpu_time_minutes': round(total_cpu_time / 60, 2),
            'memory_mb': total_memory,
            'api_calls': api_calls,
            'cost_breakdown': {
                'cpu': round(cpu_cost, 4),
                'memory': round(memory_cost, 4),
                'api': round(api_cost, 4),
            },
            'total_cost': round(total_cost, 4),
            'cost_per_run': round(total_cost, 4),
            'monthly_cost_estimate': round(total_cost * 30 * 24, 2),  # Assuming hourly runs
        }
    
    def _estimate_cpu_time(self, tool: str) -> int:
        """Estimate CPU time in seconds"""
        estimates = {
            'data_collector.py': 30,
            'analyzer.py': 120,
            'ml_model.py': 300,
            'report_generator.py': 30,
            'auto_deployer.py': 60,
        }
        return estimates.get(tool, 60)
    
    def _estimate_memory(self, tool: str) -> int:
        """Estimate memory usage in MB"""
        estimates = {
            'data_collector.py': 256,
            'analyzer.py': 512,
            'ml_model.py': 2048,
            'report_generator.py': 128,
        }
        return estimates.get(tool, 256)
    
    def _estimate_api_calls(self, tool: str) -> int:
        """Estimate API calls"""
        api_tools = ['data_collector.py', 'feishu_notification.py', 'api_caller.py']
        return 1 if tool in api_tools else 0


class AIOptimizer:
    """
    AI-powered workflow optimizer
    
    Features:
    - AI-based optimization suggestions
    - Performance analysis
    - Bottleneck detection
    - Parallel execution opportunities
    - Resource optimization
    - Cost estimation
    """
    
    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
        self.resource_optimizer = ResourceOptimizer()
        self.cost_estimator = CostEstimator()
    
    def optimize(self, workflow: Dict) -> Dict:
        """Run full optimization analysis"""
        # Performance analysis
        performance = self.performance_analyzer.analyze(workflow)
        
        # Resource optimization
        resource_suggestions = self.resource_optimizer.optimize(workflow)
        
        # Cost estimation
        cost = self.cost_estimator.estimate(workflow)
        
        # Generate AI suggestions
        ai_suggestions = self._generate_ai_suggestions(
            workflow, performance, resource_suggestions, cost
        )
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            workflow, performance, resource_suggestions
        )
        
        return {
            'status': 'success',
            'performance': performance,
            'resource_suggestions': resource_suggestions,
            'cost': cost,
            'ai_suggestions': ai_suggestions,
            'optimization_score': optimization_score,
            'timestamp': datetime.now().isoformat(),
        }
    
    def _generate_ai_suggestions(self, workflow: Dict, performance: Dict,
                                  resource_suggestions: List[Dict], cost: Dict) -> List[Dict]:
        """Generate AI-powered suggestions"""
        suggestions = []
        
        # Suggestion based on performance
        if performance.get('bottlenecks'):
            for bottleneck in performance['bottlenecks']:
                suggestions.append({
                    'type': 'performance',
                    'priority': 'high',
                    'title': f'Optimize bottleneck: {bottleneck["step"]}',
                    'description': f'This step takes {bottleneck["estimated_time"]}s ({bottleneck["estimated_time"]/performance["total_estimated_time"]*100:.1f}% of total)',
                    'suggestions': [
                        'Consider parallel execution',
                        'Optimize algorithm',
                        'Add caching',
                        'Use more efficient tool',
                    ],
                    'impact': 'high',
                    'effort': 'medium',
                })
        
        # Suggestion based on parallel opportunities
        if performance.get('parallel_opportunities'):
            for opp in performance['parallel_opportunities']:
                suggestions.append({
                    'type': 'parallelization',
                    'priority': 'high',
                    'title': opp['description'],
                    'description': f'Potential speedup: {performance["potential_speedup"]["speedup"]}x',
                    'impact': 'high',
                    'effort': 'medium',
                })
        
        # Suggestion based on cost
        if cost['total_cost'] > 0.1:  # More than $0.1 per run
            suggestions.append({
                'type': 'cost_optimization',
                'priority': 'medium',
                'title': 'Reduce execution cost',
                'description': f'Current cost: ${cost["total_cost"]:.4f}/run, ${cost["monthly_cost_estimate"]:.2f}/month',
                'suggestions': [
                    'Optimize resource usage',
                    'Reduce API calls',
                    'Use caching',
                    'Batch operations',
                ],
                'impact': 'medium',
                'effort': 'medium',
            })
        
        # Add resource optimization suggestions
        suggestions.extend([
            {
                'type': suggestion['type'],
                'priority': suggestion['priority'],
                'title': suggestion['title'],
                'description': suggestion['description'],
                'impact': suggestion['impact'],
                'effort': suggestion['effort'],
            }
            for suggestion in resource_suggestions[:3]  # Top 3
        ])
        
        return suggestions
    
    def _calculate_optimization_score(self, workflow: Dict, performance: Dict,
                                      suggestions: List[Dict]) -> float:
        """Calculate optimization score (0-1)"""
        score = 1.0
        
        # Penalize for bottlenecks
        if performance.get('bottlenecks'):
            score -= len(performance['bottlenecks']) * 0.1
        
        # Penalize for missing parallel opportunities
        if performance.get('parallel_opportunities'):
            score -= len(performance['parallel_opportunities']) * 0.05
        
        # Penalize for high-cost operations
        # (Simplified)
        
        # Bonus for good practices
        steps = workflow.get('steps', [])
        if len(steps) <= 5:
            score += 0.1  # Simple workflows are better
        
        return max(0.0, min(1.0, score))
    
    def print_report(self, result: Dict):
        """Print optimization report"""
        print("\n" + "=" * 60)
        print("🤖 AI WORKFLOW OPTIMIZATION REPORT")
        print("=" * 60)
        
        print(f"\n📊 OPTIMIZATION SCORE: {result['optimization_score']:.1%}")
        
        # Performance
        perf = result['performance']
        if perf['status'] == 'success':
            print(f"\n⏱️  PERFORMANCE:")
            print(f"   Total time: {perf['total_estimated_time_formatted']}")
            if perf['bottlenecks']:
                print(f"   Bottlenecks: {len(perf['bottlenecks'])}")
                for b in perf['bottlenecks'][:2]:
                    print(f"     - {b['step']}: {b['estimated_time']}s")
            if perf['parallel_opportunities']:
                print(f"   Parallel opportunities: {len(perf['parallel_opportunities'])}")
                print(f"   Potential speedup: {perf['potential_speedup']['speedup']}x")
        
        # Cost
        cost = result['cost']
        print(f"\n💰 COST ESTIMATE:")
        print(f"   Per run: ${cost['total_cost']:.4f}")
        print(f"   Monthly (hourly): ${cost['monthly_cost_estimate']:.2f}")
        
        # AI Suggestions
        print(f"\n💡 AI SUGGESTIONS ({len(result['ai_suggestions'])}):")
        for i, sug in enumerate(result['ai_suggestions'][:5], 1):
            print(f"\n   {i}. [{sug['priority'].upper()}] {sug['title']}")
            print(f"      {sug['description']}")
            if 'suggestions' in sug:
                print(f"      Actions: {', '.join(sug['suggestions'][:3])}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Workflow Optimizer AI")
    parser.add_argument('--optimize', type=str, help='Optimize workflow file')
    parser.add_argument('--all', action='store_true', help='Optimize all workflows')
    parser.add_argument('--report', action='store_true', help='Generate report')
    args = parser.parse_args()
    
    optimizer = AIOptimizer()
    
    if args.optimize:
        workflow_path = Path(args.optimize)
        
        if not workflow_path.exists():
            workflow_path = WORKFLOWS_DIR / args.optimize
            if not workflow_path.exists():
                workflow_path = WORKFLOWS_DIR / f"{args.optimize}.json"
        
        if not workflow_path.exists():
            print(f"❌ Workflow not found: {args.optimize}")
            return
        
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        
        result = optimizer.optimize(workflow)
        optimizer.print_report(result)
    
    elif args.all:
        workflows = list(WORKFLOWS_DIR.glob('*.json'))
        
        if not workflows:
            print("📭 No workflows found")
            return
        
        print(f"\n🤖 Optimizing {len(workflows)} workflows...\n")
        
        for workflow_path in workflows:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            
            result = optimizer.optimize(workflow)
            score = result['optimization_score']
            status = "✅" if score > 0.7 else "⚠️" if score > 0.4 else "❌"
            print(f"{status} {workflow_path.name}: {score:.1%} optimization score")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
