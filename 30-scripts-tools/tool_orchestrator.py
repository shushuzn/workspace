#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Orchestrator - Workflow orchestration and tool composition

Features:
- Multi-tool workflow definition
- Dependency resolution
- Parallel execution
- Error handling and retry
- Pipeline composition
- Execution tracking
"""

import os
import sys
import json
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
ORCHESTRATOR_DIR = WORKSPACE / 'data' / 'tool_orchestrator'
ORCHESTRATOR_DIR.mkdir(parents=True, exist_ok=True)

class WorkflowStep:
    """Single workflow step"""
    
    def __init__(self, name: str, tool: str, args: List[str] = None,
                 depends_on: List[str] = None, timeout: int = 300):
        self.name = name
        self.tool = tool
        self.args = args or []
        self.depends_on = depends_on or []
        self.timeout = timeout
        
        # Execution state
        self.status = 'pending'  # pending, running, success, failed, skipped
        self.start_time = None
        self.end_time = None
        self.output = None
        self.error = None
        self.exit_code = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'tool': self.tool,
            'args': self.args,
            'depends_on': self.depends_on,
            'timeout': self.timeout,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'output': self.output,
            'error': self.error,
            'exit_code': self.exit_code,
        }


class Workflow:
    """Workflow definition and execution"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: Dict[str, WorkflowStep] = {}
        self.created = datetime.now()
        self.status = 'draft'  # draft, running, completed, failed
    
    def add_step(self, name: str, tool: str, args: List[str] = None,
                 depends_on: List[str] = None, timeout: int = 300) -> 'Workflow':
        """Add a step to the workflow"""
        step = WorkflowStep(name, tool, args, depends_on, timeout)
        self.steps[name] = step
        return self
    
    def _get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps that are ready to execute (dependencies met)"""
        ready = []
        
        for step in self.steps.values():
            if step.status != 'pending':
                continue
            
            # Check dependencies
            deps_met = True
            for dep_name in step.depends_on:
                dep_step = self.steps.get(dep_name)
                if not dep_step or dep_step.status != 'success':
                    deps_met = False
                    break
            
            if deps_met:
                ready.append(step)
        
        return ready
    
    def _execute_step(self, step: WorkflowStep) -> bool:
        """Execute a single workflow step"""
        step.status = 'running'
        step.start_time = datetime.now()
        
        try:
            # Build command
            tool_path = TOOLS_DIR / step.tool
            if not tool_path.exists():
                tool_path = TOOLS_DIR / f"{step.tool}.py"
            
            if not tool_path.exists():
                raise FileNotFoundError(f"Tool not found: {step.tool}")
            
            cmd = [sys.executable, str(tool_path)] + step.args
            
            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=step.timeout,
                encoding='utf-8',
            )
            
            step.output = result.stdout
            step.error = result.stderr
            step.exit_code = result.returncode
            
            if result.returncode == 0:
                step.status = 'success'
                return True
            else:
                step.status = 'failed'
                return False
        
        except subprocess.TimeoutExpired:
            step.status = 'failed'
            step.error = f"Timeout after {step.timeout}s"
            return False
        
        except Exception as e:
            step.status = 'failed'
            step.error = str(e)
            return False
        
        finally:
            step.end_time = datetime.now()
    
    def execute(self, parallel: bool = False, max_workers: int = 4) -> Dict:
        """
        Execute the workflow
        
        Args:
            parallel: Enable parallel execution
            max_workers: Maximum parallel workers
        
        Returns:
            Execution results
        """
        self.status = 'running'
        start_time = datetime.now()
        
        print(f"\n🚀 Starting workflow: {self.name}")
        print(f"   Steps: {len(self.steps)}")
        print(f"   Parallel: {parallel}")
        print()
        
        completed = 0
        failed = 0
        
        if parallel:
            # Parallel execution
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                while True:
                    ready_steps = self._get_ready_steps()
                    
                    if not ready_steps:
                        # Check if all done
                        pending = [s for s in self.steps.values() if s.status == 'pending']
                        if not pending:
                            break
                        time.sleep(0.1)
                        continue
                    
                    # Submit ready steps
                    futures = {
                        executor.submit(self._execute_step, step): step
                        for step in ready_steps
                    }
                    
                    for future in as_completed(futures):
                        step = futures[future]
                        try:
                            success = future.result()
                            if success:
                                completed += 1
                                print(f"✅ {step.name} completed ({step.tool})")
                            else:
                                failed += 1
                                print(f"❌ {step.name} failed: {step.error}")
                        except Exception as e:
                            failed += 1
                            print(f"❌ {step.name} exception: {e}")
        else:
            # Sequential execution
            while True:
                ready_steps = self._get_ready_steps()
                
                if not ready_steps:
                    pending = [s for s in self.steps.values() if s.status == 'pending']
                    if not pending:
                        break
                    # Deadlock detection
                    running = [s for s in self.steps.values() if s.status == 'running']
                    if not running:
                        print("⚠️  Deadlock detected - skipping remaining steps")
                        break
                    time.sleep(0.1)
                    continue
                
                # Execute first ready step
                step = ready_steps[0]
                success = self._execute_step(step)
                
                if success:
                    completed += 1
                    print(f"✅ {step.name} completed ({step.tool})")
                else:
                    failed += 1
                    print(f"❌ {step.name} failed: {step.error}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.status = 'completed' if failed == 0 else 'failed'
        
        print(f"\n{'✅' if failed == 0 else '❌'} Workflow {'completed' if failed == 0 else 'failed'}")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Completed: {completed}/{len(self.steps)}")
        print(f"   Failed: {failed}/{len(self.steps)}")
        
        return {
            'status': self.status,
            'duration_seconds': duration,
            'completed': completed,
            'failed': failed,
            'total': len(self.steps),
        }
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'created': self.created.isoformat(),
            'status': self.status,
            'steps': {name: step.to_dict() for name, step in self.steps.items()},
        }
    
    def save(self, workflow_file: Path = None) -> Path:
        """Save workflow to disk"""
        if workflow_file is None:
            workflow_file = ORCHESTRATOR_DIR / f'workflow_{self.name}.json'
        
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        print(f"✅ Workflow saved to: {workflow_file}")
        return workflow_file
    
    @classmethod
    def load(cls, workflow_file: Path) -> 'Workflow':
        """Load workflow from disk"""
        with open(workflow_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        workflow = cls(data['name'], data.get('description', ''))
        workflow.status = data.get('status', 'draft')
        
        for step_name, step_data in data['steps'].items():
            step = WorkflowStep(
                step_data['name'],
                step_data['tool'],
                step_data.get('args', []),
                step_data.get('depends_on', []),
                step_data.get('timeout', 300),
            )
            step.status = step_data.get('status', 'pending')
            workflow.steps[step_name] = step
        
        print(f"✅ Workflow loaded from: {workflow_file}")
        return workflow


class ToolOrchestrator:
    """
    Tool orchestration and workflow management
    
    Features:
    - Workflow definition
    - Dependency resolution
    - Parallel execution
    - Error handling
    - Execution history
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.execution_history: List[Dict] = []
        
        # Load existing workflows
        self._load_workflows()
    
    def _load_workflows(self):
        """Load existing workflows"""
        if ORCHESTRATOR_DIR.exists():
            for workflow_file in ORCHESTRATOR_DIR.glob('workflow_*.json'):
                try:
                    workflow = Workflow.load(workflow_file)
                    self.workflows[workflow.name] = workflow
                except Exception as e:
                    print(f"⚠️  Error loading {workflow_file}: {e}")
    
    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(name, description)
        self.workflows[name] = workflow
        return workflow
    
    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get workflow by name"""
        return self.workflows.get(name)
    
    def list_workflows(self) -> List[Dict]:
        """List all workflows"""
        return [
            {
                'name': w.name,
                'description': w.description,
                'steps': len(w.steps),
                'status': w.status,
            }
            for w in self.workflows.values()
        ]
    
    def execute_workflow(self, name: str, parallel: bool = False,
                        max_workers: int = 4) -> Dict:
        """Execute a workflow"""
        workflow = self.workflows.get(name)
        
        if not workflow:
            raise ValueError(f"Workflow not found: {name}")
        
        # Execute
        result = workflow.execute(parallel=parallel, max_workers=max_workers)
        
        # Record history
        history_entry = {
            'workflow': name,
            'timestamp': datetime.now().isoformat(),
            'result': result,
        }
        self.execution_history.append(history_entry)
        
        return result
    
    def get_stats(self) -> Dict:
        """Get orchestrator statistics"""
        return {
            'total_workflows': len(self.workflows),
            'total_executions': len(self.execution_history),
            'workflows': [
                {
                    'name': w.name,
                    'steps': len(w.steps),
                    'status': w.status,
                }
                for w in self.workflows.values()
            ],
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tool Orchestrator")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--list', action='store_true', help='List workflows')
    parser.add_argument('--create', type=str, help='Create workflow')
    parser.add_argument('--execute', type=str, help='Execute workflow')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel execution')
    args = parser.parse_args()
    
    orchestrator = ToolOrchestrator()
    
    if args.demo:
        print("\n🎯 Tool Orchestrator Demo")
        print("=" * 80)
        
        # Create demo workflow
        workflow = orchestrator.create_workflow(
            'demo_workflow',
            'Demo workflow for testing'
        )
        
        # Add steps (using simple tools that exist)
        workflow.add_step(
            'scan_tools',
            'tool_registry.py',
            args=['--stats'],
            timeout=60
        )
        
        # Save workflow
        workflow.save()
        
        # Execute
        result = orchestrator.execute_workflow('demo_workflow', parallel=False)
        
        print(f"\n✅ Demo complete!")
        print(f"Result: {result}")
    
    elif args.list:
        workflows = orchestrator.list_workflows()
        print("\n📋 Workflows")
        print("=" * 80)
        for w in workflows:
            print(f"  {w['name']}: {w['steps']} steps ({w['status']})")
            print(f"     {w['description']}\n")
    
    elif args.create:
        workflow = orchestrator.create_workflow(args.create, 'New workflow')
        workflow.save()
        print(f"✅ Workflow '{args.create}' created")
    
    elif args.execute:
        result = orchestrator.execute_workflow(
            args.execute,
            parallel=args.parallel
        )
        print(f"\n✅ Execution complete: {result}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
