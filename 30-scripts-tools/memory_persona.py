#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7-Persona Multi-Agent System
=============================
Transforms 7 personas into independent autonomous agents
with communication, collaboration, and collective decision-making.

Features:
- Independent persona agents
- Inter-agent communication protocol
- Collective decision making
- Conflict resolution
- Shared memory space
- Agent health monitoring

Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import queue
import uuid
import random

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class PersonaType(Enum):
    """The 7 persona types."""
    PLANNER = "planner"
    EXECUTOR = "executor"
    CRITIC = "critic"
    LEARNER = "learner"
    COORDINATOR = "coordinator"
    INNOVATOR = "innovator"
    METACOGNITION = "metacognition"


class MessageType(Enum):
    """Inter-agent message types."""
    TASK_REQUEST = "task_request"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    INFORMATION_SHARE = "information_share"
    DECISION_PROPOSAL = "decision_proposal"
    DECISION_VOTE = "decision_vote"
    CONFLICT_ALERT = "conflict_alert"
    HEALTH_CHECK = "health_check"
    EMERGENCY = "emergency"


class AgentStatus(Enum):
    """Agent operational status."""
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentMessage:
    """Message between agents."""
    id: str
    sender: str
    receiver: str  # Can be "broadcast"
    message_type: str
    content: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: int = 0  # 0-10, higher = more urgent
    requires_response: bool = False
    in_reply_to: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PersonaAgent:
    """Individual persona agent."""
    id: str
    persona_type: str
    name: str
    description: str
    status: str = "active"
    capabilities: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    health_score: float = 100.0
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PersonaAgentSystem:
    """Multi-agent system for 7 personas."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.data_dir = self.workspace_dir / "data" / "agents"
        self.logs_dir = self.workspace_dir / "21-reports" / "agents"
        
        # Ensure directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Message queue
        self.message_queue: queue.Queue = queue.Queue()
        
        # Agent registry
        self.agents: Dict[str, PersonaAgent] = {}
        
        # Shared memory
        self.shared_memory: Dict[str, Any] = {}
        
        # Decision state
        self.pending_decisions: Dict[str, Dict] = {}
        self.votes: Dict[str, Dict[str, str]] = {}
        
        # Initialize agents
        self._initialize_agents()
        
        # Start time
        self.start_time = datetime.now()
        
    def _initialize_agents(self):
        """Initialize all 7 persona agents."""
        persona_configs = {
            PersonaType.PLANNER: {
                'name': 'Planner Agent',
                'description': 'Strategic planning and task decomposition',
                'capabilities': ['planning', 'decomposition', 'scheduling', 'resource_allocation']
            },
            PersonaType.EXECUTOR: {
                'name': 'Executor Agent',
                'description': 'Task execution and delivery',
                'capabilities': ['execution', 'implementation', 'testing', 'deployment']
            },
            PersonaType.CRITIC: {
                'name': 'Critic Agent',
                'description': 'Quality review and error detection',
                'capabilities': ['review', 'validation', 'scoring', 'error_detection']
            },
            PersonaType.LEARNER: {
                'name': 'Learner Agent',
                'description': 'Memory update and knowledge extraction',
                'capabilities': ['learning', 'distillation', 'memory_update', 'knowledge_extraction']
            },
            PersonaType.COORDINATOR: {
                'name': 'Coordinator Agent',
                'description': 'Agent coordination and balance',
                'capabilities': ['coordination', 'conflict_resolution', 'load_balancing']
            },
            PersonaType.INNOVATOR: {
                'name': 'Innovator Agent',
                'description': 'Creative thinking and breakthrough ideas',
                'capabilities': ['innovation', 'pattern_recognition', 'creative_synthesis']
            },
            PersonaType.METACOGNITION: {
                'name': 'Metacognition Agent',
                'description': 'System monitoring and self-reflection',
                'capabilities': ['monitoring', 'self_reflection', 'meta_learning', 'system_health']
            }
        }
        
        for persona_type, config in persona_configs.items():
            agent_id = f"agent-{persona_type.value}"
            agent = PersonaAgent(
                id=agent_id,
                persona_type=persona_type.value,
                name=config['name'],
                description=config['description'],
                capabilities=config['capabilities']
            )
            self.agents[agent_id] = agent
        
        self._log(f"Initialized {len(self.agents)} agents")
    
    def send_message(self, message: AgentMessage):
        """Send message to agent(s)."""
        self.message_queue.put(message)
        self._log(f"Message sent: {message.id} from {message.sender} to {message.receiver}")
    
    def receive_message(self, timeout: float = 1.0) -> Optional[AgentMessage]:
        """Receive message from queue."""
        try:
            message = self.message_queue.get(timeout=timeout)
            return message
        except queue.Empty:
            return None
    
    def process_messages(self):
        """Process all pending messages."""
        processed = 0
        while not self.message_queue.empty():
            message = self.message_queue.get_nowait()
            self._handle_message(message)
            processed += 1
        return processed
    
    def _handle_message(self, message: AgentMessage):
        """Handle individual message."""
        msg_type = MessageType(message.message_type)
        
        handlers = {
            MessageType.TASK_REQUEST: self._handle_task_request,
            MessageType.TASK_ASSIGNMENT: self._handle_task_assignment,
            MessageType.TASK_COMPLETE: self._handle_task_complete,
            MessageType.TASK_FAILED: self._handle_task_failed,
            MessageType.INFORMATION_SHARE: self._handle_information_share,
            MessageType.DECISION_PROPOSAL: self._handle_decision_proposal,
            MessageType.DECISION_VOTE: self._handle_decision_vote,
            MessageType.CONFLICT_ALERT: self._handle_conflict_alert,
            MessageType.HEALTH_CHECK: self._handle_health_check,
            MessageType.EMERGENCY: self._handle_emergency,
        }
        
        handler = handlers.get(msg_type)
        if handler:
            handler(message)
    
    def _handle_task_request(self, message: AgentMessage):
        """Handle task request."""
        # Find suitable agent
        task_info = message.content.get('task', {})
        required_capability = task_info.get('required_capability')
        
        suitable_agents = []
        for agent_id, agent in self.agents.items():
            if agent.status == 'active' and agent.current_task is None:
                if required_capability is None or required_capability in agent.capabilities:
                    suitable_agents.append(agent)
        
        if suitable_agents:
            # Assign to best agent
            best_agent = max(suitable_agents, key=lambda a: a.health_score)
            assignment = AgentMessage(
                id=str(uuid.uuid4()),
                sender=message.receiver,
                receiver=best_agent.id,
                message_type=MessageType.TASK_ASSIGNMENT.value,
                content=task_info
            )
            self.send_message(assignment)
    
    def _handle_task_assignment(self, message: AgentMessage):
        """Handle task assignment."""
        agent = self.agents.get(message.receiver)
        if agent:
            agent.status = 'busy'
            agent.current_task = message.content.get('task_id')
            agent.last_active = datetime.now().isoformat()
    
    def _handle_task_complete(self, message: AgentMessage):
        """Handle task completion."""
        agent = self.agents.get(message.sender)
        if agent:
            agent.status = 'active'
            agent.current_task = None
            agent.tasks_completed += 1
            agent.health_score = min(100.0, agent.health_score + 1.0)
            
            # Store result in shared memory
            task_id = message.content.get('task_id')
            self.shared_memory[f"task_result_{task_id}"] = {
                'status': 'completed',
                'result': message.content.get('result'),
                'completed_at': datetime.now().isoformat()
            }
    
    def _handle_task_failed(self, message: AgentMessage):
        """Handle task failure."""
        agent = self.agents.get(message.sender)
        if agent:
            agent.status = 'active'
            agent.current_task = None
            agent.tasks_failed += 1
            agent.health_score = max(0.0, agent.health_score - 5.0)
    
    def _handle_information_share(self, message: AgentMessage):
        """Handle information sharing."""
        # Store in shared memory
        key = message.content.get('key')
        value = message.content.get('value')
        if key:
            self.shared_memory[key] = {
                'value': value,
                'shared_by': message.sender,
                'timestamp': datetime.now().isoformat()
            }
            
            # Broadcast to all agents
            broadcast = AgentMessage(
                id=str(uuid.uuid4()),
                sender=message.sender,
                receiver="broadcast",
                message_type=MessageType.INFORMATION_SHARE.value,
                content={'key': key, 'value': value}
            )
            self.send_message(broadcast)
    
    def _handle_decision_proposal(self, message: AgentMessage):
        """Handle decision proposal."""
        proposal_id = message.content.get('proposal_id')
        self.pending_decisions[proposal_id] = {
            'proposal': message.content,
            'proposer': message.sender,
            'timestamp': datetime.now().isoformat()
        }
        self.votes[proposal_id] = {}
        
        # Request votes from all agents
        for agent_id in self.agents:
            if agent_id != message.sender:
                vote_request = AgentMessage(
                    id=str(uuid.uuid4()),
                    sender=message.sender,
                    receiver=agent_id,
                    message_type=MessageType.DECISION_VOTE.value,
                    content={'proposal_id': proposal_id, 'proposal': message.content},
                    requires_response=True
                )
                self.send_message(vote_request)
    
    def _handle_decision_vote(self, message: AgentMessage):
        """Handle decision vote."""
        proposal_id = message.content.get('proposal_id')
        if proposal_id in self.pending_decisions:
            voter = message.sender
            vote = message.content.get('vote')  # 'approve', 'reject', 'abstain'
            self.votes[proposal_id][voter] = vote
            
            # Check if all votes received
            if len(self.votes[proposal_id]) >= len(self.agents) - 1:
                self._finalize_decision(proposal_id)
    
    def _finalize_decision(self, proposal_id: str):
        """Finalize decision based on votes."""
        votes = self.votes.get(proposal_id, {})
        approve_count = sum(1 for v in votes.values() if v == 'approve')
        reject_count = sum(1 for v in votes.values() if v == 'reject')
        
        decision = 'approved' if approve_count > reject_count else 'rejected'
        
        # Store decision
        self.shared_memory[f"decision_{proposal_id}"] = {
            'decision': decision,
            'votes': votes,
            'finalized_at': datetime.now().isoformat()
        }
        
        # Broadcast result
        result_msg = AgentMessage(
            id=str(uuid.uuid4()),
            sender="system",
            receiver="broadcast",
            message_type=MessageType.INFORMATION_SHARE.value,
            content={
                'key': f"decision_{proposal_id}",
                'value': {'decision': decision, 'votes': votes}
            }
        )
        self.send_message(result_msg)
        
        # Clean up
        if proposal_id in self.pending_decisions:
            del self.pending_decisions[proposal_id]
        if proposal_id in self.votes:
            del self.votes[proposal_id]
    
    def _handle_conflict_alert(self, message: AgentMessage):
        """Handle conflict alert."""
        # Notify coordinator
        coordinator = self.agents.get('agent-coordinator')
        if coordinator:
            alert = AgentMessage(
                id=str(uuid.uuid4()),
                sender=message.sender,
                receiver='agent-coordinator',
                message_type=MessageType.CONFLICT_ALERT.value,
                content=message.content
            )
            self.send_message(alert)
    
    def _handle_health_check(self, message: AgentMessage):
        """Handle health check."""
        agent = self.agents.get(message.sender)
        if agent:
            agent.last_active = datetime.now().isoformat()
            # Respond with health status
            response = AgentMessage(
                id=str(uuid.uuid4()),
                sender=message.sender,
                receiver=message.content.get('requester', 'system'),
                message_type=MessageType.HEALTH_CHECK.value,
                content={
                    'agent_id': agent.id,
                    'health_score': agent.health_score,
                    'status': agent.status
                }
            )
            self.send_message(response)
    
    def _handle_emergency(self, message: AgentMessage):
        """Handle emergency message."""
        # Alert all agents
        emergency = AgentMessage(
            id=str(uuid.uuid4()),
            sender=message.sender,
            receiver="broadcast",
            message_type=MessageType.EMERGENCY.value,
            content=message.content,
            priority=10
        )
        self.send_message(emergency)
        
        # Log emergency
        self._log(f"🚨 EMERGENCY: {message.content}")
    
    def propose_decision(self, agent_id: str, proposal: Dict) -> str:
        """Propose a decision for collective voting."""
        proposal_id = str(uuid.uuid4())
        proposal_msg = AgentMessage(
            id=str(uuid.uuid4()),
            sender=agent_id,
            receiver="broadcast",
            message_type=MessageType.DECISION_PROPOSAL.value,
            content={
                'proposal_id': proposal_id,
                'proposal': proposal
            }
        )
        self.send_message(proposal_msg)
        return proposal_id
    
    def get_agent_status(self, agent_id: str) -> Dict:
        """Get status of individual agent."""
        agent = self.agents.get(agent_id)
        if agent:
            return agent.to_dict()
        return {}
    
    def get_system_status(self) -> Dict:
        """Get overall system status."""
        uptime = (datetime.now() - self.start_time).total_seconds() / 3600
        
        return {
            'total_agents': len(self.agents),
            'active_agents': sum(1 for a in self.agents.values() if a.status == 'active'),
            'busy_agents': sum(1 for a in self.agents.values() if a.status == 'busy'),
            'pending_messages': self.message_queue.qsize(),
            'pending_decisions': len(self.pending_decisions),
            'shared_memory_keys': len(self.shared_memory),
            'uptime_hours': uptime,
            'total_tasks_completed': sum(a.tasks_completed for a in self.agents.values()),
            'total_tasks_failed': sum(a.tasks_failed for a in self.agents.values()),
            'average_health': sum(a.health_score for a in self.agents.values()) / len(self.agents)
        }
    
    def run_collaboration_cycle(self, cycles: int = 10):
        """Run agent collaboration cycles."""
        print(f"🎭 Starting {cycles} collaboration cycles...")
        print("="*70)
        
        for cycle in range(1, cycles + 1):
            print(f"\nCycle {cycle}/{cycles}:")
            
            # Simulate task workflow
            if cycle % 3 == 1:
                # Planner proposes task
                self._simulate_planning()
            elif cycle % 3 == 2:
                # Executor completes task
                self._simulate_execution()
            else:
                # Critic reviews
                self._simulate_review()
            
            # Process messages
            processed = self.process_messages()
            
            # Health check every 5 cycles
            if cycle % 5 == 0:
                self._broadcast_health_check()
            
            print(f"  Messages processed: {processed}")
            print(f"  Shared memory size: {len(self.shared_memory)}")
            
            time.sleep(0.5)  # Simulate processing time
        
        print("="*70)
        status = self.get_system_status()
        print(f"✅ Collaboration complete!")
        print(f"  Tasks completed: {status['total_tasks_completed']}")
        print(f"  Average health: {status['average_health']:.1f}/100")
        print(f"  Shared memory: {status['shared_memory_keys']} entries")
    
    def _simulate_planning(self):
        """Simulate planning phase."""
        planner = self.agents.get('agent-planner')
        if planner:
            # Create task plan
            task = {
                'task_id': f"task-{uuid.uuid4().hex[:8]}",
                'description': 'Innovation analysis',
                'required_capability': 'execution',
                'priority': 5
            }
            
            # Request executor
            request = AgentMessage(
                id=str(uuid.uuid4()),
                sender='agent-planner',
                receiver='broadcast',
                message_type=MessageType.TASK_REQUEST.value,
                content={'task': task}
            )
            self.send_message(request)
    
    def _simulate_execution(self):
        """Simulate execution phase."""
        executor = self.agents.get('agent-executor')
        if executor and executor.current_task:
            # Complete task
            complete = AgentMessage(
                id=str(uuid.uuid4()),
                sender='agent-executor',
                receiver='broadcast',
                message_type=MessageType.TASK_COMPLETE.value,
                content={
                    'task_id': executor.current_task,
                    'result': {'success': True, 'output': 'Analysis complete'}
                }
            )
            self.send_message(complete)
    
    def _simulate_review(self):
        """Simulate review phase."""
        critic = self.agents.get('agent-critic')
        if critic:
            # Review recent work
            score = random.uniform(85, 98)
            review = AgentMessage(
                id=str(uuid.uuid4()),
                sender='agent-critic',
                receiver='broadcast',
                message_type=MessageType.INFORMATION_SHARE.value,
                content={
                    'key': f"review-{uuid.uuid4().hex[:8]}",
                    'value': {'score': score, 'feedback': 'Excellent work'}
                }
            )
            self.send_message(review)
    
    def _broadcast_health_check(self):
        """Broadcast health check to all agents."""
        for agent_id in self.agents:
            health_check = AgentMessage(
                id=str(uuid.uuid4()),
                sender='system',
                receiver=agent_id,
                message_type=MessageType.HEALTH_CHECK.value,
                content={'requester': 'system'}
            )
            self.send_message(health_check)
    
    def _log(self, message: str):
        """Log system activity."""
        log_file = self.logs_dir / f"agents-{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="7-Persona Multi-Agent System")
    parser.add_argument(
        "--workspace",
        default="D:\\OpenClaw\\workspace",
        help="Workspace directory"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status"
    )
    parser.add_argument(
        "--agent-status",
        type=str,
        help="Show specific agent status"
    )
    parser.add_argument(
        "--run",
        type=int,
        default=0,
        help="Run collaboration cycles"
    )
    
    args = parser.parse_args()
    
    # Create system
    system = PersonaAgentSystem(args.workspace)
    
    if args.status:
        status = system.get_system_status()
        print(json.dumps(status, indent=2))
        return 0
    
    if args.agent_status:
        status = system.get_agent_status(args.agent_status)
        if status:
            print(json.dumps(status, indent=2))
        else:
            print(f"Agent not found: {args.agent_status}")
        return 0
    
    if args.run > 0:
        system.run_collaboration_cycles(args.run)
        return 0
    
    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
