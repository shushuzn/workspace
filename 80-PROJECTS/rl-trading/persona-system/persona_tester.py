#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Persona Collaboration Tester
Test and demonstrate 7-persona collaboration features
Features: workflow test, conflict simulation, scoring, visualization

Usage:
    python persona_tester.py --demo
    python persona_tester.py --test
    python persona_tester.py --conflict-demo
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Workspace root
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / "00-人格系统"))

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class PersonaCollaborationTester:
    """Test persona collaboration system"""

    def __init__(self):
        from persona_collaboration import PersonaCollaborationEngine
        self.engine = PersonaCollaborationEngine()

    def run_demo(self):
        """Run full collaboration demo"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + "  7-Persona Collaboration Demo".ljust(59) + "║")
        print("╚" + "═" * 58 + "╝")

        task = "Analyze research papers and generate daily brief"

        print(f"\n📋 Task: {task}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run collaboration workflow
        result = self.engine.run_collaboration_workflow(task)

        # Show visualization
        print("\n" + self.engine.visualize_collaboration())

        # Show scores
        scores = self.engine.get_collaboration_score()

        print("\n" + "=" * 60)
        print("Collaboration Scores")
        print("=" * 60)
        print(f"Overall Score: {scores['overall']}/100")
        print("\nBy Persona:")
        for persona, score in scores['by_persona'].items():
            bar = '█' * int(score / 5) + '░' * (20 - int(score / 5))
            print(f"  {persona:15} [{bar}] {score}")
        print("=" * 60)

        return result

    def run_test(self):
        """Run automated tests"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + "  7-Persona Collaboration Tests".ljust(59) + "║")
        print("╚" + "═" * 58 + "╝")

        tests = [
            ('Message Sending', self._test_messaging),
            ('Conflict Resolution', self._test_conflict),
            ('Workflow Execution', self._test_workflow),
            ('Scoring System', self._test_scoring),
            ('State Persistence', self._test_state)
        ]

        results = []

        for test_name, test_func in tests:
            print(f"\n[Test] {test_name}...")
            try:
                success = test_func()
                results.append((test_name, success))
                print(f"  {'✅ PASS' if success else '❌ FAIL'}: {test_name}")
            except Exception as e:
                results.append((test_name, False))
                print(f"  ❌ ERROR: {test_name} - {e}")

        # Summary
        passed = sum(1 for _, success in results if success)
        total = len(results)

        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {passed /total *100:.0f}%")
        print("=" * 60)

        for test_name, success in results:
            print(f"  {'✅' if success else '❌'} {test_name}")

        return passed == total

    def _test_messaging(self) -> bool:
        """Test inter-persona messaging"""
        from persona_collaboration import PersonaRole, MessagePriority

        # Send message
        msg = self.engine.send_message(
            PersonaRole.PLANNER,
            PersonaRole.EXECUTOR,
            "Test message",
            MessagePriority.NORMAL
        )

        # Verify
        return msg is not None and msg.sender == PersonaRole.PLANNER

    def _test_conflict(self) -> bool:
        """Test conflict creation and resolution"""
        from persona_collaboration import PersonaRole

        # Create conflict
        conflict = self.engine.create_conflict(
            PersonaRole.PLANNER,
            PersonaRole.EXECUTOR,
            "Test conflict",
            'low'
        )

        # Resolve conflict
        resolved = self.engine.resolve_conflict(
            conflict.id,
            "Test resolution",
            PersonaRole.META_COGNITION
        )

        return resolved and conflict.status == 'resolved'

    def _test_workflow(self) -> bool:
        """Test workflow execution"""
        result = self.engine.run_collaboration_workflow("Test task")
        return result is not None and 'phases' in result

    def _test_scoring(self) -> bool:
        """Test scoring system"""
        scores = self.engine.get_collaboration_score()
        return 'overall' in scores and 0 <= scores['overall'] <= 100

    def _test_state(self) -> bool:
        """Test state persistence"""
        # State should be saved automatically
        state_file = WORKSPACE / "20-data-reports" / "persona_state.json"
        return state_file.exists()

    def conflict_demo(self):
        """Demonstrate conflict lifecycle"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + "  Conflict Lifecycle Demo".ljust(59) + "║")
        print("╚" + "═" * 58 + "╝")

        from persona_collaboration import PersonaRole

        # Scenario: Planner and Executor disagree on approach
        print("\n📖 Scenario: Resource Allocation Disagreement")
        print("-" * 60)

        print("\n1️⃣  Conflict Emerges:")
        conflict = self.engine.create_conflict(
            PersonaRole.PLANNER,
            PersonaRole.EXECUTOR,
            "Planner wants thorough analysis, Executor prefers quick iteration",
            'medium'
        )

        print(f"   ID: {conflict.id}")
        print(f"   Severity: {conflict.severity}")
        print(f"   Status: {conflict.status}")

        time.sleep(0.5)

        print("\n2️⃣  Meta-cognition Detects:")
        print("   - Workload imbalance detected")
        print("   - Communication breakdown identified")
        print("   - Arbitration initiated")

        time.sleep(0.5)

        print("\n3️⃣  Arbitration Process:")
        print("   - Both personas present arguments")
        print("   - Meta-cognition evaluates trade-offs")
        print("   - Compromise proposed")

        time.sleep(0.5)

        print("\n4️⃣  Resolution:")
        resolved = self.engine.resolve_conflict(
            conflict.id,
            "Hybrid approach: Quick iterations with periodic deep analysis",
            PersonaRole.META_COGNITION
        )

        if resolved:
            print("   ✅ Conflict resolved successfully")
            print(f"   Resolution: {conflict.resolution}")
            print(f"   Arbitrator: {conflict.arbitrator}")

        # Show updated scores
        scores = self.engine.get_collaboration_score()
        print(f"\n📊 Post-Resolution Collaboration Score: {scores['overall']}")


def main():
    parser = argparse.ArgumentParser(description='Persona Collaboration Tester')
    parser.add_argument('--demo', action='store_true', help='Run collaboration demo')
    parser.add_argument('--test', action='store_true', help='Run automated tests')
    parser.add_argument('--conflict-demo', action='store_true', help='Conflict lifecycle demo')
    args = parser.parse_args()

    tester = PersonaCollaborationTester()

    if args.demo:
        tester.run_demo()

    if args.test:
        tester.run_test()

    if args.conflict_demo:
        tester.conflict_demo()

    if not any([args.demo, args.test, args.conflict_demo]):
        parser.print_help()


if __name__ == "__main__":
    main()
