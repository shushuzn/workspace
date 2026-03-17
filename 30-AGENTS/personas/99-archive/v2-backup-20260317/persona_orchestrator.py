#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Persona Collaboration Orchestrator
Unified scheduler for 7-persona collaboration workflows
Features: cron integration, task queue, priority scheduling, auto-retry

Usage:
    python persona_orchestrator.py --start
    python persona_orchestrator.py --status
    python persona_orchestrator.py --run "task description"
"""

import os
import sys
import json
import time
import argparse
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from queue import PriorityQueue
from dataclasses import dataclass, field

# Workspace root
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / "00-人格系统"))

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass(order=True)
class ScheduledTask:
    """Task with priority and scheduling"""
    priority: int
    scheduled_time: datetime = field(compare=True)
    task_id: str = field(compare=False)
    description: str = field(compare=False)
    persona_workflow: bool = field(compare=False, default=True)
    retry_count: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)


class PersonaOrchestrator:
    """Unified orchestrator for persona collaboration"""
    
    def __init__(self):
        self.task_queue = PriorityQueue()
        self.running = False
        self.current_task = None
        self.completed_tasks = []
        self.failed_tasks = []
        self.state_file = WORKSPACE / "20-data-reports" / "persona_orchestrator_state.json"
        self.stats_file = WORKSPACE / "20-data-reports" / "persona_orchestrator_stats.json"
        
        # Load state
        self.load_state()
    
    def load_state(self):
        """Load orchestrator state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    # Restore pending tasks
                    for task_data in state.get('pending_tasks', []):
                        task = ScheduledTask(
                            priority=task_data['priority'],
                            scheduled_time=datetime.fromisoformat(task_data['scheduled_time']),
                            task_id=task_data['task_id'],
                            description=task_data['description'],
                            persona_workflow=task_data.get('persona_workflow', True),
                            retry_count=task_data.get('retry_count', 0),
                            max_retries=task_data.get('max_retries', 3)
                        )
                        self.task_queue.put(task)
            except Exception as e:
                print(f"[ORCHESTRATOR] Warning: Could not load state: {e}")
    
    def save_state(self):
        """Save orchestrator state"""
        state = {
            'current_task': self.current_task.task_id if self.current_task else None,
            'pending_count': self.task_queue.qsize(),
            'completed_count': len(self.completed_tasks),
            'failed_count': len(self.failed_tasks),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def save_stats(self):
        """Save detailed statistics"""
        stats = {
            'total_tasks': len(self.completed_tasks) + len(self.failed_tasks),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'success_rate': len(self.completed_tasks) / max(1, len(self.completed_tasks) + len(self.failed_tasks)) * 100,
            'avg_execution_time': self._calculate_avg_time(),
            'last_24h': self._get_last_24h_stats(),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    
    def _calculate_avg_time(self) -> float:
        """Calculate average execution time"""
        if not self.completed_tasks:
            return 0.0
        times = [t.get('execution_time', 0) for t in self.completed_tasks]
        return sum(times) / len(times)
    
    def _get_last_24h_stats(self) -> Dict:
        """Get last 24 hours statistics"""
        cutoff = datetime.now() - timedelta(hours=24)
        recent = [t for t in self.completed_tasks if datetime.fromisoformat(t['completed_at']) > cutoff]
        return {
            'count': len(recent),
            'success_rate': len(recent) / max(1, len(recent)) * 100
        }
    
    def schedule_task(self, description: str, priority: int = 2, 
                      delay_minutes: int = 0, persona_workflow: bool = True) -> str:
        """Schedule a new task"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.completed_tasks)}"
        
        scheduled_time = datetime.now() + timedelta(minutes=delay_minutes)
        
        task = ScheduledTask(
            priority=priority,
            scheduled_time=scheduled_time,
            task_id=task_id,
            description=description,
            persona_workflow=persona_workflow
        )
        
        self.task_queue.put(task)
        self.save_state()
        
        print(f"[ORCHESTRATOR] Scheduled: {task_id}")
        print(f"  Description: {description}")
        print(f"  Priority: {priority}")
        print(f"  Scheduled: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return task_id
    
    def execute_task(self, task: ScheduledTask) -> bool:
        """Execute a single task"""
        print(f"\n{'='*60}")
        print(f"[TASK] Executing: {task.task_id}")
        print(f"Description: {task.description}")
        print(f"{'='*60}\n")
        
        start_time = datetime.now()
        
        try:
            if task.persona_workflow:
                # Run persona collaboration workflow
                from persona_collaboration import PersonaCollaborationEngine
                engine = PersonaCollaborationEngine()
                
                result = engine.run_collaboration_workflow(task.description)
                
                # Save result
                result_file = WORKSPACE / "20-data-reports" / f"persona_task_{task.task_id}.json"
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                success = result.get('success', False)
            else:
                # Generic task (placeholder)
                print(f"[TASK] Generic task execution...")
                time.sleep(1)
                success = True
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if success:
                self.completed_tasks.append({
                    'task_id': task.task_id,
                    'description': task.description,
                    'started_at': start_time.isoformat(),
                    'completed_at': end_time.isoformat(),
                    'execution_time': execution_time
                })
                print(f"\n[TASK] ✅ Completed in {execution_time:.1f}s")
            else:
                raise Exception("Task failed")
            
            self.save_stats()
            return success
            
        except Exception as e:
            print(f"\n[TASK] ❌ Failed: {e}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.scheduled_time = datetime.now() + timedelta(minutes=5)
                self.task_queue.put(task)
                print(f"[TASK] Retrying in 5 minutes (attempt {task.retry_count}/{task.max_retries})")
            else:
                self.failed_tasks.append({
                    'task_id': task.task_id,
                    'description': task.description,
                    'error': str(e),
                    'failed_at': datetime.now().isoformat()
                })
            
            self.save_stats()
            return False
    
    def run_loop(self):
        """Main orchestration loop"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + "  Persona Orchestrator Started".ljust(59) + "║")
        print("╚" + "═" * 58 + "╝")
        print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        
        while self.running:
            try:
                if not self.task_queue.empty():
                    task = self.task_queue.get()
                    
                    # Check if it's time to execute
                    if datetime.now() >= task.scheduled_time:
                        self.current_task = task
                        success = self.execute_task(task)
                        self.current_task = None
                    else:
                        # Put back and wait
                        self.task_queue.put(task)
                        time.sleep(1)
                else:
                    time.sleep(5)
                
                # Save state periodically
                self.save_state()
                
            except KeyboardInterrupt:
                print("\n[ORCHESTRATOR] Stopping...")
                self.running = False
                self.save_state()
                break
            except Exception as e:
                print(f"[ORCHESTRATOR] Error: {e}")
                time.sleep(5)
    
    def get_status(self) -> Dict:
        """Get current orchestrator status"""
        return {
            'running': self.running,
            'current_task': self.current_task.task_id if self.current_task else None,
            'pending_tasks': self.task_queue.qsize(),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'success_rate': len(self.completed_tasks) / max(1, len(self.completed_tasks) + len(self.failed_tasks)) * 100
        }
    
    def print_status(self):
        """Print current status"""
        status = self.get_status()
        
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + "  Persona Orchestrator Status".ljust(59) + "║")
        print("╚" + "═" * 58 + "╝")
        
        print(f"\nRunning: {status['running']}")
        print(f"Current Task: {status['current_task'] or 'None'}")
        print(f"Pending Tasks: {status['pending_tasks']}")
        print(f"Completed: {status['completed_tasks']}")
        print(f"Failed: {status['failed_tasks']}")
        print(f"Success Rate: {status['success_rate']:.1f}%")
        
        # Show pending tasks
        if status['pending_tasks'] > 0:
            print("\nPending Tasks:")
            temp_queue = list(self.task_queue.queue)
            for i, task in enumerate(temp_queue[:5], 1):
                print(f"  {i}. {task.task_id} - {task.description[:40]}...")


def main():
    parser = argparse.ArgumentParser(description='Persona Collaboration Orchestrator')
    parser.add_argument('--start', action='store_true', help='Start orchestration loop')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--run', type=str, help='Run single task immediately')
    parser.add_argument('--schedule', type=str, help='Schedule task for later')
    parser.add_argument('--priority', type=int, default=2, help='Task priority (1-5)')
    parser.add_argument('--delay', type=int, default=0, help='Delay in minutes')
    args = parser.parse_args()
    
    orchestrator = PersonaOrchestrator()
    
    if args.start:
        orchestrator.run_loop()
    
    elif args.status:
        orchestrator.print_status()
    
    elif args.run:
        task = ScheduledTask(
            priority=args.priority,
            scheduled_time=datetime.now(),
            task_id=f"immediate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=args.run
        )
        orchestrator.execute_task(task)
    
    elif args.schedule:
        orchestrator.schedule_task(args.schedule, args.priority, args.delay)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
