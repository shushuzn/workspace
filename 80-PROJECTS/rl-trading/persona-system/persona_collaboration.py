#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Persona Collaboration Engine v2.0 - Enhanced
Advanced multi-persona collaboration with communication and arbitration
Features: inter-persona messaging, conflict resolution, collaboration workflows, scoring

Usage:
    python persona_collaboration.py --run task
    python persona_collaboration.py --visualize
    python persona_collaboration.py --conflict simulate
    python persona_collaboration.py --score
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import hashlib

# Workspace root
WORKSPACE = Path(__file__).parent.parent
PERSONAS_DIR = WORKSPACE / "00-人格系统"
MEMORY_FILE = WORKSPACE / "MEMORY.md"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


class PersonaRole(Enum):
    """7 Persona Roles"""

    PLANNER = "planner"
    EXECUTOR = "executor"
    CRITIC = "critic"
    LEARNER = "learner"
    COORDINATOR = "coordinator"
    INNOVATOR = "innovator"
    META_COGNITION = "meta_cognition"


class MessagePriority(Enum):
    """Message Priority Levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class PersonaMessage:
    """Inter-persona message"""

    def __init__(
        self,
        sender: PersonaRole,
        receiver: PersonaRole,
        content: str,
        priority: MessagePriority = MessagePriority.NORMAL,
    ):
        self.id = hashlib.md5(
            f"{sender.value}{receiver.value}{time.time()}".encode()
        ).hexdigest()[:8]
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.priority = priority
        self.timestamp = datetime.now().isoformat()
        self.read = False
        self.acted_upon = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "sender": self.sender.value,
            "receiver": self.receiver.value,
            "content": self.content,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "read": self.read,
            "acted_upon": self.acted_upon,
        }


class PersonaState:
    """Persona internal state"""

    def __init__(self, role: PersonaRole):
        self.role = role
        self.workload = 0  # 0-100
        self.confidence = 0.5  # 0-1
        self.last_active = None
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.collaboration_score = 0.5  # 0-1
        self.conflicts_involved = 0
        self.messages_sent = 0
        self.messages_received = 0

    def to_dict(self) -> Dict:
        return {
            "role": self.role.value,
            "workload": self.workload,
            "confidence": round(self.confidence, 3),
            "last_active": self.last_active,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "collaboration_score": round(self.collaboration_score, 3),
            "conflicts_involved": self.conflicts_involved,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
        }


class Conflict:
    """Persona conflict record"""

    def __init__(
        self,
        persona1: PersonaRole,
        persona2: PersonaRole,
        issue: str,
        severity: str = "medium",
    ):
        self.id = hashlib.md5(
            f"{persona1.value}{persona2.value}{issue}{time.time()}".encode()
        ).hexdigest()[:8]
        self.persona1 = persona1
        self.persona2 = persona2
        self.issue = issue
        self.severity = severity  # low, medium, high, critical
        self.status = "open"  # open, resolving, resolved
        self.created_at = datetime.now().isoformat()
        self.resolved_at = None
        self.resolution = None
        self.arbitrator = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "persona1": self.persona1.value,
            "persona2": self.persona2.value,
            "issue": self.issue,
            "severity": self.severity,
            "status": self.status,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
            "resolution": self.resolution,
            "arbitrator": self.arbitrator,
        }


class PersonaCollaborationEngine:
    """Enhanced 7-persona collaboration engine"""

    def __init__(self):
        self.personas = {role: PersonaState(role) for role in PersonaRole}
        self.message_queue: List[PersonaMessage] = []
        self.conflicts: List[Conflict] = []
        self.collaboration_history = []
        self.current_task = None
        self._load_state()

    def _load_state(self):
        """Load collaboration state from file"""
        state_file = WORKSPACE / "20-data-reports" / "persona_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Load conflicts
                    for c_data in data.get("conflicts", []):
                        conflict = Conflict(
                            PersonaRole(c_data["persona1"]),
                            PersonaRole(c_data["persona2"]),
                            c_data["issue"],
                            c_data.get("severity", "medium"),
                        )
                        conflict.id = c_data["id"]
                        conflict.status = c_data.get("status", "open")
                        self.conflicts.append(conflict)
            except Exception as e:
                print(f"[WARN] Failed to load persona state: {e}")

    def _save_state(self):
        """Save collaboration state to file"""
        state_file = WORKSPACE / "20-data-reports" / "persona_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "personas": {
                role.value: state.to_dict() for role, state in self.personas.items()
            },
            "conflicts": [c.to_dict() for c in self.conflicts],
            "message_count": len(self.message_queue),
            "last_updated": datetime.now().isoformat(),
        }

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_state(self) -> Dict:
        """Get current collaboration state"""
        return {
            "personas": {
                role.value: state.to_dict() for role, state in self.personas.items()
            },
            "conflicts": [c.to_dict() for c in self.conflicts],
            "messages": [m.to_dict() for m in self.message_queue],
            "message_count": len(self.message_queue),
            "last_updated": datetime.now().isoformat(),
        }

    def send_message(
        self,
        sender: PersonaRole,
        receiver: PersonaRole,
        content: str,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> PersonaMessage:
        """Send inter-persona message"""
        message = PersonaMessage(sender, receiver, content, priority)
        self.message_queue.append(message)

        # Update stats
        self.personas[sender].messages_sent += 1
        self.personas[receiver].messages_received += 1
        self.personas[sender].last_active = datetime.now().isoformat()

        print(f"\n📩 [{sender.value} → {receiver.value}] {content[:50]}...")

        return message

    def broadcast(
        self,
        sender: PersonaRole,
        content: str,
        exclude: List[PersonaRole] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
    ):
        """Broadcast message to all personas"""
        exclude = exclude or []

        for role in PersonaRole:
            if role != sender and role not in exclude:
                self.send_message(sender, role, content, priority)

    def create_conflict(
        self,
        persona1: PersonaRole,
        persona2: PersonaRole,
        issue: str,
        severity: str = "medium",
    ) -> Conflict:
        """Record a conflict between personas"""
        conflict = Conflict(persona1, persona2, issue, severity)
        self.conflicts.append(conflict)

        self.personas[persona1].conflicts_involved += 1
        self.personas[persona2].conflicts_involved += 1

        print(f"\n⚠️  CONFLICT [{persona1.value} ↔ {persona2.value}]: {issue}")
        print(f"   Severity: {severity}")
        print(f"   ID: {conflict.id}")

        return conflict

    def resolve_conflict(
        self,
        conflict_id: str,
        resolution: str,
        arbitrator: PersonaRole = PersonaRole.META_COGNITION,
    ) -> bool:
        """Resolve a conflict"""
        conflict = next((c for c in self.conflicts if c.id == conflict_id), None)

        if not conflict:
            print(f"[ERROR] Conflict not found: {conflict_id}")
            return False

        conflict.status = "resolved"
        conflict.resolved_at = datetime.now().isoformat()
        conflict.resolution = resolution
        conflict.arbitrator = arbitrator.value

        print(f"\n✅ CONFLICT RESOLVED: {conflict_id}")
        print(f"   Resolution: {resolution}")
        print(f"   Arbitrator: {arbitrator.value}")

        # Update collaboration scores
        self.personas[conflict.persona1].collaboration_score = min(
            1.0, self.personas[conflict.persona1].collaboration_score + 0.05
        )
        self.personas[conflict.persona2].collaboration_score = min(
            1.0, self.personas[conflict.persona2].collaboration_score + 0.05
        )

        self._save_state()

        return True

    def run_collaboration_workflow(self, task: str) -> Dict:
        """Run full 7-persona collaboration workflow"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + f"  7-Persona Collaboration: {task[:40]}".ljust(59) + "║")
        print("╚" + "═" * 58 + "╝")

        self.current_task = task
        workflow_result = {
            "task": task,
            "start_time": datetime.now().isoformat(),
            "phases": [],
            "messages": [],
            "conflicts": [],
            "outcome": "unknown",
        }

        # Phase 1: Planning
        print("\n📋 Phase 1: Planning")
        plan_result = self._planner_phase(task)
        workflow_result["phases"].append({"name": "planning", "result": plan_result})

        # Phase 2: Execution
        print("\n⚙️  Phase 2: Execution")
        exec_result = self._executor_phase(plan_result)
        workflow_result["phases"].append({"name": "execution", "result": exec_result})

        # Phase 3: Criticism
        print("\n🔍 Phase 3: Critical Review")
        critic_result = self._critic_phase(exec_result)
        workflow_result["phases"].append({"name": "criticism", "result": critic_result})

        # Phase 4: Learning (if critic passed)
        if critic_result.get("score", 0) >= 85:
            print("\n📚 Phase 4: Learning")
            learn_result = self._learner_phase(critic_result)
            workflow_result["phases"].append(
                {"name": "learning", "result": learn_result}
            )
        else:
            print("\n⚠️  Phase 4: Skipped (critic score < 85)")
            workflow_result["phases"].append({"name": "learning", "result": "skipped"})

        # Phase 5: Innovation
        print("\n💡 Phase 5: Innovation")
        innov_result = self._innovator_phase(task, exec_result)
        workflow_result["phases"].append({"name": "innovation", "result": innov_result})

        # Phase 6: Meta-cognition
        print("\n🧠 Phase 6: Meta-cognition")
        meta_result = self._meta_cognition_phase(workflow_result)
        workflow_result["phases"].append(
            {"name": "meta_cognition", "result": meta_result}
        )

        # Coordinator monitors throughout
        self._coordinator_check()

        workflow_result["outcome"] = (
            "success" if critic_result.get("score", 0) >= 85 else "needs_improvement"
        )
        workflow_result["end_time"] = datetime.now().isoformat()

        self.collaboration_history.append(workflow_result)
        self._save_state()

        # Print summary
        print("\n" + "=" * 60)
        print("Collaboration Summary")
        print("=" * 60)
        print(f"Task: {task}")
        print(f"Outcome: {workflow_result['outcome']}")
        print(f"Messages: {len(self.message_queue)}")
        print(f"Conflicts: {len([c for c in self.conflicts if c.status == 'open'])}")
        print(
            f"Duration: {(datetime.fromisoformat(workflow_result['end_time']) - datetime.fromisoformat(workflow_result['start_time'])).total_seconds():.2f}s"
        )
        print("=" * 60)

        return workflow_result

    def _planner_phase(self, task: str) -> Dict:
        """Planner persona phase"""
        self.personas[PersonaRole.PLANNER].workload = min(
            100, self.personas[PersonaRole.PLANNER].workload + 20
        )

        # Simulate planning
        plan = {
            "task": task,
            "steps": [
                {"id": 1, "action": "analyze", "assigned_to": "planner"},
                {"id": 2, "action": "execute", "assigned_to": "executor"},
                {"id": 3, "action": "review", "assigned_to": "critic"},
                {"id": 4, "action": "learn", "assigned_to": "learner"},
                {"id": 5, "action": "innovate", "assigned_to": "innovator"},
            ],
            "estimated_duration": 300,
            "confidence": 0.85,
        }

        # Send messages
        self.send_message(
            PersonaRole.PLANNER,
            PersonaRole.EXECUTOR,
            f"Plan created for: {task[:30]}...",
            MessagePriority.HIGH,
        )

        self.personas[PersonaRole.PLANNER].tasks_completed += 1
        self.personas[PersonaRole.PLANNER].confidence = min(
            1.0, self.personas[PersonaRole.PLANNER].confidence + 0.02
        )

        print(f"   ✅ Plan created: {len(plan['steps'])} steps")

        return plan

    def _executor_phase(self, plan: Dict) -> Dict:
        """Executor persona phase"""
        self.personas[PersonaRole.EXECUTOR].workload = min(
            100, self.personas[PersonaRole.EXECUTOR].workload + 30
        )

        # Simulate execution
        exec_result = {
            "plan_id": plan.get("task", "unknown"),
            "steps_executed": len(plan.get("steps", [])),
            "success_rate": 0.92,
            "duration": 180,
            "output": "Task completed successfully",
            "artifacts": ["output_1.txt", "output_2.txt"],
        }

        # Send messages
        self.send_message(
            PersonaRole.EXECUTOR,
            PersonaRole.CRITIC,
            "Execution complete, ready for review",
            MessagePriority.NORMAL,
        )

        self.send_message(
            PersonaRole.EXECUTOR,
            PersonaRole.PLANNER,
            f"Executed {exec_result['steps_executed']} steps",
            MessagePriority.LOW,
        )

        self.personas[PersonaRole.EXECUTOR].tasks_completed += 1
        self.personas[PersonaRole.EXECUTOR].confidence = min(
            1.0, self.personas[PersonaRole.EXECUTOR].confidence + 0.03
        )

        print(f"   ✅ Executed: {exec_result['steps_executed']} steps")
        print(f"   Success rate: {exec_result['success_rate'] * 100:.0f}%")

        return exec_result

    def _critic_phase(self, exec_result: Dict) -> Dict:
        """Critic persona phase"""
        self.personas[PersonaRole.CRITIC].workload = min(
            100, self.personas[PersonaRole.CRITIC].workload + 25
        )

        # Simulate critical review
        score = 88  # Simulated score
        issues = [
            {"severity": "low", "description": "Minor formatting issue"},
            {"severity": "medium", "description": "Could optimize step 3"},
        ]

        critic_result = {
            "score": score,
            "passed": score >= 85,
            "issues": issues,
            "recommendations": ["Improve formatting", "Optimize step 3"],
            "review_time": 45,
        }

        # Potential conflict with executor
        if score < 90:
            if len(self.conflicts) % 3 == 0:  # Simulate occasional conflict
                conflict = self.create_conflict(
                    PersonaRole.CRITIC,
                    PersonaRole.EXECUTOR,
                    "Quality standards disagreement",
                    "low",
                )
                # Auto-resolve
                time.sleep(0.1)
                self.resolve_conflict(
                    conflict.id, "Agreed on quality metrics", PersonaRole.META_COGNITION
                )

        # Send messages
        self.send_message(
            PersonaRole.CRITIC,
            PersonaRole.EXECUTOR,
            f"Review complete: {score}/100",
            MessagePriority.HIGH,
        )

        if critic_result["passed"]:
            self.send_message(
                PersonaRole.CRITIC,
                PersonaRole.LEARNER,
                "Ready for learning extraction",
                MessagePriority.NORMAL,
            )

        self.personas[PersonaRole.CRITIC].tasks_completed += 1

        print(f"   ✅ Score: {score}/100")
        print(
            f"   {'✅ PASSED' if critic_result['passed'] else '❌ NEEDS IMPROVEMENT'}"
        )
        print(f"   Issues: {len(issues)}")

        return critic_result

    def _learner_phase(self, critic_result: Dict) -> Dict:
        """Learner persona phase"""
        self.personas[PersonaRole.LEARNER].workload = min(
            100, self.personas[PersonaRole.LEARNER].workload + 15
        )

        # Simulate learning extraction
        learn_result = {
            "lessons": [
                {
                    "id": "LEARN-001",
                    "insight": "Optimization opportunity identified",
                    "confidence": 0.8,
                },
                {
                    "id": "LEARN-002",
                    "insight": "Quality metric adjustment needed",
                    "confidence": 0.7,
                },
            ],
            "memory_updates": 2,
            "knowledge_graph_updates": 1,
        }

        # Send messages
        self.send_message(
            PersonaRole.LEARNER,
            PersonaRole.META_COGNITION,
            f"Extracted {len(learn_result['lessons'])} lessons",
            MessagePriority.LOW,
        )

        self.personas[PersonaRole.LEARNER].tasks_completed += 1
        self.personas[PersonaRole.LEARNER].collaboration_score = min(
            1.0, self.personas[PersonaRole.LEARNER].collaboration_score + 0.03
        )

        print(f"   ✅ Lessons: {len(learn_result['lessons'])}")
        print(f"   Memory updates: {learn_result['memory_updates']}")

        return learn_result

    def _innovator_phase(self, task: str, exec_result: Dict) -> Dict:
        """Innovator persona phase"""
        self.personas[PersonaRole.INNOVATOR].workload = min(
            100, self.personas[PersonaRole.INNOVATOR].workload + 20
        )

        # Simulate innovation
        innov_result = {
            "innovations": [
                {
                    "id": "INNOV-001",
                    "idea": "Automate step 2",
                    "impact": "high",
                    "feasibility": 0.85,
                },
                {
                    "id": "INNOV-002",
                    "idea": "Parallel processing",
                    "impact": "medium",
                    "feasibility": 0.7,
                },
            ],
            "creativity_score": 0.78,
            "implementation_priority": ["INNOV-001"],
        }

        # Send messages
        self.send_message(
            PersonaRole.INNOVATOR,
            PersonaRole.PLANNER,
            f"Generated {len(innov_result['innovations'])} innovations",
            MessagePriority.NORMAL,
        )

        self.personas[PersonaRole.INNOVATOR].tasks_completed += 1

        print(f"   ✅ Innovations: {len(innov_result['innovations'])}")
        print(f"   Creativity: {innov_result['creativity_score'] * 100:.0f}%")

        return innov_result

    def _meta_cognition_phase(self, workflow_result: Dict) -> Dict:
        """Meta-cognition persona phase"""
        self.personas[PersonaRole.META_COGNITION].workload = min(
            100, self.personas[PersonaRole.META_COGNITION].workload + 10
        )

        # System monitoring
        meta_result = {
            "system_health": "good",
            "persona_states": {
                role.value: state.to_dict() for role, state in self.personas.items()
            },
            "active_conflicts": len([c for c in self.conflicts if c.status == "open"]),
            "collaboration_efficiency": 0.85,
            "recommendations": [],
        }

        # Check for issues
        avg_workload = sum(p.workload for p in self.personas.values()) / len(
            self.personas
        )
        if avg_workload > 80:
            meta_result["recommendations"].append("High workload detected")

        print(f"   ✅ System health: {meta_result['system_health']}")
        print(f"   Active conflicts: {meta_result['active_conflicts']}")
        print(
            f"   Collaboration efficiency: {meta_result['collaboration_efficiency'] * 100:.0f}%"
        )

        self.personas[PersonaRole.META_COGNITION].tasks_completed += 1

        return meta_result

    def _coordinator_check(self):
        """Coordinator persona monitoring"""
        self.personas[PersonaRole.COORDINATOR].workload = min(
            100, self.personas[PersonaRole.COORDINATOR].workload + 5
        )

        # Check workload balance
        workloads = {
            role.value: state.workload for role, state in self.personas.items()
        }
        max_workload = max(workloads.values())
        min_workload = min(workloads.values())

        if max_workload - min_workload > 40:
            print(
                f"\n⚖️  Coordinator: Workload imbalance detected ({max_workload - min_workload}%)"
            )
            # Send balancing messages
            self.broadcast(
                PersonaRole.COORDINATOR,
                "Consider workload redistribution",
                priority=MessagePriority.NORMAL,
            )

        self.personas[PersonaRole.COORDINATOR].tasks_completed += 1

    def get_collaboration_score(self) -> Dict:
        """Calculate overall collaboration score"""
        scores = []

        for role, state in self.personas.items():
            # Calculate individual score
            individual_score = (
                state.collaboration_score * 0.4
                + (1 - state.conflicts_involved / max(1, len(self.conflicts))) * 0.3
                + (
                    state.tasks_completed
                    / max(1, state.tasks_completed + state.tasks_failed)
                )
                * 0.3
            )
            scores.append(individual_score)

        return {
            "overall": round(sum(scores) / len(scores) * 100, 2),
            "by_persona": {
                role.value: round(s * 100, 2) for role, s in zip(PersonaRole, scores)
            },
            "total_messages": len(self.message_queue),
            "resolved_conflicts": len(
                [c for c in self.conflicts if c.status == "resolved"]
            ),
            "open_conflicts": len([c for c in self.conflicts if c.status == "open"]),
        }

    def visualize_collaboration(self) -> str:
        """Generate ASCII visualization of collaboration network"""
        viz = []
        viz.append("\n" + "╔" + "═" * 58 + "╗")
        viz.append("║" + "  7-Persona Collaboration Network".ljust(59) + "║")
        viz.append("╚" + "═" * 58 + "╝")
        viz.append("")

        # Show persona states
        viz.append("Persona States:")
        viz.append("")

        for role, state in self.personas.items():
            workload_bar = "█" * int(state.workload / 5) + "░" * (
                20 - int(state.workload / 5)
            )
            viz.append(f"  {role.value:15} [{workload_bar}] {state.workload}%")
            viz.append(
                f"                   Confidence: {state.confidence:.2f} | Collaboration: {state.collaboration_score:.2f}"
            )

        viz.append("")
        viz.append("Message Flow:")
        viz.append("")

        # Show recent messages
        for msg in self.message_queue[-5:]:
            viz.append(
                f"  {msg.sender.value:15} → {msg.receiver.value:15} | {msg.content[:30]}"
            )

        viz.append("")
        viz.append("Conflict Status:")
        viz.append("")

        open_conflicts = [c for c in self.conflicts if c.status == "open"]
        if open_conflicts:
            for conflict in open_conflicts:
                viz.append(
                    f"  ⚠️  {conflict.persona1.value} ↔ {conflict.persona2.value} | {conflict.issue[:30]}"
                )
        else:
            viz.append("  ✅ No active conflicts")

        viz.append("")

        return "\n".join(viz)


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

    parser = argparse.ArgumentParser(description="Persona Collaboration Engine v2.0")
    parser.add_argument(
        "--run", type=str, metavar="TASK", help="Run collaboration workflow"
    )
    parser.add_argument(
        "--visualize", action="store_true", help="Visualize collaboration network"
    )
    parser.add_argument(
        "--score", action="store_true", help="Show collaboration scores"
    )
    parser.add_argument(
        "--conflict", type=str, metavar="ACTION", help="Conflict simulation"
    )
    args = parser.parse_args()

    engine = PersonaCollaborationEngine()

    if args.run:
        engine.run_collaboration_workflow(args.run)

    if args.visualize:
        print(engine.visualize_collaboration())

    if args.score:
        scores = engine.get_collaboration_score()
        print("\n" + "=" * 60)
        print("Collaboration Scores")
        print("=" * 60)
        print(f"Overall: {scores['overall']}")
        print("\nBy Persona:")
        for persona, score in scores["by_persona"].items():
            print(f"  {persona:15} {score}")
        print(f"\nTotal Messages: {scores['total_messages']}")
        print(f"Resolved Conflicts: {scores['resolved_conflicts']}")
        print(f"Open Conflicts: {scores['open_conflicts']}")
        print("=" * 60)

    if args.conflict == "simulate":
        # Simulate a conflict
        conflict = engine.create_conflict(
            PersonaRole.PLANNER,
            PersonaRole.EXECUTOR,
            "Resource allocation disagreement",
            "medium",
        )
        print(f"\nSimulated conflict: {conflict.id}")

        # Auto-resolve
        time.sleep(0.5)
        engine.resolve_conflict(
            conflict.id, "Agreed on resource distribution", PersonaRole.META_COGNITION
        )

    if not any([args.run, args.visualize, args.score, args.conflict]):
        parser.print_help()


if __name__ == "__main__":
    main()
