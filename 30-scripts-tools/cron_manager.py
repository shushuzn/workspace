#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Cron Task Auto-Manager
Automatically manage cron tasks

Usage:
    python cron_manager.py [--add TASK] [--remove TASK] [--list] [--validate]
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class CronManager:
    """Manage cron tasks"""
    
    def __init__(self, config_file: str = None):
        self.config_file = Path(config_file) if config_file else Path(__file__).parent / 'cron_tasks.json'
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> list:
        """Load cron tasks"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both list and object format
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get('tasks', [])
        return []
    
    def _save_tasks(self):
        """Save cron tasks"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)
    
    def add_task(self, name: str, command: str, schedule: str, 
                 enabled: bool = True) -> dict:
        """Add cron task"""
        # Check for conflicts
        conflicts = self._check_conflicts(name, schedule)
        
        if conflicts:
            return {
                'status': 'conflict',
                'message': f'Conflicts with: {", ".join(conflicts)}',
                'conflicts': conflicts
            }
        
        task = {
            'name': name,
            'command': command,
            'schedule': schedule,
            'enabled': enabled,
            'created_at': datetime.now().isoformat(),
            'last_run': None,
            'run_count': 0
        }
        
        self.tasks.append(task)
        self._save_tasks()
        
        return {
            'status': 'success',
            'message': f'Task "{name}" added',
            'task': task
        }
    
    def remove_task(self, name: str) -> dict:
        """Remove cron task"""
        for i, task in enumerate(self.tasks):
            if task['name'] == name:
                removed = self.tasks.pop(i)
                self._save_tasks()
                return {
                    'status': 'success',
                    'message': f'Task "{name}" removed',
                    'task': removed
                }
        
        return {
            'status': 'not_found',
            'message': f'Task "{name}" not found'
        }
    
    def list_tasks(self) -> list:
        """List all tasks"""
        return self.tasks
    
    def _check_conflicts(self, name: str, schedule: str) -> list:
        """Check for schedule conflicts"""
        conflicts = []
        
        for task in self.tasks:
            if task['name'] == name:
                conflicts.append(f"{name} (same name)")
            elif task['schedule'] == schedule and task['enabled']:
                conflicts.append(f"{task['name']} (same schedule)")
        
        return conflicts
    
    def validate_all(self) -> dict:
        """Validate all tasks"""
        validation = {
            'total': len(self.tasks),
            'enabled': sum(1 for t in self.tasks if t.get('enabled')),
            'disabled': sum(1 for t in self.tasks if not t.get('enabled')),
            'conflicts': [],
            'warnings': []
        }
        
        # Check for duplicate schedules
        schedules = {}
        for task in self.tasks:
            if task.get('enabled'):
                sched = task['schedule']
                if sched in schedules:
                    validation['conflicts'].append({
                        'tasks': [schedules[sched], task['name']],
                        'schedule': sched
                    })
                else:
                    schedules[sched] = task['name']
        
        return validation


class ConflictDetector:
    """Detect cron task conflicts"""
    
    def detect(self, tasks: list) -> list:
        """Detect conflicts"""
        conflicts = []
        
        # Group by schedule
        by_schedule = {}
        for task in tasks:
            if task.get('enabled'):
                sched = task['schedule']
                if sched not in by_schedule:
                    by_schedule[sched] = []
                by_schedule[sched].append(task['name'])
        
        # Find conflicts
        for schedule, names in by_schedule.items():
            if len(names) > 1:
                conflicts.append({
                    'type': 'schedule_conflict',
                    'schedule': schedule,
                    'tasks': names,
                    'severity': 'warning' if len(names) == 2 else 'high'
                })
        
        return conflicts


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cron Manager')
    parser.add_argument('--add', type=str, nargs=3, metavar=('NAME', 'CMD', 'SCHEDULE'),
                       help='Add task: name command schedule')
    parser.add_argument('--remove', type=str, help='Remove task by name')
    parser.add_argument('--list', action='store_true', help='List tasks')
    parser.add_argument('--validate', action='store_true', help='Validate tasks')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    manager = CronManager()
    
    # Add
    if args.add:
        name, cmd, schedule = args.add
        result = manager.add_task(name, cmd, schedule)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"[{result['status'].upper()}] {result['message']}")
    
    # Remove
    elif args.remove:
        result = manager.remove_task(args.remove)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"[{result['status'].upper()}] {result['message']}")
    
    # List
    elif args.list:
        tasks = manager.list_tasks()
        
        if args.json:
            print(json.dumps(tasks, indent=2, ensure_ascii=False))
        else:
            print(f"[TASKS] {len(tasks)} tasks")
            for task in tasks:
                status = "[OK]" if task.get('enabled') else "[FAIL]"
                print(f"  {status} {task['name']}: {task['schedule']}")
    
    # Validate
    elif args.validate:
        validation = manager.validate_all()
        
        if args.json:
            print(json.dumps(validation, indent=2, ensure_ascii=False))
        else:
            print(f"[VALIDATE] {validation['total']} tasks")
            print(f"  Enabled: {validation['enabled']}")
            print(f"  Disabled: {validation['disabled']}")
            if validation['conflicts']:
                print(f"  Conflicts: {len(validation['conflicts'])}")
                for c in validation['conflicts']:
                    print(f"    [WARN] {c['tasks']} at {c['schedule']}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
