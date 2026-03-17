#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maintenance Scheduler - Proactive maintenance scheduling

Features:
- Optimal timing calculation
- Impact minimization
- Auto-scheduling
- Maintenance window optimization
- Conflict detection
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / 'data' / 'maintenance'
DATA_DIR.mkdir(parents=True, exist_ok=True)

SCHEDULE_FILE = DATA_DIR / 'maintenance_schedule.json'
HISTORY_FILE = DATA_DIR / 'maintenance_history.json'

class MaintenanceTask:
    """Represents a maintenance task"""
    
    def __init__(self, task_id: str, name: str, duration_minutes: int, priority: str = 'medium'):
        self.task_id = task_id
        self.name = name
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.dependencies = []
        self.impact_level = 'medium'
        self.requires_downtime = False
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'name': self.name,
            'duration_minutes': self.duration_minutes,
            'priority': self.priority,
            'dependencies': self.dependencies,
            'impact_level': self.impact_level,
            'requires_downtime': self.requires_downtime,
        }


class OptimalTimingCalculator:
    """Calculate optimal maintenance timing"""
    
    def __init__(self):
        # Low-traffic windows (default: 2-5 AM)
        self.preferred_windows = {
            'weekday': {'start': 2, 'end': 5},
            'weekend': {'start': 3, 'end': 7},
        }
        
        # Blackout periods (avoid these)
        self.blackout_periods = [
            {'name': 'Business hours', 'start': 9, 'end': 18},
            {'name': 'Peak traffic', 'start': 12, 'end': 14},
        ]
    
    def calculate(self, task: MaintenanceTask, urgency: str = 'normal') -> Dict:
        """Calculate optimal timing"""
        now = datetime.now()
        
        # Find next available window
        next_window = self._find_next_window(now, task.duration_minutes)
        
        # Adjust for urgency
        if urgency == 'critical':
            # Schedule immediately
            optimal_time = now + timedelta(minutes=15)  # 15 min prep
            score = 1.0
        elif urgency == 'high':
            # Schedule within 24 hours
            optimal_time = next_window['start']
            score = 0.8
        else:
            # Use optimal window
            optimal_time = next_window['start']
            score = next_window['score']
        
        # Calculate end time
        end_time = optimal_time + timedelta(minutes=task.duration_minutes)
        
        return {
            'optimal_start': optimal_time.isoformat(),
            'optimal_end': end_time.isoformat(),
            'duration_minutes': task.duration_minutes,
            'timing_score': round(score, 2),
            'window_type': next_window.get('type', 'custom'),
            'reasoning': self._generate_reasoning(optimal_time, urgency, next_window),
        }
    
    def _find_next_window(self, now: datetime, duration: int) -> Dict:
        """Find next available maintenance window"""
        # Check if weekend
        is_weekend = now.weekday() >= 5
        
        window_config = self.preferred_windows['weekend' if is_weekend else 'weekday']
        
        # Today's window
        window_start = now.replace(
            hour=window_config['start'],
            minute=0,
            second=0,
            microsecond=0
        )
        
        # If window already passed today, use tomorrow
        if now > window_start:
            window_start += timedelta(days=1)
            is_weekend = window_start.weekday() >= 5
            window_config = self.preferred_windows['weekend' if is_weekend else 'weekday']
            window_start = window_start.replace(hour=window_config['start'])
        
        # Check if window is long enough
        window_duration = window_config['end'] - window_config['start']
        
        if window_duration * 60 >= duration:
            return {
                'start': window_start,
                'score': 0.9,
                'type': 'preferred',
            }
        else:
            # Need extended window
            return {
                'start': window_start,
                'score': 0.7,
                'type': 'extended',
            }
    
    def _generate_reasoning(self, time: datetime, urgency: str, window: Dict) -> str:
        """Generate timing reasoning"""
        if urgency == 'critical':
            return 'Critical maintenance - scheduled immediately'
        
        hour = time.hour
        if 2 <= hour <= 5:
            return 'Scheduled during low-traffic window (2-5 AM)'
        elif time.weekday() >= 5:
            return 'Scheduled during weekend for minimal impact'
        else:
            return f'Scheduled during {window["type"]} maintenance window'


class ImpactAnalyzer:
    """Analyze maintenance impact"""
    
    def __init__(self):
        self.impact_factors = {
            'time_of_day': {'low': 0.2, 'medium': 0.5, 'high': 0.9},
            'day_of_week': {'weekend': 0.3, 'weekday': 0.7},
            'duration': {'short': 0.2, 'medium': 0.5, 'long': 0.8},
            'scope': {'single': 0.3, 'partial': 0.6, 'full': 1.0},
        }
    
    def analyze(self, task: MaintenanceTask, scheduled_time: datetime) -> Dict:
        """Analyze impact"""
        # Time of day impact
        hour = scheduled_time.hour
        if 2 <= hour <= 5:
            time_impact = 'low'
        elif 9 <= hour <= 18:
            time_impact = 'high'
        else:
            time_impact = 'medium'
        
        # Day of week impact
        dow_impact = 'weekend' if scheduled_time.weekday() >= 5 else 'weekday'
        
        # Duration impact
        if task.duration_minutes < 30:
            duration_impact = 'short'
        elif task.duration_minutes < 120:
            duration_impact = 'medium'
        else:
            duration_impact = 'long'
        
        # Calculate overall impact score
        impact_score = (
            self.impact_factors['time_of_day'][time_impact] * 0.3 +
            self.impact_factors['day_of_week'][dow_impact] * 0.3 +
            self.impact_factors['duration'][duration_impact] * 0.2 +
            self.impact_factors['scope']['single'] * 0.2
        )
        
        # Impact level
        if impact_score >= 0.7:
            level = 'high'
        elif impact_score >= 0.4:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'overall_score': round(impact_score, 2),
            'level': level,
            'factors': {
                'time_of_day': time_impact,
                'day_of_week': dow_impact,
                'duration': duration_impact,
                'scope': 'single',
            },
            'affected_users': self._estimate_affected_users(time_impact, dow_impact),
            'downtime_minutes': task.duration_minutes if task.requires_downtime else 0,
        }
    
    def _estimate_affected_users(self, time_impact: str, dow_impact: str) -> str:
        """Estimate affected users"""
        base_users = 1000  # Assumed total users
        
        time_multiplier = {'low': 0.1, 'medium': 0.3, 'high': 0.8}
        dow_multiplier = {'weekend': 0.5, 'weekday': 1.0}
        
        affected = int(base_users * time_multiplier[time_impact] * dow_multiplier[dow_impact])
        
        return f"~{affected} users"


class ConflictDetector:
    """Detect scheduling conflicts"""
    
    def __init__(self):
        self.scheduled_maintenance = self._load_schedule()
    
    def _load_schedule(self) -> List[Dict]:
        """Load scheduled maintenance"""
        if SCHEDULE_FILE.exists():
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def check_conflict(self, task: MaintenanceTask, proposed_time: datetime) -> Dict:
        """Check for conflicts"""
        end_time = proposed_time + timedelta(minutes=task.duration_minutes)
        
        conflicts = []
        
        for scheduled in self.scheduled_maintenance:
            sched_start = datetime.fromisoformat(scheduled['start_time'])
            sched_end = datetime.fromisoformat(scheduled['end_time'])
            
            # Check overlap
            if proposed_time < sched_end and end_time > sched_start:
                conflicts.append({
                    'task_id': scheduled['task_id'],
                    'task_name': scheduled['task_name'],
                    'overlap_minutes': self._calculate_overlap(
                        proposed_time, end_time, sched_start, sched_end
                    ),
                    'severity': 'high',
                })
        
        # Check blackout periods
        blackout_conflicts = self._check_blackout(proposed_time, end_time)
        
        return {
            'has_conflict': len(conflicts) > 0 or len(blackout_conflicts) > 0,
            'maintenance_conflicts': conflicts,
            'blackout_conflicts': blackout_conflicts,
            'total_conflicts': len(conflicts) + len(blackout_conflicts),
            'can_proceed': len(conflicts) == 0 and len(blackout_conflicts) == 0,
        }
    
    def _calculate_overlap(self, start1: datetime, end1: datetime,
                          start2: datetime, end2: datetime) -> int:
        """Calculate overlap in minutes"""
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        if overlap_start < overlap_end:
            return int((overlap_end - overlap_start).total_seconds() / 60)
        return 0
    
    def _check_blackout(self, start: datetime, end: datetime) -> List[Dict]:
        """Check blackout period conflicts"""
        conflicts = []
        
        blackout_periods = [
            {'name': 'Business hours', 'start': 9, 'end': 18},
        ]
        
        for period in blackout_periods:
            # Check if maintenance overlaps with blackout
            maint_hours = set(range(start.hour, (end.hour % 24) + 1))
            blackout_hours = set(range(period['start'], period['end']))
            
            overlap = maint_hours & blackout_hours
            
            if overlap:
                conflicts.append({
                    'period': period['name'],
                    'overlap_hours': list(overlap),
                    'severity': 'medium',
                    'recommendation': 'Reschedule to non-business hours',
                })
        
        return conflicts


class AutoScheduler:
    """Automatically schedule maintenance"""
    
    def __init__(self):
        self.timing_calculator = OptimalTimingCalculator()
        self.impact_analyzer = ImpactAnalyzer()
        self.conflict_detector = ConflictDetector()
    
    def schedule(self, task: MaintenanceTask, urgency: str = 'normal') -> Dict:
        """Auto-schedule maintenance task"""
        # Calculate optimal timing
        timing = self.timing_calculator.calculate(task, urgency)
        
        proposed_time = datetime.fromisoformat(timing['optimal_start'])
        
        # Check conflicts
        conflicts = self.conflict_detector.check_conflict(task, proposed_time)
        
        # If conflicts, find alternative
        if conflicts['has_conflict']:
            # For simplicity, just add 24 hours
            proposed_time += timedelta(days=1)
            timing = self.timing_calculator.calculate(task, urgency)
            timing['optimal_start'] = proposed_time.isoformat()
            timing['optimal_end'] = (proposed_time + timedelta(minutes=task.duration_minutes)).isoformat()
            conflicts = self.conflict_detector.check_conflict(task, proposed_time)
        
        # Analyze impact
        impact = self.impact_analyzer.analyze(task, proposed_time)
        
        # Generate schedule
        schedule = {
            'task_id': task.task_id,
            'task_name': task.name,
            'start_time': timing['optimal_start'],
            'end_time': timing['optimal_end'],
            'duration_minutes': task.duration_minutes,
            'urgency': urgency,
            'timing_score': timing['timing_score'],
            'impact_level': impact['level'],
            'impact_score': impact['overall_score'],
            'conflicts': conflicts,
            'status': 'scheduled' if conflicts['can_proceed'] else 'conflict',
        }
        
        # Save schedule
        self._save_schedule(schedule)
        
        return schedule
    
    def _save_schedule(self, schedule: Dict):
        """Save schedule"""
        schedules = []
        if SCHEDULE_FILE.exists():
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                schedules = json.load(f)
        
        schedules.append(schedule)
        
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, indent=2)


class MaintenanceScheduler:
    """
    Proactive maintenance scheduling
    
    Features:
    - Optimal timing calculation
    - Impact minimization
    - Auto-scheduling
    - Maintenance window optimization
    - Conflict detection
    """
    
    def __init__(self):
        self.scheduler = AutoScheduler()
        self.task_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load maintenance task templates"""
        return {
            'system_update': {
                'name': 'System Update',
                'duration': 60,
                'priority': 'medium',
                'requires_downtime': True,
            },
            'database_maintenance': {
                'name': 'Database Maintenance',
                'duration': 90,
                'priority': 'high',
                'requires_downtime': False,
            },
            'security_patch': {
                'name': 'Security Patch',
                'duration': 30,
                'priority': 'critical',
                'requires_downtime': True,
            },
            'backup_verification': {
                'name': 'Backup Verification',
                'duration': 45,
                'priority': 'low',
                'requires_downtime': False,
            },
            'performance_tuning': {
                'name': 'Performance Tuning',
                'duration': 120,
                'priority': 'medium',
                'requires_downtime': False,
            },
        }
    
    def create_task(self, template: str, custom_name: str = None) -> MaintenanceTask:
        """Create maintenance task from template"""
        config = self.task_templates.get(template, {
            'name': 'Custom Maintenance',
            'duration': 60,
            'priority': 'medium',
            'requires_downtime': False,
        })
        
        task = MaintenanceTask(
            task_id=f"{template}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=custom_name or config['name'],
            duration_minutes=config['duration'],
            priority=config['priority'],
        )
        
        task.requires_downtime = config['requires_downtime']
        
        return task
    
    def schedule_maintenance(self, task: MaintenanceTask, urgency: str = 'normal') -> Dict:
        """Schedule maintenance"""
        return self.scheduler.schedule(task, urgency)
    
    def get_upcoming_maintenance(self, days: int = 7) -> List[Dict]:
        """Get upcoming maintenance"""
        if not SCHEDULE_FILE.exists():
            return []
        
        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            schedules = json.load(f)
        
        cutoff = datetime.now() + timedelta(days=days)
        
        upcoming = [
            s for s in schedules
            if datetime.fromisoformat(s['start_time']) <= cutoff
            and s['status'] == 'scheduled'
        ]
        
        upcoming.sort(key=lambda x: x['start_time'])
        
        return upcoming
    
    def print_schedule(self, schedule: Dict):
        """Print maintenance schedule"""
        print("\n" + "=" * 60)
        print("📅 MAINTENANCE SCHEDULE")
        print("=" * 60)
        
        print(f"\n🔧 Task: {schedule['task_name']}")
        print(f"ID: {schedule['task_id']}")
        
        start = datetime.fromisoformat(schedule['start_time'])
        end = datetime.fromisoformat(schedule['end_time'])
        
        print(f"\n⏰ Schedule:")
        print(f"   Start: {start.strftime('%Y-%m-%d %H:%M')}")
        print(f"   End: {end.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Duration: {schedule['duration_minutes']} minutes")
        
        print(f"\n📊 Impact:")
        print(f"   Level: {schedule['impact_level']}")
        print(f"   Score: {schedule['impact_score']:.1%}")
        print(f"   Timing Score: {schedule['timing_score']:.1%}")
        
        if schedule['conflicts']['has_conflict']:
            print(f"\n⚠️  Conflicts Detected:")
            for conflict in schedule['conflicts'].get('maintenance_conflicts', []):
                print(f"   - {conflict['task_name']} ({conflict['overlap_minutes']} min overlap)")
            for conflict in schedule['conflicts'].get('blackout_conflicts', []):
                print(f"   - {conflict['period']}")
        else:
            print(f"\n✅ No conflicts detected")
        
        print(f"\n🎯 Status: {schedule['status'].upper()}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Maintenance Scheduler")
    parser.add_argument('--schedule', action='store_true', help='Demo scheduling')
    parser.add_argument('--template', type=str, default='system_update', help='Task template')
    parser.add_argument('--urgency', type=str, default='normal', help='Urgency level')
    args = parser.parse_args()
    
    scheduler = MaintenanceScheduler()
    
    if args.schedule:
        # Create task from template
        task = scheduler.create_task(args.template)
        
        # Schedule
        schedule = scheduler.schedule_maintenance(task, args.urgency)
        
        # Print
        scheduler.print_schedule(schedule)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
