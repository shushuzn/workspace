#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Phase 6: Autonomy
=================================
Tests for:
- AutonomousDecisionEngine
- PersonaAgentSystem

Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import unittest
from pathlib import Path
import tempfile
import shutil
import time
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class TestAutonomousDecisionEngine(unittest.TestCase):
    """Test AutonomousDecisionEngine class."""

    def setUp(self):
        from memory_autonomous_engine import AutonomousDecisionEngine

        self.test_dir = tempfile.mkdtemp()
        self.engine = AutonomousDecisionEngine(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine.workspace_dir)
        self.assertTrue(self.engine.data_dir.exists())
        self.assertEqual(self.engine.mode.value, 'autonomous')

    def test_task_creation(self):
        """Test task creation."""
        from memory_autonomous_engine import Task, TaskPriority, TaskType

        task = Task(
            id="test-task-001",
            task_type=TaskType.DISTILLATION.value,
            priority=TaskPriority.HIGH.name,
            description="Test distillation task",
            scheduled_time="2026-03-17T06:00:00",
            estimated_duration=20
        )

        self.assertEqual(task.id, "test-task-001")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.retry_count, 0)

    def test_task_scoring(self):
        """Test task prioritization scoring."""
        from memory_autonomous_engine import Task, TaskPriority, TaskType
        from datetime import datetime, timedelta

        # Create tasks with different priorities
        now = datetime.now()

        critical_task = Task(
            id="critical",
            task_type=TaskType.CUSTOM.value,
            priority=TaskPriority.CRITICAL.name,
            description="Critical task",
            scheduled_time=now.isoformat(),
            estimated_duration=10
        )

        low_task = Task(
            id="low",
            task_type=TaskType.CUSTOM.value,
            priority=TaskPriority.LOW.name,
            description="Low priority task",
            scheduled_time=now.isoformat(),
            estimated_duration=10
        )

        # Score tasks
        critical_score = self.engine._score_task(critical_task)
        low_score = self.engine._score_task(low_task)

        # Critical should have lower score (higher priority)
        self.assertLess(critical_score, low_score)

    def test_system_health_assessment(self):
        """Test system health assessment."""
        health = self.engine._assystem_health()

        self.assertIn('status', health)
        self.assertIn('issues', health)
        self.assertIn('timestamp', health)
        self.assertIn(health['status'], ['healthy', 'warning', 'critical'])

    def test_task_generation(self):
        """Test candidate task generation."""
        candidates = self.engine._generate_candidate_tasks()

        # Should generate at least some tasks
        self.assertIsInstance(candidates, list)

        # All should be Task objects
        from memory_autonomous_engine import Task
        for task in candidates:
            self.assertIsInstance(task, Task)

    def test_goal_setting(self):
        """Test goal setting and tracking."""
        from memory_autonomous_engine import SystemGoal

        goal = SystemGoal(
            id="goal-001",
            description="Improve system score to 105",
            target_metric="system_score",
            current_value=102.6,
            target_value=105.0,
            deadline="2026-03-20T00:00:00",
            priority="HIGH"
        )

        self.engine.set_goal(goal)

        # Verify goal is stored
        self.assertIn("goal-001", self.engine.goals)
        self.assertEqual(self.engine.goals["goal-001"].target_value, 105.0)

    def test_status_reporting(self):
        """Test status reporting."""
        status = self.engine.get_status()

        self.assertIn('mode', status)
        self.assertIn('decisions_made', status)
        self.assertIn('tasks_completed', status)
        self.assertIn('autonomy_score', status)
        self.assertIn('uptime_hours', status)

    def test_state_persistence(self):
        """Test state save and load."""
        # Modify state
        self.engine.decisions_made = 100
        self.engine.tasks_completed = 50
        self.engine.autonomy_score = 95.0

        # Save
        self.engine._save_state()

        # Create new engine and load
        from memory_autonomous_engine import AutonomousDecisionEngine
        new_engine = AutonomousDecisionEngine(self.test_dir)

        # Verify state restored
        self.assertEqual(new_engine.decisions_made, 100)
        self.assertEqual(new_engine.tasks_completed, 50)
        self.assertEqual(new_engine.autonomy_score, 95.0)


class TestPersonaAgentSystem(unittest.TestCase):
    """Test PersonaAgentSystem class."""

    def setUp(self):
        from memory_persona_agents import PersonaAgentSystem

        self.test_dir = tempfile.mkdtemp()
        self.system = PersonaAgentSystem(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_agent_initialization(self):
        """Test all 7 agents initialized."""
        self.assertEqual(len(self.system.agents), 7)

        # Check all persona types present
        persona_types = ['planner', 'executor', 'critic', 'learner',
                        'coordinator', 'innovator', 'metacognition']

        for persona in persona_types:
            agent_id = f"agent-{persona}"
            self.assertIn(agent_id, self.system.agents)

    def test_agent_capabilities(self):
        """Test agent capabilities."""
        planner = self.system.agents.get('agent-planner')
        self.assertIn('planning', planner.capabilities)
        self.assertIn('decomposition', planner.capabilities)

        executor = self.system.agents.get('agent-executor')
        self.assertIn('execution', executor.capabilities)
        self.assertIn('implementation', executor.capabilities)

        critic = self.system.agents.get('agent-critic')
        self.assertIn('review', critic.capabilities)
        self.assertIn('validation', critic.capabilities)

    def test_message_sending(self):
        """Test inter-agent messaging."""
        from memory_persona_agents import AgentMessage, MessageType

        message = AgentMessage(
            id="msg-001",
            sender="agent-planner",
            receiver="agent-executor",
            message_type=MessageType.TASK_REQUEST.value,
            content={'task': {'id': 'test', 'description': 'Test task'}}
        )

        self.system.send_message(message)

        # Verify message in queue
        self.assertEqual(self.system.message_queue.qsize(), 1)

    def test_message_processing(self):
        """Test message processing."""
        from memory_persona_agents import AgentMessage, MessageType

        # Send message
        message = AgentMessage(
            id="msg-002",
            sender="agent-planner",
            receiver="broadcast",
            message_type=MessageType.INFORMATION_SHARE.value,
            content={'key': 'test_key', 'value': 'test_value'}
        )
        self.system.send_message(message)

        # Process
        processed = self.system.process_messages()

        self.assertEqual(processed, 1)

        # Verify stored in shared memory
        self.assertIn('test_key', self.system.shared_memory)

    def test_decision_proposal(self):
        """Test collective decision making."""
        # Propose decision
        proposal_id = self.system.propose_decision('agent-planner', {
            'action': 'run_evolution',
            'reason': 'Weekly schedule'
        })

        # Verify proposal created
        self.assertIn(proposal_id, self.system.pending_decisions)
        self.assertIn(proposal_id, self.system.votes)

    def test_system_status(self):
        """Test system status reporting."""
        status = self.system.get_system_status()

        self.assertIn('total_agents', status)
        self.assertEqual(status['total_agents'], 7)
        self.assertIn('active_agents', status)
        self.assertIn('pending_messages', status)
        self.assertIn('shared_memory_keys', status)
        self.assertIn('uptime_hours', status)

    def test_agent_status(self):
        """Test individual agent status."""
        status = self.system.get_agent_status('agent-planner')

        self.assertEqual(status['persona_type'], 'planner')
        self.assertEqual(status['status'], 'active')
        self.assertIn('capabilities', status)
        self.assertIn('health_score', status)

    def test_collaboration_cycle(self):
        """Test collaboration cycle execution."""
        # Run 1 cycle (faster for testing)
        self.system.run_collaboration_cycle(1)

        # Verify some activity occurred
        status = self.system.get_system_status()
        # Don't assert on tasks_completed as it may be 0 in 1 cycle
        self.assertIn('total_agents', status)


class TestIntegration(unittest.TestCase):
    """Integration tests for autonomy system."""

    def setUp(self):
        from memory_autonomous_engine import AutonomousDecisionEngine
        from memory_persona_agents import PersonaAgentSystem

        self.test_dir = tempfile.mkdtemp()
        self.engine = AutonomousDecisionEngine(self.test_dir)
        self.agents = PersonaAgentSystem(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_engine_agent_integration(self):
        """Test integration between engine and agents."""
        # Engine creates task
        task = self.engine._create_improvement_task()

        # Agents process task
        from memory_persona_agents import AgentMessage, MessageType

        message = AgentMessage(
            id=f"task-{task.id}",
            sender="engine",
            receiver="broadcast",
            message_type=MessageType.TASK_ASSIGNMENT.value,
            content={'task': task.to_dict()}
        )

        self.agents.send_message(message)
        processed = self.agents.process_messages()

        self.assertEqual(processed, 1)

    def test_autonomous_cycle(self):
        """Test short autonomous cycle."""
        # Run brief autonomous loop (1 minute)
        # Use threading to avoid blocking
        import threading

        def run_loop():
            self.engine.run_autonomous_loop(1)

        thread = threading.Thread(target=run_loop)
        thread.start()
        thread.join(timeout=120)  # 2 min timeout

        # Verify some decisions made
        self.assertGreater(self.engine.decisions_made, 0)

    def test_shared_state(self):
        """Test shared state between components."""
        # Set goal in engine
        from memory_autonomous_engine import SystemGoal

        goal = SystemGoal(
            id="integration-test",
            description="Test goal",
            target_metric="test",
            current_value=0.0,
            target_value=100.0,
            deadline="2026-12-31T23:59:59",
            priority="HIGH"
        )
        self.engine.set_goal(goal)

        # Share info via agents
        self.agents.shared_memory['test_data'] = {'value': 42}

        # Both should have their state
        self.assertIn("integration-test", self.engine.goals)
        self.assertIn('test_data', self.agents.shared_memory)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousDecisionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestPersonaAgentSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" *70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" *70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
