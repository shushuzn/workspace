#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cluster Manager - Distributed system orchestration

Features:
- Node registration
- Health monitoring
- Load balancing
- Task distribution
- Failover handling
- Cluster statistics
"""

import os
import sys
import json
import time
import socket
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import threading

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
CLUSTER_DIR = WORKSPACE / 'data' / 'cluster'
CLUSTER_DIR.mkdir(parents=True, exist_ok=True)

class Node:
    """Cluster node representation"""
    
    def __init__(self, node_id: str, host: str, port: int, metadata: Dict = None):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.metadata = metadata or {}
        self.status = 'unknown'
        self.last_heartbeat = None
        self.registered_at = datetime.now()
        self.tasks_completed = 0
        self.load = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'node_id': self.node_id,
            'host': self.host,
            'port': self.port,
            'metadata': self.metadata,
            'status': self.status,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'registered_at': self.registered_at.isoformat(),
            'tasks_completed': self.tasks_completed,
            'load': self.load,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Node':
        """Create from dictionary"""
        node = cls(
            data['node_id'],
            data['host'],
            data['port'],
            data.get('metadata', {}),
        )
        node.status = data.get('status', 'unknown')
        if data.get('last_heartbeat'):
            node.last_heartbeat = datetime.fromisoformat(data['last_heartbeat'])
        node.registered_at = datetime.fromisoformat(data['registered_at'])
        node.tasks_completed = data.get('tasks_completed', 0)
        node.load = data.get('load', 0.0)
        return node
    
    def is_healthy(self, timeout_seconds: int = 60) -> bool:
        """Check if node is healthy"""
        if not self.last_heartbeat:
            return False
        
        return (datetime.now() - self.last_heartbeat).total_seconds() < timeout_seconds
    
    def update_status(self):
        """Update node status based on heartbeat"""
        if self.is_healthy():
            self.status = 'online'
        else:
            self.status = 'offline'


class ClusterManager:
    """
    Distributed cluster manager
    
    Features:
    - Node registration
    - Health monitoring
    - Load balancing
    - Task distribution
    - Failover handling
    """
    
    def __init__(self, cluster_file: Path = None):
        self.cluster_file = cluster_file or (CLUSTER_DIR / 'cluster_state.json')
        self.nodes: Dict[str, Node] = {}
        self.tasks: Dict[str, Dict] = {}
        self.task_queue: List[Dict] = []
        
        # Load existing cluster state
        self._load_state()
    
    def _load_state(self):
        """Load cluster state from file"""
        if self.cluster_file.exists():
            with open(self.cluster_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.nodes = {
                node_id: Node.from_dict(node_data)
                for node_id, node_data in data.get('nodes', {}).items()
            }
            self.tasks = data.get('tasks', {})
            self.task_queue = data.get('task_queue', [])
            
            # Update statuses
            for node in self.nodes.values():
                node.update_status()
            
            print(f"✅ Loaded cluster state ({len(self.nodes)} nodes)")
    
    def _save_state(self):
        """Save cluster state to file"""
        self.cluster_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'tasks': self.tasks,
            'task_queue': self.task_queue,
            'last_updated': datetime.now().isoformat(),
        }
        
        with open(self.cluster_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def register_node(self, node_id: str, host: str, port: int, metadata: Dict = None) -> Node:
        """
        Register a new node
        
        Args:
            node_id: Unique node identifier
            host: Node hostname/IP
            port: Node port
            metadata: Optional metadata
        
        Returns:
            Registered node
        """
        node = Node(node_id, host, port, metadata)
        node.last_heartbeat = datetime.now()
        node.status = 'online'
        
        self.nodes[node_id] = node
        self._save_state()
        
        print(f"✅ Node registered: {node_id} ({host}:{port})")
        return node
    
    def unregister_node(self, node_id: str) -> bool:
        """Unregister a node"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self._save_state()
            print(f"✅ Node unregistered: {node_id}")
            return True
        return False
    
    def heartbeat(self, node_id: str, load: float = None) -> bool:
        """
        Receive heartbeat from node
        
        Args:
            node_id: Node identifier
            load: Current node load (0.0-1.0)
        
        Returns:
            Success status
        """
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        node.last_heartbeat = datetime.now()
        node.status = 'online'
        
        if load is not None:
            node.load = load
        
        self._save_state()
        return True
    
    def get_healthy_nodes(self) -> List[Node]:
        """Get all healthy nodes"""
        return [
            node for node in self.nodes.values()
            if node.is_healthy()
        ]
    
    def get_best_node(self, strategy: str = 'load') -> Optional[Node]:
        """
        Get best node for task assignment
        
        Args:
            strategy: Selection strategy (load/random/round_robin)
        
        Returns:
            Selected node or None
        """
        healthy = self.get_healthy_nodes()
        
        if not healthy:
            return None
        
        if strategy == 'load':
            # Select node with lowest load
            return min(healthy, key=lambda n: n.load)
        elif strategy == 'random':
            import random
            return random.choice(healthy)
        else:
            return healthy[0]
    
    def submit_task(self, task_id: str, task_data: Dict, priority: int = 0) -> str:
        """
        Submit task to cluster
        
        Args:
            task_id: Task identifier
            task_data: Task data
            priority: Task priority (higher = more urgent)
        
        Returns:
            Task ID
        """
        task = {
            'task_id': task_id,
            'data': task_data,
            'priority': priority,
            'status': 'pending',
            'submitted_at': datetime.now().isoformat(),
            'assigned_to': None,
            'completed_at': None,
        }
        
        self.tasks[task_id] = task
        self.task_queue.append(task)
        
        # Sort by priority
        self.task_queue.sort(key=lambda t: t['priority'], reverse=True)
        
        self._save_state()
        return task_id
    
    def assign_tasks(self) -> List[Tuple[str, str]]:
        """
        Assign pending tasks to available nodes
        
        Returns:
            List of (task_id, node_id) assignments
        """
        assignments = []
        
        # Get pending tasks
        pending = [t for t in self.task_queue if t['status'] == 'pending']
        
        for task in pending:
            node = self.get_best_node()
            
            if node:
                # Assign task
                task['status'] = 'assigned'
                task['assigned_to'] = node.node_id
                
                assignments.append((task['task_id'], node.node_id))
        
        self._save_state()
        return assignments
    
    def complete_task(self, task_id: str, node_id: str, result: Any = None) -> bool:
        """
        Mark task as complete
        
        Args:
            task_id: Task identifier
            node_id: Node that completed the task
            result: Task result
        
        Returns:
            Success status
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task['status'] = 'completed'
        task['completed_at'] = datetime.now().isoformat()
        task['result'] = result
        
        # Update node stats
        if node_id in self.nodes:
            self.nodes[node_id].tasks_completed += 1
        
        # Remove from queue
        self.task_queue = [t for t in self.task_queue if t['task_id'] != task_id]
        
        self._save_state()
        return True
    
    def get_cluster_stats(self) -> Dict:
        """Get cluster statistics"""
        healthy = self.get_healthy_nodes()
        
        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t['status'] == 'completed')
        pending = sum(1 for t in self.tasks.values() if t['status'] == 'pending')
        assigned = sum(1 for t in self.tasks.values() if t['status'] == 'assigned')
        
        return {
            'total_nodes': len(self.nodes),
            'healthy_nodes': len(healthy),
            'offline_nodes': len(self.nodes) - len(healthy),
            'total_tasks': total_tasks,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'assigned_tasks': assigned,
            'avg_load': sum(n.load for n in healthy) / max(1, len(healthy)),
            'total_tasks_completed': sum(n.tasks_completed for n in self.nodes.values()),
        }
    
    def list_nodes(self) -> List[Dict]:
        """List all nodes"""
        return [node.to_dict() for node in self.nodes.values()]
    
    def list_tasks(self, status: str = None) -> List[Dict]:
        """List tasks with optional status filter"""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t['status'] == status]
        
        return tasks
    
    def health_check(self) -> Dict:
        """Perform cluster health check"""
        stats = self.get_cluster_stats()
        
        # Determine overall health
        if stats['healthy_nodes'] == 0:
            health = 'critical'
        elif stats['healthy_nodes'] < len(self.nodes) * 0.5:
            health = 'warning'
        else:
            health = 'healthy'
        
        return {
            'overall_health': health,
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'nodes': [
                {
                    'node_id': node.node_id,
                    'status': node.status,
                    'load': node.load,
                    'last_heartbeat': node.last_heartbeat.isoformat() if node.last_heartbeat else None,
                }
                for node in self.nodes.values()
            ],
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cluster Manager")
    parser.add_argument('--register', type=str, help='Register node (format: node_id@host:port)')
    parser.add_argument('--unregister', type=str, help='Unregister node')
    parser.add_argument('--heartbeat', type=str, help='Send heartbeat (format: node_id@load)')
    parser.add_argument('--submit', type=str, help='Submit task (format: task_id@priority)')
    parser.add_argument('--assign', action='store_true', help='Assign pending tasks')
    parser.add_argument('--stats', action='store_true', help='Show cluster statistics')
    parser.add_argument('--health', action='store_true', help='Health check')
    parser.add_argument('--list-nodes', action='store_true', help='List nodes')
    parser.add_argument('--list-tasks', action='store_true', help='List tasks')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    args = parser.parse_args()
    
    manager = ClusterManager()
    
    if args.register:
        parts = args.register.split('@')
        if len(parts) != 2:
            print("❌ Invalid format. Use: node_id@host:port")
            sys.exit(1)
        
        node_id = parts[0]
        host_port = parts[1].split(':')
        if len(host_port) != 2:
            print("❌ Invalid host:port format")
            sys.exit(1)
        
        manager.register_node(node_id, host_port[0], int(host_port[1]))
    
    elif args.unregister:
        if not manager.unregister_node(args.unregister):
            print(f"❌ Node not found: {args.unregister}")
            sys.exit(1)
    
    elif args.heartbeat:
        parts = args.heartbeat.split('@')
        node_id = parts[0]
        load = float(parts[1]) if len(parts) > 1 else 0.0
        
        if manager.heartbeat(node_id, load):
            print(f"✅ Heartbeat received from {node_id}")
        else:
            print(f"❌ Node not found: {node_id}")
    
    elif args.submit:
        parts = args.submit.split('@')
        task_id = parts[0]
        priority = int(parts[1]) if len(parts) > 1 else 0
        
        manager.submit_task(task_id, {'demo': True}, priority)
        print(f"✅ Task submitted: {task_id}")
    
    elif args.assign:
        assignments = manager.assign_tasks()
        if assignments:
            print(f"✅ Assigned {len(assignments)} tasks:")
            for task_id, node_id in assignments:
                print(f"   {task_id} → {node_id}")
        else:
            print("ℹ️  No tasks to assign or no healthy nodes")
    
    elif args.stats:
        stats = manager.get_cluster_stats()
        print("\n📊 CLUSTER STATISTICS")
        print("=" * 60)
        print(f"Total nodes: {stats['total_nodes']}")
        print(f"Healthy nodes: {stats['healthy_nodes']}")
        print(f"Offline nodes: {stats['offline_nodes']}")
        print(f"Total tasks: {stats['total_tasks']}")
        print(f"Completed: {stats['completed_tasks']}")
        print(f"Pending: {stats['pending_tasks']}")
        print(f"Assigned: {stats['assigned_tasks']}")
        print(f"Average load: {stats['avg_load']:.2f}")
        print(f"Total tasks completed: {stats['total_tasks_completed']}")
        print("=" * 60)
    
    elif args.health:
        health = manager.health_check()
        print(f"\n🏥 CLUSTER HEALTH: {health['overall_health'].upper()}")
        print("=" * 60)
        for node in health['nodes']:
            status_icon = '🟢' if node['status'] == 'online' else '🔴'
            print(f"{status_icon} {node['node_id']}: {node['status']} (load: {node['load']:.2f})")
        print("=" * 60)
    
    elif args.list_nodes:
        nodes = manager.list_nodes()
        if nodes:
            print("\n📋 CLUSTER NODES")
            print("=" * 60)
            for node in nodes:
                print(f"ID: {node['node_id']}")
                print(f"  Host: {node['host']}:{node['port']}")
                print(f"  Status: {node['status']}")
                print(f"  Load: {node['load']:.2f}")
                print(f"  Tasks completed: {node['tasks_completed']}")
                print()
        else:
            print("ℹ️  No nodes registered")
    
    elif args.list_tasks:
        tasks = manager.list_tasks()
        if tasks:
            print("\n📋 TASKS")
            print("=" * 60)
            for task in tasks:
                print(f"ID: {task['task_id']}")
                print(f"  Status: {task['status']}")
                print(f"  Priority: {task['priority']}")
                print(f"  Assigned to: {task.get('assigned_to', 'N/A')}")
                print()
        else:
            print("ℹ️  No tasks")
    
    elif args.demo:
        print("\n🔗 CLUSTER MANAGER DEMO")
        print("=" * 60)
        
        # Register nodes
        print("\n📝 Registering nodes...")
        manager.register_node('worker-1', '192.168.1.10', 8001, {'cpu': 4, 'memory': 8})
        manager.register_node('worker-2', '192.168.1.11', 8002, {'cpu': 8, 'memory': 16})
        manager.register_node('worker-3', '192.168.1.12', 8003, {'cpu': 4, 'memory': 8})
        
        # Send heartbeats
        print("\n💓 Sending heartbeats...")
        manager.heartbeat('worker-1', 0.3)
        manager.heartbeat('worker-2', 0.5)
        manager.heartbeat('worker-3', 0.2)
        
        # Submit tasks
        print("\n📤 Submitting tasks...")
        for i in range(5):
            manager.submit_task(f'task-{i}', {'data': f'task_data_{i}'}, priority=i)
        
        # Assign tasks
        print("\n📋 Assigning tasks...")
        assignments = manager.assign_tasks()
        for task_id, node_id in assignments:
            print(f"   {task_id} → {node_id}")
        
        # Health check
        print("\n🏥 Health check...")
        health = manager.health_check()
        print(f"   Overall: {health['overall_health']}")
        
        # Stats
        stats = manager.get_cluster_stats()
        print(f"\n📊 Stats: {stats['healthy_nodes']}/{stats['total_nodes']} nodes healthy")
        
        print("\n" + "=" * 60)
        print("✅ Demo complete!")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
