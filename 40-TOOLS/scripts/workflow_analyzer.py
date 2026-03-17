#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Analyzer - Enhanced
Analyze workflow performance and provide optimization suggestions
Features: bottleneck detection, parallelization suggestions, metrics analysis

Usage:
    python workflow_analyzer.py --analyze daily_brief
    python workflow_analyzer.py --benchmark
    python workflow_analyzer.py --optimize workflow.json
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Workspace root
WORKSPACE = Path(__file__).parent.parent
WORKFLOWS_DIR = WORKSPACE / "40-workflows"
TOOLS_DIR = WORKSPACE / "30-scripts-tools"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class WorkflowAnalyzer:
    """Analyze and optimize workflows"""
    
    def __init__(self):
        self.workflows = self._load_workflows()
        self.metrics = self._load_metrics()
    
    def _load_workflows(self) -> Dict:
        """Load workflows"""
        workflows = {}
        
        if WORKFLOWS_DIR.exists():
            for wf_file in WORKFLOWS_DIR.glob("*.json"):
                try:
                    with open(wf_file, 'r', encoding='utf-8') as f:
                        wf = json.load(f)
                        workflows[wf.get('id', wf_file.stem)] = wf
                except:
                    pass
        
        return workflows
    
    def _load_metrics(self) -> Dict:
        """Load execution metrics"""
        metrics_file = WORKSPACE / "20-data-reports" / "workflow_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {'total_executions': 0, 'successful': 0, 'failed': 0, 'avg_duration': 0}
    
    def analyze(self, workflow_id: str) -> Dict:
        """Analyze workflow structure and performance"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + f"  Workflow Analysis: {workflow_id}".ljust(59) + "║")
        print("╚" + "═" * 58 + "╝")
        
        if workflow_id not in self.workflows:
            print(f"[ERROR] Workflow not found: {workflow_id}")
            return None
        
        workflow = self.workflows[workflow_id]
        steps = workflow.get('steps', [])
        
        print(f"\n📋 {workflow.get('name', workflow_id)}")
        print(f"   Steps: {len(steps)}")
        print(f"   Version: {workflow.get('version', '1.0')}")
        
        # Analyze structure
        analysis = {
            'workflow_id': workflow_id,
            'name': workflow.get('name', workflow_id),
            'total_steps': len(steps),
            'parallel_steps': sum(1 for s in steps if s.get('parallel', False)),
            'sequential_steps': sum(1 for s in steps if not s.get('parallel', False)),
            'steps_with_deps': sum(1 for s in steps if 'depends_on' in s),
            'steps_with_conditions': sum(1 for s in steps if 'condition' in s),
            'estimated_duration': 0,
            'bottlenecks': [],
            'optimizations': [],
            'parallelization_potential': 0
        }
        
        # Analyze dependencies
        print("\n📊 Dependency Analysis:")
        dep_graph = {}
        for step in steps:
            step_id = step.get('id', 'unknown')
            deps = step.get('depends_on', [])
            dep_graph[step_id] = deps
            
            if deps:
                print(f"   {step_id} ← {', '.join(deps)}")
            else:
                print(f"   {step_id} (root)")
        
        # Detect bottlenecks
        print("\n🔍 Bottleneck Detection:")
        
        # Find steps with many dependents
        dependent_count = {}
        for step_id, deps in dep_graph.items():
            for dep in deps:
                dependent_count[dep] = dependent_count.get(dep, 0) + 1
        
        for step_id, count in dependent_count.items():
            if count >= 3:
                print(f"   ⚠️  Bottleneck: {step_id} ({count} dependents)")
                analysis['bottlenecks'].append({
                    'step': step_id,
                    'type': 'high_dependency',
                    'impact': f'{count} steps waiting',
                    'severity': 'high' if count >= 4 else 'medium'
                })
        
        # Find long sequential chains
        chain_length = self._find_longest_chain(dep_graph)
        if chain_length >= 4:
            print(f"   ⚠️  Long chain: {chain_length} sequential steps")
            analysis['bottlenecks'].append({
                'step': 'chain',
                'type': 'long_sequential_chain',
                'impact': f'{chain_length} steps in sequence',
                'severity': 'high' if chain_length >= 6 else 'medium'
            })
        
        if not analysis['bottlenecks']:
            print("   ✅ No major bottlenecks detected")
        
        # Calculate parallelization potential
        total_steps = len(steps)
        root_steps = sum(1 for deps in dep_graph.values() if not deps)
        max_parallel = max(dependent_count.values()) if dependent_count else 0
        
        analysis['parallelization_potential'] = round(
            (1 - (chain_length / total_steps)) * 100, 2
        ) if total_steps > 0 else 0
        
        print(f"\n⚡ Parallelization Potential: {analysis['parallelization_potential']}%")
        
        # Generate optimization suggestions
        print("\n💡 Optimization Suggestions:")
        
        if analysis['parallelization_potential'] > 50:
            print("   ✅ Good parallelization")
        else:
            print("   💡 Consider parallelizing independent steps")
            analysis['optimizations'].append({
                'type': 'parallelization',
                'description': 'Mark independent steps as parallel',
                'impact': 'high',
                'effort': 'low'
            })
        
        if analysis['bottlenecks']:
            print("   💡 Address bottlenecks to improve throughput")
            analysis['optimizations'].append({
                'type': 'bottleneck_resolution',
                'description': 'Split bottleneck steps or add caching',
                'impact': 'high',
                'effort': 'medium'
            })
        
        # Check for missing timeouts
        steps_without_timeout = sum(1 for s in steps if 'timeout' not in s)
        if steps_without_timeout > 0:
            print(f"   ⚠️  {steps_without_timeout} steps without timeout")
            analysis['optimizations'].append({
                'type': 'timeout_configuration',
                'description': f'Add timeout to {steps_without_timeout} steps',
                'impact': 'medium',
                'effort': 'low'
            })
        
        # Estimate duration
        avg_step_duration = 30  # seconds
        sequential_duration = chain_length * avg_step_duration
        parallel_duration = (len(steps) - chain_length) * avg_step_duration / 4  # 4 workers
        
        analysis['estimated_duration'] = sequential_duration + parallel_duration
        
        print(f"\n⏱️  Estimated Duration: {analysis['estimated_duration']:.0f}s")
        print(f"   Sequential: {sequential_duration:.0f}s")
        print(f"   Parallel: {parallel_duration:.0f}s")
        
        # Print summary
        print("\n" + "=" * 60)
        print("Analysis Summary")
        print("=" * 60)
        print(f"Total Steps: {analysis['total_steps']}")
        print(f"Parallel Steps: {analysis['parallel_steps']}")
        print(f"Sequential Steps: {analysis['sequential_steps']}")
        print(f"Steps with Dependencies: {analysis['steps_with_deps']}")
        print(f"Steps with Conditions: {analysis['steps_with_conditions']}")
        print(f"Bottlenecks: {len(analysis['bottlenecks'])}")
        print(f"Optimizations: {len(analysis['optimizations'])}")
        print(f"Parallelization Potential: {analysis['parallelization_potential']}%")
        print("=" * 60)
        
        return analysis
    
    def _find_longest_chain(self, dep_graph: Dict) -> int:
        """Find longest dependency chain"""
        def dfs(node, visited):
            if node in visited:
                return 0
            visited.add(node)
            
            max_depth = 0
            for next_node, deps in dep_graph.items():
                if node in deps:
                    max_depth = max(max_depth, dfs(next_node, visited))
            
            return max_depth + 1
        
        max_chain = 0
        for node in dep_graph:
            if not dep_graph[node]:  # Root nodes
                max_chain = max(max_chain, dfs(node, set()))
        
        return max_chain if max_chain > 0 else 1
    
    def benchmark(self) -> Dict:
        """Run workflow benchmarks"""
        print("\n" + "=" * 60)
        print("Workflow Benchmarks")
        print("=" * 60)
        
        benchmarks = []
        
        for workflow_id in list(self.workflows.keys())[:3]:  # First 3 workflows
            print(f"\n🏃 Benchmarking: {workflow_id}...")
            
            start_time = time.time()
            
            # Simulate execution (don't actually run)
            workflow = self.workflows[workflow_id]
            steps = workflow.get('steps', [])
            
            # Estimate based on step count
            estimated_time = len(steps) * 2  # 2 seconds per step
            
            duration = time.time() - start_time
            
            benchmarks.append({
                'workflow_id': workflow_id,
                'steps': len(steps),
                'estimated_duration': estimated_time,
                'actual_duration': duration
            })
            
            print(f"   Steps: {len(steps)}")
            print(f"   Estimated: {estimated_time}s")
        
        print("\n" + "=" * 60)
        print("Benchmark Results")
        print("=" * 60)
        
        for bench in benchmarks:
            print(f"{bench['workflow_id']}: {bench['steps']} steps, ~{bench['estimated_duration']}s")
        
        print("=" * 60)
        
        return {'benchmarks': benchmarks}
    
    def optimize(self, workflow_file: str) -> str:
        """Generate optimized workflow"""
        print(f"\nOptimizing: {workflow_file}")
        
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load: {e}")
            return ""
        
        # Apply optimizations
        optimized = workflow.copy()
        steps = optimized.get('steps', [])
        
        optimization_count = 0
        
        # Add timeouts to steps without
        for step in steps:
            if 'timeout' not in step:
                step['timeout'] = 300
                optimization_count += 1
        
        # Mark independent steps as parallel
        step_ids = {s['id'] for s in steps}
        for step in steps:
            if 'depends_on' not in step and 'parallel' not in step:
                step['parallel'] = True
                optimization_count += 1
        
        # Add metadata
        optimized['optimized'] = True
        optimized['optimization_date'] = datetime.now().isoformat()
        optimized['optimizations_applied'] = optimization_count
        
        # Save optimized version
        optimized_file = Path(workflow_file).parent / f"{Path(workflow_file).stem}_optimized.json"
        
        with open(optimized_file, 'w', encoding='utf-8') as f:
            json.dump(optimized, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Optimized workflow saved: {optimized_file}")
        print(f"   Optimizations applied: {optimization_count}")
        
        return str(optimized_file)


def main():
    parser = argparse.ArgumentParser(description='Workflow Analyzer')
    parser.add_argument('--analyze', type=str, metavar='WORKFLOW', help='Analyze workflow')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmarks')
    parser.add_argument('--optimize', type=str, metavar='FILE', help='Optimize workflow')
    args = parser.parse_args()
    
    analyzer = WorkflowAnalyzer()
    
    if args.analyze:
        analyzer.analyze(args.analyze)
    
    if args.benchmark:
        analyzer.benchmark()
    
    if args.optimize:
        analyzer.optimize(args.optimize)
    
    if not any([args.analyze, args.benchmark, args.optimize]):
        parser.print_help()


if __name__ == "__main__":
    main()
