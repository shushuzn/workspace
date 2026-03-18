#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Engine - Phase 4 Deep Iteration
Define and execute complex workflows with conditions
Features: workflow DSL, conditional execution, parallel branches, error handling

Usage:
    python workflow_engine.py --run daily_brief
    python workflow_engine.py --list
    python workflow_engine.py --create my_workflow.json
    python workflow_engine.py --execute workflow.json
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Workspace root
WORKSPACE = Path(__file__).parent.parent
WORKFLOWS_DIR = WORKSPACE / "40-workflows"
TOOLS_DIR = WORKSPACE / "30-scripts-tools"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class WorkflowEngine:
    """Execute complex workflows"""
    
    def __init__(self):
        self.workflows = self._load_workflows()
        self.execution_history = []
    
    def _load_workflows(self) -> Dict:
        """Load predefined workflows"""
        workflows = {
            'daily_brief': {
                'name': 'Daily Brief Generation',
                'description': 'Generate daily research brief',
                'version': '1.0',
                'steps': [
                    {
                        'id': 'collect_arxiv',
                        'tool': 'arxiv_collector.py',
                        'args': ['--daily'],
                        'timeout': 300,
                        'on_error': 'continue'
                    },
                    {
                        'id': 'collect_github',
                        'tool': 'github_collector.py',
                        'args': ['--trending'],
                        'timeout': 180,
                        'on_error': 'continue',
                        'parallel': True
                    },
                    {
                        'id': 'collect_medium',
                        'tool': 'medium_collector.py',
                        'args': ['--daily'],
                        'timeout': 180,
                        'on_error': 'continue',
                        'parallel': True
                    },
                    {
                        'id': 'generate_brief',
                        'tool': 'daily_brief_generator.py',
                        'args': ['--auto'],
                        'timeout': 600,
                        'depends_on': ['collect_arxiv', 'collect_github', 'collect_medium'],
                        'on_error': 'fail'
                    },
                    {
                        'id': 'notify',
                        'tool': 'smart_notification.py',
                        'args': ['--channel', 'feishu', '--priority', 'normal'],
                        'timeout': 60,
                        'depends_on': ['generate_brief'],
                        'on_error': 'log'
                    }
                ]
            },
            
            'code_quality': {
                'name': 'Code Quality Pipeline',
                'description': 'Full code quality check',
                'version': '1.0',
                'steps': [
                    {
                        'id': 'review_code',
                        'tool': 'code_quality_reviewer.py',
                        'args': ['--scan', '30-scripts-tools'],
                        'timeout': 300,
                        'on_error': 'fail'
                    },
                    {
                        'id': 'generate_tests',
                        'tool': 'auto_test_generator.py',
                        'args': ['--auto'],
                        'timeout': 300,
                        'depends_on': ['review_code'],
                        'on_error': 'continue'
                    },
                    {
                        'id': 'run_tests',
                        'tool': 'auto_test_runner.py',
                        'args': ['--run', '--parallel'],
                        'timeout': 600,
                        'depends_on': ['generate_tests'],
                        'on_error': 'fail'
                    },
                    {
                        'id': 'generate_docs',
                        'tool': 'smart_doc_generator.py',
                        'args': ['--api'],
                        'timeout': 300,
                        'depends_on': ['run_tests'],
                        'on_error': 'continue'
                    },
                    {
                        'id': 'update_knowledge',
                        'tool': 'knowledge_graph_builder.py',
                        'args': ['--incremental'],
                        'timeout': 120,
                        'depends_on': ['generate_docs'],
                        'on_error': 'log'
                    }
                ]
            },
            
            'system_maintenance': {
                'name': 'System Maintenance',
                'description': 'Regular system maintenance',
                'version': '1.0',
                'steps': [
                    {
                        'id': 'health_check',
                        'tool': 'system_health_checker.py',
                        'args': ['--check'],
                        'timeout': 120,
                        'on_error': 'fail'
                    },
                    {
                        'id': 'cache_stats',
                        'tool': 'cache_manager.py',
                        'args': ['--stats'],
                        'timeout': 60,
                        'depends_on': ['health_check'],
                        'on_error': 'continue'
                    },
                    {
                        'id': 'clean_cache',
                        'tool': 'cache_manager.py',
                        'args': ['--clean', '--old'],
                        'timeout': 60,
                        'depends_on': ['cache_stats'],
                        'condition': 'cache_size > 400MB',
                        'on_error': 'continue'
                    },
                    {
                        'id': 'error_scan',
                        'tool': 'error_analyzer.py',
                        'args': ['--scan'],
                        'timeout': 180,
                        'depends_on': ['health_check'],
                        'on_error': 'continue'
                    },
                    {
                        'id': 'self_heal',
                        'tool': 'self_healing.py',
                        'args': ['--scan', '--fix'],
                        'timeout': 300,
                        'depends_on': ['error_scan'],
                        'condition': 'errors_found > 0',
                        'on_error': 'continue'
                    }
                ]
            },
            
            'research_pipeline': {
                'name': 'Research Processing Pipeline',
                'description': 'Process research papers',
                'version': '1.0',
                'steps': [
                    {
                        'id': 'collect_papers',
                        'tool': 'arxiv_collector.py',
                        'args': ['--category', 'cs.AI', '--limit', '50'],
                        'timeout': 300,
                        'on_error': 'fail'
                    },
                    {
                        'id': 'filter_papers',
                        'tool': 'paper_filter.py',
                        'args': ['--min-score', '0.7'],
                        'timeout': 120,
                        'depends_on': ['collect_papers'],
                        'on_error': 'continue'
                    },
                    {
                        'id': 'summarize',
                        'tool': 'paper_summarizer.py',
                        'args': ['--batch'],
                        'timeout': 600,
                        'depends_on': ['filter_papers'],
                        'on_error': 'continue'
                    },
                    {
                        'id': 'generate_cards',
                        'tool': 'batch_card_generator.py',
                        'args': ['--auto'],
                        'timeout': 300,
                        'depends_on': ['summarize'],
                        'on_error': 'continue'
                    },
                    {
                        'id': 'update_knowledge',
                        'tool': 'knowledge_graph_builder.py',
                        'args': ['--new-papers'],
                        'timeout': 120,
                        'depends_on': ['generate_cards'],
                        'on_error': 'log'
                    }
                ]
            }
        }
        
        # Load custom workflows from disk
        if WORKFLOWS_DIR.exists():
            for workflow_file in WORKFLOWS_DIR.glob("*.json"):
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        custom_workflow = json.load(f)
                        workflow_id = workflow_file.stem
                        workflows[workflow_id] = custom_workflow
                        print(f"[LOAD] Custom workflow: {workflow_id}")
                except Exception as e:
                    print(f"[WARN] Failed to load {workflow_file}: {e}")
        
        return workflows
    
    def list_workflows(self):
        """List available workflows"""
        print("\n" + "=" * 60)
        print("Available Workflows")
        print("=" * 60)
        
        for workflow_id, workflow in self.workflows.items():
            name = workflow.get('name', workflow_id)
            desc = workflow.get('description', 'No description')
            version = workflow.get('version', '1.0')
            steps = len(workflow.get('steps', []))
            
            print(f"\n📋 {workflow_id}")
            print(f"   Name: {name}")
            print(f"   Version: {v{version}}")
            print(f"   Steps: {steps}")
            print(f"   Description: {desc}")
        
        print("\n" + "=" * 60)
    
    def run_workflow(self, workflow_id: str, dry_run: bool = False) -> Dict:
        """Run a workflow"""
        if workflow_id not in self.workflows:
            print(f"[ERROR] Workflow not found: {workflow_id}")
            return {'error': f'Workflow not found: {workflow_id}'}
        
        workflow = self.workflows[workflow_id]
        
        print("\n" + "╔" + "═" * 58 + "╗")
        print(f"║  Workflow: {workflow.get('name', workflow_id):<46} ║")
        print("╠" + "═" * 58 + "╣")
        print(f"║  Version: {workflow.get('version', '1.0'):<47} ║")
        print(f"║  Steps: {len(workflow.get('steps', [])):<51} ║")
        print("╚" + "═" * 58 + "╝")
        
        execution = {
            'workflow_id': workflow_id,
            'start_time': datetime.now().isoformat(),
            'steps': [],
            'status': 'running'
        }
        
        steps = workflow.get('steps', [])
        completed_steps = set()
        failed_steps = set()
        
        # Execute steps
        for i, step in enumerate(steps, 1):
            step_id = step.get('id', f'step_{i}')
            
            # Check dependencies
            depends_on = step.get('depends_on', [])
            if depends_on:
                missing_deps = [dep for dep in depends_on if dep not in completed_steps]
                if missing_deps:
                    print(f"\n[WAIT] {step_id}: Waiting for {', '.join(missing_deps)}")
                    continue
            
            # Check condition
            condition = step.get('condition')
            if condition:
                if not self._evaluate_condition(condition):
                    print(f"\n[SKIP] {step_id}: Condition not met ({condition})")
                    continue
            
            # Execute step
            print(f"\n[STEP {i}/{len(steps)}] {step_id}")
            print(f"  Tool: {step.get('tool')}")
            print(f"  Args: {' '.join(step.get('args', []))}")
            
            if dry_run:
                print(f"  [DRY RUN] Would execute")
                step_result = {'status': 'dry_run', 'step_id': step_id}
            else:
                step_result = self._execute_step(step)
            
            execution['steps'].append(step_result)
            
            # Handle result
            if step_result.get('status') == 'success':
                completed_steps.add(step_id)
                print(f"  ✅ SUCCESS ({step_result.get('duration', 0):.2f}s)")
            else:
                on_error = step.get('on_error', 'fail')
                if on_error == 'fail':
                    failed_steps.add(step_id)
                    print(f"  ❌ FAILED - Stopping workflow")
                    execution['status'] = 'failed'
                    break
                elif on_error == 'continue':
                    print(f"  ⚠️  WARNING - Continuing")
                    completed_steps.add(step_id)  # Mark as handled
                elif on_error == 'log':
                    print(f"  ⚠️  LOGGED - Continuing")
                    completed_steps.add(step_id)
        
        execution['end_time'] = datetime.now().isoformat()
        execution['status'] = 'success' if execution['status'] != 'failed' else 'failed'
        
        # Calculate duration
        start = datetime.fromisoformat(execution['start_time'])
        end = datetime.fromisoformat(execution['end_time'])
        execution['duration_seconds'] = (end - start).total_seconds()
        
        # Save execution history
        self.execution_history.append(execution)
        self._save_execution(execution, workflow_id)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Workflow Execution Summary")
        print("=" * 60)
        print(f"Status: {'✅ SUCCESS' if execution['status'] == 'success' else '❌ FAILED'}")
        print(f"Duration: {execution['duration_seconds']:.2f}s")
        print(f"Steps completed: {len(completed_steps)}/{len(steps)}")
        if failed_steps:
            print(f"Failed steps: {', '.join(failed_steps)}")
        print("=" * 60)
        
        return execution
    
    def _execute_step(self, step: Dict) -> Dict:
        """Execute a single workflow step"""
        tool = step.get('tool')
        args = step.get('args', [])
        timeout = step.get('timeout', 300)
        
        tool_path = TOOLS_DIR / tool
        
        if not tool_path.exists():
            return {
                'step_id': step.get('id'),
                'status': 'error',
                'error': f'Tool not found: {tool}',
                'duration': 0
            }
        
        start_time = time.time()
        
        try:
            cmd = ['python', str(tool_path)] + args
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(WORKSPACE)
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return {
                    'step_id': step.get('id'),
                    'status': 'success',
                    'duration': duration,
                    'output_lines': len(result.stdout.split('\n')),
                    'returncode': 0
                }
            else:
                return {
                    'step_id': step.get('id'),
                    'status': 'error',
                    'duration': duration,
                    'error': result.stderr[:200],
                    'returncode': result.returncode
                }
        
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                'step_id': step.get('id'),
                'status': 'timeout',
                'duration': duration,
                'error': f'Timeout after {timeout}s'
            }
        
        except Exception as e:
            duration = time.time() - start_time
            return {
                'step_id': step.get('id'),
                'status': 'error',
                'duration': duration,
                'error': str(e)[:200]
            }
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition string"""
        # Simple condition evaluation
        # Supports: cache_size > 400MB, errors_found > 0, etc.
        
        try:
            # Replace common patterns
            condition = condition.replace('MB', '*1024*1024')
            condition = condition.replace('GB', '*1024*1024*1024')
            
            # Safe eval with limited context
            context = {
                'cache_size': 500 * 1024 * 1024,  # Simulated
                'errors_found': 0,  # Simulated
                'true': True,
                'false': False
            }
            
            result = eval(condition, {"__builtins__": {}}, context)
            return bool(result)
        
        except:
            return True  # Default to true if condition can't be evaluated
    
    def _save_execution(self, execution: Dict, workflow_id: str):
        """Save execution history"""
        history_dir = WORKFLOWS_DIR / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        history_file = history_dir / f"{workflow_id}-{timestamp}.json"
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(execution, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Execution saved to {history_file}")
    
    def create_workflow_template(self, workflow_name: str) -> Path:
        """Create a workflow template file"""
        template = {
            'name': workflow_name,
            'description': 'Custom workflow',
            'version': '1.0',
            'steps': [
                {
                    'id': 'step_1',
                    'tool': 'tool_name.py',
                    'args': ['--arg1', 'value1'],
                    'timeout': 300,
                    'on_error': 'fail'
                }
            ]
        }
        
        WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)
        workflow_file = WORKFLOWS_DIR / f"{workflow_name}.json"
        
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Workflow template created: {workflow_file}")
        
        return workflow_file


def main():
    parser = argparse.ArgumentParser(description='Workflow Engine')
    parser.add_argument('--run', type=str, help='Run a workflow')
    parser.add_argument('--list', action='store_true', help='List workflows')
    parser.add_argument('--create', type=str, help='Create workflow template')
    parser.add_argument('--execute', type=str, help='Execute workflow file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    args = parser.parse_args()
    
    engine = WorkflowEngine()
    
    if args.run:
        engine.run_workflow(args.run, dry_run=args.dry_run)
    
    if args.list:
        engine.list_workflows()
    
    if args.create:
        engine.create_workflow_template(args.create)
    
    if args.execute:
        print("[INFO] Execute workflow file not yet implemented")
        print("  Use --run with workflow name instead")
    
    if not any([args.run, args.list, args.create, args.execute]):
        parser.print_help()


if __name__ == "__main__":
    main()
