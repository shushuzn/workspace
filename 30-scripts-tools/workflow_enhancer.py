#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Enhancer - Advanced Workflow Management
Features: Visual DAG, parallel execution, progress tracking, analytics

Usage:
    python workflow_enhancer.py --visualize daily_brief
    python workflow_enhancer.py --analyze
    python workflow_enhancer.py --optimize
    python workflow_enhancer.py --execute daily_brief
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class WorkflowStep:
    """Workflow step definition"""
    id: str
    name: str
    command: str
    dependencies: List[str]
    estimated_time: float  # seconds
    category: str  # collect/analyze/generate/cleanup
    priority: int  # 1-10


@dataclass
class WorkflowExecution:
    """Execution record"""
    workflow_id: str
    start_time: str
    end_time: str
    duration: float
    status: str  # success/failed/partial
    steps_completed: int
    steps_total: int
    parallel_speedup: float


class WorkflowEnhancer:
    """Advanced workflow management and enhancement"""
    
    def __init__(self):
        self.workflows_dir = WORKSPACE / "30-scripts-tools" / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        self.workflows = {}
        self.execution_history = []
        
        # Built-in workflows
        self._load_builtin_workflows()
    
    def _load_builtin_workflows(self):
        """Load built-in workflows"""
        
        # Daily Brief Workflow
        self.workflows['daily_brief'] = {
            'name': 'Daily Brief',
            'description': 'Generate daily briefing with data collection and analysis',
            'steps': [
                WorkflowStep('collect_arxiv', 'Collect arXiv Papers', 
                           'python 30-scripts-tools/arxiv_collector.py --daily',
                           [], 30.0, 'collect', 8),
                WorkflowStep('collect_github', 'Collect GitHub Trending',
                           'python 30-scripts-tools/github_collector.py --daily',
                           [], 20.0, 'collect', 8),
                WorkflowStep('collect_medium', 'Collect Medium Articles',
                           'python 30-scripts-tools/medium_collector.py --daily',
                           [], 25.0, 'collect', 7),
                WorkflowStep('analyze_papers', 'Analyze Papers',
                           'python 30-scripts-tools/paper_analyzer.py --batch',
                           ['collect_arxiv'], 60.0, 'analyze', 9),
                WorkflowStep('analyze_code', 'Analyze Code Quality',
                           'python 30-scripts-tools/code_reviewer.py --scan',
                           ['collect_github'], 45.0, 'analyze', 7),
                WorkflowStep('generate_brief', 'Generate Brief',
                           'python 30-scripts-tools/brief_generator.py --daily',
                           ['analyze_papers', 'analyze_code', 'collect_medium'], 30.0, 'generate', 10),
                WorkflowStep('update_dashboard', 'Update Dashboard',
                           'python 30-scripts-tools/dashboard_updater.py',
                           ['generate_brief'], 15.0, 'generate', 6),
                WorkflowStep('cleanup', 'Cleanup Temp Files',
                           'python 30-scripts-tools/cleanup.py',
                           ['update_dashboard'], 10.0, 'cleanup', 5),
            ]
        }
        
        # Security Audit Workflow
        self.workflows['security_audit'] = {
            'name': 'Security Audit',
            'description': 'Comprehensive security scanning and reporting',
            'steps': [
                WorkflowStep('scan_secrets', 'Scan for Secrets',
                           'python 30-scripts-tools/security_auditor.py --secrets',
                           [], 60.0, 'collect', 9),
                WorkflowStep('scan_code', 'Scan Code Security',
                           'python 30-scripts-tools/security_auditor.py --code',
                           [], 90.0, 'collect', 9),
                WorkflowStep('check_deps', 'Check Dependencies',
                           'python 30-scripts-tools/security_auditor.py --dependencies',
                           [], 30.0, 'collect', 7),
                WorkflowStep('generate_report', 'Generate Security Report',
                           'python 30-scripts-tools/security_auditor.py --report',
                           ['scan_secrets', 'scan_code', 'check_deps'], 20.0, 'generate', 10),
            ]
        }
        
        # Self-Iteration Workflow
        self.workflows['self_iteration'] = {
            'name': 'Self-Iteration Cycle',
            'description': 'Complete self-improvement cycle',
            'steps': [
                WorkflowStep('collect_events', 'Collect Events',
                           'python 30-scripts-tools/self_iteration.py --collect',
                           [], 10.0, 'collect', 8),
                WorkflowStep('analyze', 'Analyze Systems',
                           'python 30-scripts-tools/self_iteration.py --analyze',
                           ['collect_events'], 30.0, 'analyze', 9),
                WorkflowStep('plan', 'Create Improvement Plan',
                           'python 30-scripts-tools/self_iteration.py --plan',
                           ['analyze'], 20.0, 'analyze', 9),
                WorkflowStep('execute', 'Execute Improvements',
                           'python 30-scripts-tools/self_iteration.py --execute',
                           ['plan'], 60.0, 'execute', 10),
                WorkflowStep('validate', 'Validate Results',
                           'python 30-scripts-tools/self_iteration.py --validate',
                           ['execute'], 20.0, 'analyze', 9),
                WorkflowStep('learn', 'Extract Learnings',
                           'python 30-scripts-tools/meta_learning.py --extract',
                           ['validate'], 15.0, 'analyze', 8),
            ]
        }
        
        # Report Generation Workflow
        self.workflows['report_gen'] = {
            'name': 'Report Generation',
            'description': 'Generate comprehensive reports',
            'steps': [
                WorkflowStep('collect_metrics', 'Collect Metrics',
                           'python 30-scripts-tools/metrics_collector.py',
                           [], 20.0, 'collect', 7),
                WorkflowStep('collect_health', 'Collect Health Data',
                           'python 30-scripts-tools/health_checker.py --all',
                           [], 15.0, 'collect', 7),
                WorkflowStep('generate_md', 'Generate Markdown',
                           'python 30-scripts-tools/advanced_report_gen.py --generate daily',
                           ['collect_metrics', 'collect_health'], 30.0, 'generate', 9),
                WorkflowStep('generate_html', 'Generate HTML',
                           'python 30-scripts-tools/advanced_report_gen.py --generate daily --format html',
                           ['collect_metrics', 'collect_health'], 30.0, 'generate', 8),
                WorkflowStep('generate_json', 'Generate JSON',
                           'python 30-scripts-tools/advanced_report_gen.py --generate daily --format json',
                           ['collect_metrics', 'collect_health'], 30.0, 'generate', 7),
            ]
        }
    
    def topological_sort(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Topological sort for dependency resolution"""
        # Build adjacency list
        graph = defaultdict(list)
        in_degree = {step.id: 0 for step in steps}
        
        for step in steps:
            for dep in step.dependencies:
                graph[dep].append(step.id)
                in_degree[step.id] += 1
        
        # Kahn's algorithm
        queue = [s for s in steps if in_degree[s.id] == 0]
        result = []
        
        while queue:
            # Sort by priority (higher first)
            queue.sort(key=lambda x: -x.priority)
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current.id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    neighbor_step = next(s for s in steps if s.id == neighbor)
                    queue.append(neighbor_step)
        
        if len(result) != len(steps):
            raise ValueError("Circular dependency detected!")
        
        return result
    
    def get_parallel_groups(self, steps: List[WorkflowStep]) -> List[List[WorkflowStep]]:
        """Group steps that can run in parallel"""
        sorted_steps = self.topological_sort(steps)
        
        groups = []
        completed = set()
        remaining = set(s.id for s in sorted_steps)
        
        while remaining:
            # Find all steps whose dependencies are completed
            ready = []
            for step in sorted_steps:
                if step.id in remaining:
                    if all(dep in completed for dep in step.dependencies):
                        ready.append(step)
            
            if not ready:
                break
            
            groups.append(ready)
            for step in ready:
                completed.add(step.id)
                remaining.remove(step.id)
        
        return groups
    
    def visualize_ascii(self, workflow_name: str) -> str:
        """Generate ASCII visualization"""
        if workflow_name not in self.workflows:
            return f"Workflow '{workflow_name}' not found"
        
        workflow = self.workflows[workflow_name]
        steps = workflow['steps']
        
        sorted_steps = self.topological_sort(steps)
        parallel_groups = self.get_parallel_groups(steps)
        
        # Calculate max parallelism
        max_parallel = max(len(g) for g in parallel_groups) if parallel_groups else 1
        
        output = []
        output.append("\n" + "="*70)
        output.append(f" Workflow: {workflow['name']}")
        output.append(f" Description: {workflow['description']}")
        output.append(f" Total Steps: {len(steps)} | Max Parallel: {max_parallel}")
        output.append("="*70 + "\n")
        
        # Draw DAG
        for i, group in enumerate(parallel_groups):
            output.append(f"Stage {i+1} (Parallel: {len(group)})")
            output.append("-" * 40)
            
            for step in group:
                deps = f" ← [{', '.join(step.dependencies)}]" if step.dependencies else ""
                output.append(f"  [{step.id}]{deps}")
                output.append(f"    └─ {step.name}")
                output.append(f"    └─ Est: {step.estimated_time}s | Priority: {step.priority}")
            
            output.append("")
        
        # Calculate metrics
        total_sequential = sum(s.estimated_time for s in steps)
        
        # Parallel time (sum of max in each group)
        parallel_time = sum(
            max(s.estimated_time for s in group)
            for group in parallel_groups
        )
        
        speedup = total_sequential / parallel_time if parallel_time > 0 else 1.0
        parallelism = len(steps) / len(parallel_groups) if parallel_groups else 1.0
        
        output.append("="*70)
        output.append(" Performance Analysis")
        output.append("="*70)
        output.append(f"  Sequential Time: {total_sequential:.1f}s")
        output.append(f"  Parallel Time:   {parallel_time:.1f}s")
        output.append(f"  Speedup:         {speedup:.2f}x")
        output.append(f"  Parallelism:     {parallelism:.2f}")
        output.append(f"  Efficiency:      {(speedup/parallelism)*100:.1f}%")
        output.append("="*70 + "\n")
        
        return "\n".join(output)
    
    def analyze_workflow(self, workflow_name: str) -> Dict:
        """Analyze workflow for optimization opportunities"""
        if workflow_name not in self.workflows:
            return {'error': f'Workflow not found: {workflow_name}'}
        
        workflow = self.workflows[workflow_name]
        steps = workflow['steps']
        
        sorted_steps = self.topological_sort(steps)
        parallel_groups = self.get_parallel_groups(steps)
        
        # Calculate metrics
        total_time = sum(s.estimated_time for s in steps)
        parallel_time = sum(max(s.estimated_time for s in g) for g in parallel_groups)
        speedup = total_time / parallel_time if parallel_time > 0 else 1.0
        
        # Find bottlenecks
        bottlenecks = []
        for i, group in enumerate(parallel_groups):
            max_step = max(group, key=lambda s: s.estimated_time)
            if len(group) > 1:
                bottlenecks.append({
                    'stage': i + 1,
                    'bottleneck': max_step.id,
                    'time': max_step.estimated_time,
                    'impact': 'High' if max_step.estimated_time > 60 else 'Medium'
                })
        
        # Find long sequential chains
        chains = []
        for step in sorted_steps:
            if len(step.dependencies) == 1:
                chains.append(step.id)
        
        # Optimization recommendations
        recommendations = []
        
        if speedup < 2.0:
            recommendations.append({
                'type': 'parallelism',
                'priority': 'high',
                'suggestion': 'Increase parallelization - current speedup is low',
                'impact': f'Potential {parallel_time * 0.7:.0f}s reduction'
            })
        
        for bn in bottlenecks:
            if bn['impact'] == 'High':
                recommendations.append({
                    'type': 'bottleneck',
                    'priority': 'high',
                    'suggestion': f'Optimize step {bn["bottleneck"]} (stage {bn["stage"]})',
                    'impact': f'Reduce {bn["time"]:.0f}s bottleneck'
                })
        
        if len(chains) > len(steps) * 0.5:
            recommendations.append({
                'type': 'architecture',
                'priority': 'medium',
                'suggestion': 'Reduce sequential dependencies',
                'impact': 'Improve parallelization potential'
            })
        
        return {
            'workflow': workflow_name,
            'metrics': {
                'total_steps': len(steps),
                'stages': len(parallel_groups),
                'max_parallel': max(len(g) for g in parallel_groups),
                'sequential_time': total_time,
                'parallel_time': parallel_time,
                'speedup': round(speedup, 2),
                'parallelism': round(len(steps) / len(parallel_groups), 2) if parallel_groups else 1.0
            },
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'parallel_groups': [[s.id for s in g] for g in parallel_groups]
        }
    
    def execute_workflow(self, workflow_name: str, simulate: bool = True) -> WorkflowExecution:
        """Execute workflow with parallel execution"""
        if workflow_name not in self.workflows:
            raise ValueError(f'Workflow not found: {workflow_name}')
        
        workflow = self.workflows[workflow_name]
        steps = workflow['steps']
        
        sorted_steps = self.topological_sort(steps)
        parallel_groups = self.get_parallel_groups(steps)
        
        start_time = datetime.now()
        completed = set()
        failed = []
        
        print(f"\n{'='*60}")
        print(f" Executing: {workflow['name']}")
        print(f"{'='*60}\n")
        
        for i, group in enumerate(parallel_groups):
            print(f"Stage {i+1}/{len(parallel_groups)} (Parallel: {len(group)})")
            print("-" * 40)
            
            if simulate:
                # Simulate execution
                max_time = max(s.estimated_time for s in group)
                time.sleep(min(max_time / 10, 2.0))  # Scaled down for demo
                
                for step in group:
                    print(f"  ✅ {step.id}: {step.name}")
                    completed.add(step.id)
            else:
                # Real execution
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = {}
                    for step in group:
                        # In production, would actually execute command
                        future = executor.submit(self._execute_step, step)
                        futures[future] = step
                    
                    for future in as_completed(futures):
                        step = futures[future]
                        try:
                            success = future.result()
                            if success:
                                print(f"  ✅ {step.id}: {step.name}")
                                completed.add(step.id)
                            else:
                                print(f"  ❌ {step.id}: {step.name} - FAILED")
                                failed.append(step.id)
                        except Exception as e:
                            print(f"  ❌ {step.id}: {step.name} - {e}")
                            failed.append(step.id)
            
            print()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate speedup
        sequential_time = sum(s.estimated_time for s in steps)
        speedup = sequential_time / duration if duration > 0 else 1.0
        
        execution = WorkflowExecution(
            workflow_id=workflow_name,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration=duration,
            status='success' if not failed else 'partial' if completed else 'failed',
            steps_completed=len(completed),
            steps_total=len(steps),
            parallel_speedup=round(speedup, 2)
        )
        
        self.execution_history.append(execution)
        
        # Print summary
        print(f"{'='*60}")
        print(" Execution Summary")
        print(f"{'='*60}")
        print(f"  Status: {execution.status.upper()}")
        print(f"  Duration: {duration:.1f}s")
        print(f"  Steps: {execution.steps_completed}/{execution.steps_total}")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"{'='*60}\n")
        
        return execution
    
    def _execute_step(self, step: WorkflowStep) -> bool:
        """Execute single step"""
        import subprocess
        
        try:
            result = subprocess.run(
                step.command.split(),
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                timeout=step.estimated_time * 2
            )
            return result.returncode == 0
        except:
            return False
    
    def list_workflows(self) -> List[Dict]:
        """List all workflows"""
        return [
            {
                'name': name,
                'description': wf['description'],
                'steps': len(wf['steps'])
            }
            for name, wf in self.workflows.items()
        ]
    
    def save_workflow(self, workflow_name: str):
        """Save workflow to file"""
        if workflow_name not in self.workflows:
            return
        
        workflow = self.workflows[workflow_name]
        filepath = self.workflows_dir / f"{workflow_name}.json"
        
        data = {
            'name': workflow['name'],
            'description': workflow['description'],
            'steps': [asdict(s) for s in workflow['steps']]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Workflow saved: {filepath}")
    
    def get_execution_history(self) -> List[Dict]:
        """Get execution history"""
        return [asdict(e) for e in self.execution_history[-20:]]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Workflow Enhancer')
    parser.add_argument('--list', action='store_true', help='List workflows')
    parser.add_argument('--visualize', type=str, help='Visualize workflow (ASCII)')
    parser.add_argument('--analyze', type=str, help='Analyze workflow')
    parser.add_argument('--execute', type=str, help='Execute workflow')
    parser.add_argument('--simulate', action='store_true', help='Simulate execution')
    parser.add_argument('--save', type=str, help='Save workflow to file')
    parser.add_argument('--history', action='store_true', help='Show execution history')
    args = parser.parse_args()
    
    enhancer = WorkflowEnhancer()
    
    if args.list:
        workflows = enhancer.list_workflows()
        print("\nAvailable Workflows:\n")
        for wf in workflows:
            print(f"  • {wf['name']}")
            print(f"    {wf['description']}")
            print(f"    Steps: {wf['steps']}\n")
    
    elif args.visualize:
        output = enhancer.visualize_ascii(args.visualize)
        print(output)
    
    elif args.analyze:
        analysis = enhancer.analyze_workflow(args.analyze)
        print(json.dumps(analysis, indent=2))
    
    elif args.execute:
        execution = enhancer.execute_workflow(args.execute, simulate=args.simulate)
        print(f"\nExecution complete: {execution.status}")
    
    elif args.save:
        enhancer.save_workflow(args.save)
    
    elif args.history:
        history = enhancer.get_execution_history()
        print(json.dumps(history, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
