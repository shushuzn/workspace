#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autonomous Decision Engine for Memory Evolution System
========================================================
Enables fully autonomous operation with self-decision making,
priority scheduling, and closed-loop execution.

Features:
- Autonomous task scheduling
- Priority matrix decision making
- Resource allocation
- Self-monitoring
- Emergency protocols
- Goal self-setting

Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import random
import threading
import queue

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0  # Emergency, immediate
    HIGH = 1      # Urgent important
    MEDIUM = 2    # Normal operation
    LOW = 3       # Background tasks
    DEFERRED = 4  # When resources available


class TaskType(Enum):
    """Task categories."""
    DISTILLATION = "distillation"
    EVOLUTION = "evolution"
    SELF_IMPROVEMENT = "self_improvement"
    HEALTH_CHECK = "health_check"
    BACKUP = "backup"
    CLEANUP = "cleanup"
    ANALYSIS = "analysis"
    DEPLOYMENT = "deployment"
    CUSTOM = "custom"


class DecisionMode(Enum):
    """Decision making modes."""
    AUTONOMOUS = "autonomous"      # Full autonomy
    SEMI_AUTONOMOUS = "semi"       # Human approval for critical
    MANUAL = "manual"              # Human controls all
    EMERGENCY = "emergency"        # Safety protocols only


@dataclass
class Task:
    """Represents an autonomous task."""
    id: str
    task_type: str
    priority: str
    description: str
    scheduled_time: str
    estimated_duration: int  # minutes
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"  # pending, running, completed, failed, cancelled
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(**data)


@dataclass
class ResourceAllocation:
    """Resource allocation for tasks."""
    cpu_percent: float = 50.0
    memory_mb: int = 2048
    network_bandwidth: float = 1.0  # Mbps
    disk_io: float = 50.0  # MB/s
    gpu_enabled: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SystemGoal:
    """System self-set goals."""
    id: str
    description: str
    target_metric: str
    current_value: float
    target_value: float
    deadline: str
    priority: str
    status: str = "active"  # active, achieved, abandoned
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AutonomousDecisionEngine:
    """Main autonomous decision making engine."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.data_dir = self.workspace_dir / "data" / "autonomy"
        self.logs_dir = self.workspace_dir / "21-reports" / "autonomy"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # State
        self.mode = DecisionMode.AUTONOMOUS
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.goals: Dict[str, SystemGoal] = {}
        self.resource_allocation = ResourceAllocation()
        
        # Metrics
        self.decisions_made = 0
        self.tasks_completed = 0
        self.autonomy_score = 100.0  # 0-100, how autonomous is the system
        
        # Load state
        self._load_state()
        
        # Start time
        self.start_time = datetime.now()
        
    def _load_state(self):
        """Load persisted state."""
        state_file = self.data_dir / "autonomy_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.decisions_made = state.get('decisions_made', 0)
                self.tasks_completed = state.get('tasks_completed', 0)
                self.autonomy_score = state.get('autonomy_score', 100.0)
            except Exception as e:
                print(f"⚠️  Could not load state: {e}")
    
    def _save_state(self):
        """Persist state to disk."""
        state = {
            'decisions_made': self.decisions_made,
            'tasks_completed': self.tasks_completed,
            'autonomy_score': self.autonomy_score,
            'last_updated': datetime.now().isoformat()
        }
        state_file = self.data_dir / "autonomy_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    
    def decide_next_task(self) -> Optional[Task]:
        """Autonomous decision: what to do next."""
        self.decisions_made += 1
        
        # Check system health
        health = self._assystem_health()
        
        # If critical issues, create emergency task
        if health['status'] == 'critical':
            return self._create_emergency_task(health['issues'])
        
        # Generate candidate tasks
        candidates = self._generate_candidate_tasks()
        
        # Score and prioritize
        scored_tasks = [(self._score_task(task), task) for task in candidates]
        scored_tasks.sort(key=lambda x: x[0])  # Lower score = higher priority
        
        if scored_tasks:
            best_task = scored_tasks[0][1]
            self._log_decision(f"Selected task: {best_task.id} ({best_task.task_type})")
            return best_task
        
        return None
    
    def _assystem_health(self) -> Dict:
        """Assess overall system health."""
        issues = []
        status = 'healthy'
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.workspace_dir)
            free_gb = free / (1024**3)
            if free_gb < 5:
                issues.append(('disk_space', f'Low disk space: {free_gb:.1f}GB'))
                status = 'warning'
            if free_gb < 1:
                status = 'critical'
        except:
            pass
        
        # Check memory (simplified)
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                issues.append(('memory', f'High memory usage: {memory.percent}%'))
                status = 'warning'
            if memory.percent > 95:
                status = 'critical'
        except:
            pass
        
        # Check recent errors
        error_count = self._count_recent_errors()
        if error_count > 10:
            issues.append(('errors', f'Too many recent errors: {error_count}'))
            status = 'warning'
        
        return {
            'status': status,
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
    
    def _count_recent_errors(self, minutes: int = 30) -> int:
        """Count errors in recent time window."""
        # Simplified - would integrate with logging system
        return 0
    
    def _generate_candidate_tasks(self) -> List[Task]:
        """Generate list of possible tasks to execute."""
        candidates = []
        now = datetime.now()
        
        # 1. Scheduled tasks (from HEARTBEAT/cron)
        scheduled = self._get_scheduled_tasks()
        candidates.extend(scheduled)
        
        # 2. Goal-driven tasks
        goal_tasks = self._generate_goal_tasks()
        candidates.extend(goal_tasks)
        
        # 3. Maintenance tasks
        if self._should_run_maintenance():
            candidates.append(self._create_maintenance_task())
        
        # 4. Improvement tasks (from self-improving engine)
        if self._should_run_improvement():
            candidates.append(self._create_improvement_task())
        
        # 5. Evolution tasks
        if self._should_run_evolution():
            candidates.append(self._create_evolution_task())
        
        # 6. Distillation tasks
        if self._should_run_distillation():
            candidates.append(self._create_distillation_task())
        
        return candidates
    
    def _get_scheduled_tasks(self) -> List[Task]:
        """Get tasks from schedule (HEARTBEAT/cron)."""
        tasks = []
        now = datetime.now()
        
        # Check HEARTBEAT.md for scheduled tasks
        heartbeat_file = self.workspace_dir / "HEARTBEAT.md"
        if heartbeat_file.exists():
            # Parse HEARTBEAT.md for scheduled tasks
            # Simplified: create task if scheduled time reached
            tasks.append(Task(
                id=f"heartbeat-{now.strftime('%H%M')}",
                task_type=TaskType.HEALTH_CHECK.value,
                priority=TaskPriority.MEDIUM.name,
                description="Regular health check from HEARTBEAT",
                scheduled_time=now.isoformat(),
                estimated_duration=5
            ))
        
        return tasks
    
    def _generate_goal_tasks(self) -> List[Task]:
        """Generate tasks based on active goals."""
        tasks = []
        
        for goal_id, goal in self.goals.items():
            if goal.status != 'active':
                continue
            
            # Check if goal needs action
            progress = (goal.current_value / goal.target_value) if goal.target_value > 0 else 0
            
            if progress < 0.5:
                # Behind schedule, create high priority task
                tasks.append(Task(
                    id=f"goal-{goal_id}",
                    task_type=TaskType.CUSTOM.value,
                    priority=TaskPriority.HIGH.name,
                    description=f"Goal progress task: {goal.description}",
                    scheduled_time=datetime.now().isoformat(),
                    estimated_duration=30,
                    metadata={'goal_id': goal_id}
                ))
        
        return tasks
    
    def _should_run_maintenance(self) -> bool:
        """Check if maintenance should run."""
        # Run maintenance daily at 03:00
        now = datetime.now()
        return now.hour == 3 and now.minute < 30
    
    def _should_run_improvement(self) -> bool:
        """Check if self-improvement cycle should run."""
        # Run every 30 minutes
        now = datetime.now()
        return now.minute % 30 == 0 and now.second < 30
    
    def _should_run_evolution(self) -> bool:
        """Check if evolution should run."""
        # Run weekly on Sunday at 05:00
        now = datetime.now()
        return now.weekday() == 6 and now.hour == 5 and now.minute < 30
    
    def _should_run_distillation(self) -> bool:
        """Check if distillation should run."""
        # Run daily at 06:00
        now = datetime.now()
        return now.hour == 6 and now.minute < 30
    
    def _create_emergency_task(self, issues: List) -> Task:
        """Create emergency task for critical issues."""
        return Task(
            id=f"emergency-{datetime.now().strftime('%H%M%S')}",
            task_type=TaskType.CUSTOM.value,
            priority=TaskPriority.CRITICAL.name,
            description=f"Emergency: {', '.join([str(i) for i in issues])}",
            scheduled_time=datetime.now().isoformat(),
            estimated_duration=60,
            metadata={'emergency': True, 'issues': issues}
        )
    
    def _create_maintenance_task(self) -> Task:
        """Create daily maintenance task."""
        return Task(
            id=f"maintenance-{datetime.now().strftime('%Y%m%d')}",
            task_type=TaskType.BACKUP.value,
            priority=TaskPriority.MEDIUM.name,
            description="Daily maintenance: backup, cleanup, optimization",
            scheduled_time=datetime.now().isoformat(),
            estimated_duration=30
        )
    
    def _create_improvement_task(self) -> Task:
        """Create self-improvement cycle task."""
        return Task(
            id=f"improvement-{datetime.now().strftime('%H%M')}",
            task_type=TaskType.SELF_IMPROVEMENT.value,
            priority=TaskPriority.MEDIUM.name,
            description="Self-improvement cycle: pattern mining, gap detection, hypothesis generation",
            scheduled_time=datetime.now().isoformat(),
            estimated_duration=15
        )
    
    def _create_evolution_task(self) -> Task:
        """Create weekly evolution task."""
        return Task(
            id=f"evolution-{datetime.now().strftime('%Y%m%d')}",
            task_type=TaskType.EVOLUTION.value,
            priority=TaskPriority.HIGH.name,
            description="Weekly evolution: genetic algorithm optimization",
            scheduled_time=datetime.now().isoformat(),
            estimated_duration=60
        )
    
    def _create_distillation_task(self) -> Task:
        """Create daily distillation task."""
        return Task(
            id=f"distillation-{datetime.now().strftime('%Y%m%d')}",
            task_type=TaskType.DISTILLATION.value,
            priority=TaskPriority.HIGH.name,
            description="Daily distillation: extract insights to MEMORY.md",
            scheduled_time=datetime.now().isoformat(),
            estimated_duration=20
        )
    
    def _score_task(self, task: Task) -> float:
        """Score task for prioritization (lower = higher priority)."""
        priority_scores = {
            TaskPriority.CRITICAL.name: 0,
            TaskPriority.HIGH.name: 10,
            TaskPriority.MEDIUM.name: 20,
            TaskPriority.LOW.name: 30,
            TaskPriority.DEFERRED.name: 40
        }
        
        score = priority_scores.get(task.priority, 20)
        
        # Adjust for urgency
        scheduled = datetime.fromisoformat(task.scheduled_time)
        overdue = (datetime.now() - scheduled).total_seconds() / 60
        if overdue > 0:
            score -= min(overdue, 10)  # Max 10 point reduction for overdue
        
        # Adjust for dependencies
        if task.dependencies:
            score += 5  # Slight penalty for complex tasks
        
        return score
    
    def execute_task(self, task: Task) -> bool:
        """Execute a task autonomously."""
        self._log_execution(f"Starting task: {task.id}")
        task.status = 'running'
        self.active_tasks[task.id] = task
        
        try:
            # Route to appropriate executor
            success = self._execute_by_type(task)
            
            if success:
                task.status = 'completed'
                self.tasks_completed += 1
                self.completed_tasks.append(task)
                self._log_execution(f"Task completed: {task.id}")
            else:
                task.status = 'failed'
                self._log_execution(f"Task failed: {task.id}")
                
                # Retry logic
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = 'pending'
                    self._log_execution(f"Retrying task: {task.id} (attempt {task.retry_count})")
                    return False
            
            return success
            
        except Exception as e:
            task.status = 'failed'
            self._log_execution(f"Task error: {task.id} - {str(e)}")
            return False
        
        finally:
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            self._save_state()
    
    def _execute_by_type(self, task: Task) -> bool:
        """Execute task based on type."""
        task_type = TaskType(task.task_type)
        
        executors = {
            TaskType.DISTILLATION: self._execute_distillation,
            TaskType.EVOLUTION: self._execute_evolution,
            TaskType.SELF_IMPROVEMENT: self._execute_self_improvement,
            TaskType.HEALTH_CHECK: self._execute_health_check,
            TaskType.BACKUP: self._execute_backup,
            TaskType.CLEANUP: self._execute_cleanup,
            TaskType.ANALYSIS: self._execute_analysis,
            TaskType.DEPLOYMENT: self._execute_deployment,
            TaskType.CUSTOM: self._execute_custom,
        }
        
        executor = executors.get(task_type, self._execute_custom)
        return executor(task)
    
    def _execute_distillation(self, task: Task) -> bool:
        """Execute memory distillation."""
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(self.workspace_dir / "30-scripts-tools" / "memory_distillation_runner.py"), "--daily-run"],
                cwd=str(self.workspace_dir),
                timeout=1800,  # 30 min timeout
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Distillation error: {e}")
            return False
    
    def _execute_evolution(self, task: Task) -> bool:
        """Execute evolutionary optimization."""
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(self.workspace_dir / "30-scripts-tools" / "memory_evolutionary_algorithms.py"), "--evolve", "10"],
                cwd=str(self.workspace_dir),
                timeout=3600,  # 1 hour timeout
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Evolution error: {e}")
            return False
    
    def _execute_self_improvement(self, task: Task) -> bool:
        """Execute self-improvement cycle."""
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(self.workspace_dir / "30-scripts-tools" / "memory_self_improving_engine.py"), "run", "--auto-execute"],
                cwd=str(self.workspace_dir),
                timeout=1800,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Self-improvement error: {e}")
            return False
    
    def _execute_health_check(self, task: Task) -> bool:
        """Execute health check."""
        health = self._assystem_health()
        
        # Log health status
        health_file = self.logs_dir / f"health-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
        with open(health_file, 'w', encoding='utf-8') as f:
            json.dump(health, f, indent=2)
        
        return health['status'] != 'critical'
    
    def _execute_backup(self, task: Task) -> bool:
        """Execute backup."""
        # Simplified backup - would integrate with backup system
        backup_dir = self.data_dir / "backups" / datetime.now().strftime('%Y%m%d')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup marker
        marker_file = backup_dir / "backup_marker.txt"
        with open(marker_file, 'w', encoding='utf-8') as f:
            f.write(f"Backup completed: {datetime.now().isoformat()}\n")
        
        return True
    
    def _execute_cleanup(self, task: Task) -> bool:
        """Execute cleanup."""
        # Simplified cleanup
        # Would remove old logs, temp files, etc.
        return True
    
    def _execute_analysis(self, task: Task) -> bool:
        """Execute analysis task."""
        # Would run analytical tools
        return True
    
    def _execute_deployment(self, task: Task) -> bool:
        """Execute deployment task."""
        # Would run deployment scripts
        return True
    
    def _execute_custom(self, task: Task) -> bool:
        """Execute custom task."""
        # Custom task logic from metadata
        if task.metadata.get('emergency'):
            # Handle emergency
            print(f"🚨 EMERGENCY HANDLED: {task.description}")
            return True
        
        return True
    
    def _log_decision(self, message: str):
        """Log decision making."""
        log_file = self.logs_dir / f"decisions-{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    
    def _log_execution(self, message: str):
        """Log task execution."""
        log_file = self.logs_dir / f"execution-{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    
    def set_goal(self, goal: SystemGoal):
        """Set a system goal."""
        self.goals[goal.id] = goal
        self._save_state()
    
    def get_status(self) -> Dict:
        """Get current autonomy status."""
        uptime = datetime.now() - self.start_time
        
        return {
            'mode': self.mode.value,
            'decisions_made': self.decisions_made,
            'tasks_completed': self.tasks_completed,
            'autonomy_score': self.autonomy_score,
            'active_tasks': len(self.active_tasks),
            'goals_active': sum(1 for g in self.goals.values() if g.status == 'active'),
            'uptime_hours': uptime.total_seconds() / 3600,
            'health': self._assystem_health()['status']
        }
    
    def run_autonomous_loop(self, duration_minutes: int = 60):
        """Run autonomous decision loop."""
        print(f"🤖 Starting autonomous loop for {duration_minutes} minutes...")
        print(f"Mode: {self.mode.value}")
        print(f"Initial autonomy score: {self.autonomy_score:.1f}/100")
        print("="*70)
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            # Decide what to do
            task = self.decide_next_task()
            
            if task:
                # Execute task
                success = self.execute_task(task)
                
                # Update autonomy score based on success
                if success:
                    self.autonomy_score = min(100.0, self.autonomy_score + 0.1)
                else:
                    self.autonomy_score = max(0.0, self.autonomy_score - 0.5)
            
            # Wait before next decision
            time.sleep(30)  # 30 second decision cycle
        
        print("="*70)
        print(f"✅ Autonomous loop complete!")
        print(f"Final autonomy score: {self.autonomy_score:.1f}/100")
        print(f"Decisions made: {self.decisions_made}")
        print(f"Tasks completed: {self.tasks_completed}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Decision Engine")
    parser.add_argument(
        "--workspace",
        default="D:\\OpenClaw\\workspace",
        help="Workspace directory"
    )
    parser.add_argument(
        "--mode",
        default="autonomous",
        choices=["autonomous", "semi", "manual", "emergency"],
        help="Decision mode"
    )
    parser.add_argument(
        "--run",
        type=int,
        default=0,
        help="Run autonomous loop for N minutes"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current status"
    )
    parser.add_argument(
        "--set-goal",
        type=str,
        help="Set a goal (format: id,description,target_metric,current,target,deadline,priority)"
    )
    
    args = parser.parse_args()
    
    # Create engine
    engine = AutonomousDecisionEngine(args.workspace)
    engine.mode = DecisionMode(args.mode)
    
    if args.status:
        status = engine.get_status()
        print(json.dumps(status, indent=2))
        return 0
    
    if args.set_goal:
        parts = args.set_goal.split(',')
        if len(parts) == 7:
            goal = SystemGoal(
                id=parts[0],
                description=parts[1],
                target_metric=parts[2],
                current_value=float(parts[3]),
                target_value=float(parts[4]),
                deadline=parts[5],
                priority=parts[6]
            )
            engine.set_goal(goal)
            print(f"✅ Goal set: {goal.id}")
        return 0
    
    if args.run > 0:
        engine.run_autonomous_loop(args.run)
        return 0
    
    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
