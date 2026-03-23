#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Framework Core v1
多智能体协作框架核心
"""

import uuid
import json
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from collections import deque
import threading
import queue

# ==================== 消息类型 ====================

class MessageType(Enum):
    TASK_ASSIGN = "task_assign"
    TASK_COMPLETE = "task_complete"
    REVIEW_REQUEST = "review_request"
    REVIEW_RESULT = "review_result"
    ERROR_REPORT = "error_report"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEWING = "reviewing"

# ==================== 数据结构 ====================

@dataclass
class Message:
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: str

    def to_dict(self):
        return {
            'message_id': self.message_id,
            'from_agent': self.from_agent,
            'to_agent': self.to_agent,
            'message_type': self.message_type.value,
            'payload': self.payload,
            'timestamp': self.timestamp
        }

    @classmethod
    def create(cls, from_agent: str, to_agent: str, msg_type: MessageType, payload: dict):
        return cls(
            message_id=str(uuid.uuid4()),
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=msg_type,
            payload=payload,
            timestamp=datetime.now().isoformat()
        )

@dataclass
class Task:
    task_id: str
    description: str
    priority: int  # 1-5, 1=highest
    status: TaskStatus
    assigned_to: Optional[str]
    result: Optional[Any]
    created_at: str
    deadline: Optional[str]

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'description': self.description,
            'priority': self.priority,
            'status': self.status.value,
            'assigned_to': self.assigned_to,
            'result': self.result,
            'created_at': self.created_at,
            'deadline': self.deadline
        }

# ==================== 任务队列 ====================

class TaskQueue:
    """任务队列 - 优先级调度"""

    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.high_priority = deque()  # 1-2
        self.normal_priority = deque()  # 3-4
        self.low_priority = deque()  # 5
        self.running = {}  # task_id -> Task
        self.lock = threading.Lock()

    def add_task(self, task: Task):
        """添加任务到队列"""
        with self.lock:
            if task.priority <= 2:
                self.high_priority.append(task)
            elif task.priority <= 4:
                self.normal_priority.append(task)
            else:
                self.low_priority.append(task)
            print(f"  [QUEUE] Added task {task.task_id} (priority {task.priority})")

    def get_next_task(self) -> Optional[Task]:
        """获取下一个任务 (优先级顺序)"""
        with self.lock:
            if len(self.running) >= self.max_concurrent:
                return None

            # 按优先级获取
            for q in [self.high_priority, self.normal_priority, self.low_priority]:
                if q:
                    task = q.popleft()
                    task.status = TaskStatus.RUNNING
                    self.running[task.task_id] = task
                    return task
            return None

    def complete_task(self, task_id: str, result: Any):
        """完成任务"""
        with self.lock:
            if task_id in self.running:
                task = self.running.pop(task_id)
                task.status = TaskStatus.COMPLETED
                task.result = result
                print(f"  [QUEUE] Completed task {task_id}")
                return task
        return None

    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        with self.lock:
            if task_id in self.running:
                task = self.running.pop(task_id)
                task.status = TaskStatus.FAILED
                task.result = {'error': error}
                print(f"  [QUEUE] Failed task {task_id}: {error}")
                return task
        return None

    def get_status(self) -> dict:
        """获取队列状态"""
        return {
            'high_priority': len(self.high_priority),
            'normal_priority': len(self.normal_priority),
            'low_priority': len(self.low_priority),
            'running': len(self.running),
            'total_queued': len(self.high_priority) + len(self.normal_priority) + len(self.low_priority)
        }

# ==================== 消息总线 ====================

class MessageBus:
    """消息总线 - Agent 间通信"""

    def __init__(self):
        self.queues = {}  # agent_id -> queue.Queue
        self.lock = threading.Lock()

    def register_agent(self, agent_id: str):
        """注册 Agent"""
        with self.lock:
            if agent_id not in self.queues:
                self.queues[agent_id] = queue.Queue()
                print(f"  [BUS] Registered agent: {agent_id}")

    def send_message(self, message: Message):
        """发送消息"""
        with self.lock:
            if message.to_agent in self.queues:
                self.queues[message.to_agent].put(message)
                print(f"  [BUS] Sent {message.message_type.value} from {message.from_agent} to {message.to_agent}")
            else:
                print(f"  [BUS] Agent not found: {message.to_agent}")

    def receive_message(self, agent_id: str, timeout=1.0) -> Optional[Message]:
        """接收消息"""
        with self.lock:
            if agent_id in self.queues:
                try:
                    return self.queues[agent_id].get(timeout=timeout)
                except queue.Empty:
                    return None
        return None

# ==================== Agent 基类 ====================

class AgentBase:
    """Agent 基类"""

    def __init__(self, agent_id: str, agent_type: str, message_bus: MessageBus):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.message_bus = message_bus
        self.running = False

        # 注册到消息总线
        self.message_bus.register_agent(agent_id)
        print(f"[AGENT] {agent_id} ({agent_type}) initialized")

    def start(self):
        """启动 Agent"""
        self.running = True
        print(f"[AGENT] {self.agent_id} started")

    def stop(self):
        """停止 Agent"""
        self.running = False
        print(f"[AGENT] {self.agent_id} stopped")

    def send_message(self, to_agent: str, msg_type: MessageType, payload: dict):
        """发送消息"""
        message = Message.create(self.agent_id, to_agent, msg_type, payload)
        self.message_bus.send_message(message)

    def receive_message(self, timeout=1.0) -> Optional[Message]:
        """接收消息"""
        return self.message_bus.receive_message(self.agent_id, timeout)

    def process_message(self, message: Message):
        """处理消息 (子类实现)"""
        raise NotImplementedError

    def run(self):
        """运行循环"""
        self.start()
        while self.running:
            message = self.receive_message(timeout=1.0)
            if message:
                try:
                    self.process_message(message)
                except Exception as e:
                    print(f"[AGENT] Error processing message: {e}")
                    self.send_message(
                        message.from_agent,
                        MessageType.ERROR_REPORT,
                        {'error': str(e), 'original_message': message.to_dict()}
                    )
        self.stop()

# ==================== 调度器 ====================

class Scheduler:
    """任务调度器"""

    def __init__(self, task_queue: TaskQueue, message_bus: MessageBus):
        self.task_queue = task_queue
        self.message_bus = message_bus
        self.running = False

    def submit_task(self, task: Task):
        """提交任务"""
        self.task_queue.add_task(task)

    def run(self):
        """运行调度循环"""
        self.running = True
        print("[SCHEDULER] Started")

        while self.running:
            # 获取下一个任务
            task = self.task_queue.get_next_task()
            if task:
                # 分配给 Executor
                executor_id = f"executor_{hash(task.task_id) % 5}"  # 简单轮询
                self.message_bus.send_message(
                    Message.create(
                        "scheduler",
                        executor_id,
                        MessageType.TASK_ASSIGN,
                        {'task': task.to_dict()}
                    )
                )
            else:
                import time
                time.sleep(0.5)

        print("[SCHEDULER] Stopped")

    def stop(self):
        """停止调度器"""
        self.running = False

# ==================== 测试 ====================

def test_framework():
    """测试框架"""
    print("=" * 60)
    print("Multi-Agent Framework Test")
    print("=" * 60)

    # 初始化
    message_bus = MessageBus()
    task_queue = TaskQueue(max_concurrent=3)
    scheduler = Scheduler(task_queue, message_bus)

    # 创建测试任务
    tasks = [
        Task(str(uuid.uuid4()), "PDF 解析任务 1", 1, TaskStatus.PENDING, None, None, datetime.now().isoformat(), None),
        Task(str(uuid.uuid4()), "元数据提取任务", 2, TaskStatus.PENDING, None, None, datetime.now().isoformat(), None),
        Task(str(uuid.uuid4()), "贡献总结任务", 3, TaskStatus.PENDING, None, None, datetime.now().isoformat(), None),
    ]

    # 提交任务
    print("\n[TEST] Submitting tasks...")
    for task in tasks:
        scheduler.submit_task(task)

    # 查看队列状态
    print("\n[TEST] Queue status:")
    status = task_queue.get_status()
    print(f"  {status}")

    # 模拟任务执行
    print("\n[TEST] Executing tasks...")
    for _ in range(3):
        task = task_queue.get_next_task()
        if task:
            print(f"  Executing: {task.description}")
            task_queue.complete_task(task.task_id, {'result': 'success'})

    # 最终状态
    print("\n[TEST] Final queue status:")
    status = task_queue.get_status()
    print(f"  {status}")

    print("\n" + "=" * 60)
    print("[TEST] Framework test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_framework()
