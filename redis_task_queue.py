#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis-backed Task Queue for Dashboard API v4
提供持久化任务队列和分布式支持

Author: Claw 🐾
"""

import asyncio
import json
import time
import redis.asyncio as redis
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import sys

# UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    task_id: str
    task_type: str
    payload: Dict
    priority: int = 5
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""
    updated_at: str = ""
    progress: int = 0
    result: Optional[Dict] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

class RedisTaskQueue:
    """
    Redis 支持的任务队列
    
    Features:
    - 持久化存储
    - 优先级队列
    - 分布式支持
    - 任务超时检测
    - 失败重试
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0",
                 queue_name: str = "dashboard:tasks",
                 max_retries: int = 3,
                 timeout_seconds: int = 300):
        self.redis_url = redis_url
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
    
    async def connect(self):
        """连接到 Redis"""
        self.redis = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        await self.redis.ping()
        print(f"✅ Redis 连接成功：{self.redis_url}")
    
    async def close(self):
        """关闭连接"""
        if self.redis:
            await self.redis.close()
            print("👋 Redis 连接已关闭")
    
    async def enqueue(self, task: Task) -> str:
        """将任务加入队列"""
        task_data = asdict(task)
        task_json = json.dumps(task_data, ensure_ascii=False)
        
        # 存储任务详情
        await self.redis.hset(
            f"{self.queue_name}:task:{task.task_id}",
            mapping=task_data
        )
        
        # 加入优先级队列 (ZSET, score=priority, member=task_id)
        # priority 越高，score 越小，越先执行
        score = 10 - task.priority  # 反转优先级
        await self.redis.zadd(
            f"{self.queue_name}:queue",
            {task.task_id: score}
        )
        
        # 发布事件
        await self.redis.publish(
            f"{self.queue_name}:events",
            json.dumps({
                'event': 'task_created',
                'task_id': task.task_id,
                'timestamp': datetime.now().isoformat()
            })
        )
        
        print(f"📥 任务已入队：{task.task_id} (优先级：{task.priority})")
        return task.task_id
    
    async def dequeue(self, timeout: float = 1.0) -> Optional[Task]:
        """从队列取出任务 (优先级最高)"""
        # 从 ZSET 中取出优先级最高的任务
        result = await self.redis.zpopmin(f"{self.queue_name}:queue", count=1)
        
        if not result:
            return None
        
        task_id = result[0][0]
        
        # 获取任务详情
        task_data = await self.redis.hgetall(
            f"{self.queue_name}:task:{task_id}"
        )
        
        if not task_data:
            return None
        
        # 转换为 Task 对象
        task = Task(
            task_id=task_data['task_id'],
            task_type=task_data['task_type'],
            payload=json.loads(task_data['payload']),
            priority=int(task_data['priority']),
            status=TaskStatus(task_data['status']),
            created_at=task_data['created_at'],
            updated_at=task_data['updated_at'],
            progress=int(task_data.get('progress', 0)),
            result=json.loads(task_data['result']) if task_data.get('result') else None,
            error=task_data.get('error')
        )
        
        # 更新状态为运行中
        await self.update_task(task_id, {'status': TaskStatus.RUNNING.value})
        
        print(f"📤 任务已出队：{task.task_id}")
        return task
    
    async def update_task(self, task_id: str, updates: Dict) -> bool:
        """更新任务状态"""
        key = f"{self.queue_name}:task:{task_id}"
        
        # 检查任务是否存在
        exists = await self.redis.exists(key)
        if not exists:
            return False
        
        # 更新字段
        updates['updated_at'] = datetime.now().isoformat()
        await self.redis.hset(key, mapping=updates)
        
        # 发布更新事件
        await self.redis.publish(
            f"{self.queue_name}:events",
            json.dumps({
                'event': 'task_updated',
                'task_id': task_id,
                'updates': updates,
                'timestamp': datetime.now().isoformat()
            })
        )
        
        return True
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务详情"""
        task_data = await self.redis.hgetall(
            f"{self.queue_name}:task:{task_id}"
        )
        
        if not task_data:
            return None
        
        return Task(
            task_id=task_data['task_id'],
            task_type=task_data['task_type'],
            payload=json.loads(task_data['payload']),
            priority=int(task_data['priority']),
            status=TaskStatus(task_data['status']),
            created_at=task_data['created_at'],
            updated_at=task_data['updated_at'],
            progress=int(task_data.get('progress', 0)),
            result=json.loads(task_data['result']) if task_data.get('result') else None,
            error=task_data.get('error')
        )
    
    async def list_tasks(self, status: Optional[str] = None, 
                        limit: int = 100) -> List[Task]:
        """列出任务"""
        # 获取所有任务 ID
        if status:
            # 按状态过滤 (需要额外索引)
            task_ids = await self.redis.smembers(
                f"{self.queue_name}:status:{status}"
            )
        else:
            # 获取最近的任务 (从 ZSET)
            task_ids = await self.redis.zrange(
                f"{self.queue_name}:queue",
                0, limit - 1
            )
        
        tasks = []
        for task_id in list(task_ids)[:limit]:
            task = await self.get_task(task_id)
            if task:
                tasks.append(task)
        
        return tasks
    
    async def get_queue_stats(self) -> Dict:
        """获取队列统计"""
        queue_size = await self.redis.zcard(f"{self.queue_name}:queue")
        
        # 统计各状态任务数
        status_counts = {}
        for status in TaskStatus:
            count = await self.redis.scard(f"{self.queue_name}:status:{status.value}")
            status_counts[status.value] = count
        
        return {
            'queue_size': queue_size,
            'by_status': status_counts,
            'timestamp': datetime.now().isoformat()
        }
    
    async def cleanup_timeout_tasks(self) -> int:
        """清理超时任务"""
        cutoff_time = time.time() - self.timeout_seconds
        cleaned = 0
        
        # 查找运行中超时的任务
        async for key in self.redis.scan_iter(f"{self.queue_name}:task:*"):
            task_data = await self.redis.hgetall(key)
            if not task_data:
                continue
            
            if task_data.get('status') != TaskStatus.RUNNING.value:
                continue
            
            updated_at = task_data.get('updated_at', '')
            if not updated_at:
                continue
            
            try:
                update_time = datetime.fromisoformat(updated_at).timestamp()
                if update_time < cutoff_time:
                    task_id = task_data['task_id']
                    await self.update_task(task_id, {
                        'status': TaskStatus.FAILED.value,
                        'error': 'Task timeout'
                    })
                    cleaned += 1
            except:
                pass
        
        if cleaned > 0:
            print(f"🧹 清理了 {cleaned} 个超时任务")
        
        return cleaned
    
    async def subscribe_events(self):
        """订阅任务事件"""
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(f"{self.queue_name}:events")
        return self.pubsub


async def demo():
    """演示 Redis 任务队列"""
    print("\n🚀 Redis Task Queue Demo")
    print("=" * 60)
    
    queue = RedisTaskQueue()
    
    try:
        # 连接 Redis
        await queue.connect()
        
        # 创建任务
        task1 = Task(
            task_id="task-001",
            task_type="workflow",
            payload={"steps": 10},
            priority=8
        )
        
        task2 = Task(
            task_id="task-002",
            task_type="analysis",
            payload={"data": "sample"},
            priority=5
        )
        
        task3 = Task(
            task_id="task-003",
            task_type="memory",
            payload={"action": "distill"},
            priority=3
        )
        
        # 入队
        await queue.enqueue(task1)
        await queue.enqueue(task2)
        await queue.enqueue(task3)
        
        # 查看队列统计
        stats = await queue.get_queue_stats()
        print(f"\n📊 队列统计：{json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        # 出队 (应该按优先级)
        print("\n📤 按优先级出队:")
        for i in range(3):
            task = await queue.dequeue()
            if task:
                print(f"   {i+1}. {task.task_id} (优先级：{task.priority})")
                
                # 模拟任务完成
                await queue.update_task(task.task_id, {
                    'status': TaskStatus.COMPLETED.value,
                    'progress': 100,
                    'result': {'success': True}
                })
        
        # 最终统计
        stats = await queue.get_queue_stats()
        print(f"\n✅ 最终统计：{json.dumps(stats, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        print("💡 提示：确保 Redis 正在运行 (redis-server)")
    
    finally:
        await queue.close()


if __name__ == "__main__":
    # 检查 Redis
    try:
        import redis.asyncio
    except ImportError:
        print("❌ 缺少依赖：redis")
        print("请运行：pip install redis")
        sys.exit(1)
    
    asyncio.run(demo())
