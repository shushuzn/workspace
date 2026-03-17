#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard API v4.0 - 7-Persona Enhanced Version
多人格增强版 - 异步 API + 多人格协作引擎

Features:
- 异步非阻塞 I/O
- Redis 任务队列
- WebSocket 实时推送
- 7-Persona 多人格协作
- 人格任务分发
- 人格状态追踪

Author: Claw 🐾
Version: 4.1-Persona
"""

import os
import sys
import json
import time
import asyncio
import datetime
import socket
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, asdict
from enum import Enum

# FastAPI & Async
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Redis
import redis.asyncio as redis

# System monitoring
import psutil

# UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Configuration
PORT = 8448  # Changed to 8448 to avoid conflict
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

WORKSPACE_DIR = Path(__file__).parent.parent
DATA_DIR = WORKSPACE_DIR / 'dashboard-data'
PERSONA_DIR = DATA_DIR / 'personas'
TASKS_DIR = DATA_DIR / 'tasks'

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PERSONA_DIR.mkdir(parents=True, exist_ok=True)
TASKS_DIR.mkdir(parents=True, exist_ok=True)


# ============== 7-Persona System ==============

PERSONA_LIST = [
    'planner',      # 规划者 - 任务分解与规划
    'executor',     # 执行者 - 任务执行
    'critic',       # 批判者 - 质量审查
    'learner',      # 学习者 - 知识吸收
    'coordinator',  # 协调者 - 资源协调
    'innovator',    # 创新者 - 创意生成
    'metacognition' # 元认知 - 全局监控
]

PERSONA_ROLES = {
    'planner': {
        'name': '规划者',
        'color': '🔵',
        'priority': 'high',
        'description': '任务分解与规划'
    },
    'executor': {
        'name': '执行者',
        'color': '🟢',
        'priority': 'high',
        'description': '任务执行'
    },
    'critic': {
        'name': '批判者',
        'color': '🔴',
        'priority': 'critical',
        'description': '质量审查'
    },
    'learner': {
        'name': '学习者',
        'color': '🟡',
        'priority': 'medium',
        'description': '知识吸收'
    },
    'coordinator': {
        'name': '协调者',
        'color': '🟣',
        'priority': 'high',
        'description': '资源协调'
    },
    'innovator': {
        'name': '创新者',
        'color': '🟠',
        'priority': 'medium',
        'description': '创意生成'
    },
    'metacognition': {
        'name': '元认知',
        'color': '⚫',
        'priority': 'critical',
        'description': '全局监控'
    }
}


@dataclass
class PersonaTask:
    """人格任务"""
    task_id: str
    persona: str
    action: str
    payload: Dict
    priority: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class PersonaState:
    """人格状态"""
    persona: str
    status: str  # idle, busy, waiting
    current_task: Optional[str]
    tasks_completed: int
    tasks_failed: int
    avg_response_time: float
    last_active: str
    
    def to_dict(self):
        return asdict(self)


class PersonaManager:
    """
    多人格管理器
    支持：任务分发、状态追踪、消息队列
    """
    
    def __init__(self):
        self.persona_states: Dict[str, PersonaState] = {}
        self.task_queues: Dict[str, List[PersonaTask]] = {p: [] for p in PERSONA_LIST}
        self.completed_tasks: List[PersonaTask] = []
        self.message_log: List[Dict] = []
        
        # Initialize states
        for persona in PERSONA_LIST:
            self.persona_states[persona] = PersonaState(
                persona=persona,
                status='idle',
                current_task=None,
                tasks_completed=0,
                tasks_failed=0,
                avg_response_time=0.0,
                last_active=datetime.datetime.now().isoformat()
            )
    
    def assign_task(self, persona: str, action: str, payload: Dict, 
                   priority: str = 'normal') -> str:
        """分配任务给人格"""
        if persona not in PERSONA_LIST:
            raise ValueError(f"Unknown persona: {persona}")
        
        task_id = str(uuid.uuid4())
        task = PersonaTask(
            task_id=task_id,
            persona=persona,
            action=action,
            payload=payload,
            priority=priority,
            status='pending',
            created_at=datetime.datetime.now().isoformat()
        )
        
        # Add to persona's queue
        self.task_queues[persona].append(task)
        
        # Update state
        state = self.persona_states[persona]
        if state.status == 'idle':
            state.status = 'waiting'
        
        print(f"[PERSONA] {PERSONA_ROLES[persona]['color']} {persona} assigned: {action}")
        return task_id
    
    async def process_task(self, persona: str, task_id: str):
        """处理任务 (模拟)"""
        task = None
        for t in self.task_queues[persona]:
            if t.task_id == task_id:
                task = t
                break
        
        if not task:
            return
        
        # Update status
        task.status = 'running'
        task.started_at = datetime.datetime.now().isoformat()
        
        state = self.persona_states[persona]
        state.status = 'busy'
        state.current_task = task_id
        
        # Simulate task execution
        start_time = time.time()
        await asyncio.sleep(0.5)  # Simulate work
        duration = time.time() - start_time
        
        # Complete task
        task.status = 'completed'
        task.completed_at = datetime.datetime.now().isoformat()
        task.result = {
            'message': f'Task completed by {persona}',
            'duration_ms': duration * 1000
        }
        
        # Update state
        state.status = 'idle'
        state.current_task = None
        state.tasks_completed += 1
        state.avg_response_time = (state.avg_response_time * (state.tasks_completed - 1) + duration * 1000) / state.tasks_completed
        state.last_active = datetime.datetime.now().isoformat()
        
        # Move to completed
        self.task_queues[persona].remove(task)
        self.completed_tasks.append(task)
        
        print(f"[PERSONA] {PERSONA_ROLES[persona]['color']} {persona} completed: {task.action}")
    
    def get_persona_status(self, persona: str) -> Optional[Dict]:
        """获取人格状态"""
        if persona not in self.persona_states:
            return None
        
        state = self.persona_states[persona]
        queue_len = len(self.task_queues[persona])
        
        return {
            **state.to_dict(),
            'pending_tasks': queue_len,
            'role': PERSONA_ROLES[persona]['name'],
            'color': PERSONA_ROLES[persona]['color'],
            'description': PERSONA_ROLES[persona]['description']
        }
    
    def get_all_personas_status(self) -> Dict:
        """获取所有人格状态"""
        return {
            persona: self.get_persona_status(persona)
            for persona in PERSONA_LIST
        }
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_completed = sum(s.tasks_completed for s in self.persona_states.values())
        total_failed = sum(s.tasks_failed for s in self.persona_states.values())
        
        return {
            'total_personas': len(PERSONA_LIST),
            'total_tasks_completed': total_completed,
            'total_tasks_failed': total_failed,
            'success_rate': total_completed / (total_completed + total_failed) if (total_completed + total_failed) > 0 else 0,
            'active_personas': sum(1 for s in self.persona_states.values() if s.status == 'busy'),
            'pending_tasks': sum(len(q) for q in self.task_queues.values())
        }


# ============== Dashboard API with Persona Support ==============

class DashboardAPIWithPersona:
    """Dashboard API Server with 7-Persona Support"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Innovator Dashboard v4.1 - 7-Persona Enhanced",
            description="High Performance Async API with Redis Queue, WebSocket & 7-Persona System",
            version="4.1.0-Persona"
        )
        self.persona_manager = PersonaManager()
        self.setup_middleware()
        self.setup_routes()
    
    def setup_middleware(self):
        """配置中间件"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """配置路由"""
        
        # Health check
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.datetime.now().isoformat(),
                "version": "4.1.0-Persona"
            }
        
        # ============== Persona Endpoints ==============
        
        @self.app.get("/api/personas")
        async def get_all_personas():
            """获取所有人格状态"""
            return self.persona_manager.get_all_personas_status()
        
        @self.app.get("/api/personas/{persona}")
        async def get_persona_status(persona: str):
            """获取特定人格状态"""
            status = self.persona_manager.get_persona_status(persona)
            if not status:
                raise HTTPException(status_code=404, detail=f"Persona {persona} not found")
            return status
        
        @self.app.post("/api/personas/{persona}/task")
        async def assign_persona_task(persona: str, task_data: Dict[str, Any], 
                                     background_tasks: BackgroundTasks):
            """分配任务给人格"""
            if persona not in PERSONA_LIST:
                raise HTTPException(status_code=400, detail=f"Unknown persona: {persona}")
            
            task_id = self.persona_manager.assign_task(
                persona=persona,
                action=task_data.get("action", "generic"),
                payload=task_data.get("payload", {}),
                priority=task_data.get("priority", "normal")
            )
            
            # Background processing
            background_tasks.add_task(
                self.persona_manager.process_task,
                persona,
                task_id
            )
            
            return {
                "task_id": task_id,
                "persona": persona,
                "status": "assigned",
                "message": f"Task assigned to {PERSONA_ROLES[persona]['name']}"
            }
        
        @self.app.get("/api/personas/statistics")
        async def get_persona_statistics():
            """获取人格统计信息"""
            return self.persona_manager.get_statistics()
        
        @self.app.get("/api/personas/queue/{persona}")
        async def get_persona_queue(persona: str):
            """获取人格任务队列"""
            if persona not in PERSONA_LIST:
                raise HTTPException(status_code=400, detail=f"Unknown persona: {persona}")
            
            tasks = [
                {
                    'task_id': t.task_id,
                    'action': t.action,
                    'priority': t.priority,
                    'status': t.status,
                    'created_at': t.created_at
                }
                for t in self.persona_manager.task_queues[persona]
            ]
            
            return {
                'persona': persona,
                'queue_length': len(tasks),
                'tasks': tasks
            }
        
        # ============== System Endpoints ==============
        
        @self.app.get("/api/health/system")
        async def get_system_health():
            """获取系统健康指标"""
            return {
                "local": {
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('C:\\').percent,
                    "status": "healthy"
                },
                "personas": self.persona_manager.get_statistics(),
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @self.app.get("/api/dashboard")
        async def get_dashboard_summary():
            """获取仪表板汇总"""
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "personas": self.persona_manager.get_all_personas_status(),
                "statistics": self.persona_manager.get_statistics(),
                "system": {
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent
                }
            }
    
    def run(self, host: str = "0.0.0.0", port: int = PORT, workers: int = 4):
        """启动服务器"""
        print("\n" + "="*80)
        print("[INNOVATOR] Dashboard API v4.1 - 7-Persona Enhanced")
        print("="*80)
        print(f"[SERVER] Running on http://{host}:{port}")
        print(f"[WORKERS] {workers} worker processes")
        print(f"[PERSONAS] 7-Persona System Enabled")
        print(f"[DATA] Directory: {DATA_DIR}")
        print(f"[WORKSPACE] {WORKSPACE_DIR}")
        print("\n[PERSONAS]")
        for p in PERSONA_LIST:
            role = PERSONA_ROLES[p]
            print(f"   {role['color']} {p:15} - {role['name']:8} ({role['description']})")
        print("\n[API] Endpoints:")
        print("  GET  /api/personas              - All personas status")
        print("  GET  /api/personas/{persona}    - Specific persona status")
        print("  POST /api/personas/{persona}/task - Assign task to persona")
        print("  GET  /api/personas/statistics   - Persona statistics")
        print("  GET  /api/health/system         - System health")
        print("  GET  /api/dashboard             - Dashboard summary")
        print("\n[INFO] Press Ctrl+C to stop\n")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            workers=workers,
            log_level="info"
        )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Dashboard API v4.1 - 7-Persona Enhanced")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=PORT, help='Port to bind')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    parser.add_argument('--demo', action='store_true', help='Run demo with sample tasks')
    args = parser.parse_args()
    
    if args.demo:
        # Demo mode
        print("\n[DEMO] Running 7-Persona Demo...\n")
        
        api = DashboardAPIWithPersona()
        
        # Show initial status
        print("Initial Persona Status:")
        status = api.persona_manager.get_all_personas_status()
        for persona, data in status.items():
            print(f"  {data['color']} {persona}: {data['status']}")
        
        # Assign sample tasks
        print("\n[DEMO] Assigning sample tasks...")
        
        tasks = [
            ('planner', 'analyze_requirements', {'project': 'test'}),
            ('executor', 'execute_task', {'action': 'run_test'}),
            ('critic', 'review_code', {'file': 'test.py'}),
            ('learner', 'learn_pattern', {'topic': 'async'}),
            ('coordinator', 'allocate_resources', {'cpu': 4}),
            ('innovator', 'generate_idea', {'domain': 'AI'}),
            ('metacognition', 'monitor_system', {'metrics': ['cpu', 'memory']})
        ]
        
        for persona, action, payload in tasks:
            task_id = api.persona_manager.assign_task(persona, action, payload)
            print(f"  Assigned {action} to {persona}: {task_id}")
        
        # Process tasks
        print("\n[DEMO] Processing tasks...")
        
        async def process_all():
            for persona, _, _ in tasks:
                task = api.persona_manager.task_queues[persona][0]
                await api.persona_manager.process_task(persona, task.task_id)
        
        asyncio.run(process_all())
        
        # Show final statistics
        print("\n[DEMO] Final Statistics:")
        stats = api.persona_manager.get_statistics()
        print(f"  Tasks Completed: {stats['total_tasks_completed']}")
        print(f"  Success Rate: {stats['success_rate']*100:.1f}%")
        print(f"  Active Personas: {stats['active_personas']}")
        
        print("\n✅ Demo complete!")
    
    else:
        api = DashboardAPIWithPersona()
        api.run(host=args.host, port=args.port, workers=args.workers)


if __name__ == '__main__':
    main()
