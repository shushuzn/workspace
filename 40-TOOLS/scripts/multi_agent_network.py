#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Multi-Agent Collaboration Network - Distributed AI Agent System
Features: 5 agent types, blackboard architecture, message passing, auction mechanism

Usage:
    python multi_agent_network.py --start
    python multi_agent_network.py --status
    python multi_agent_network.py --task "collect_papers"
"""

import os
import sys
import json
import time
import uuid
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from enum import Enum
import queue
import random

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class AgentType(Enum):
    """Agent types"""
    COLLECTOR = "collector"      # arXiv/GitHub/Medium data collection
    ANALYZER = "analyzer"        # Paper/code/data analysis
    WRITER = "writer"            # Report/doc/paper writing
    REVIEWER = "reviewer"        # Quality/security/compliance review
    COORDINATOR = "coordinator"  # Task allocation/conflict resolution


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessagePriority(Enum):
    """Message priority"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class Agent:
    """Agent definition"""
    id: str
    type: AgentType
    name: str
    capabilities: List[str]
    workload: float = 0.0  # 0-1
    status: str = "idle"
    tasks_completed: int = 0
    success_rate: float = 1.0
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Task:
    """Task definition"""
    id: str
    name: str
    description: str
    required_capabilities: List[str]
    priority: int = 2  # 0=critical, 3=low
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class Message:
    """Inter-agent message"""
    id: str
    from_agent: str
    to_agent: Optional[str]  # None = broadcast
    subject: str
    content: Dict
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    read: bool = False
    in_reply_to: Optional[str] = None


@dataclass
class BlackboardEntry:
    """Blackboard shared knowledge"""
    id: str
    key: str
    value: Any
    owner: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ttl_seconds: Optional[int] = None


class MultiAgentNetwork:
    """Multi-agent collaboration network"""
    
    def __init__(self):
        self.data_dir = WORKSPACE / "20-data-reports" / "agents"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.agents_file = self.data_dir / "agents.json"
        self.tasks_file = self.data_dir / "tasks.json"
        self.messages_file = self.data_dir / "messages.json"
        self.blackboard_file = self.data_dir / "blackboard.json"
        
        # Core components
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.messages: List[Message] = []
        self.blackboard: Dict[str, BlackboardEntry] = {}
        
        # Message queues per agent
        self.message_queues: Dict[str, queue.Queue] = {}
        
        # Task handlers
        self.task_handlers: Dict[str, Callable] = {}
        
        # Coordinator agent (special)
        self.coordinator_id: Optional[str] = None
        
        self.load_state()
        self._register_default_handlers()
    
    def load_state(self):
        """Load state"""
        if self.agents_file.exists():
            with open(self.agents_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.agents = {
                    k: Agent(
                        id=v['id'],
                        type=AgentType(v['type']),
                        name=v['name'],
                        capabilities=v['capabilities'],
                        workload=v.get('workload', 0),
                        status=v.get('status', 'idle'),
                        tasks_completed=v.get('tasks_completed', 0),
                        success_rate=v.get('success_rate', 1.0),
                        last_active=v.get('last_active', datetime.now().isoformat())
                    )
                    for k, v in data.get('agents', {}).items()
                }
        
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = {
                    k: Task(
                        id=v['id'],
                        name=v['name'],
                        description=v['description'],
                        required_capabilities=v['required_capabilities'],
                        priority=v.get('priority', 2),
                        status=TaskStatus(v.get('status', 'pending')),
                        assigned_to=v.get('assigned_to'),
                        created_at=v.get('created_at', datetime.now().isoformat()),
                        started_at=v.get('started_at'),
                        completed_at=v.get('completed_at'),
                        result=v.get('result'),
                        error=v.get('error')
                    )
                    for k, v in data.get('tasks', {}).items()
                }
        
        if self.messages_file.exists():
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.messages = [
                    Message(
                        id=v['id'],
                        from_agent=v['from_agent'],
                        to_agent=v.get('to_agent'),
                        subject=v['subject'],
                        content=v['content'],
                        priority=MessagePriority(v.get('priority', 2)),
                        timestamp=v.get('timestamp', datetime.now().isoformat()),
                        read=v.get('read', False),
                        in_reply_to=v.get('in_reply_to')
                    )
                    for v in data.get('messages', [])
                ]
        
        if self.blackboard_file.exists():
            with open(self.blackboard_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.blackboard = {
                    k: BlackboardEntry(
                        id=v['id'],
                        key=v['key'],
                        value=v['value'],
                        owner=v['owner'],
                        timestamp=v.get('timestamp', datetime.now().isoformat()),
                        ttl_seconds=v.get('ttl_seconds')
                    )
                    for k, v in data.get('entries', {}).items()
                }
    
    def save_state(self):
        """Save state"""
        with open(self.agents_file, 'w', encoding='utf-8') as f:
            json.dump({
                'agents': {
                    k: {
                        **asdict(v),
                        'type': v.type.value  # Convert enum to string
                    }
                    for k, v in self.agents.items()
                },
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump({
                'tasks': {
                    k: {
                        **asdict(v),
                        'status': v.status.value  # Convert enum to string
                    }
                    for k, v in self.tasks.items()
                },
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.messages_file, 'w', encoding='utf-8') as f:
            json.dump({
                'messages': [
                    {
                        **asdict(m),
                        'priority': m.priority.value  # Convert enum to string
                    }
                    for m in self.messages[-1000:]
                ],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.blackboard_file, 'w', encoding='utf-8') as f:
            json.dump({
                'entries': {k: asdict(v) for k, v in self.blackboard.items()},
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def register_agent(self, agent_id: str, agent_type: AgentType, name: str, 
                      capabilities: List[str]) -> Agent:
        """Register new agent"""
        agent = Agent(
            id=agent_id,
            type=agent_type,
            name=name,
            capabilities=capabilities
        )
        
        self.agents[agent_id] = agent
        self.message_queues[agent_id] = queue.Queue()
        
        if agent_type == AgentType.COORDINATOR:
            self.coordinator_id = agent_id
        
        print(f"✅ Agent registered: {name} ({agent_type.value})")
        print(f"   Capabilities: {', '.join(capabilities)}\n")
        
        return agent
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register task handler"""
        self.task_handlers[task_type] = handler
    
    def _register_default_handlers(self):
        """Register default task handlers"""
        def mock_handler(task: Task) -> Dict:
            """Mock handler for testing"""
            time.sleep(0.1)  # Simulate work
            return {
                'status': 'success',
                'task_id': task.id,
                'result': f'Completed {task.name}'
            }
        
        self.task_handlers['default'] = mock_handler
        self.task_handlers['collect_papers'] = mock_handler
        self.task_handlers['analyze_paper'] = mock_handler
        self.task_handlers['write_report'] = mock_handler
        self.task_handlers['review_code'] = mock_handler
    
    def create_task(self, name: str, description: str, 
                   required_capabilities: List[str],
                   priority: int = 2) -> Task:
        """Create new task"""
        task = Task(
            id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            required_capabilities=required_capabilities,
            priority=priority
        )
        
        self.tasks[task.id] = task
        
        # Broadcast task announcement
        self._broadcast_message(
            subject='new_task',
            content={'task_id': task.id, 'task': asdict(task)},
            priority=MessagePriority(priority)
        )
        
        print(f"📋 Task created: {task.name} (ID: {task.id})")
        print(f"   Priority: {['critical', 'high', 'normal', 'low'][priority]}")
        print(f"   Required: {', '.join(required_capabilities)}\n")
        
        return task
    
    def allocate_task(self, task_id: str) -> Optional[str]:
        """Allocate task to best agent using auction mechanism"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        # Find eligible agents
        eligible = [
            agent for agent in self.agents.values()
            if agent.status == 'idle'
            and all(cap in agent.capabilities for cap in task.required_capabilities)
        ]
        
        if not eligible:
            print(f"⚠️  No eligible agents for task: {task.name}")
            return None
        
        # Auction: agents bid based on capability match and workload
        bids = []
        for agent in eligible:
            # Score: capability match + availability
            capability_score = len(task.required_capabilities) / len(agent.capabilities)
            availability_score = 1 - agent.workload
            success_score = agent.success_rate
            
            bid = (capability_score * 0.4 + availability_score * 0.4 + success_score * 0.2)
            bids.append((agent.id, bid))
        
        # Select highest bidder
        winner_id = max(bids, key=lambda x: x[1])[0]
        
        # Assign task
        task.assigned_to = winner_id
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()
        
        # Update agent
        agent = self.agents[winner_id]
        agent.status = 'busy'
        agent.workload = min(1.0, agent.workload + 0.2)
        
        # Notify winner
        self._send_message(
            from_agent='system',
            to_agent=winner_id,
            subject='task_assigned',
            content={'task_id': task.id, 'task_name': task.name}
        )
        
        print(f"🎯 Task allocated: {task.name} → {agent.name}")
        print(f"   Bid score: {max(b[1] for b in bids):.3f}\n")
        
        return winner_id
    
    def execute_task(self, task_id: str) -> bool:
        """Execute assigned task"""
        task = self.tasks.get(task_id)
        if not task or not task.assigned_to:
            return False
        
        agent = self.agents.get(task.assigned_to)
        if not agent:
            return False
        
        # Find handler
        handler = self.task_handlers.get(task.name, self.task_handlers['default'])
        
        try:
            # Execute
            result = handler(task)
            
            # Update task
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.result = result
            
            # Update agent
            agent.status = 'idle'
            agent.workload = max(0.0, agent.workload - 0.2)
            agent.tasks_completed += 1
            # Update success rate (exponential moving average)
            agent.success_rate = agent.success_rate * 0.9 + 1.0 * 0.1
            
            print(f"✅ Task completed: {task.name}")
            print(f"   Agent: {agent.name}")
            print(f"   Result: {result}\n")
            
        except Exception as e:
            # Handle failure
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            agent.status = 'idle'
            agent.workload = max(0.0, agent.workload - 0.2)
            agent.success_rate = agent.success_rate * 0.9 + 0.0 * 0.1
            
            print(f"❌ Task failed: {task.name}")
            print(f"   Error: {e}\n")
        
        return task.status == TaskStatus.COMPLETED
    
    def _send_message(self, from_agent: str, to_agent: str, 
                    subject: str, content: Dict,
                    priority: MessagePriority = MessagePriority.NORMAL) -> Message:
        """Send message to specific agent (internal)"""
        return self.send_message(from_agent, to_agent, subject, content, priority)
    
    def send_message(self, from_agent: str, to_agent: str, 
                    subject: str, content: Dict,
                    priority: MessagePriority = MessagePriority.NORMAL) -> Message:
        """Send message to specific agent"""
        msg = Message(
            id=str(uuid.uuid4())[:8],
            from_agent=from_agent,
            to_agent=to_agent,
            subject=subject,
            content=content,
            priority=priority
        )
        
        self.messages.append(msg)
        
        if to_agent in self.message_queues:
            self.message_queues[to_agent].put(msg)
        
        return msg
    
    def _broadcast_message(self, subject: str, content: Dict,
                          priority: MessagePriority = MessagePriority.NORMAL):
        """Broadcast message to all agents"""
        for agent_id in self.agents.keys():
            self.send_message(
                from_agent='system',
                to_agent=agent_id,
                subject=subject,
                content=content,
                priority=priority
            )
    
    def write_to_blackboard(self, key: str, value: Any, owner: str, 
                           ttl_seconds: int = None) -> BlackboardEntry:
        """Write to shared blackboard"""
        entry = BlackboardEntry(
            id=str(uuid.uuid4())[:8],
            key=key,
            value=value,
            owner=owner,
            ttl_seconds=ttl_seconds
        )
        
        self.blackboard[key] = entry
        
        # Notify all agents
        self._broadcast_message(
            subject='blackboard_update',
            content={'key': key, 'owner': owner}
        )
        
        return entry
    
    def read_from_blackboard(self, key: str) -> Optional[Any]:
        """Read from blackboard"""
        entry = self.blackboard.get(key)
        if not entry:
            return None
        
        # Check TTL
        if entry.ttl_seconds:
            created = datetime.fromisoformat(entry.timestamp)
            if (datetime.now() - created).total_seconds() > entry.ttl_seconds:
                del self.blackboard[key]
                return None
        
        return entry.value
    
    def get_agent_messages(self, agent_id: str) -> List[Message]:
        """Get messages for agent"""
        messages = []
        q = self.message_queues.get(agent_id)
        
        if q:
            while not q.empty():
                messages.append(q.get())
        
        return messages
    
    def get_statistics(self) -> Dict:
        """Get network statistics"""
        agents_by_type = defaultdict(int)
        for agent in self.agents.values():
            agents_by_type[agent.type.value] += 1
        
        tasks_by_status = defaultdict(int)
        for task in self.tasks.values():
            tasks_by_status[task.status.value] += 1
        
        return {
            'total_agents': len(self.agents),
            'agents_by_type': dict(agents_by_type),
            'total_tasks': len(self.tasks),
            'tasks_by_status': dict(tasks_by_status),
            'messages': len(self.messages),
            'blackboard_entries': len(self.blackboard),
            'avg_success_rate': round(
                sum(a.success_rate for a in self.agents.values()) / len(self.agents), 3
            ) if self.agents else 0
        }
    
    def get_status(self) -> Dict:
        """Get network status"""
        return {
            'agents': [
                {
                    'id': a.id,
                    'name': a.name,
                    'type': a.type.value,
                    'status': a.status,
                    'workload': round(a.workload, 2),
                    'success_rate': round(a.success_rate, 3)
                }
                for a in self.agents.values()
            ],
            'pending_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            'active_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Agent Collaboration Network')
    parser.add_argument('--start', action='store_true', help='Start network simulation')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--task', type=str, help='Create and execute task')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    args = parser.parse_args()
    
    network = MultiAgentNetwork()
    
    if args.start:
        print("Starting multi-agent network (Ctrl+C to stop)...")
        # Initialize default agents if none exist
        if not network.agents:
            network.register_agent('coord-1', AgentType.COORDINATOR, 'Coordinator', 
                                  ['task_allocation', 'conflict_resolution'])
            network.register_agent('collect-1', AgentType.COLLECTOR, 'Collector-1',
                                  ['arxiv', 'github', 'medium'])
            network.register_agent('analyze-1', AgentType.ANALYZER, 'Analyzer-1',
                                  ['paper_analysis', 'code_review'])
            network.register_agent('write-1', AgentType.WRITER, 'Writer-1',
                                  ['report_writing', 'documentation'])
            network.register_agent('review-1', AgentType.REVIEWER, 'Reviewer-1',
                                  ['quality_check', 'security_audit'])
            network.save_state()
        
        try:
            while True:
                # Allocate pending tasks
                for task in network.tasks.values():
                    if task.status == TaskStatus.PENDING and not task.assigned_to:
                        network.allocate_task(task.id)
                
                # Execute assigned tasks
                for task in network.tasks.values():
                    if task.status == TaskStatus.IN_PROGRESS:
                        network.execute_task(task.id)
                
                time.sleep(1)
        except KeyboardInterrupt:
            network.save_state()
            print("\nNetwork stopped")
    
    elif args.status:
        status = network.get_status()
        stats = network.get_statistics()
        
        print("\n📊 Multi-Agent Network Status\n")
        print("Agents:")
        for agent in status['agents']:
            print(f"  {agent['name']} ({agent['type']})")
            print(f"    Status: {agent['status']}, Workload: {agent['workload']}")
            print(f"    Success Rate: {agent['success_rate']}")
        print()
        print(f"Pending Tasks: {status['pending_tasks']}")
        print(f"Active Tasks: {status['active_tasks']}")
        print(f"Average Success Rate: {stats['avg_success_rate']}")
        print()
    
    elif args.task:
        task_name = args.task
        task = network.create_task(
            name=task_name,
            description=f'Execute {task_name}',
            required_capabilities=[task_name.split('_')[0]]
        )
        
        agent_id = network.allocate_task(task.id)
        if agent_id:
            network.execute_task(task.id)
        
        network.save_state()
    
    elif args.demo:
        print("\n🧪 Multi-Agent Network Demo\n")
        
        # Register agents
        print("1. Registering Agents:")
        network.register_agent('coord-1', AgentType.COORDINATOR, 'Coordinator',
                              ['task_allocation', 'conflict_resolution'])
        network.register_agent('collect-1', AgentType.COLLECTOR, 'Collector-1',
                              ['arxiv', 'github', 'medium'])
        network.register_agent('collect-2', AgentType.COLLECTOR, 'Collector-2',
                              ['arxiv', 'github'])
        network.register_agent('analyze-1', AgentType.ANALYZER, 'Analyzer-1',
                              ['paper_analysis', 'code_review'])
        network.register_agent('write-1', AgentType.WRITER, 'Writer-1',
                              ['report_writing', 'documentation'])
        network.register_agent('review-1', AgentType.REVIEWER, 'Reviewer-1',
                              ['quality_check', 'security_audit'])
        
        # Create tasks
        print("\n2. Creating Tasks:")
        network.create_task('collect_papers', 'Collect latest 50 papers from arXiv',
                           ['arxiv'], priority=1)
        network.create_task('analyze_paper', 'Analyze paper for key contributions',
                           ['paper_analysis'], priority=2)
        network.create_task('write_report', 'Write daily research report',
                           ['report_writing'], priority=2)
        network.create_task('review_code', 'Security audit of new code',
                           ['security_audit'], priority=0)
        
        # Allocate and execute
        print("\n3. Allocating & Executing Tasks:")
        for task_id in list(network.tasks.keys()):
            network.allocate_task(task_id)
            network.execute_task(task_id)
        
        # Blackboard usage
        print("\n4. Blackboard Communication:")
        network.write_to_blackboard('latest_papers', ['paper1', 'paper2'], 'collect-1', ttl_seconds=3600)
        papers = network.read_from_blackboard('latest_papers')
        print(f"   Read from blackboard: {papers}")
        
        # Show statistics
        print("\n5. Network Statistics:")
        stats = network.get_statistics()
        print(json.dumps(stats, indent=2))
        
        network.save_state()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
