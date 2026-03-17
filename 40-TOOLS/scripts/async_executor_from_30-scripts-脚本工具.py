#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务执行器 - 基于 OpenClaw-RL 异步架构启发

功能:
- 异步执行耗时任务
- 不阻塞主对话
- 支持任务状态查询
- 支持任务取消
"""

import asyncio
import threading
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import json
from workflow_prm import WorkflowPRM


class AsyncTask:
    """异步任务类"""
    
    def __init__(self, task_id: str, func: Callable, *args, **kwargs):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = 'pending'  # pending, running, completed, failed, cancelled
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.progress = 0  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'status': self.status,
            'result': self.result,
            'error': str(self.error) if self.error else None,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress': self.progress,
            'prm_score': self.prm_score
        }


class AsyncExecutor:
    """异步执行器"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks: Dict[str, AsyncTask] = {}
        self._lock = threading.Lock()
        self._worker_count = 0
        self._worker_semaphore = threading.Semaphore(max_workers)
        self.prm = WorkflowPRM()  # PRM 评估器
    
    def submit(self, task_id: str, func: Callable, *args, **kwargs) -> str:
        """提交异步任务"""
        with self._lock:
            task = AsyncTask(task_id, func, *args, **kwargs)
            self.tasks[task_id] = task
        
        # 启动工作线程
        thread = threading.Thread(target=self._run_task, args=(task,), daemon=True)
        thread.start()
        
        return task_id
    
    def _run_task(self, task: AsyncTask) -> None:
        """运行任务"""
        with self._worker_semaphore:
            try:
                task.status = 'running'
                task.started_at = datetime.now()
                
                # 执行任务
                result = task.func(*task.args, **task.kwargs, task=task)
                
                task.result = result
                task.status = 'completed'
                task.progress = 100
                
                # PRM 评估
                task.prm_score = self.prm.evaluate(result, getattr(task, 'user_feedback', None))
                
            except Exception as e:
                task.error = e
                task.status = 'failed'
                # 失败任务 PRM 评分
                task.prm_score = {'total': 0.0, 'level': 'bad'}
            
            finally:
                task.completed_at = datetime.now()
    
    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        with self._lock:
            task = self.tasks.get(task_id)
            return task.to_dict() if task else None
    
    def cancel(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            task = self.tasks.get(task_id)
            if task and task.status in ('pending', 'running'):
                task.status = 'cancelled'
                return True
            return False
    
    def list_tasks(self, status: Optional[str] = None) -> list:
        """列出任务"""
        with self._lock:
            tasks = list(self.tasks.values())
            if status:
                tasks = [t for t in tasks if t.status == status]
            return [t.to_dict() for t in tasks]
    
    def cleanup_completed(self, max_age_hours: int = 24) -> int:
        """清理完成的任务"""
        with self._lock:
            now = datetime.now()
            to_remove = []
            
            for task_id, task in self.tasks.items():
                if task.status in ('completed', 'failed', 'cancelled'):
                    if task.completed_at:
                        age = (now - task.completed_at).total_seconds() / 3600
                        if age > max_age_hours:
                            to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]
            
            return len(to_remove)


# ==================== 示例任务 ====================

def example_long_task(duration: int = 10, task: AsyncTask = None) -> Dict[str, Any]:
    """示例：长时间运行任务"""
    for i in range(duration):
        if task:
            task.progress = int((i + 1) / duration * 100)
        
        if task and task.status == 'cancelled':
            return {'cancelled': True}
        
        time.sleep(1)
    
    return {
        'duration': duration,
        'message': f'任务完成，耗时{duration}秒'
    }


def example_knowledge_graph_task(pdf_paths: list, task: AsyncTask = None) -> Dict[str, Any]:
    """示例：知识图谱生成任务"""
    total = len(pdf_paths)
    
    for i, pdf_path in enumerate(pdf_paths):
        if task:
            task.progress = int((i + 1) / total * 100)
        
        if task and task.status == 'cancelled':
            return {'cancelled': True}
        
        # 模拟 PDF 处理
        print(f'处理 {i+1}/{total}: {pdf_path}')
        time.sleep(0.5)
    
    return {
        'processed': total,
        'message': f'已处理 {total} 篇 PDF'
    }


# ==================== Web 集成 ====================

def create_async_routes(app):
    """创建异步任务 API 路由 (Flask)"""
    
    @app.route('/api/task/submit', methods=['POST'])
    def submit_task():
        from flask import request, jsonify
        data = request.json
        task_id = data.get('task_id')
        task_type = data.get('type')
        
        if task_type == 'knowledge_graph':
            pdf_paths = data.get('pdf_paths', [])
            executor.submit(task_id, example_knowledge_graph_task, pdf_paths)
            return jsonify({'success': True, 'task_id': task_id})
        
        return jsonify({'error': 'Unknown task type'}), 400
    
    @app.route('/api/task/status/<task_id>', methods=['GET'])
    def task_status(task_id):
        from flask import jsonify
        status = executor.get_status(task_id)
        if status:
            return jsonify({'success': True, 'status': status})
        return jsonify({'error': 'Task not found'}), 404
    
    @app.route('/api/task/cancel/<task_id>', methods=['POST'])
    def cancel_task(task_id):
        from flask import jsonify
        success = executor.cancel(task_id)
        return jsonify({'success': success})
    
    @app.route('/api/task/list', methods=['GET'])
    def list_tasks():
        from flask import request, jsonify
        status = request.args.get('status')
        tasks = executor.list_tasks(status)
        return jsonify({'success': True, 'tasks': tasks})


# ==================== 全局执行器 ====================

executor = AsyncExecutor(max_workers=3)


# ==================== 测试 ====================

if __name__ == '__main__':
    print('测试异步执行器...')
    
    # 提交任务
    task_id = executor.submit('test-1', example_long_task, duration=5)
    print(f'提交任务：{task_id}')
    
    # 查询状态
    time.sleep(2)
    status = executor.get_status(task_id)
    print(f'任务状态：{status}')
    
    # 等待完成
    time.sleep(5)
    status = executor.get_status(task_id)
    print(f'最终状态：{status}')
    
    # 列出任务
    tasks = executor.list_tasks()
    print(f'任务列表：{tasks}')
    
    # 清理
    cleaned = executor.cleanup_completed(max_age_hours=0)
    print(f'清理了 {cleaned} 个任务')
