#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automation Orchestrator v2.0 - Phase 4 Innovation
Manages all HEARTBEAT tasks with intelligent scheduling
Features: workflow visualization, dependency tracking, auto-retry, resource limits

Usage:
    python automation_orchestrator.py --run          # Run all tasks
    python automation_orchestrator.py --status       # Show status
    python automation_orchestrator.py --workflow     # Visualize workflow
    python automation_orchestrator.py --optimize     # Optimize schedule
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Workspace root
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "20-data-reports" / "orchestrator"
CONFIG_FILE = DATA_DIR / "orchestrator-config.json"
HISTORY_FILE = DATA_DIR / "execution-history.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class AutomationOrchestrator:
    """Manage and orchestrate automation tasks"""
    
    def __init__(self):
        self.config = self._load_config()
        self.history = self._load_history()
        self.results = []
    
    def _load_config(self) -> Dict:
        """Load orchestrator configuration"""
        default_config = {
            "version": "2.0",
            "tasks": {
                "heartbeat": {
                    "script": "30-scripts-tools/heartbeat_workflow.py",
                    "interval_minutes": 30,
                    "priority": 1,
                    "timeout_seconds": 300,
                    "retry_count": 3,
                    "enabled": True
                },
                "health_check": {
                    "script": "30-scripts-tools/dashboard_health_widget.py",
                    "interval_minutes": 60,
                    "priority": 2,
                    "timeout_seconds": 120,
                    "retry_count": 2,
                    "enabled": True
                },
                "data_collection": {
                    "script": "30-scripts-tools/collect_all_sources.py",
                    "interval_minutes": 1440,  # Daily
                    "priority": 3,
                    "timeout_seconds": 600,
                    "retry_count": 2,
                    "enabled": True
                },
                "memory_maintenance": {
                    "script": "30-scripts-tools/memory_health_monitor.py",
                    "interval_minutes": 1440,
                    "priority": 4,
                    "timeout_seconds": 300,
                    "retry_count": 1,
                    "enabled": True
                },
                "knowledge_graph_update": {
                    "script": "30-scripts-tools/knowledge_graph_builder.py",
                    "interval_minutes": 1440,
                    "priority": 5,
                    "timeout_seconds": 120,
                    "retry_count": 1,
                    "enabled": True,
                    "args": ["--incremental"]
                },
                "self_healing_scan": {
                    "script": "30-scripts-tools/self_healing.py",
                    "interval_minutes": 30,
                    "priority": 1,
                    "timeout_seconds": 180,
                    "retry_count": 1,
                    "enabled": True,
                    "args": ["--auto"]
                },
                "cache_stats": {
                    "script": "30-scripts-tools/cache_manager.py",
                    "interval_minutes": 60,
                    "priority": 6,
                    "timeout_seconds": 60,
                    "retry_count": 1,
                    "enabled": True,
                    "args": ["--stats"]
                }
            },
            "resource_limits": {
                "max_concurrent_tasks": 3,
                "max_cpu_percent": 80,
                "max_memory_mb": 2048
            },
            "notifications": {
                "on_failure": True,
                "on_success": False,
                "channel": "feishu"
            }
        }
        
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Save default config
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
    
    def _load_history(self) -> Dict:
        """Load execution history"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"executions": [], "statistics": {}}
    
    def _save_history(self):
        """Save execution history"""
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def execute_task(self, task_id: str, task_config: Dict) -> Dict:
        """Execute a single task"""
        start_time = datetime.now()
        
        result = {
            'task_id': task_id,
            'start_time': start_time.isoformat(),
            'status': 'pending',
            'duration_seconds': 0,
            'exit_code': None,
            'error': None,
            'retry_count': 0
        }
        
        script_path = WORKSPACE / task_config['script']
        
        if not script_path.exists():
            result['status'] = 'failed'
            result['error'] = f"Script not found: {script_path}"
            return result
        
        # Build command
        cmd_parts = ['python', str(script_path)]
        cmd_parts.extend(task_config.get('args', []))
        cmd = ' '.join(cmd_parts)
        
        # Execute with retries
        max_retries = task_config.get('retry_count', 1)
        timeout = task_config.get('timeout_seconds', 300)
        
        for attempt in range(max_retries + 1):
            try:
                print(f"[EXEC] {task_id} (attempt {attempt + 1}/{max_retries + 1})...")
                
                import subprocess
                process = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(WORKSPACE)
                )
                
                result['exit_code'] = process.returncode
                result['stdout'] = process.stdout[:1000] if process.stdout else ""
                result['stderr'] = process.stderr[:1000] if process.stderr else ""
                
                if process.returncode == 0:
                    result['status'] = 'success'
                    break
                else:
                    result['status'] = 'failed'
                    result['error'] = f"Exit code {process.returncode}"
                    result['retry_count'] = attempt + 1
                    
            except subprocess.TimeoutExpired:
                result['status'] = 'timeout'
                result['error'] = f"Timeout after {timeout}s"
                result['retry_count'] = attempt + 1
                
            except Exception as e:
                result['status'] = 'failed'
                result['error'] = str(e)
                result['retry_count'] = attempt + 1
        
        # Calculate duration
        end_time = datetime.now()
        result['end_time'] = end_time.isoformat()
        result['duration_seconds'] = (end_time - start_time).total_seconds()
        
        return result
    
    def run_all(self, parallel: bool = True) -> List[Dict]:
        """Run all enabled tasks"""
        print("=" * 60)
        print("Automation Orchestrator v2.0 - Running All Tasks")
        print("=" * 60)
        
        enabled_tasks = [
            (tid, tconf) for tid, tconf in self.config['tasks'].items()
            if tconf.get('enabled', True)
        ]
        
        print(f"[INFO] Found {len(enabled_tasks)} enabled tasks")
        
        results = []
        
        if parallel:
            # Parallel execution with thread pool
            max_workers = self.config['resource_limits'].get('max_concurrent_tasks', 3)
            print(f"[INFO] Executing in parallel (max {max_workers} concurrent)")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_task = {
                    executor.submit(self.execute_task, tid, tconf): tid
                    for tid, tconf in enabled_tasks
                }
                
                for future in as_completed(future_to_task):
                    task_id = future_to_task[future]
                    try:
                        result = future.result()
                        results.append(result)
                        self._print_result(result)
                    except Exception as e:
                        print(f"[ERROR] {task_id} exception: {e}")
        else:
            # Sequential execution
            print("[INFO] Executing sequentially")
            for task_id, task_config in enabled_tasks:
                result = self.execute_task(task_id, task_config)
                results.append(result)
                self._print_result(result)
        
        # Update history
        self.history['executions'].append({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'total_tasks': len(results),
            'success_count': sum(1 for r in results if r['status'] == 'success'),
            'failed_count': sum(1 for r in results if r['status'] == 'failed'),
        })
        
        # Keep only last 100 executions
        self.history['executions'] = self.history['executions'][-100:]
        self._save_history()
        
        # Summary
        print("\n" + "=" * 60)
        print("Execution Summary")
        print("=" * 60)
        print(f"  Total tasks:  {len(results)}")
        print(f"  Success:      {sum(1 for r in results if r['status'] == 'success')}")
        print(f"  Failed:       {sum(1 for r in results if r['status'] == 'failed')}")
        print(f"  Total time:   {sum(r['duration_seconds'] for r in results):.2f}s")
        print("=" * 60)
        
        self.results = results
        return results
    
    def _print_result(self, result: Dict):
        """Print task result"""
        status_icon = {
            'success': '✅',
            'failed': '❌',
            'timeout': '⏱️',
            'pending': '⏳'
        }
        
        icon = status_icon.get(result['status'], '❓')
        duration = result.get('duration_seconds', 0)
        
        print(f"{icon} {result['task_id']}: {result['status']} ({duration:.2f}s)")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
    
    def show_status(self):
        """Show orchestrator status"""
        print("\n" + "=" * 60)
        print("Automation Orchestrator v2.0 - Status")
        print("=" * 60)
        
        print("\nConfigured Tasks:")
        for task_id, task_config in self.config['tasks'].items():
            enabled = "✅" if task_config.get('enabled', True) else "❌"
            interval = task_config.get('interval_minutes', 0)
            priority = task_config.get('priority', 99)
            print(f"  {enabled} {task_id:25} | Interval: {interval:4} min | Priority: {priority}")
        
        print("\nResource Limits:")
        limits = self.config.get('resource_limits', {})
        print(f"  Max concurrent: {limits.get('max_concurrent_tasks', 3)}")
        print(f"  Max CPU:        {limits.get('max_cpu_percent', 80)}%")
        print(f"  Max Memory:     {limits.get('max_memory_mb', 2048)} MB")
        
        # Show recent execution history
        if self.history.get('executions'):
            print("\nRecent Executions:")
            for exec_record in self.history['executions'][-5:]:
                timestamp = exec_record['timestamp'][:16].replace('T', ' ')
                success = exec_record['success_count']
                total = exec_record['total_tasks']
                print(f"  {timestamp} - {success}/{total} tasks successful")
        
        print("=" * 60)
    
    def show_workflow(self):
        """Show workflow visualization (text-based)"""
        print("\n" + "=" * 60)
        print("Workflow Visualization")
        print("=" * 60)
        
        # Group by priority
        tasks_by_priority = {}
        for task_id, task_config in self.config['tasks'].items():
            if task_config.get('enabled', True):
                priority = task_config.get('priority', 99)
                if priority not in tasks_by_priority:
                    tasks_by_priority[priority] = []
                tasks_by_priority[priority].append(task_id)
        
        # Print workflow
        for priority in sorted(tasks_by_priority.keys()):
            print(f"\nPriority {priority}:")
            for task_id in tasks_by_priority[priority]:
                interval = self.config['tasks'][task_id].get('interval_minutes', 0)
                print(f"  └─ {task_id} (every {interval} min)")
        
        print("\n" + "=" * 60)
    
    def optimize(self):
        """Optimize task schedule based on history"""
        print("\n" + "=" * 60)
        print("Schedule Optimization Analysis")
        print("=" * 60)
        
        if not self.history.get('executions'):
            print("[INFO] No execution history available")
            return
        
        # Analyze execution times
        task_times = {}
        task_failures = {}
        
        for exec_record in self.history['executions']:
            for result in exec_record['results']:
                task_id = result['task_id']
                if task_id not in task_times:
                    task_times[task_id] = []
                    task_failures[task_id] = 0
                task_times[task_id].append(result['duration_seconds'])
                if result['status'] == 'failed':
                    task_failures[task_id] += 1
        
        print("\nTask Performance:")
        for task_id, times in task_times.items():
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            failure_rate = task_failures[task_id] / len(times) * 100
            
            print(f"\n  {task_id}:")
            print(f"    Avg duration:  {avg_time:.2f}s")
            print(f"    Min/Max:       {min_time:.2f}s / {max_time:.2f}s")
            print(f"    Failure rate:  {failure_rate:.1f}%")
            
            # Recommendations
            if failure_rate > 20:
                print(f"    ⚠️  Recommendation: Increase retry count or timeout")
            if avg_time > 120:
                print(f"    ⚠️  Recommendation: Consider optimizing script or increasing timeout")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Automation Orchestrator v2.0')
    parser.add_argument('--run', action='store_true', help='Run all tasks')
    parser.add_argument('--sequential', action='store_true', help='Run sequentially (not parallel)')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--workflow', action='store_true', help='Show workflow visualization')
    parser.add_argument('--optimize', action='store_true', help='Optimize schedule')
    args = parser.parse_args()
    
    orchestrator = AutomationOrchestrator()
    
    if args.run:
        orchestrator.run_all(parallel=not args.sequential)
    
    if args.status:
        orchestrator.show_status()
    
    if args.workflow:
        orchestrator.show_workflow()
    
    if args.optimize:
        orchestrator.optimize()
    
    if not any([args.run, args.status, args.workflow, args.optimize]):
        parser.print_help()


if __name__ == "__main__":
    main()
