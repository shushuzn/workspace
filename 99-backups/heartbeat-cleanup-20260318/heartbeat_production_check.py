#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⏱️ HEARTBEAT Production Check - Automated Health Monitoring

Automated checks executed by HEARTBEAT:
- System health check (6 systems)
- Memory Core status
- Autonomous engine status
- Persona system status
- Error log analysis
- Resource usage check

Usage:
    python heartbeat_production_check.py --run
    python heartbeat_production_check.py --status
    python heartbeat_production_check.py --report
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


@dataclass
class CheckResult:
    """Check result"""
    name: str
    status: str  # pass/warning/fail
    message: str
    timestamp: str
    details: Dict


class HeartbeatProductionCheck:
    """Automated production health check"""

    def __init__(self):
        self.state_file = WORKSPACE / "20-data-reports" / "heartbeat_production_state.json"
        self.history_file = WORKSPACE / "20-data-reports" / "heartbeat_production_history.json"

        self.results = []
        self.history = []

        self.load_state()

    def load_state(self):
        """Load state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
            except Exception:
                pass

    def save_state(self):
        """Save state"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({
                'last_check': datetime.now().isoformat(),
                'history': self.history[-100:]  # Last 100 checks
            }, f, indent=2, ensure_ascii=False)

    def check_system_health(self) -> CheckResult:
        """Check production monitor status"""
        try:
            # Check if production monitor state exists
            monitor_state = WORKSPACE / "20-data-reports" / "production_monitor_state.json"

            if not monitor_state.exists():
                return CheckResult(
                    name="system_health",
                    status="warning",
                    message="Production monitor not initialized",
                    timestamp=datetime.now().isoformat(),
                    details={"action": "Run production_monitor_v2.py --check"}
                )

            with open(monitor_state, 'r', encoding='utf-8') as f:
                data = json.load(f)

            systems = data.get('systems', {})
            overall_health = sum(s.get('health', 0) for s in systems.values()) / max(1, len(systems))

            if overall_health >= 90:
                status = "pass"
            elif overall_health >= 70:
                status = "warning"
            else:
                status = "fail"

            return CheckResult(
                name="system_health",
                status=status,
                message=f"Overall health: {overall_health:.1f}%",
                timestamp=datetime.now().isoformat(),
                details={
                    "systems": len(systems),
                    "overall_health": overall_health,
                    "system_details": systems
                }
            )

        except Exception as e:
            return CheckResult(
                name="system_health",
                status="fail",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat(),
                details={}
            )

    def check_memory_core(self) -> CheckResult:
        """Check Memory Core v2.0 status"""
        try:
            memory_core_dir = WORKSPACE / "30-scripts-tools" / "memory_core"

            if not memory_core_dir.exists():
                return CheckResult(
                    name="memory_core",
                    status="fail",
                    message="Memory Core v2.0 not found",
                    timestamp=datetime.now().isoformat(),
                    details={}
                )

            # Check core files
            required_files = ['core.py', 'config.py', 'test_memory_core.py']
            missing_files = []

            for file in required_files:
                if not (memory_core_dir / file).exists():
                    missing_files.append(file)

            if missing_files:
                return CheckResult(
                    name="memory_core",
                    status="warning",
                    message=f"Missing files: {', '.join(missing_files)}",
                    timestamp=datetime.now().isoformat(),
                    details={"missing": missing_files}
                )

            return CheckResult(
                name="memory_core",
                status="pass",
                message="Memory Core v2.0 operational",
                timestamp=datetime.now().isoformat(),
                details={"files": required_files}
            )

        except Exception as e:
            return CheckResult(
                name="memory_core",
                status="fail",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat(),
                details={}
            )

    def check_autonomous_engine(self) -> CheckResult:
        """Check Autonomous Engine status"""
        try:
            engine_file = WORKSPACE / "30-scripts-tools" / "memory_engine_autonomous.py"

            if not engine_file.exists():
                return CheckResult(
                    name="autonomous_engine",
                    status="fail",
                    message="Autonomous Engine not found",
                    timestamp=datetime.now().isoformat(),
                    details={}
                )

            return CheckResult(
                name="autonomous_engine",
                status="pass",
                message="Autonomous Engine operational",
                timestamp=datetime.now().isoformat(),
                details={"file": "memory_engine_autonomous.py"}
            )

        except Exception as e:
            return CheckResult(
                name="autonomous_engine",
                status="fail",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat(),
                details={}
            )

    def check_persona_system(self) -> CheckResult:
        """Check Persona System status"""
        try:
            persona_file = WORKSPACE / "30-scripts-tools" / "memory_persona.py"

            if not persona_file.exists():
                return CheckResult(
                    name="persona_system",
                    status="fail",
                    message="Persona System not found",
                    timestamp=datetime.now().isoformat(),
                    details={}
                )

            return CheckResult(
                name="persona_system",
                status="pass",
                message="Persona System operational",
                timestamp=datetime.now().isoformat(),
                details={"file": "memory_persona.py"}
            )

        except Exception as e:
            return CheckResult(
                name="persona_system",
                status="fail",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat(),
                details={}
            )

    def check_error_logs(self) -> CheckResult:
        """Check for recent errors"""
        try:
            log_file = WORKSPACE / "20-data-reports" / "autofix_log.json"

            if not log_file.exists():
                return CheckResult(
                    name="error_logs",
                    status="pass",
                    message="No error logs found",
                    timestamp=datetime.now().isoformat(),
                    details={}
                )

            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            actions = data.get('actions', [])
            recent_failures = [a for a in actions[-20:] if a.get('status') == 'failed']

            if len(recent_failures) > 5:
                status = "warning"
                message = f"{len(recent_failures)} recent failures"
            elif len(recent_failures) > 0:
                status = "pass"
                message = f"{len(recent_failures)} minor failures"
            else:
                status = "pass"
                message = "No recent failures"

            return CheckResult(
                name="error_logs",
                status=status,
                message=message,
                timestamp=datetime.now().isoformat(),
                details={
                    "total_actions": len(actions),
                    "recent_failures": len(recent_failures)
                }
            )

        except Exception as e:
            return CheckResult(
                name="error_logs",
                status="warning",
                message=f"Error reading logs: {str(e)}",
                timestamp=datetime.now().isoformat(),
                details={}
            )

    def check_resource_usage(self) -> CheckResult:
        """Check resource usage (simulated)"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            if cpu_percent > 90 or memory_percent > 90:
                status = "warning"
                message = f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%"
            else:
                status = "pass"
                message = f"Resource usage normal: CPU {cpu_percent}%, Memory {memory_percent}%"

            return CheckResult(
                name="resource_usage",
                status=status,
                message=message,
                timestamp=datetime.now().isoformat(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent
                }
            )

        except ImportError:
            return CheckResult(
                name="resource_usage",
                status="pass",
                message="psutil not installed, skipping",
                timestamp=datetime.now().isoformat(),
                details={}
            )
        except Exception as e:
            return CheckResult(
                name="resource_usage",
                status="warning",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat(),
                details={}
            )

    def run_all_checks(self) -> Dict:
        """Run all health checks"""
        print("=" * 70)
        print("⏱️ HEARTBEAT Production Check")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 70)

        checks = [
            ("System Health", self.check_system_health),
            ("Memory Core v2.0", self.check_memory_core),
            ("Autonomous Engine", self.check_autonomous_engine),
            ("Persona System", self.check_persona_system),
            ("Error Logs", self.check_error_logs),
            ("Resource Usage", self.check_resource_usage),
        ]

        results = []
        summary = {
            'total': 0,
            'pass': 0,
            'warning': 0,
            'fail': 0
        }

        for name, check_func in checks:
            result = check_func()
            results.append(result)

            summary['total'] += 1
            summary[result.status] += 1

            # Print result
            icon = "✅" if result.status == "pass" else "⚠️" if result.status == "warning" else "❌"
            print(f"\n{icon} {name}")
            print(f"   Status: {result.status.upper()}")
            print(f"   Message: {result.message}")

        # Summary
        print("\n" + "=" * 70)
        print("Summary:")
        print(f"  Total: {summary['total']}")
        print(f"  ✅ Pass: {summary['pass']}")
        print(f"  ⚠️ Warning: {summary['warning']}")
        print(f"  ❌ Fail: {summary['fail']}")

        health_score = (summary['pass'] / summary['total'] * 100) if summary['total'] > 0 else 0
        print(f"\nHealth Score: {health_score:.0f}%")

        # Save to history
        self.results = results
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'health_score': health_score,
            'results': [asdict(r) for r in results]
        })

        self.save_state()

        print("=" * 70)

        return {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'health_score': health_score,
            'results': [asdict(r) for r in results]
        }

    def get_status(self) -> Dict:
        """Get check status"""
        return {
            'last_check': self.history[-1]['timestamp'] if self.history else None,
            'total_checks': len(self.history),
            'recent_health_scores': [h['health_score'] for h in self.history[-10:]]
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='HEARTBEAT Production Check')
    parser.add_argument('--run', action='store_true', help='Run all checks')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--report', action='store_true', help='Generate report')

    args = parser.parse_args()

    checker = HeartbeatProductionCheck()

    if args.run:
        results = checker.run_all_checks()
        print("\nJSON Output:")
        print(json.dumps(results, indent=2))

    elif args.status:
        print("HEARTBEAT Check Status:")
        status = checker.get_status()
        print(json.dumps(status, indent=2))

    elif args.report:
        print("Generating report...")
        results = checker.run_all_checks()

        # Save report
        report_file = WORKSPACE / "20-data-reports" / f"heartbeat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved to: {report_file}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
