#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Windows Task Scheduler - Auto-configure Windows scheduled tasks

Usage:
    python windows_task_scheduler.py --install    # Install all tasks
    python windows_task_scheduler.py --uninstall  # Remove all tasks
    python windows_task_scheduler.py --list       # List installed tasks
    python windows_task_scheduler.py --status     # Check task status
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Config
WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / '30-scripts-tools'
TASK_PREFIX = "OpenClaw"

class WindowsTaskScheduler:
    """Windows Task Scheduler configuration"""
    
    def __init__(self):
        self.tasks = self._define_tasks()
    
    def _define_tasks(self) -> List[Dict]:
        """Define all scheduled tasks"""
        python_exe = sys.executable
        
        return [
            {
                'name': f'{TASK_PREFIX}-Heartbeat',
                'description': 'Run HEARTBEAT workflow every 30 minutes',
                'command': f'{python_exe} "{SCRIPTS_DIR}\\heartbeat_workflow.py"',
                'schedule': '*/30 * * * *',  # Every 30 minutes
                'trigger': 'ONLOGON',
                'repetition': 'MINUTE:30',
                'enabled': True,
                'run_as': 'SYSTEM',
                'priority': 'HIGH'
            },
            {
                'name': f'{TASK_PREFIX}-Daily-Collection',
                'description': 'Collect data from arXiv, GitHub, Medium at 7AM',
                'command': f'{python_exe} "{SCRIPTS_DIR}\\automation_orchestrator.py" --daily',
                'schedule': '0 7 * * *',  # Daily at 7AM
                'trigger': 'DAILY:07:00',
                'enabled': True,
                'run_as': 'SYSTEM',
                'priority': 'NORMAL'
            },
            {
                'name': f'{TASK_PREFIX}-Hourly-Health',
                'description': 'Run health check every hour',
                'command': f'{python_exe} "{SCRIPTS_DIR}\\dashboard_health_widget.py"',
                'schedule': '0 * * * *',  # Every hour
                'trigger': 'ONLOGON',
                'repetition': 'HOUR:1',
                'enabled': True,
                'run_as': 'SYSTEM',
                'priority': 'LOW'
            },
            {
                'name': f'{TASK_PREFIX}-Memory-Maintenance',
                'description': 'Run memory maintenance daily at 11PM',
                'command': f'{python_exe} "{SCRIPTS_DIR}\\memory-maintenance.py"',
                'schedule': '0 23 * * *',  # Daily at 11PM
                'trigger': 'DAILY:23:00',
                'enabled': True,
                'run_as': 'SYSTEM',
                'priority': 'LOW'
            },
            {
                'name': f'{TASK_PREFIX}-Weekly-Distill',
                'description': 'Run memory distiller every Sunday at 5AM',
                'command': f'{python_exe} "{SCRIPTS_DIR}\\memory-distiller.py" --weekly',
                'schedule': '0 5 * * 0',  # Sunday at 5AM
                'trigger': 'WEEKLY:Sunday:05:00',
                'enabled': True,
                'run_as': 'SYSTEM',
                'priority': 'NORMAL'
            },
            {
                'name': f'{TASK_PREFIX}-Quality-Review',
                'description': 'Run quality scorer every 6 hours',
                'command': f'{python_exe} "{SCRIPTS_DIR}\\quality_scorer.py" --all "{WORKSPACE}" --save',
                'schedule': '0 */6 * * *',  # Every 6 hours
                'trigger': 'ONLOGON',
                'repetition': 'HOUR:6',
                'enabled': False,  # Disabled by default (resource intensive)
                'run_as': 'SYSTEM',
                'priority': 'LOW'
            },
            {
                'name': f'{TASK_PREFIX}-Knowledge-Graph',
                'description': 'Update knowledge graph daily at 8AM',
                'command': f'{python_exe} "{SCRIPTS_DIR}\\knowledge_graph_updater.py" --update --save',
                'schedule': '0 8 * * *',  # Daily at 8AM
                'trigger': 'DAILY:08:00',
                'enabled': True,
                'run_as': 'SYSTEM',
                'priority': 'NORMAL'
            }
        ]
    
    def install_tasks(self) -> Dict:
        """Install all tasks to Windows Task Scheduler"""
        results = {'installed': [], 'failed': [], 'skipped': []}
        
        print(f"\n[LIST] Installing {len(self.tasks)} scheduled tasks...\n")
        
        for task in self.tasks:
            if not task.get('enabled', True):
                print(f"⏭️ Skipping (disabled): {task['name']}")
                results['skipped'].append(task['name'])
                continue
            
            try:
                # Create task using schtasks
                cmd = self._build_schtasks_command(task)
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"[OK] Installed: {task['name']}")
                    results['installed'].append(task['name'])
                else:
                    # Task might already exist, update it
                    if 'ERROR' in result.stdout or 'ERROR' in result.stderr:
                        # Try to update existing task
                        update_cmd = self._build_schtasks_command(task, update=True)
                        update_result = subprocess.run(
                            update_cmd,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if update_result.returncode == 0:
                            print(f"🔄 Updated: {task['name']}")
                            results['installed'].append(task['name'])
                        else:
                            print(f"[FAIL] Failed: {task['name']} - {update_result.stderr[:100]}")
                            results['failed'].append({
                                'name': task['name'],
                                'error': update_result.stderr[:100]
                            })
                    else:
                        print(f"[OK] Installed: {task['name']}")
                        results['installed'].append(task['name'])
                        
            except Exception as e:
                print(f"[FAIL] Failed: {task['name']} - {str(e)}")
                results['failed'].append({
                    'name': task['name'],
                    'error': str(e)
                })
        
        return results
    
    def _build_schtasks_command(self, task: Dict, update: bool = False) -> List[str]:
        """Build schtasks command"""
        cmd = ['schtasks']
        
        if update:
            cmd.extend(['/Change', '/TN', task['name']])
        else:
            cmd.extend(['/Create', '/TN', task['name']])
        
        cmd.extend(['/TR', task['command']])
        
        # Build schedule based on trigger type
        schedule_cmd = self._build_schedule_command(task['trigger'])
        cmd.extend(schedule_cmd)
        
        cmd.extend(['/RL', 'HIGHEST'])  # Run with highest privileges
        cmd.extend(['/F'])  # Force
        
        return cmd
    
    def _build_schedule_command(self, trigger: str) -> List[str]:
        """Build schedule command based on trigger type"""
        result = []
        
        if trigger == 'ONLOGON':
            result.extend(['/SC', 'ONLOGON'])
        elif trigger.startswith('MINUTE:'):
            interval = trigger.split(':')[1]
            result.extend(['/SC', 'MINUTE', '/MO', interval])
        elif trigger.startswith('HOUR:'):
            interval = trigger.split(':')[1]
            result.extend(['/SC', 'HOURLY', '/MO', interval])
        elif trigger.startswith('DAILY:'):
            time = trigger.split(':')[1] + ':' + trigger.split(':')[2] if ':' in trigger.split(':')[1] else trigger.split(':')[1] + ':00'
            result.extend(['/SC', 'DAILY', '/ST', time.replace(':', '')[:4]])
        elif trigger.startswith('WEEKLY:'):
            parts = trigger.split(':')
            day = parts[1]
            time = parts[2] + ':00' if len(parts) > 2 else '00:00'
            result.extend(['/SC', 'WEEKLY', '/D', day.upper()[:2], '/ST', time.replace(':', '')[:4]])
        
        return result
    
    def uninstall_tasks(self) -> Dict:
        """Uninstall all tasks from Windows Task Scheduler"""
        results = {'uninstalled': [], 'failed': [], 'not_found': []}
        
        print(f"\n🗑️ Uninstalling {TASK_PREFIX}* tasks...\n")
        
        # First, list all existing tasks
        existing = self.list_tasks()
        
        for task_name in existing.get('tasks', []):
            if not task_name.startswith(TASK_PREFIX):
                continue
            
            try:
                cmd = ['schtasks', '/Delete', '/TN', task_name, '/F']
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"[OK] Uninstalled: {task_name}")
                    results['uninstalled'].append(task_name)
                else:
                    print(f"[FAIL] Failed: {task_name}")
                    results['failed'].append(task_name)
                    
            except Exception as e:
                print(f"[FAIL] Failed: {task_name} - {str(e)}")
                results['failed'].append(task_name)
        
        return results
    
    def list_tasks(self) -> Dict:
        """List all OpenClaw tasks"""
        results = {'tasks': [], 'details': []}
        
        try:
            cmd = ['schtasks', '/Query', '/FO', 'LIST', '/V']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            # Parse output
            lines = result.stdout.split('\n')
            current_task = {}
            
            for line in lines:
                if line.startswith(f"{TASK_PREFIX}-"):
                    if current_task:
                        results['details'].append(current_task)
                    current_task = {'name': line.split(':')[1].strip() if ':' in line else line.strip()}
                    results['tasks'].append(current_task['name'])
                elif ':' in line and current_task:
                    key, value = line.split(':', 1)
                    current_task[key.strip()] = value.strip()
            
            if current_task:
                results['details'].append(current_task)
                
        except Exception as e:
            print(f"[WARN] List failed: {e}")
        
        return results
    
    def check_status(self) -> Dict:
        """Check status of all tasks"""
        results = {}
        
        existing = self.list_tasks()
        
        for task_name in existing.get('tasks', []):
            try:
                cmd = ['schtasks', '/Query', '/TN', task_name, '/FO', 'LIST', '/V']
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8'
                )
                
                # Parse status
                status = 'Unknown'
                last_run = 'Never'
                next_run = 'Unknown'
                
                for line in result.stdout.split('\n'):
                    if 'Status:' in line:
                        status = line.split(':')[1].strip()
                    elif 'Last Run Time:' in line:
                        last_run = line.split(':')[1].strip()
                    elif 'Next Run Time:' in line:
                        next_run = line.split(':')[1].strip()
                
                results[task_name] = {
                    'status': status,
                    'last_run': last_run,
                    'next_run': next_run
                }
                
            except Exception as e:
                results[task_name] = {'error': str(e)}
        
        return results
    
    def save_config(self, output_file: Path = None):
        """Save task configuration to JSON"""
        if output_file is None:
            output_file = SCRIPTS_DIR / 'windows_tasks_config.json'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'workspace': str(WORKSPACE),
            'tasks': self.tasks
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Config saved to {output_file}")
    
    def print_summary(self, results: Dict):
        """Print installation summary"""
        print(f"\n{'='*60}")
        print(f"[CHART] Task Scheduler Summary")
        print(f"{'='*60}")
        
        if 'installed' in results:
            print(f"[OK] Installed: {len(results['installed'])}")
            for name in results['installed']:
                print(f"   - {name}")
        
        if 'failed' in results:
            print(f"[FAIL] Failed: {len(results['failed'])}")
            for item in results['failed']:
                if isinstance(item, dict):
                    print(f"   - {item['name']}: {item['error'][:50]}")
                else:
                    print(f"   - {item}")
        
        if 'skipped' in results:
            print(f"⏭️ Skipped: {len(results['skipped'])}")
            for name in results['skipped']:
                print(f"   - {name}")
        
        print(f"{'='*60}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows Task Scheduler')
    parser.add_argument('--install', action='store_true', help='Install all tasks')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall all tasks')
    parser.add_argument('--list', action='store_true', help='List installed tasks')
    parser.add_argument('--status', action='store_true', help='Check task status')
    parser.add_argument('--save-config', action='store_true', help='Save configuration')
    
    args = parser.parse_args()
    
    scheduler = WindowsTaskScheduler()
    
    if args.install:
        results = scheduler.install_tasks()
        scheduler.print_summary(results)
    elif args.uninstall:
        results = scheduler.uninstall_tasks()
        scheduler.print_summary(results)
    elif args.list:
        results = scheduler.list_tasks()
        print(f"\n[LIST] Installed Tasks ({len(results['tasks'])}):")
        for task in results['tasks']:
            print(f"   - {task}")
    elif args.status:
        results = scheduler.check_status()
        print(f"\n[CHART] Task Status:")
        for name, status in results.items():
            icon = '[OK]' if status.get('status') == 'Ready' else '[WARN]'
            print(f"   {icon} {name}: {status.get('status', 'Unknown')}")
    elif args.save_config:
        scheduler.save_config()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
