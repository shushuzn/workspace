#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Engine v2.0 - Enhanced
Advanced workflow orchestration with visualization
Features: DAG execution, visual progress, templates, error recovery, metrics

Usage:
    python workflow_engine_v2.py --run daily_brief
    python workflow_engine_v2.py --visualize data_collection
    python workflow_engine_v2.py --list
    python workflow_engine_v2.py --template
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
import hashlib

# Workspace root
WORKSPACE = Path(__file__).parent.parent
WORKFLOWS_DIR = WORKSPACE / "40-workflows"
TOOLS_DIR = WORKSPACE / "30-scripts-tools"
TEMPLATES_DIR = WORKSPACE / "30-scripts-tools" / "workflow_templates"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class WorkflowEngineV2:
    """Enhanced workflow engine with DAG support"""
    
    def __init__(self):
        self.workflows = self._load_workflows()
        self.templates = self._load_templates()
        self.execution_history = []
        self.metrics = {
            'total_executions': 0,
            'successful': 0,
            'failed': 0,
            'avg_duration': 0
        }
        self._load_metrics()
    
    def _load_workflows(self) -> Dict:
        """Load workflows from directory"""
        workflows = {}
        
        # Load from files
        if WORKFLOWS_DIR.exists():
            for wf_file in WORKFLOWS_DIR.glob("*.json"):
                try:
                    with open(wf_file, 'r', encoding='utf-8') as f:
                        wf = json.load(f)
                        workflows[wf.get('id', wf_file.stem)] = wf
                except Exception as e:
                    print(f"[WARN] Failed to load {wf_file}: {e}")
        
        # Add built-in workflows
        workflows.update(self._get_builtin_workflows())
        
        return workflows
    
    def _get_builtin_workflows(self) -> Dict:
        """Get built-in workflows"""
        return {
            'daily_brief': {
                'id': 'daily_brief',
                'name': 'Daily Research Brief',
                'description': 'Generate daily research brief from all sources',
                'version': '2.0',
                'steps': [
                    {'id': 'collect_arxiv', 'tool': 'arxiv_collector.py', 'parallel': False},
                    {'id': 'collect_github', 'tool': 'github_collector.py', 'parallel': False},
                    {'id': 'collect_medium', 'tool': 'medium_collector.py', 'parallel': False},
                    {'id': 'review_code', 'tool': 'code_reviewer.py', 'depends_on': ['collect_github']},
                    {'id': 'review_papers', 'tool': 'paper_reviewer.py', 'depends_on': ['collect_arxiv']},
                    {'id': 'update_kg', 'tool': 'knowledge_graph_builder.py', 'depends_on': ['review_code', 'review_papers']},
                    {'id': 'generate_brief', 'tool': 'daily_brief_generator.py', 'depends_on': ['update_kg']}
                ]
            },
            'data_collection': {
                'id': 'data_collection',
                'name': 'Multi-Source Data Collection',
                'description': 'Collect data from all sources in parallel',
                'version': '2.0',
                'steps': [
                    {'id': 'arxiv', 'tool': 'arxiv_collector.py', 'parallel': True},
                    {'id': 'github', 'tool': 'github_collector.py', 'parallel': True},
                    {'id': 'medium', 'tool': 'medium_collector.py', 'parallel': True},
                    {'id': 'merge', 'tool': 'data_merger.py', 'depends_on': ['arxiv', 'github', 'medium']}
                ]
            },
            'quality_check': {
                'id': 'quality_check',
                'name': 'Quality Assurance',
                'description': 'Run all quality checks',
                'version': '2.0',
                'steps': [
                    {'id': 'code_review', 'tool': 'code_reviewer.py', 'parallel': False},
                    {'id': 'paper_review', 'tool': 'paper_reviewer.py', 'parallel': False},
                    {'id': 'health_check', 'tool': 'system_health_checker.py', 'parallel': False},
                    {'id': 'config_validate', 'tool': 'config_center.py', 'args': ['--validate'], 'parallel': False}
                ]
            },
            'system_maintenance': {
                'id': 'system_maintenance',
                'name': 'System Maintenance',
                'description': 'Cache cleanup + self-healing scan',
                'version': '2.0',
                'steps': [
                    {'id': 'cache_clean', 'tool': 'cache_manager.py', 'args': ['--clean'], 'parallel': False},
                    {'id': 'self_heal', 'tool': 'self_healing.py', 'args': ['--scan'], 'parallel': False},
                    {'id': 'health_check', 'tool': 'system_health_checker.py', 'parallel': False},
                    {'id': 'report', 'tool': 'smart_report_generator.py', 'args': ['--daily'], 'depends_on': ['cache_clean', 'self_heal', 'health_check']}
                ]
            }
        }
    
    def _load_templates(self) -> Dict:
        """Load workflow templates"""
        templates = {}
        
        if TEMPLATES_DIR.exists():
            for tpl_file in TEMPLATES_DIR.glob("*.json"):
                try:
                    with open(tpl_file, 'r', encoding='utf-8') as f:
                        tpl = json.load(f)
                        templates[tpl.get('id', tpl_file.stem)] = tpl
                except:
                    pass
        
        # Built-in templates
        templates.update({
            'sequential': {
                'id': 'sequential',
                'name': 'Sequential Workflow',
                'description': 'Execute steps one by one',
                'steps': [
                    {'id': 'step1', 'tool': '', 'parallel': False},
                    {'id': 'step2', 'tool': '', 'depends_on': ['step1']}
                ]
            },
            'parallel': {
                'id': 'parallel',
                'name': 'Parallel Workflow',
                'description': 'Execute steps in parallel',
                'steps': [
                    {'id': 'branch1', 'tool': '', 'parallel': True},
                    {'id': 'branch2', 'tool': '', 'parallel': True},
                    {'id': 'merge', 'tool': '', 'depends_on': ['branch1', 'branch2']}
                ]
            },
            'conditional': {
                'id': 'conditional',
                'name': 'Conditional Workflow',
                'description': 'Execute based on conditions',
                'steps': [
                    {'id': 'check', 'tool': '', 'parallel': False},
                    {'id': 'if_true', 'tool': '', 'condition': 'check.success', 'depends_on': ['check']},
                    {'id': 'if_false', 'tool': '', 'condition': 'not check.success', 'depends_on': ['check']}
                ]
            }
        })
        
        return templates
    
    def _load_metrics(self):
        """Load execution metrics"""
        metrics_file = WORKSPACE / "20-data-reports" / "workflow_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    self.metrics = json.load(f)
            except:
                pass
    
    def _save_metrics(self):
        """Save execution metrics"""
        metrics_file = WORKSPACE / "20-data-reports" / "workflow_metrics.json"
        metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
    
    def _build_dag(self, workflow: Dict) -> Dict[str, List[str]]:
        """Build dependency graph (DAG)"""
        dag = {}
        steps = workflow.get('steps', [])
        
        # Initialize all nodes
        for step in steps:
            dag[step['id']] = []
        
        # Add dependencies
        for step in steps:
            if 'depends_on' in step:
                for dep in step['depends_on']:
                    if dep in dag:
                        dag[dep].append(step['id'])
        
        return dag
    
    def _topological_sort(self, workflow: Dict) -> List[List[str]]:
        """Topological sort with parallel grouping"""
        steps = workflow.get('steps', [])
        dag = self._build_dag(workflow)
        
        # Calculate in-degree
        in_degree = {step['id']: 0 for step in steps}
        for step in steps:
            for dep in step.get('depends_on', []):
                if dep in in_degree:
                    in_degree[step['id']] += 1
        
        # Group by levels (parallel execution)
        levels = []
        remaining = set(in_degree.keys())
        
        while remaining:
            # Find all nodes with in-degree 0
            level = [node for node in remaining if in_degree[node] == 0]
            
            if not level:
                print("[ERROR] Circular dependency detected!")
                break
            
            levels.append(level)
            
            # Remove processed nodes
            for node in level:
                remaining.remove(node)
                for neighbor in dag.get(node, []):
                    if neighbor in in_degree:
                        in_degree[neighbor] -= 1
        
        return levels
    
    def _check_condition(self, condition: str, results: Dict) -> bool:
        """Check execution condition"""
        if not condition:
            return True
        
        # Simple condition evaluation
        if 'success' in condition:
            step_id = condition.split('.')[0]
            step_result = results.get(step_id, {})
            
            if 'not' in condition:
                return not step_result.get('success', False)
            else:
                return step_result.get('success', False)
        
        return True
    
    def _execute_step(self, step: Dict, results: Dict) -> Dict:
        """Execute a single workflow step"""
        step_id = step['id']
        tool = step.get('tool', '')
        args = step.get('args', [])
        
        print(f"\n  ▶️  Executing: {step_id}")
        print(f"     Tool: {tool}")
        
        start_time = time.time()
        
        # Check condition
        condition = step.get('condition')
        if condition and not self._check_condition(condition, results):
            print(f"  ⏭️  Skipped (condition not met)")
            return {
                'success': True,
                'skipped': True,
                'duration': 0
            }
        
        # Execute tool
        if tool:
            tool_path = TOOLS_DIR / tool
            
            if tool_path.exists():
                cmd = [sys.executable, str(tool_path)] + args
                
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=str(WORKSPACE)
                    )
                    
                    success = result.returncode == 0
                    duration = time.time() - start_time
                    
                    print(f"  {'✅' if success else '❌'} Completed in {duration:.2f}s")
                    
                    return {
                        'success': success,
                        'skipped': False,
                        'duration': duration,
                        'returncode': result.returncode,
                        'output': result.stdout[-500:] if result.stdout else '',
                        'error': result.stderr[-500:] if result.stderr else ''
                    }
                
                except subprocess.TimeoutExpired:
                    print(f"  ❌ Timeout (>5min)")
                    return {'success': False, 'skipped': False, 'duration': 300, 'error': 'Timeout'}
                
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    return {'success': False, 'skipped': False, 'duration': time.time() - start_time, 'error': str(e)}
            else:
                print(f"  ⚠️  Tool not found: {tool}")
                return {'success': False, 'skipped': False, 'duration': 0, 'error': 'Tool not found'}
        
        return {'success': True, 'skipped': False, 'duration': time.time() - start_time}
    
    def run(self, workflow_id: str, verbose: bool = False) -> Dict:
        """Execute workflow with DAG scheduling"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + f"  Workflow: {workflow_id}".ljust(59) + "║")
        print("╚" + "═" * 58 + "╝")
        
        if workflow_id not in self.workflows:
            print(f"[ERROR] Workflow not found: {workflow_id}")
            return {'success': False, 'error': 'Workflow not found'}
        
        workflow = self.workflows[workflow_id]
        print(f"\n📋 {workflow.get('name', workflow_id)}")
        print(f"   {workflow.get('description', '')}")
        print(f"   Version: {workflow.get('version', '1.0')}")
        print(f"   Steps: {len(workflow.get('steps', []))}")
        
        # Build execution plan
        levels = self._topological_sort(workflow)
        print(f"\n📊 Execution Plan: {len(levels)} levels")
        for i, level in enumerate(levels):
            print(f"   Level {i+1}: {', '.join(level)}")
        
        # Execute
        print("\n⚙️  Execution:")
        results = {}
        total_start = time.time()
        
        for level_idx, level in enumerate(levels):
            print(f"\n📍 Level {level_idx + 1}/{len(levels)}")
            
            # Execute level in parallel
            level_results = {}
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {}
                
                for step_id in level:
                    step = next((s for s in workflow['steps'] if s['id'] == step_id), None)
                    if step:
                        futures[executor.submit(self._execute_step, step, results)] = step_id
                
                for future in as_completed(futures):
                    step_id = futures[future]
                    try:
                        level_results[step_id] = future.result()
                    except Exception as e:
                        level_results[step_id] = {'success': False, 'error': str(e)}
            
            results.update(level_results)
            
            # Visual progress
            progress = (level_idx + 1) / len(levels) * 100
            bar_length = 40
            filled = int(bar_length * progress / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\n[{bar}] {progress:.0f}%")
        
        total_duration = time.time() - total_start
        
        # Summary
        success_count = sum(1 for r in results.values() if r.get('success', False))
        total_count = len(results)
        
        print("\n" + "=" * 60)
        print("Workflow Summary")
        print("=" * 60)
        print(f"Total Steps: {total_count}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_count - success_count}")
        print(f"Duration: {total_duration:.2f}s")
        print(f"Status: {'✅ SUCCESS' if success_count == total_count else '⚠️ PARTIAL'}")
        print("=" * 60)
        
        # Update metrics
        self.metrics['total_executions'] += 1
        if success_count == total_count:
            self.metrics['successful'] += 1
        else:
            self.metrics['failed'] += 1
        
        # Update average duration
        total = self.metrics['total_executions']
        self.metrics['avg_duration'] = (
            (self.metrics['avg_duration'] * (total - 1) + total_duration) / total
        )
        
        self._save_metrics()
        
        execution_result = {
            'workflow_id': workflow_id,
            'success': success_count == total_count,
            'total_steps': total_count,
            'successful_steps': success_count,
            'duration': total_duration,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        self.execution_history.append(execution_result)
        
        return execution_result
    
    def visualize(self, workflow_id: str) -> str:
        """Generate ASCII visualization of workflow"""
        if workflow_id not in self.workflows:
            return f"[ERROR] Workflow not found: {workflow_id}"
        
        workflow = self.workflows[workflow_id]
        levels = self._topological_sort(workflow)
        
        viz = []
        viz.append("\n" + "╔" + "═" * 58 + "╗")
        viz.append("║" + f"  Workflow Visualization: {workflow_id}".ljust(59) + "║")
        viz.append("╚" + "═" * 58 + "╝")
        viz.append("")
        viz.append(f"📋 {workflow.get('name', workflow_id)}")
        viz.append(f"   {workflow.get('description', '')}")
        viz.append("")
        viz.append("Execution Flow:")
        viz.append("")
        
        for i, level in enumerate(levels):
            viz.append(f"  ┌─ Level {i+1} ─" + "─" * 30)
            viz.append("  │")
            
            for step_id in level:
                step = next((s for s in workflow['steps'] if s['id'] == step_id), None)
                if step:
                    deps = step.get('depends_on', [])
                    deps_str = f" ← [{', '.join(deps)}]" if deps else ""
                    parallel = "∥" if step.get('parallel') else "→"
                    viz.append(f"  │  {parallel} {step_id}{deps_str}")
            
            viz.append("  │")
            
            if i < len(levels) - 1:
                viz.append("  ▼")
        
        viz.append("")
        viz.append("  ✅ End")
        viz.append("")
        
        return '\n'.join(viz)
    
    def list_workflows(self) -> str:
        """List all available workflows"""
        output = []
        output.append("\n" + "=" * 60)
        output.append("Available Workflows")
        output.append("=" * 60)
        
        for wf_id, wf in self.workflows.items():
            status = "📦 Built-in" if wf_id in self._get_builtin_workflows() else "📁 Custom"
            output.append(f"\n{wf_id}")
            output.append(f"  Name: {wf.get('name', 'N/A')}")
            output.append(f"  Description: {wf.get('description', 'N/A')}")
            output.append(f"  Version: {wf.get('version', '1.0')}")
            output.append(f"  Steps: {len(wf.get('steps', []))}")
            output.append(f"  Type: {status}")
        
        output.append("\n" + "=" * 60)
        output.append(f"Total: {len(self.workflows)} workflows")
        output.append("=" * 60)
        
        return '\n'.join(output)
    
    def list_templates(self) -> str:
        """List workflow templates"""
        output = []
        output.append("\n" + "=" * 60)
        output.append("Workflow Templates")
        output.append("=" * 60)
        
        for tpl_id, tpl in self.templates.items():
            output.append(f"\n{tpl_id}")
            output.append(f"  Name: {tpl.get('name', 'N/A')}")
            output.append(f"  Description: {tpl.get('description', 'N/A')}")
            output.append(f"  Steps: {len(tpl.get('steps', []))}")
        
        output.append("\n" + "=" * 60)
        output.append(f"Total: {len(self.templates)} templates")
        output.append("=" * 60)
        
        return '\n'.join(output)
    
    def show_metrics(self) -> str:
        """Show execution metrics"""
        output = []
        output.append("\n" + "=" * 60)
        output.append("Workflow Execution Metrics")
        output.append("=" * 60)
        output.append(f"Total Executions: {self.metrics['total_executions']}")
        output.append(f"Successful: {self.metrics['successful']}")
        output.append(f"Failed: {self.metrics['failed']}")
        
        success_rate = (
            self.metrics['successful'] / self.metrics['total_executions'] * 100
            if self.metrics['total_executions'] > 0 else 0
        )
        output.append(f"Success Rate: {success_rate:.1f}%")
        output.append(f"Average Duration: {self.metrics['avg_duration']:.2f}s")
        output.append("=" * 60)
        
        return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Workflow Engine v2.0')
    parser.add_argument('--run', type=str, metavar='WORKFLOW', help='Run workflow')
    parser.add_argument('--visualize', type=str, metavar='WORKFLOW', help='Visualize workflow')
    parser.add_argument('--list', action='store_true', help='List workflows')
    parser.add_argument('--templates', action='store_true', help='List templates')
    parser.add_argument('--metrics', action='store_true', help='Show metrics')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    engine = WorkflowEngineV2()
    
    if args.run:
        engine.run(args.run, verbose=args.verbose)
    
    if args.visualize:
        print(engine.visualize(args.visualize))
    
    if args.list:
        print(engine.list_workflows())
    
    if args.templates:
        print(engine.list_templates())
    
    if args.metrics:
        print(engine.show_metrics())
    
    if not any([args.run, args.visualize, args.list, args.templates, args.metrics]):
        parser.print_help()


if __name__ == "__main__":
    main()
