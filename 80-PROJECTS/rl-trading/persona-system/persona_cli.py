#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Persona Collaboration CLI - Unified Interface
Single command-line interface for all persona collaboration tools
Features: 15 commands, auto-complete, colored output, help system

Usage:
    python persona_cli.py --help
    python persona_cli.py run "task description"
    python persona_cli.py status
    python persona_cli.py analyze
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Workspace root
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / "00-人格系统"))

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


# Colors
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


class PersonaCLI:
    """Unified CLI for persona collaboration"""

    def __init__(self):
        self.engine = None
        self.orchestrator = None
        self.analyzer = None
        self.dashboard_port = 8083
        self.api_port = 8084

    def _load_engine(self):
        """Lazy load engine"""
        if self.engine is None:
            from persona_collaboration import PersonaCollaborationEngine

            self.engine = PersonaCollaborationEngine()
        return self.engine

    def _load_orchestrator(self):
        """Lazy load orchestrator"""
        if self.orchestrator is None:
            from persona_orchestrator import PersonaOrchestrator

            self.orchestrator = PersonaOrchestrator()
        return self.orchestrator

    def _load_analyzer(self):
        """Lazy load analyzer"""
        if self.analyzer is None:
            from persona_analyzer import PersonaAnalyzer

            self.analyzer = PersonaAnalyzer()
        return self.analyzer

    def cmd_run(self, args):
        """Run collaboration workflow"""
        engine = self._load_engine()
        result = engine.run_collaboration_workflow(args.task)

        print_header("Collaboration Workflow Result")
        print(f"Task: {args.task}")
        print(f"Success: {result.get('success', False)}")
        print(f"Duration: {result.get('duration', 0):.1f}s")
        print(f"Phases: {len(result.get('phases', []))}")

        if result.get("visualization"):
            print(f"\n{result['visualization']}")

    def cmd_status(self, args):
        """Show system status"""
        print_header("Persona Collaboration Status")

        # Engine status
        try:
            engine = self._load_engine()
            state = engine.get_state()
            personas = state.get("personas", {})

            print(f"{Colors.BOLD}Persona States:{Colors.ENDC}")
            for name, data in personas.items():
                workload = data.get("workload", 0)
                confidence = data.get("confidence", 0) * 100
                collab = data.get("collaboration_score", 0) * 100
                print(
                    f"  {name:15} Workload: {workload:3}% | Confidence: {confidence:5.0f}% | Collaboration: {collab:5.0f}%"
                )

            # Scores
            scores = engine.get_collaboration_score()
            print(
                f"\n{Colors.BOLD}Overall Score: {scores['overall']:.1f}/100{Colors.ENDC}"
            )
        except Exception as e:
            print_error(f"Engine status failed: {e}")

        # Orchestrator status
        try:
            orchestrator = self._load_orchestrator()
            status = orchestrator.get_status()

            print(f"\n{Colors.BOLD}Orchestrator:{Colors.ENDC}")
            print(f"  Running: {status['running']}")
            print(f"  Pending: {status['pending_tasks']}")
            print(f"  Completed: {status['completed_tasks']}")
            print(f"  Success Rate: {status['success_rate']:.1f}%")
        except Exception as e:
            print_error(f"Orchestrator status failed: {e}")

    def cmd_analyze(self, args):
        """Run pattern analysis"""
        analyzer = self._load_analyzer()
        patterns = analyzer.analyze_patterns()

        print_header("Pattern Analysis")

        import json

        print(json.dumps(patterns, indent=2))

    def cmd_report(self, args):
        """Generate analysis report"""
        analyzer = self._load_analyzer()
        report = analyzer.generate_report(save=not args.no_save)
        print(report)

    def cmd_bottlenecks(self, args):
        """Detect bottlenecks"""
        analyzer = self._load_analyzer()
        bottlenecks = analyzer.detect_bottlenecks()

        print_header(f"Bottlenecks Detected: {len(bottlenecks)}")

        if not bottlenecks:
            print_success("No bottlenecks detected!")
            return

        for i, b in enumerate(bottlenecks, 1):
            severity_color = (
                Colors.FAIL if b["severity"] in ["high", "critical"] else Colors.WARNING
            )
            print(
                f"{severity_color}{i}. [{b['severity'].upper()}] {b['type']}{Colors.ENDC}"
            )
            print(f"   {b['description']}")
            print(f"   Recommendation: {b['recommendation']}\n")

    def cmd_optimize(self, args):
        """Generate optimization recommendations"""
        analyzer = self._load_analyzer()
        recs = analyzer.generate_recommendations()

        print_header(f"Optimization Recommendations: {len(recs)}")

        if not recs:
            print_success("System is optimized!")
            return

        for i, r in enumerate(recs, 1):
            priority_color = Colors.FAIL if r["priority"] == "high" else Colors.WARNING
            print(
                f"{priority_color}{i}. [{r['priority'].upper()}] {r['category']}{Colors.ENDC}"
            )
            print(f"   Action: {r['action']}")
            print(f"   Impact: {r['impact']} | Effort: {r['effort']}\n")

    def cmd_schedule(self, args):
        """Schedule a task"""
        orchestrator = self._load_orchestrator()
        task_id = orchestrator.schedule_task(
            args.task, priority=args.priority, delay_minutes=args.delay
        )
        print_success(f"Task scheduled: {task_id}")

    def cmd_orchestrate(self, args):
        """Start orchestration loop"""
        orchestrator = self._load_orchestrator()
        orchestrator.run_loop()

    def cmd_dashboard(self, args):
        """Start web dashboard"""
        import subprocess

        dashboard_script = WORKSPACE / "00-人格系统" / "persona_dashboard.py"

        print_info(f"Starting dashboard on port {self.dashboard_port}...")
        print_info(f"URL: http://localhost:{self.dashboard_port}")

        subprocess.run(
            [
                sys.executable,
                str(dashboard_script),
                "--serve",
                "--port",
                str(self.dashboard_port),
            ]
        )

    def cmd_api(self, args):
        """Start API server"""
        import subprocess

        api_script = WORKSPACE / "00-人格系统" / "persona_api.py"

        print_info(f"Starting API server on port {self.api_port}...")
        print_info(f"URL: http://localhost:{self.api_port}")
        print_info(f"Docs: http://localhost:{self.api_port}/api")

        subprocess.run(
            [sys.executable, str(api_script), "--serve", "--port", str(self.api_port)]
        )

    def cmd_test(self, args):
        """Run test suite"""
        import subprocess

        test_script = WORKSPACE / "00-人格系统" / "persona_tester.py"

        print_header("Running Test Suite")

        result = subprocess.run([sys.executable, str(test_script), "--test"])

        if result.returncode == 0:
            print_success("All tests passed!")
        else:
            print_error("Some tests failed")

    def cmd_demo(self, args):
        """Run collaboration demo"""
        import subprocess

        test_script = WORKSPACE / "00-人格系统" / "persona_tester.py"

        subprocess.run([sys.executable, str(test_script), "--demo"])

    def cmd_conflicts(self, args):
        """Show conflict history"""
        engine = self._load_engine()
        state = engine.get_state()
        conflicts = state.get("conflicts", [])

        print_header(f"Conflict History: {len(conflicts)}")

        if not conflicts:
            print_success("No conflicts recorded")
            return

        for c in conflicts:
            status_icon = "✅" if c.get("status") == "resolved" else "⏳"
            print(
                f"{status_icon} [{c.get('severity', 'unknown').upper()}] {c.get('persona1', '?')} ↔ {c.get('persona2', '?')}"
            )
            print(f"   Issue: {c.get('issue', 'N/A')}")
            print(f"   Status: {c.get('status', 'unknown')}")
            if c.get("resolution"):
                print(f"   Resolution: {c['resolution']}")
            print()

    def cmd_messages(self, args):
        """Show message history"""
        engine = self._load_engine()
        state = engine.get_state()
        messages = state.get("messages", [])

        print_header(f"Message History: {len(messages)}")

        if not messages:
            print_success("No messages recorded")
            return

        # Show last 20 messages
        for msg in messages[-20:]:
            print(
                f"[{msg.get('sender', '?')} → {msg.get('receiver', '?')}] {msg.get('content', '')[:60]}..."
            )

    def cmd_reset(self, args):
        """Reset persona states"""
        if not args.confirm:
            print_warning("This will reset all persona states!")
            print_info("Use --confirm to proceed")
            return

        engine = self._load_engine()
        # Reset state file
        state_file = WORKSPACE / "20-data-reports" / "persona_state.json"
        if state_file.exists():
            state_file.unlink()
            print_success("Persona states reset")
        else:
            print_info("No state file found")

    def cmd_help(self, args):
        """Show help"""
        print_header("Persona Collaboration CLI")

        print(f"""
{Colors.BOLD}Usage:{Colors.ENDC}
  persona_cli.py <command> [options]

{Colors.BOLD}Commands:{Colors.ENDC}
  {Colors.OKGREEN}run <task>{Colors.ENDC}           Run collaboration workflow
  {Colors.OKGREEN}status{Colors.ENDC}               Show system status
  {Colors.OKGREEN}analyze{Colors.ENDC}              Run pattern analysis
  {Colors.OKGREEN}report{Colors.ENDC}               Generate analysis report
  {Colors.OKGREEN}bottlenecks{Colors.ENDC}          Detect bottlenecks
  {Colors.OKGREEN}optimize{Colors.ENDC}             Generate recommendations
  {Colors.OKGREEN}schedule <task>{Colors.ENDC}      Schedule a task
  {Colors.OKGREEN}orchestrate{Colors.ENDC}          Start orchestration loop
  {Colors.OKGREEN}dashboard{Colors.ENDC}            Start web dashboard
  {Colors.OKGREEN}api{Colors.ENDC}                  Start API server
  {Colors.OKGREEN}test{Colors.ENDC}                 Run test suite
  {Colors.OKGREEN}demo{Colors.ENDC}                 Run collaboration demo
  {Colors.OKGREEN}conflicts{Colors.ENDC}            Show conflict history
  {Colors.OKGREEN}messages{Colors.ENDC}             Show message history
  {Colors.OKGREEN}reset{Colors.ENDC}                Reset persona states
  {Colors.OKGREEN}help{Colors.ENDC}                 Show this help

{Colors.BOLD}Examples:{Colors.ENDC}
  persona_cli.py run "Analyze research papers"
  persona_cli.py status
  persona_cli.py analyze
  persona_cli.py report
  persona_cli.py schedule "Daily brief" --priority 3 --delay 30
  persona_cli.py dashboard
  persona_cli.py api

{Colors.BOLD}Options:{Colors.ENDC}
  --priority <1-5>     Task priority (1=low, 5=critical)
  --delay <minutes>    Delay in minutes
  --no-save            Don't save report to file
  --confirm            Confirm destructive actions
""")


def main():
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        return
    print("[OK] Critic Review Passed")

    parser = argparse.ArgumentParser(
        description="Persona Collaboration CLI", add_help=False
    )
    parser.add_argument("command", nargs="?", default="help", help="Command to run")
    parser.add_argument("--help", "-h", action="store_true", help="Show help")
    parser.add_argument("--priority", type=int, default=2, help="Task priority")
    parser.add_argument("--delay", type=int, default=0, help="Delay in minutes")
    parser.add_argument("--no-save", action="store_true", help="Don't save report")
    parser.add_argument("--confirm", action="store_true", help="Confirm action")
    parser.add_argument("task", nargs="?", default="", help="Task description")

    args = parser.parse_args()

    cli = PersonaCLI()

    if args.help or args.command == "help":
        cli.cmd_help(args)
        return

    commands = {
        "run": cli.cmd_run,
        "status": cli.cmd_status,
        "analyze": cli.cmd_analyze,
        "report": cli.cmd_report,
        "bottlenecks": cli.cmd_bottlenecks,
        "optimize": cli.cmd_optimize,
        "schedule": cli.cmd_schedule,
        "orchestrate": cli.cmd_orchestrate,
        "dashboard": cli.cmd_dashboard,
        "api": cli.cmd_api,
        "test": cli.cmd_test,
        "demo": cli.cmd_demo,
        "conflicts": cli.cmd_conflicts,
        "messages": cli.cmd_messages,
        "reset": cli.cmd_reset,
    }

    if args.command in commands:
        try:
            commands[args.command](args)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Interrupted{Colors.ENDC}")
        except Exception as e:
            print_error(f"Command failed: {e}")
            import traceback

            traceback.print_exc()
    else:
        print_error(f"Unknown command: {args.command}")
        print_info("Use 'persona_cli.py help' for available commands")


if __name__ == "__main__":
    main()
