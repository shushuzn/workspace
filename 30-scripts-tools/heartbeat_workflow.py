#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HEARTBEAT Workflow Orchestrator v2.0
Automated 7-persona workflow execution every 30 minutes

Usage:
    python heartbeat_workflow.py [--config CONFIG] [--dry-run]
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class HeartbeatWorkflow:
    """Orchestrate 7-persona automated workflow"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or Path(__file__).parent / 'heartbeat_config.json'
        self.config = self._load_config()
        self.results = {}
        self.start_time = datetime.now()
        
    def _load_config(self) -> dict:
        """Load workflow configuration"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> dict:
        """Default workflow configuration"""
        return {
            "workflow_name": "7-Persona Auto-Workflow",
            "version": "2.0",
            "interval_minutes": 30,
            "enabled_personas": [
                "metacognition",
                "planner",
                "critic",
                "coordinator",
                "innovator",
                "executor",
                "learner"
            ],
            "tools": {
                "metacognition": "dashboard_integration.py",
                "planner": "task_priority_scorer.py",
                "critic": "critic_auto_fix.py",
                "coordinator": "load_balancer.py",
                "innovator": "innovation_pattern_matcher.py",
                "executor": "parallel_executor.py",
                "learner": "auto_distill.py"
            },
            "notifications": {
                "enabled": True,
                "channel": "feishu",
                "on_complete": True,
                "on_error": True
            },
            "auto_execute": {
                "low_risk_only": True,
                "max_risk_score": 40,
                "require_confirmation_above": 60
            }
        }
    
    def execute(self, dry_run: bool = False) -> dict:
        """Execute complete workflow"""
        print("=" * 60)
        print(f"[HEARTBEAT] Workflow Started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        for persona in self.config['enabled_personas']:
            print(f"\n[{persona.upper()}] Starting...")
            
            if dry_run:
                print(f"  [DRY-RUN] Would execute {self.config['tools'].get(persona, 'N/A')}")
                self.results[persona] = {"status": "dry_run", "duration": 0}
                continue
            
            result = self._execute_persona(persona)
            self.results[persona] = result
            
            if result['status'] == 'error':
                print(f"  [ERROR] {result.get('message', 'Unknown error')}")
                if self.config['notifications']['on_error']:
                    self._send_notification(persona, result, error=True)
            else:
                print(f"  [OK] {result.get('message', 'Completed')}")
        
        # Generate summary
        summary = self._generate_summary()
        
        # Send notification
        if self.config['notifications']['on_complete']:
            self._send_notification('workflow_complete', summary)
        
        print("\n" + "=" * 60)
        print(f"[HEARTBEAT] Workflow Completed in {summary['total_duration']:.2f}s")
        print("=" * 60)
        
        return summary
    
    def _execute_persona(self, persona: str) -> dict:
        """Execute single persona tool"""
        start = time.time()
        tool = self.config['tools'].get(persona)
        
        if not tool:
            return {"status": "skipped", "message": "No tool configured"}
        
        tool_path = Path(__file__).parent / tool
        
        if not tool_path.exists():
            return {"status": "skipped", "message": f"Tool not found: {tool}"}
        
        try:
            # Execute tool with appropriate parameters
            import subprocess
            cmd = [sys.executable, str(tool_path), "--json"]
            
            # Add auto-execute flag for autonomous decision
            if persona == 'planner':
                cmd.extend(["--auto"])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per persona
                encoding='utf-8'
            )
            
            duration = time.time() - start
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "duration": duration,
                    "message": f"Executed in {duration:.2f}s",
                    "output": result.stdout[:500] if result.stdout else ""
                }
            else:
                return {
                    "status": "error",
                    "duration": duration,
                    "message": result.stderr[:200] if result.stderr else "Execution failed"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": f"Timeout after 300s"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _generate_summary(self) -> dict:
        """Generate workflow execution summary"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        success_count = sum(1 for r in self.results.values() if r['status'] == 'success')
        error_count = sum(1 for r in self.results.values() if r['status'] == 'error')
        skipped_count = sum(1 for r in self.results.values() if r['status'] == 'skipped')
        
        return {
            "workflow_name": self.config['workflow_name'],
            "version": self.config['version'],
            "started_at": self.start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "total_duration": total_duration,
            "persona_count": len(self.config['enabled_personas']),
            "success_count": success_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "success_rate": success_count / len(self.config['enabled_personas']) * 100 if self.config['enabled_personas'] else 0,
            "results": self.results
        }
    
    def _send_notification(self, event_type: str, data: dict, error: bool = False):
        """Send notification via Feishu"""
        if not self.config['notifications']['enabled']:
            return
        
        try:
            from feishu_api import FeishuNotifier
            
            notifier = FeishuNotifier()
            
            if event_type == 'workflow_complete':
                title = "HEARTBEAT Workflow Complete"
                content = {
                    "workflow": data['workflow_name'],
                    "duration": f"{data['total_duration']:.2f}s",
                    "success_rate": f"{data['success_rate']:.1f}%",
                    "persona_status": f"{data['success_count']}/{data['persona_count']} success"
                }
            else:
                title = f"HEARTBEAT Error: {event_type}"
                content = {
                    "error": data.get('message', 'Unknown error'),
                    "persona": event_type
                }
            
            notifier.send_text(f"{title}\n{json.dumps(content, indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            print(f"[NOTIFICATION] Failed to send: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='HEARTBEAT Workflow Orchestrator')
    parser.add_argument('--config', type=str, help='Config file path')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    workflow = HeartbeatWorkflow(args.config)
    result = workflow.execute(dry_run=args.dry_run)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
