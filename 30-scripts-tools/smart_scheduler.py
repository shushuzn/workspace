#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Smart Scheduler Optimizer - Phase 4 Innovation
Optimizes task scheduling based on historical performance
Features: ML-based prediction, resource allocation, conflict resolution

Usage:
    python smart_scheduler.py --optimize
    python smart_scheduler.py --simulate
    python smart_scheduler.py --schedule
    python smart_scheduler.py --analyze
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

# Workspace root
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "20-data-reports" / "scheduler"
CONFIG_FILE = DATA_DIR / "scheduler-config.json"
HISTORY_FILE = DATA_DIR / "execution-history.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class SmartSchedulerOptimizer:
    """Optimize task scheduling with ML-based predictions"""
    
    def __init__(self):
        self.config = self._load_config()
        self.history = self._load_history()
    
    def _load_config(self) -> Dict:
        """Load scheduler configuration"""
        default_config = {
            "version": "1.0",
            "tasks": {
                "heartbeat": {"priority": 1, "interval_minutes": 30, "estimated_duration_seconds": 180},
                "health_check": {"priority": 2, "interval_minutes": 60, "estimated_duration_seconds": 60},
                "data_collection": {"priority": 3, "interval_minutes": 1440, "estimated_duration_seconds": 300},
                "memory_maintenance": {"priority": 4, "interval_minutes": 1440, "estimated_duration_seconds": 120},
                "knowledge_graph_update": {"priority": 5, "interval_minutes": 1440, "estimated_duration_seconds": 90},
                "self_healing_scan": {"priority": 1, "interval_minutes": 30, "estimated_duration_seconds": 120},
                "cache_stats": {"priority": 6, "interval_minutes": 60, "estimated_duration_seconds": 30},
            },
            "constraints": {
                "max_concurrent": 3,
                "max_cpu_percent": 80,
                "quiet_hours": {"start": 2, "end": 6},  # 2AM-6AM
                "preferred_hours": {"start": 9, "end": 18}
            }
        }
        
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
    
    def _load_history(self) -> Dict:
        """Load execution history"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"executions": []}
    
    def _save_config(self):
        """Save configuration"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def analyze_execution_times(self) -> Dict[str, Dict]:
        """Analyze historical execution times"""
        task_stats = {}
        
        for execution in self.history.get('executions', []):
            for result in execution.get('results', []):
                task_id = result.get('task_id', 'unknown')
                
                if task_id not in task_stats:
                    task_stats[task_id] = {
                        'times': [],
                        'failures': 0,
                        'successes': 0
                    }
                
                if 'duration_seconds' in result:
                    task_stats[task_id]['times'].append(result['duration_seconds'])
                
                if result.get('status') == 'success':
                    task_stats[task_id]['successes'] += 1
                else:
                    task_stats[task_id]['failures'] += 1
        
        # Calculate statistics
        for task_id, stats in task_stats.items():
            times = stats['times']
            if times:
                stats['avg_duration'] = sum(times) / len(times)
                stats['min_duration'] = min(times)
                stats['max_duration'] = max(times)
                stats['total_runs'] = len(times)
                
                # Calculate failure rate
                total = stats['successes'] + stats['failures']
                stats['failure_rate'] = stats['failures'] / total if total > 0 else 0
        
        return task_stats
    
    def predict_optimal_schedule(self) -> List[Dict]:
        """Predict optimal schedule based on history"""
        task_stats = self.analyze_execution_times()
        
        # Update estimated durations with actual averages
        for task_id, stats in task_stats.items():
            if task_id in self.config['tasks'] and 'avg_duration' in stats:
                # Use weighted average of configured and actual
                configured = self.config['tasks'][task_id].get('estimated_duration_seconds', 0)
                actual = stats['avg_duration']
                
                # Weight actual data more if we have enough samples
                if stats.get('total_runs', 0) >= 5:
                    predicted = actual * 0.8 + configured * 0.2
                else:
                    predicted = configured
                
                self.config['tasks'][task_id]['predicted_duration_seconds'] = round(predicted, 2)
                self.config['tasks'][task_id]['failure_rate'] = round(stats.get('failure_rate', 0), 3)
        
        self._save_config()
        
        # Generate schedule
        schedule = self._generate_schedule()
        
        return schedule
    
    def _generate_schedule(self) -> List[Dict]:
        """Generate optimized schedule"""
        schedule = []
        
        # Sort tasks by priority
        sorted_tasks = sorted(
            self.config['tasks'].items(),
            key=lambda x: x[1].get('priority', 99)
        )
        
        current_time = datetime.now()
        scheduled_times = []
        
        for task_id, task_config in sorted_tasks:
            interval = task_config.get('interval_minutes', 60)
            
            # Calculate next run time
            next_run = current_time + timedelta(minutes=interval)
            
            # Adjust for quiet hours
            if self._is_in_quiet_hours(next_run):
                next_run = self._get_post_quiet_time(next_run)
            
            # Check for conflicts
            next_run = self._resolve_conflicts(next_run, scheduled_times, task_config)
            
            scheduled_times.append(next_run)
            
            schedule.append({
                'task_id': task_id,
                'next_run': next_run.isoformat(),
                'interval_minutes': interval,
                'priority': task_config.get('priority', 99),
                'estimated_duration': task_config.get('predicted_duration_seconds', 
                                    task_config.get('estimated_duration_seconds', 0)),
                'failure_rate': task_config.get('failure_rate', 0)
            })
        
        return schedule
    
    def _is_in_quiet_hours(self, dt: datetime) -> bool:
        """Check if time is in quiet hours"""
        quiet = self.config['constraints'].get('quiet_hours', {})
        start = quiet.get('start', 2)
        end = quiet.get('end', 6)
        
        if start <= end:
            return start <= dt.hour < end
        else:
            # Quiet hours span midnight
            return dt.hour >= start or dt.hour < end
    
    def _get_post_quiet_time(self, dt: datetime) -> datetime:
        """Get first time after quiet hours"""
        quiet = self.config['constraints'].get('quiet_hours', {})
        end = quiet.get('end', 6)
        
        return dt.replace(hour=end, minute=0, second=0, microsecond=0)
    
    def _resolve_conflicts(self, proposed_time: datetime, 
                          scheduled_times: List[datetime],
                          task_config: Dict) -> datetime:
        """Resolve scheduling conflicts"""
        max_concurrent = self.config['constraints'].get('max_concurrent', 3)
        
        # Simple conflict resolution: shift by 5 minutes if too many concurrent
        for offset in range(0, 60, 5):
            test_time = proposed_time + timedelta(minutes=offset)
            
            concurrent = sum(
                1 for t in scheduled_times
                if abs((t - test_time).total_seconds()) < 300  # Within 5 minutes
            )
            
            if concurrent < max_concurrent:
                return test_time
        
        return proposed_time  # Return original if no better slot found
    
    def simulate_schedule(self, hours: int = 24) -> Dict:
        """Simulate schedule execution"""
        print(f"[SIMULATE] Simulating {hours}h schedule...")
        
        schedule = self.predict_optimal_schedule()
        
        # Simulate execution
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=hours)
        
        execution_timeline = []
        resource_usage = []
        
        current_time = start_time
        while current_time < end_time:
            # Find tasks running at this time
            running = []
            for task in schedule:
                next_run = datetime.fromisoformat(task['next_run'])
                duration = timedelta(seconds=task.get('estimated_duration', 60))
                
                if next_run <= current_time < next_run + duration:
                    running.append(task['task_id'])
            
            if running:
                execution_timeline.append({
                    'time': current_time.isoformat(),
                    'running_tasks': running,
                    'concurrent_count': len(running)
                })
            
            resource_usage.append({
                'time': current_time.isoformat(),
                'concurrent_tasks': len(running)
            })
            
            current_time += timedelta(minutes=5)
        
        # Calculate statistics
        max_concurrent = max(r['concurrent_tasks'] for r in resource_usage) if resource_usage else 0
        avg_concurrent = sum(r['concurrent_tasks'] for r in resource_usage) / len(resource_usage) if resource_usage else 0
        
        print(f"\n{'=' * 60}")
        print(f"Simulation Results ({hours}h)")
        print(f"{'=' * 60}")
        print(f"Max concurrent tasks: {max_concurrent}")
        print(f"Avg concurrent tasks: {avg_concurrent:.2f}")
        print(f"Total execution points: {len(execution_timeline)}")
        print(f"{'=' * 60}")
        
        return {
            'schedule': schedule,
            'timeline': execution_timeline[:100],  # Limit
            'statistics': {
                'max_concurrent': max_concurrent,
                'avg_concurrent': avg_concurrent,
                'total_points': len(execution_timeline)
            }
        }
    
    def show_analysis(self):
        """Show scheduling analysis"""
        print("\n" + "=" * 60)
        print("Scheduler Optimization Analysis")
        print("=" * 60)
        
        task_stats = self.analyze_execution_times()
        
        print("\nTask Performance:")
        for task_id, stats in sorted(task_stats.items()):
            print(f"\n  {task_id}:")
            print(f"    Total runs:    {stats.get('total_runs', 0)}")
            print(f"    Avg duration:  {stats.get('avg_duration', 0):.2f}s")
            print(f"    Min/Max:       {stats.get('min_duration', 0):.2f}s / {stats.get('max_duration', 0):.2f}s")
            print(f"    Failure rate:  {stats.get('failure_rate', 0) * 100:.1f}%")
        
        print("\n" + "=" * 60)
    
    def show_schedule(self):
        """Show optimized schedule"""
        print("\n" + "=" * 60)
        print("Optimized Schedule")
        print("=" * 60)
        
        schedule = self.predict_optimal_schedule()
        
        print(f"\n{'Task':<25} {'Next Run':<22} {'Interval':<10} {'Priority':<8} {'Est. Duration':<12}")
        print("-" * 80)
        
        for task in schedule:
            next_run = datetime.fromisoformat(task['next_run']).strftime('%Y-%m-%d %H:%M')
            interval = f"{task['interval_minutes']} min"
            priority = str(task['priority'])
            duration = f"{task.get('estimated_duration', 0):.1f}s"
            
            print(f"{task['task_id']:<25} {next_run:<22} {interval:<10} {priority:<8} {duration:<12}")
        
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Smart Scheduler Optimizer')
    parser.add_argument('--optimize', action='store_true', help='Optimize schedule')
    parser.add_argument('--simulate', type=int, nargs='?', default=24, help='Simulate N hours')
    parser.add_argument('--schedule', action='store_true', help='Show schedule')
    parser.add_argument('--analyze', action='store_true', help='Analyze performance')
    args = parser.parse_args()
    
    optimizer = SmartSchedulerOptimizer()
    
    if args.optimize:
        optimizer.predict_optimal_schedule()
        print("[OK] Schedule optimized")
    
    if args.simulate:
        optimizer.simulate_schedule(args.simulate)
    
    if args.schedule:
        optimizer.show_schedule()
    
    if args.analyze:
        optimizer.show_analysis()
    
    if not any([args.optimize, args.simulate, args.schedule, args.analyze]):
        parser.print_help()


if __name__ == "__main__":
    main()
