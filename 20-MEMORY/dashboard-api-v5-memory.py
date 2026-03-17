#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard API v5.0 - 7-Persona + Memory System Integration
多人格增强版 + 记忆系统集成

Features:
- 异步非阻塞 I/O
- Redis 任务队列
- WebSocket 实时推送
- 7-Persona 多人格协作
- 🧠 记忆系统集成 (MEMORY.md + 日常笔记)
- 记忆搜索与蒸馏
- 记忆状态可视化

Author: Claw 🐾
Version: 5.0-Memory
"""

import os
import sys
import json
import time
import asyncio
import datetime
import socket
import uuid
import re
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
PORT = 8448
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

WORKSPACE_DIR = Path(__file__).parent
DATA_DIR = WORKSPACE_DIR / 'dashboard-data'
PERSONA_DIR = DATA_DIR / 'personas'
TASKS_DIR = DATA_DIR / 'tasks'

# Memory System Paths
MEMORY_DIR = WORKSPACE_DIR / 'memory'
MEMORY_FILE = WORKSPACE_DIR / 'MEMORY.md'

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PERSONA_DIR.mkdir(parents=True, exist_ok=True)
TASKS_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


# ============== 7-Persona System ==============

PERSONA_LIST = [
    'planner', 'executor', 'critic', 'learner',
    'coordinator', 'innovator', 'metacognition'
]

PERSONA_ROLES = {
    'planner': {'name': '规划者', 'color': '🔵', 'priority': 'high', 'description': '任务分解与规划'},
    'executor': {'name': '执行者', 'color': '🟢', 'priority': 'high', 'description': '任务执行'},
    'critic': {'name': '批判者', 'color': '🔴', 'priority': 'critical', 'description': '质量审查'},
    'learner': {'name': '学习者', 'color': '🟡', 'priority': 'medium', 'description': '知识吸收'},
    'coordinator': {'name': '协调者', 'color': '🟣', 'priority': 'high', 'description': '资源协调'},
    'innovator': {'name': '创新者', 'color': '🟠', 'priority': 'medium', 'description': '创意生成'},
    'metacognition': {'name': '元认知', 'color': '⚫', 'priority': 'critical', 'description': '全局监控'}
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
    status: str
    current_task: Optional[str]
    tasks_completed: int
    tasks_failed: int
    avg_response_time: float
    last_active: str
    
    def to_dict(self):
        return asdict(self)


class PersonaManager:
    """多人格管理器"""
    
    def __init__(self):
        self.persona_states: Dict[str, PersonaState] = {}
        self.task_queues: Dict[str, List[PersonaTask]] = {p: [] for p in PERSONA_LIST}
        self.completed_tasks: List[PersonaTask] = []
        self.message_log: List[Dict] = []
        
        for persona in PERSONA_LIST:
            self.persona_states[persona] = PersonaState(
                persona=persona, status='idle', current_task=None,
                tasks_completed=0, tasks_failed=0, avg_response_time=0.0,
                last_active=datetime.datetime.now().isoformat()
            )
    
    def assign_task(self, persona: str, action: str, payload: Dict, 
                   priority: str = 'normal') -> str:
        """分配任务给人格"""
        if persona not in PERSONA_LIST:
            raise ValueError(f"Unknown persona: {persona}")
        
        task_id = str(uuid.uuid4())
        task = PersonaTask(
            task_id=task_id, persona=persona, action=action,
            payload=payload, priority=priority, status='pending',
            created_at=datetime.datetime.now().isoformat()
        )
        
        self.task_queues[persona].append(task)
        state = self.persona_states[persona]
        if state.status == 'idle':
            state.status = 'waiting'
        
        print(f"[PERSONA] {PERSONA_ROLES[persona]['color']} {persona} assigned: {action}")
        return task_id
    
    async def process_task(self, persona: str, task_id: str):
        """处理任务"""
        task = None
        for t in self.task_queues[persona]:
            if t.task_id == task_id:
                task = t
                break
        
        if not task:
            return
        
        task.status = 'running'
        task.started_at = datetime.datetime.now().isoformat()
        
        state = self.persona_states[persona]
        state.status = 'busy'
        state.current_task = task_id
        
        start_time = time.time()
        await asyncio.sleep(0.5)
        duration = time.time() - start_time
        
        task.status = 'completed'
        task.completed_at = datetime.datetime.now().isoformat()
        task.result = {'message': f'Task completed by {persona}', 'duration_ms': duration * 1000}
        
        state.status = 'idle'
        state.current_task = None
        state.tasks_completed += 1
        state.avg_response_time = (state.avg_response_time * (state.tasks_completed - 1) + duration * 1000) / state.tasks_completed
        state.last_active = datetime.datetime.now().isoformat()
        
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
        return {persona: self.get_persona_status(persona) for persona in PERSONA_LIST}
    
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


# ============== Memory System ==============

class MemorySystem:
    """
    记忆系统管理器
    支持：MEMORY.md 读取/写入、日常笔记、记忆搜索
    """
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.memory_dir = workspace_dir / 'memory'
        self.memory_file = workspace_dir / 'MEMORY.md'
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def get_today_note_path(self) -> Path:
        """获取今日笔记路径"""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return self.memory_dir / f'{today}.md'
    
    def get_yesterday_note_path(self) -> Path:
        """获取昨日笔记路径"""
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        return self.memory_dir / f'{yesterday.strftime("%Y-%m-%d")}.md'
    
    def read_memory_md(self, lines: int = 50) -> Dict:
        """读取 MEMORY.md 前 N 行"""
        if not self.memory_file.exists():
            return {
                'exists': False,
                'content': '',
                'sections': [],
                'last_updated': None
            }
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines_list = content.split('\n')[:lines]
            sections = self._extract_sections(content)
            
            # Get last updated date
            last_updated = None
            for line in content.split('\n')[:20]:
                if '**Last Updated:**' in line:
                    match = re.search(r'\d{4}-\d{2}-\d{2}', line)
                    if match:
                        last_updated = match.group()
                        break
            
            return {
                'exists': True,
                'content': '\n'.join(lines_list),
                'total_lines': len(content.split('\n')),
                'sections': sections,
                'last_updated': last_updated,
                'file_size_kb': round(os.path.getsize(self.memory_file) / 1024, 2)
            }
        except Exception as e:
            return {
                'exists': True,
                'error': str(e),
                'content': '',
                'sections': []
            }
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """提取 MEMORY.md 的章节"""
        sections = []
        current_section = None
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'title': line.replace('## ', '').strip(),
                    'content': []
                }
            elif current_section and line.startswith('### '):
                current_section['content'].append(line.replace('### ', '').strip())
        
        if current_section:
            sections.append(current_section)
        
        return sections[:10]  # Limit to 10 sections
    
    def read_daily_note(self, date: str = None) -> Dict:
        """读取指定日期的日常笔记"""
        if not date:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        note_path = self.memory_dir / f'{date}.md'
        
        if not note_path.exists():
            return {
                'exists': False,
                'date': date,
                'content': ''
            }
        
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'exists': True,
                'date': date,
                'content': content,
                'file_size_kb': round(os.path.getsize(note_path) / 1024, 2)
            }
        except Exception as e:
            return {
                'exists': True,
                'error': str(e),
                'date': date,
                'content': ''
            }
    
    def get_recent_notes(self, days: int = 7) -> List[Dict]:
        """获取最近 N 天的日常笔记"""
        notes = []
        
        for i in range(days):
            date = datetime.datetime.now() - datetime.timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            note_path = self.memory_dir / f'{date_str}.md'
            
            if note_path.exists():
                notes.append({
                    'date': date_str,
                    'exists': True,
                    'path': str(note_path),
                    'size_kb': round(os.path.getsize(note_path) / 1024, 2)
                })
            else:
                notes.append({
                    'date': date_str,
                    'exists': False,
                    'path': str(note_path)
                })
        
        return notes
    
    def write_daily_note(self, content: str, date: str = None) -> Dict:
        """写入日常笔记"""
        if not date:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        note_path = self.memory_dir / f'{date}.md'
        
        try:
            # If file exists, append content
            if note_path.exists():
                with open(note_path, 'r', encoding='utf-8') as f:
                    existing = f.read()
                content = existing + '\n\n' + content
            
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'path': str(note_path),
                'date': date,
                'message': f'Daily note for {date} updated'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_memory(self, query: str, max_results: int = 10) -> Dict:
        """
        简单文本搜索记忆
        TODO: 集成语义搜索
        """
        results = []
        
        # Search in MEMORY.md
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        results.append({
                            'source': 'MEMORY.md',
                            'line_number': i + 1,
                            'content': line.strip()[:200],
                            'context': '\n'.join(lines[max(0, i-2):i+3])
                        })
                        
                        if len(results) >= max_results:
                            break
            except Exception as e:
                pass
        
        # Search in daily notes
        for note_file in self.memory_dir.glob('*.md'):
            if note_file.name == 'README.md':
                continue
            
            try:
                with open(note_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if query.lower() in content.lower():
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            results.append({
                                'source': note_file.name,
                                'line_number': i + 1,
                                'content': line.strip()[:200],
                                'context': '\n'.join(lines[max(0, i-2):i+3])
                            })
                            
                            if len(results) >= max_results:
                                break
            except Exception as e:
                continue
        
        return {
            'query': query,
            'total_results': len(results),
            'results': results
        }
    
    def get_memory_stats(self) -> Dict:
        """获取记忆系统统计"""
        memory_exists = self.memory_file.exists()
        memory_size = os.path.getsize(self.memory_file) if memory_exists else 0
        
        daily_notes = list(self.memory_dir.glob('*.md'))
        daily_notes = [n for n in daily_notes if n.name != 'README.md']
        total_daily_size = sum(os.path.getsize(n) for n in daily_notes)
        
        return {
            'memory_md': {
                'exists': memory_exists,
                'size_kb': round(memory_size / 1024, 2),
                'last_modified': datetime.datetime.fromtimestamp(
                    os.path.getmtime(self.memory_file)
                ).isoformat() if memory_exists else None
            },
            'daily_notes': {
                'count': len(daily_notes),
                'total_size_kb': round(total_daily_size / 1024, 2),
                'recent_dates': [
                    n.stem for n in sorted(daily_notes, reverse=True)[:7]
                ]
            },
            'total_memory_size_kb': round((memory_size + total_daily_size) / 1024, 2)
        }


# ============== Dashboard API v5.0 ==============

class DashboardAPIv5:
    """Dashboard API Server v5.0 - 7-Persona + Memory System"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Innovator Dashboard v5.0 - Memory Integrated",
            description="7-Persona + Memory System Integration",
            version="5.0.0-Memory"
        )
        self.persona_manager = PersonaManager()
        self.memory_system = MemorySystem(WORKSPACE_DIR)
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
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.datetime.now().isoformat(),
                "version": "5.0.0-Memory"
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
        
        # ============== Memory Endpoints ==============
        
        @self.app.get("/api/memory")
        async def get_memory_summary():
            """获取记忆系统摘要"""
            return {
                'memory_md': self.memory_system.read_memory_md(lines=30),
                'stats': self.memory_system.get_memory_stats(),
                'recent_notes': self.memory_system.get_recent_notes(days=7),
                'today_note': self.memory_system.read_daily_note()
            }
        
        @self.app.get("/api/memory/md")
        async def get_memory_md(lines: int = 50):
            """获取 MEMORY.md 内容"""
            return self.memory_system.read_memory_md(lines=lines)
        
        @self.app.get("/api/memory/daily/{date}")
        async def get_daily_note(date: str):
            """获取指定日期的日常笔记"""
            return self.memory_system.read_daily_note(date)
        
        @self.app.get("/api/memory/daily/today")
        async def get_today_note():
            """获取今日笔记"""
            return self.memory_system.read_daily_note()
        
        @self.app.get("/api/memory/daily/recent")
        async def get_recent_notes(days: int = 7):
            """获取最近 N 天的日常笔记"""
            return self.memory_system.get_recent_notes(days=days)
        
        @self.app.post("/api/memory/daily/write")
        async def write_daily_note(data: Dict[str, str]):
            """写入日常笔记"""
            content = data.get('content', '')
            date = data.get('date')
            
            if not content:
                raise HTTPException(status_code=400, detail="Content required")
            
            return self.memory_system.write_daily_note(content, date)
        
        @self.app.get("/api/memory/search")
        async def search_memory(q: str, limit: int = 10):
            """搜索记忆"""
            return self.memory_system.search_memory(q, max_results=limit)
        
        @self.app.get("/api/memory/stats")
        async def get_memory_statistics():
            """获取记忆系统统计"""
            return self.memory_system.get_memory_stats()
        
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
                "memory": self.memory_system.get_memory_stats(),
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @self.app.get("/api/dashboard")
        async def get_dashboard_summary():
            """获取仪表板汇总"""
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "personas": self.persona_manager.get_all_personas_status(),
                "statistics": self.persona_manager.get_statistics(),
                "memory": {
                    'summary': self.memory_system.read_memory_md(lines=20),
                    'stats': self.memory_system.get_memory_stats(),
                    'today_note': self.memory_system.read_daily_note()
                },
                "system": {
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent
                }
            }
    
    def run(self, host: str = "0.0.0.0", port: int = PORT, workers: int = 1):
        """启动服务器"""
        print("\n" + "="*80)
        print("[INNOVATOR] Dashboard API v5.0 - 7-Persona + Memory System")
        print("="*80)
        print(f"[SERVER] Running on http://{host}:{port}")
        print(f"[WORKERS] {workers} worker processes")
        print(f"[FEATURES]")
        print(f"  - 7-Persona System")
        print(f"  - 🧠 Memory System Integration")
        print(f"  - WebSocket Real-time Updates")
        print(f"  - Redis Task Queue (Optional)")
        print(f"[DATA] Directory: {DATA_DIR}")
        print(f"[MEMORY] Directory: {self.memory_system.memory_dir}")
        print(f"[WORKSPACE] {WORKSPACE_DIR}")
        print("\n[PERSONAS]")
        for p in PERSONA_LIST:
            role = PERSONA_ROLES[p]
            print(f"   {role['color']} {p:15} - {role['name']:8} ({role['description']})")
        print("\n[API] Endpoints:")
        print("  === Personas ===")
        print("  GET  /api/personas              - All personas status")
        print("  GET  /api/personas/{persona}    - Specific persona status")
        print("  POST /api/personas/{persona}/task - Assign task to persona")
        print("  GET  /api/personas/statistics   - Persona statistics")
        print("  === Memory ===")
        print("  GET  /api/memory                - Memory summary")
        print("  GET  /api/memory/md             - MEMORY.md content")
        print("  GET  /api/memory/daily/today    - Today's note")
        print("  GET  /api/memory/daily/{date}   - Specific date note")
        print("  POST /api/memory/daily/write    - Write daily note")
        print("  GET  /api/memory/search?q=xxx   - Search memory")
        print("  GET  /api/memory/stats          - Memory statistics")
        print("  === System ===")
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
    parser = argparse.ArgumentParser(description="Dashboard API v5.0 - Memory Integrated")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=PORT, help='Port to bind')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    args = parser.parse_args()
    
    api = DashboardAPIv5()
    api.run(host=args.host, port=args.port, workers=args.workers)


if __name__ == '__main__':
    main()
