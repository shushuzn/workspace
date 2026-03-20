#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定时任务调度增强 - 基于 cron 技能的增强集成
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class CronEnhanced:
    """定时任务调度增强"""
    
    def __init__(self):
        self.config_file = Path("flow-archive/20260318-universal-workflow-001/cron-tasks.json")
        self.log_file = Path("flow-archive/20260318-universal-workflow-001/cron-execution-log.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "tasks": {},
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0
        }
    
    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def register_task(self, task_id: str, task_config: Dict) -> bool:
        """注册定时任务"""
        
        self.config['tasks'][task_id] = {
            "id": task_id,
            "name": task_config.get('name', task_id),
            "schedule": task_config.get('schedule'),  # cron 表达式
            "command": task_config.get('command'),
            "description": task_config.get('description', ''),
            "enabled": task_config.get('enabled', True),
            "last_run": None,
            "next_run": None,
            "execution_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_config()
        return True
    
    def create_default_tasks(self):
        """创建默认任务"""
        
        default_tasks = {
            "daily-arxiv-scan": {
                "name": "Daily arXiv Scan",
                "schedule": "0 7 * * *",  # 每天 7:00
                "command": "py 40-arxiv/arxiv_scan.py",
                "description": "每日 arXiv 论文扫描"
            },
            "daily-memory-distill": {
                "name": "Daily Memory Distillation",
                "schedule": "0 6 * * *",  # 每天 6:00
                "command": "py 30-scripts-tools/auto_memory_distiller.py",
                "description": "每日记忆蒸馏"
            },
            "hourly-heartbeat": {
                "name": "Hourly Heartbeat Check",
                "schedule": "0 * * * *",  # 每小时
                "command": "py 30-scripts-tools/heartbeat_check.py",
                "description": "每小时心跳检查"
            },
            "weekly-performance-report": {
                "name": "Weekly Performance Report",
                "schedule": "0 5 * * 0",  # 每周日 5:00
                "command": "py 30-scripts-tools/performance_analyzer.py --weekly",
                "description": "每周性能报告"
            }
        }
        
        for task_id, task_config in default_tasks.items():
            self.register_task(task_id, task_config)
        
        print(f"[OK] Created {len(default_tasks)} default cron tasks")
    
    def list_tasks(self) -> List[Dict]:
        """列出所有任务"""
        return list(self.config['tasks'].values())
    
    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        if task_id in self.config['tasks']:
            self.config['tasks'][task_id]['enabled'] = True
            self._save_config()
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        if task_id in self.config['tasks']:
            self.config['tasks'][task_id]['enabled'] = False
            self._save_config()
            return True
        return False
    
    def execute_task(self, task_id: str) -> Dict:
        """执行任务"""
        if task_id not in self.config['tasks']:
            return {"success": False, "error": f"Task '{task_id}' not found"}
        
        task = self.config['tasks'][task_id]
        
        if not task['enabled']:
            return {"success": False, "error": "Task is disabled"}
        
        # 记录执行
        self.config['total_executions'] += 1
        task['execution_count'] += 1
        task['last_run'] = datetime.now().isoformat()
        
        # 模拟执行成功（实际应调用 subprocess 运行命令）
        self.config['successful_executions'] += 1
        self._save_config()
        
        return {
            "success": True,
            "task_id": task_id,
            "executed_at": task['last_run']
        }
    
    def get_stats(self) -> Dict:
        """获取统计"""
        total = len(self.config['tasks'])
        enabled = sum(1 for t in self.config['tasks'].values() if t['enabled'])
        
        return {
            "total_tasks": total,
            "enabled_tasks": enabled,
            "disabled_tasks": total - enabled,
            "total_executions": self.config['total_executions'],
            "successful_executions": self.config['successful_executions'],
            "failed_executions": self.config['failed_executions'],
            "success_rate": (
                self.config['successful_executions'] / self.config['total_executions'] * 100
            ) if self.config['total_executions'] > 0 else 0
        }
    
    def display_status(self) -> str:
        """显示状态"""
        stats = self.get_stats()
        tasks = self.list_tasks()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 22 + "Cron Task Scheduler")
        output.append("=" * 70)
        
        output.append(f"\n[Stats]")
        output.append(f"  Total Tasks:      {stats['total_tasks']}")
        output.append(f"  Enabled:          {stats['enabled_tasks']}")
        output.append(f"  Disabled:         {stats['disabled_tasks']}")
        output.append(f"  Total Executions: {stats['total_executions']}")
        output.append(f"  Success Rate:     {stats['success_rate']:.1f}%")
        
        output.append(f"\n[Tasks]")
        for task in tasks:
            status = "ON" if task['enabled'] else "OFF"
            output.append(f"\n  [{status}] {task['id']}: {task['name']}")
            output.append(f"    Schedule: {task['schedule']}")
            output.append(f"    Command:  {task['command']}")
            output.append(f"    Last Run: {task['last_run'] or 'Never'}")
            output.append(f"    Executions: {task['execution_count']}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)
    
    def run(self) -> Dict:
        """运行"""
        return {
            "stats": self.get_stats(),
            "tasks": self.list_tasks(),
            "success": True
        }

def main():
    """测试入口"""
    cron = CronEnhanced()
    
    print("Cron Enhanced Test")
    print("=" * 70)
    
    # 创建默认任务
    cron.create_default_tasks()
    
    # 列出任务
    tasks = cron.list_tasks()
    print(f"\n[OK] Total tasks: {len(tasks)}")
    
    # 显示状态
    print(cron.display_status())
    
    print(f"\n[OK] Cron test completed")

if __name__ == "__main__":
    main()
