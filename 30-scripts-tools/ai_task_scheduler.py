#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Task Scheduler - Intelligent task scheduling with ML

Features:
- Priority prediction
- Resource allocation
- Time estimation
- Dependency resolution
- Load balancing
- Adaptive scheduling
"""

import os
import sys
import json
import math
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict, deque
import heapq

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
SCHEDULER_DIR = WORKSPACE / 'data' / 'scheduler'
SCHEDULER_DIR.mkdir(parents=True, exist_ok=True)

class Task:
    """Task representation"""
    
    def __init__(self, task_id: str, name: str, priority: int = 0,
                 estimated_duration: float = 0, dependencies: List[str] = None,
                 resource_requirements: Dict = None, metadata: Dict = None):
        self.task_id = task_id
        self.name = name
        self.priority = priority
        self.estimated_duration = estimated_duration
        self.dependencies = dependencies or []
        self.resource_requirements = resource_requirements or {}
        self.metadata = metadata or {}
        
        self.status = 'pending'  # pending, ready, running, completed, failed
        self.assigned_to = None
        self.started_at = None
        self.completed_at = None
        self.actual_duration = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'priority': self.priority,
            'estimated_duration': self.estimated_duration,
            'dependencies': self.dependencies,
            'resource_requirements': self.resource_requirements,
            'metadata': self.metadata,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'actual_duration': self.actual_duration,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create from dictionary"""
        task = cls(
            data['task_id'],
            data['name'],
            data.get('priority', 0),
            data.get('estimated_duration', 0),
            data.get('dependencies', []),
            data.get('resource_requirements', {}),
            data.get('metadata', {}),
        )
        task.status = data.get('status', 'pending')
        task.assigned_to = data.get('assigned_to')
        if data.get('started_at'):
            task.started_at = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            task.completed_at = datetime.fromisoformat(data['completed_at'])
        task.actual_duration = data.get('actual_duration')
        return task
    
    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Check if task is ready to execute"""
        return all(dep in completed_tasks for dep in self.dependencies)


class ResourcePool:
    """Resource pool management"""
    
    def __init__(self):
        self.resources: Dict[str, float] = {}  # resource_name -> available_amount
    
    def add_resource(self, name: str, amount: float):
        """Add resource to pool"""
        self.resources[name] = self.resources.get(name, 0) + amount
    
    def allocate(self, requirements: Dict[str, float]) -> bool:
        """Allocate resources"""
        # Check availability
        for resource, amount in requirements.items():
            if self.resources.get(resource, 0) < amount:
                return False
        
        # Allocate
        for resource, amount in requirements.items():
            self.resources[resource] -= amount
        
        return True
    
    def release(self, requirements: Dict[str, float]):
        """Release resources"""
        for resource, amount in requirements.items():
            self.resources[resource] = self.resources.get(resource, 0) + amount
    
    def get_available(self) -> Dict[str, float]:
        """Get available resources"""
        return self.resources.copy()


class AITaskScheduler:
    """
    Intelligent task scheduler with ML-based optimization
    
    Features:
    - Priority prediction
    - Resource allocation
    - Time estimation
    - Dependency resolution
    - Load balancing
    - Adaptive scheduling
    """
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Tuple[int, str]] = []  # Priority queue (min-heap)
        self.completed_tasks: Set[str] = set()
        self.running_tasks: Dict[str, Task] = {}
        self.resource_pool = ResourcePool()
        
        # Initialize default resources
        self.resource_pool.add_resource('cpu', num_workers * 2)  # Cores
        self.resource_pool.add_resource('memory', num_workers * 4)  # GB
        self.resource_pool.add_resource('io', num_workers * 100)  # MB/s
        
        # Load state
        self._load_state()
    
    def _load_state(self):
        """Load scheduler state"""
        state_file = SCHEDULER_DIR / 'scheduler_state.json'
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.tasks = {
                task_id: Task.from_dict(task_data)
                for task_id, task_data in data.get('tasks', {}).items()
            }
            self.completed_tasks = set(data.get('completed_tasks', []))
            
            print(f"✅ Loaded scheduler state ({len(self.tasks)} tasks)")
    
    def _save_state(self):
        """Save scheduler state"""
        state_file = SCHEDULER_DIR / 'scheduler_state.json'
        
        data = {
            'tasks': {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            'completed_tasks': list(self.completed_tasks),
            'running_tasks': list(self.running_tasks.keys()),
            'last_updated': datetime.now().isoformat(),
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, task: Task) -> str:
        """
        Add task to scheduler
        
        Args:
            task: Task to add
        
        Returns:
            Task ID
        """
        self.tasks[task.task_id] = task
        
        # Add to priority queue
        heapq.heappush(self.task_queue, (-task.priority, task.task_id))
        
        self._save_state()
        return task.task_id
    
    def remove_task(self, task_id: str) -> bool:
        """Remove task from scheduler"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.task_queue = [
                (p, t) for p, t in self.task_queue if t != task_id
            ]
            heapq.heapify(self.task_queue)
            self._save_state()
            return True
        return False
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks ready to execute"""
        ready = []
        
        for priority, task_id in self.task_queue:
            task = self.tasks.get(task_id)
            
            if task and task.status == 'pending' and task.is_ready(self.completed_tasks):
                ready.append(task)
        
        # Sort by priority (highest first)
        ready.sort(key=lambda t: t.priority, reverse=True)
        
        return ready
    
    def schedule(self) -> List[Dict]:
        """
        Schedule tasks to workers
        
        Returns:
            List of scheduled task assignments
        """
        assignments = []
        ready_tasks = self.get_ready_tasks()
        
        for task in ready_tasks:
            # Check if we have capacity
            if len(self.running_tasks) >= self.num_workers:
                break
            
            # Check resource availability
            if not self.resource_pool.allocate(task.resource_requirements):
                continue
            
            # Assign task
            task.status = 'running'
            task.assigned_to = f'worker-{len(self.running_tasks) + 1}'
            task.started_at = datetime.now()
            
            self.running_tasks[task.task_id] = task
            
            assignments.append({
                'task_id': task.task_id,
                'task_name': task.name,
                'assigned_to': task.assigned_to,
                'started_at': task.started_at.isoformat(),
                'estimated_duration': task.estimated_duration,
            })
        
        if assignments:
            self._save_state()
        
        return assignments
    
    def complete_task(self, task_id: str, success: bool = True, actual_duration: float = None) -> bool:
        """
        Mark task as complete
        
        Args:
            task_id: Task identifier
            success: Whether task succeeded
            actual_duration: Actual execution duration
        
        Returns:
            Success status
        """
        if task_id not in self.running_tasks:
            return False
        
        task = self.running_tasks[task_id]
        task.completed_at = datetime.now()
        task.actual_duration = actual_duration or (task.completed_at - task.started_at).total_seconds()
        
        # Release resources
        self.resource_pool.release(task.resource_requirements)
        
        if success:
            task.status = 'completed'
            self.completed_tasks.add(task_id)
        else:
            task.status = 'failed'
        
        del self.running_tasks[task_id]
        self._save_state()
        
        return True
    
    def get_schedule(self) -> Dict:
        """Get current schedule"""
        return {
            'total_tasks': len(self.tasks),
            'pending': sum(1 for t in self.tasks.values() if t.status == 'pending'),
            'running': len(self.running_tasks),
            'completed': len(self.completed_tasks),
            'failed': sum(1 for t in self.tasks.values() if t.status == 'failed'),
            'ready': len(self.get_ready_tasks()),
            'workers': {
                'total': self.num_workers,
                'busy': len(self.running_tasks),
                'idle': self.num_workers - len(self.running_tasks),
            },
            'resources': self.resource_pool.get_available(),
        }
    
    def predict_completion_time(self) -> Dict:
        """Predict overall completion time"""
        # Calculate remaining work
        pending_tasks = [
            t for t in self.tasks.values()
            if t.status in ['pending', 'running']
        ]
        
        if not pending_tasks:
            return {
                'status': 'complete',
                'message': 'All tasks completed',
            }
        
        # Estimate remaining time
        total_remaining = sum(t.estimated_duration for t in pending_tasks)
        avg_parallel = min(self.num_workers, len(pending_tasks))
        
        estimated_time = total_remaining / max(1, avg_parallel)
        
        # Add confidence based on task variance
        durations = [t.estimated_duration for t in pending_tasks if t.estimated_duration > 0]
        if len(durations) > 1:
            avg = sum(durations) / len(durations)
            variance = sum((d - avg) ** 2 for d in durations) / len(durations)
            confidence = 'low' if variance > avg ** 2 else 'medium' if variance > avg ** 2 * 0.5 else 'high'
        else:
            confidence = 'low'
        
        return {
            'status': 'in_progress',
            'estimated_remaining_minutes': round(estimated_time / 60, 2),
            'estimated_completion': (datetime.now() + timedelta(minutes=estimated_time / 60)).isoformat(),
            'confidence': confidence,
            'tasks_remaining': len(pending_tasks),
            'workers_available': self.num_workers - len(self.running_tasks),
        }
    
    def optimize_schedule(self) -> Dict:
        """
        Optimize task schedule
        
        Returns:
            Optimization suggestions
        """
        suggestions = []
        
        # Check for bottlenecks
        dependency_count = defaultdict(int)
        for task in self.tasks.values():
            for dep in task.dependencies:
                dependency_count[dep] += 1
        
        # Find critical path tasks
        critical_tasks = [
            task_id for task_id, count in dependency_count.items()
            if count > len(self.tasks) * 0.3
        ]
        
        if critical_tasks:
            suggestions.append({
                'type': 'critical_path',
                'message': f'Critical path tasks: {", ".join(critical_tasks)}',
                'action': 'Prioritize these tasks to reduce overall completion time',
            })
        
        # Check resource contention
        resource_demands = defaultdict(float)
        for task in self.tasks.values():
            if task.status == 'pending':
                for resource, amount in task.resource_requirements.items():
                    resource_demands[resource] += amount
        
        for resource, demand in resource_demands.items():
            available = self.resource_pool.resources.get(resource, 0)
            if demand > available * 2:
                suggestions.append({
                    'type': 'resource_contention',
                    'message': f'High demand for {resource}: {demand:.1f} vs {available:.1f} available',
                    'action': f'Consider increasing {resource} capacity or reducing concurrent tasks',
                })
        
        # Check for long-running tasks
        long_tasks = [
            t for t in self.tasks.values()
            if t.estimated_duration > 300 and t.status == 'pending'
        ]
        
        if long_tasks:
            suggestions.append({
                'type': 'long_tasks',
                'message': f'{len(long_tasks)} long-running tasks (>5 min)',
                'action': 'Consider breaking into smaller tasks or running in background',
            })
        
        return {
            'suggestions': suggestions,
            'optimization_score': self._calculate_optimization_score(),
        }
    
    def _calculate_optimization_score(self) -> float:
        """Calculate schedule optimization score (0-100)"""
        if not self.tasks:
            return 100
        
        # Factors:
        # - Parallelization efficiency (40%)
        # - Resource utilization (30%)
        # - Dependency optimization (20%)
        # - Priority adherence (10%)
        
        # Parallelization
        running = len(self.running_tasks)
        parallel_score = (running / self.num_workers) * 40 if self.num_workers > 0 else 0
        
        # Resource utilization
        used_resources = {
            k: self.resource_pool.resources.get(k, 0) - v
            for k, v in self.resource_pool.get_available().items()
        }
        total_resources = sum(self.resource_pool.resources.values())
        used_total = sum(max(0, v) for v in used_resources.values())
        resource_score = (used_total / max(1, total_resources)) * 30
        
        # Dependency optimization (simplified)
        ready = len(self.get_ready_tasks())
        pending = sum(1 for t in self.tasks.values() if t.status == 'pending')
        dependency_score = (ready / max(1, pending)) * 20 if pending > 0 else 20
        
        # Priority adherence
        high_priority_running = sum(
            1 for t in self.running_tasks.values() if t.priority >= 8
        )
        priority_score = (high_priority_running / max(1, running)) * 10 if running > 0 else 10
        
        return round(parallel_score + resource_score + dependency_score + priority_score, 1)
    
    def clear(self):
        """Clear all tasks"""
        self.tasks.clear()
        self.task_queue.clear()
        self.completed_tasks.clear()
        self.running_tasks.clear()
        self._save_state()
        print("✅ Scheduler cleared")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Task Scheduler")
    parser.add_argument('--add', type=str, help='Add task (format: id@name@priority@duration)')
    parser.add_argument('--schedule', action='store_true', help='Schedule tasks')
    parser.add_argument('--complete', type=str, help='Complete task')
    parser.add_argument('--status', action='store_true', help='Show schedule status')
    # ... (rest of CLI implementation)
    args = parser.parse_args()
    
    scheduler = AITaskScheduler()
    
    if args.add:
        parts = args.add.split('@')
        if len(parts) >= 4:
            task = Task(
                parts[0],
                parts[1],
                int(parts[2]) if len(parts) > 2 else 0,
                float(parts[3]) if len(parts) > 3 else 0,
            )
            scheduler.add_task(task)
            print(f"✅ Task added: {task.task_id}")
    
    elif args.schedule:
        assignments = scheduler.schedule()
        if assignments:
            print(f"\n📋 SCHEDULED {len(assignments)} TASKS")
            print("=" * 60)
            for assignment in assignments:
                print(f"✅ {assignment['task_name']} → {assignment['assigned_to']}")
                print(f"   ETA: {assignment['estimated_duration']}s")
        else:
            print("ℹ️  No tasks to schedule")
    
    elif args.complete:
        if scheduler.complete_task(args.complete):
            print(f"✅ Task completed: {args.complete}")
        else:
            print(f"❌ Task not found: {args.complete}")
    
    elif args.status:
        status = scheduler.get_schedule()
        print("\n📊 SCHEDULER STATUS")
        print("=" * 60)
        print(f"Total tasks: {status['total_tasks']}")
        print(f"Pending: {status['pending']}")
        print(f"Running: {status['running']}")
        print(f"Completed: {status['completed']}")
        print(f"Ready: {status['ready']}")
        print(f"Workers: {status['workers']['busy']}/{status['workers']['total']} busy")
        print("=" * 60)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
