#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cross-System Orchestrator - Unified Coordination
Coordinates all Phase 4+ systems for optimal collaboration
Features: System registry, dependency management, execution planning, conflict resolution

Usage:
    python system_orchestrator.py --status
    python system_orchestrator.py --plan
    python system_orchestrator.py --execute
    python system_orchestrator.py --optimize
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class SystemStatus(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class SystemInfo:
    """System registry information"""
    id: str
    name: str
    script: str
    status: SystemStatus
    last_run: Optional[str]
    run_count: int
    avg_duration: float
    dependencies: List[str]
    priority: int  # 1-10, higher = more important


@dataclass
class ExecutionPlan:
    """Execution plan"""
    id: str
    created_at: str
    systems: List[str]
    order: List[str]
    estimated_duration: float
    status: str  # pending/running/completed/failed


class CrossSystemOrchestrator:
    """Orchestrate all Phase 4+ systems"""
    
    def __init__(self):
        self.registry_file = WORKSPACE / "20-data-reports" / "system_registry.json"
        self.plans_file = WORKSPACE / "20-data-reports" / "execution_plans.json"
        
        self.systems = {}
        self.plans = []
        
        self._register_systems()
        self.load_state()
    
    def _register_systems(self):
        """Register all Phase 4+ systems"""
        default_systems = [
            SystemInfo(
                id='self_iteration',
                name='Self-Iteration Engine',
                script='30-scripts-tools/self_iter_cli.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=[],
                priority=10
            ),
            SystemInfo(
                id='meta_learning',
                name='Meta-Learning System',
                script='30-scripts-tools/meta_learning.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=['self_iteration'],
                priority=9
            ),
            SystemInfo(
                id='evolution',
                name='Evolution Engine',
                script='30-scripts-tools/evolution_engine.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=['meta_learning'],
                priority=9
            ),
            SystemInfo(
                id='recommendations',
                name='Smart Recommendations',
                script='30-scripts-tools/smart_recommendations.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=['self_iteration', 'meta_learning'],
                priority=8
            ),
            SystemInfo(
                id='dashboard',
                name='Self-Iteration Dashboard',
                script='30-scripts-tools/self_iter_dashboard.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=[],
                priority=7
            ),
            SystemInfo(
                id='heartbeat',
                name='HEARTBEAT Integration',
                script='30-scripts-tools/heartbeat_integration.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=['self_iteration'],
                priority=10
            ),
            SystemInfo(
                id='persona_collab',
                name='7-Persona Collaboration',
                script='30-scripts-tools/persona_cli.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=[],
                priority=10
            ),
            SystemInfo(
                id='workflow_engine',
                name='Workflow Engine',
                script='30-scripts-tools/workflow_engine_v2.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=[],
                priority=9
            ),
            SystemInfo(
                id='cache_manager',
                name='Cache Manager',
                script='30-scripts-tools/cache_manager.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=[],
                priority=8
            ),
            SystemInfo(
                id='self_healing',
                name='Self-Healing System',
                script='30-scripts-tools/self_healing.py',
                status=SystemStatus.IDLE,
                last_run=None,
                run_count=0,
                avg_duration=0.0,
                dependencies=[],
                priority=10
            )
        ]
        
        self.systems = {s.id: s for s in default_systems}
    
    def load_state(self):
        """Load state"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for sys_id, sys_data in data.get('systems', {}).items():
                        if sys_id in self.systems:
                            self.systems[sys_id].last_run = sys_data.get('last_run')
                            self.systems[sys_id].run_count = sys_data.get('run_count', 0)
                            self.systems[sys_id].avg_duration = sys_data.get('avg_duration', 0.0)
            except:
                pass
        
        if self.plans_file.exists():
            try:
                with open(self.plans_file, 'r', encoding='utf-8') as f:
                    self.plans = json.load(f)
            except:
                pass
    
    def save_state(self):
        """Save state"""
        data = {
            'systems': {sid: asdict(s) for sid, s in self.systems.items()},
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        with open(self.plans_file, 'w', encoding='utf-8') as f:
            json.dump(self.plans, f, indent=2, ensure_ascii=False)
    
    def get_status(self) -> Dict:
        """Get system status"""
        status = {
            'total_systems': len(self.systems),
            'by_status': {},
            'systems': {},
            'last_updated': datetime.now().isoformat()
        }
        
        for sys_id, sys_info in self.systems.items():
            # Count by status
            status_str = sys_info.status.value
            status['by_status'][status_str] = status['by_status'].get(status_str, 0) + 1
            
            # System details
            status['systems'][sys_id] = {
                'name': sys_info.name,
                'status': status_str,
                'last_run': sys_info.last_run,
                'run_count': sys_info.run_count,
                'avg_duration': f"{sys_info.avg_duration:.1f}s",
                'priority': sys_info.priority,
                'dependencies': sys_info.dependencies
            }
        
        return status
    
    def create_execution_plan(self, system_ids: List[str] = None) -> ExecutionPlan:
        """Create execution plan"""
        print("\n" + "="*60)
        print(" Creating Execution Plan")
        print("="*60 + "\n")
        
        if not system_ids:
            # Default: run all active systems in dependency order
            system_ids = list(self.systems.keys())
        
        # Topological sort by dependencies
        ordered = self._topological_sort(system_ids)
        
        # Estimate duration
        total_duration = sum(self.systems[sid].avg_duration for sid in ordered if sid in self.systems)
        
        plan = ExecutionPlan(
            id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            created_at=datetime.now().isoformat(),
            systems=ordered,
            order=ordered,
            estimated_duration=total_duration,
            status='pending'
        )
        
        self.plans.append(asdict(plan))
        self.save_state()
        
        print(f"Created execution plan: {plan.id}")
        print(f"Systems: {len(ordered)}")
        print(f"Order: {' → '.join(ordered)}")
        print(f"Estimated duration: {total_duration:.1f}s\n")
        
        return plan
    
    def _topological_sort(self, system_ids: List[str]) -> List[str]:
        """Sort systems by dependencies"""
        visited = set()
        result = []
        
        def visit(sys_id: str):
            if sys_id in visited:
                return
            visited.add(sys_id)
            
            # Visit dependencies first
            if sys_id in self.systems:
                for dep in self.systems[sys_id].dependencies:
                    if dep in system_ids:
                        visit(dep)
            
            result.append(sys_id)
        
        for sys_id in system_ids:
            visit(sys_id)
        
        return result
    
    def execute_plan(self, plan_id: str = None) -> bool:
        """Execute execution plan"""
        print("\n" + "="*60)
        print(" Executing Plan")
        print("="*60 + "\n")
        
        # Find plan
        if plan_id:
            plan = next((p for p in self.plans if p['id'] == plan_id), None)
        else:
            # Use latest pending plan
            plan = next((p for p in self.plans if p['status'] == 'pending'), None)
        
        if not plan:
            print("❌ No plan found")
            return False
        
        plan['status'] = 'running'
        plan['started_at'] = datetime.now().isoformat()
        
        success_count = 0
        
        for sys_id in plan['order']:
            if sys_id not in self.systems:
                continue
            
            sys_info = self.systems[sys_id]
            
            print(f"\n▶️  Running: {sys_info.name}")
            print(f"   Script: {sys_info.script}")
            
            try:
                # Execute system
                start_time = datetime.now()
                
                cmd = [sys.executable, str(WORKSPACE / sys_info.script)]
                
                # Add appropriate command based on system
                if sys_id == 'self_iteration':
                    cmd.append('full')
                elif sys_id == 'meta_learning':
                    cmd.append('--full')
                elif sys_id == 'evolution':
                    cmd.append('--evolve')
                elif sys_id == 'recommendations':
                    cmd.append('--generate')
                elif sys_id == 'heartbeat':
                    cmd.append('--run')
                else:
                    cmd.append('--status')
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Update system stats
                sys_info.run_count += 1
                sys_info.avg_duration = (
                    (sys_info.avg_duration * (sys_info.run_count - 1) + duration) /
                    sys_info.run_count
                )
                sys_info.last_run = end_time.isoformat()
                
                if result.returncode == 0:
                    print(f"   ✅ Success ({duration:.1f}s)")
                    success_count += 1
                else:
                    print(f"   ❌ Failed: {result.stderr[:200]}")
                
            except subprocess.TimeoutExpired:
                print(f"   ❌ Timeout (5 minutes)")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        plan['status'] = 'completed'
        plan['completed_at'] = datetime.now().isoformat()
        plan['success_rate'] = success_count / len(plan['order'])
        
        self.save_state()
        
        print(f"\n{'='*60}")
        print(f" Execution Complete")
        print(f"{'='*60}")
        print(f"Success: {success_count}/{len(plan['order'])}")
        print(f"Rate: {plan['success_rate']*100:.0f}%")
        
        return True
    
    def optimize_systems(self) -> Dict:
        """Optimize system configuration"""
        print("\n" + "="*60)
        print(" System Optimization")
        print("="*60 + "\n")
        
        optimizations = []
        
        # Optimization 1: Parallel execution
        independent_systems = [
            sid for sid, s in self.systems.items()
            if not s.dependencies
        ]
        
        if len(independent_systems) > 1:
            optimizations.append({
                'id': 'opt_parallel',
                'type': 'parallel_execution',
                'description': f'Run {len(independent_systems)} independent systems in parallel',
                'systems': independent_systems,
                'estimated_savings': '40-60%',
                'priority': 'high'
            })
        
        # Optimization 2: Priority scheduling
        high_priority = [
            sid for sid, s in self.systems.items()
            if s.priority >= 9
        ]
        
        optimizations.append({
            'id': 'opt_priority',
            'type': 'priority_scheduling',
            'description': f'Prioritize {len(high_priority)} high-priority systems',
            'systems': high_priority,
            'estimated_impact': 'Better resource allocation',
            'priority': 'medium'
        })
        
        # Optimization 3: Caching
        optimizations.append({
            'id': 'opt_caching',
            'type': 'result_caching',
            'description': 'Cache system results to avoid redundant execution',
            'ttl_minutes': 30,
            'estimated_savings': '30-50%',
            'priority': 'high'
        })
        
        for opt in optimizations:
            print(f"🔧 [{opt['type'].upper()}] {opt['description']}")
            print(f"   Priority: {opt['priority']}")
            if 'estimated_savings' in opt:
                print(f"   Savings: {opt['estimated_savings']}")
            print()
        
        return {
            'optimizations': optimizations,
            'count': len(optimizations)
        }
    
    def get_recommendations(self) -> List[Dict]:
        """Get orchestration recommendations"""
        recommendations = []
        
        # Check for systems that haven't run recently
        for sys_id, sys_info in self.systems.items():
            if sys_info.last_run:
                last_run = datetime.fromisoformat(sys_info.last_run)
                hours_since = (datetime.now() - last_run).total_seconds() / 3600
                
                if hours_since > 24:
                    recommendations.append({
                        'type': 'stale_system',
                        'system': sys_id,
                        'message': f'{sys_info.name} hasn\'t run in {hours_since:.1f} hours',
                        'action': f'Run {sys_id}'
                    })
        
        return recommendations


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cross-System Orchestrator')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--plan', action='store_true', help='Create execution plan')
    parser.add_argument('--execute', action='store_true', help='Execute plan')
    parser.add_argument('--optimize', action='store_true', help='Optimize systems')
    parser.add_argument('--systems', nargs='+', help='Specific systems to include')
    args = parser.parse_args()
    
    orchestrator = CrossSystemOrchestrator()
    
    if args.status:
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.plan:
        plan = orchestrator.create_execution_plan(args.systems)
        print(f"Plan created: {plan.id}")
    
    elif args.execute:
        success = orchestrator.execute_plan()
        sys.exit(0 if success else 1)
    
    elif args.optimize:
        result = orchestrator.optimize_systems()
        print(f"Found {result['count']} optimizations")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
