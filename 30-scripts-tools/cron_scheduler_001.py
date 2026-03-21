import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CRON-001 Cron 定时任务配置
功能:
  - 自动执行每日任务
  - 每周批处理
  - 定时扫描
  
使用方法:
  py cron_001_scheduler.py --list      列出任务
  py cron_001_scheduler.py --add "task" "schedule"  添加任务
  py cron_001_scheduler.py --remove "task"  删除任务
  py cron_001_scheduler.py --run "task"    立即运行任务
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 配置目录
CRON_DIR = Path("60-DATA/cron_001")
CONFIG_FILE = CRON_DIR / "tasks.json"
LOG_FILE = CRON_DIR / "execution_log.json"


class CronScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.cron_dir = CRON_DIR
        self.config_file = CONFIG_FILE
        self.log_file = LOG_FILE
        
        self.cron_dir.mkdir(parents=True, exist_ok=True)
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> dict:
        default = {
            "tasks": {
                "memory-distill": {
                    "name": "Memory Auto-Distillation",
                    "description": "每日内存自动蒸馏",
                    "schedule": "0 6 * * *",  # 每天 06:00
                    "enabled": True,
                    "last_run": None,
                    "next_run": None,
                    "command": "py 30-scripts-tools/memory_distiller.py"
                },
                "arxiv-scan": {
                    "name": "arXiv Daily Scan",
                    "description": "每日 arXiv 论文扫描",
                    "schedule": "0 7 * * *",  # 每天 07:00
                    "enabled": True,
                    "last_run": None,
                    "next_run": None,
                    "command": "py 30-scripts-tools/arxiv_scanner.py"
                },
                "domain-rank": {
                    "name": "Domain Ranking Update",
                    "description": "每周领域排名更新",
                    "schedule": "0 5 * * 0",  # 每周日 05:00
                    "enabled": True,
                    "last_run": None,
                    "next_run": None,
                    "command": "py domain_ranker_v2.py --compare"
                },
                "session-cleanup": {
                    "name": "Session Cleanup",
                    "description": "清理过期会话文件",
                    "schedule": "0 3 * * *",  # 每天 03:00
                    "enabled": True,
                    "last_run": None,
                    "next_run": None,
                    "command": "py 30-scripts-tools/session_cleanup.py"
                },
                "backup-daily": {
                    "name": "Daily Backup",
                    "description": "每日配置备份",
                    "schedule": "0 2 * * *",  # 每天 02:00
                    "enabled": True,
                    "last_run": None,
                    "next_run": None,
                    "command": "py 30-scripts-tools/auto_backup.py --daily"
                },
                "health-check": {
                    "name": "System Health Check",
                    "description": "系统健康检查",
                    "schedule": "0 */4 * * *",  # 每4小时
                    "enabled": True,
                    "last_run": None,
                    "next_run": None,
                    "command": "py 30-scripts-tools/health_check.py"
                }
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (Exception,):
                return default
        return default
    
    def _save_tasks(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def list_tasks(self) -> dict:
        """列出所有任务"""
        task_list = []
        
        for task_id, task in self.tasks["tasks"].items():
            task_list.append({
                "id": task_id,
                "name": task["name"],
                "schedule": task["schedule"],
                "enabled": task["enabled"],
                "last_run": task.get("last_run"),
                "next_run": task.get("next_run")
            })
        
        return {
            "status": "success",
            "total_tasks": len(task_list),
            "enabled_tasks": sum(1 for t in task_list if t["enabled"]),
            "tasks": task_list
        }
    
    def add_task(self, task_id: str, name: str, schedule: str, command: str) -> dict:
        """添加新任务"""
        if task_id in self.tasks["tasks"]:
            return {"status": "error", "message": f"Task {task_id} already exists"}
        
        self.tasks["tasks"][task_id] = {
            "name": name,
            "description": "",
            "schedule": schedule,
            "enabled": True,
            "last_run": None,
            "next_run": None,
            "command": command
        }
        
        self._save_tasks()
        
        return {
            "status": "success",
            "message": f"Task {task_id} added",
            "task": self.tasks["tasks"][task_id]
        }
    
    def remove_task(self, task_id: str) -> dict:
        """删除任务"""
        if task_id not in self.tasks["tasks"]:
            return {"status": "error", "message": f"Task {task_id} not found"}
        
        del self.tasks["tasks"][task_id]
        self._save_tasks()
        
        return {
            "status": "success",
            "message": f"Task {task_id} removed"
        }
    
    def enable_task(self, task_id: str) -> dict:
        """启用任务"""
        if task_id not in self.tasks["tasks"]:
            return {"status": "error", "message": f"Task {task_id} not found"}
        
        self.tasks["tasks"][task_id]["enabled"] = True
        self._save_tasks()
        
        return {"status": "success", "message": f"Task {task_id} enabled"}
    
    def disable_task(self, task_id: str) -> dict:
        """禁用任务"""
        if task_id not in self.tasks["tasks"]:
            return {"status": "error", "message": f"Task {task_id} not found"}
        
        self.tasks["tasks"][task_id]["enabled"] = False
        self._save_tasks()
        
        return {"status": "success", "message": f"Task {task_id} disabled"}
    
    def run_task(self, task_id: str) -> dict:
        """立即运行任务"""
        if task_id not in self.tasks["tasks"]:
            return {"status": "error", "message": f"Task {task_id} not found"}
        
        task = self.tasks["tasks"][task_id]
        
        # 记录执行日志
        log_entry = {
            "task_id": task_id,
            "task_name": task["name"],
            "command": task["command"],
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }
        
        # 更新最后运行时间
        task["last_run"] = datetime.now().isoformat()
        self._save_tasks()
        
        return {
            "status": "success",
            "message": f"Task {task_id} execution triggered",
            "command": task["command"],
            "last_run": task["last_run"]
        }
    
    def generate_cron_script(self) -> str:
        """生成 cron 脚本 (用于系统级调度)"""
        script = """#!/bin/bash
# OpenClaw Cron Jobs
# Install: crontab -e

# Memory Auto-Distillation - Daily at 06:00
0 6 * * * cd /path/to/workspace && py 30-scripts-tools/memory_distiller.py >> logs/cron.log 2>&1

# arXiv Scan - Daily at 07:00
0 7 * * * cd /path/to/workspace && py 30-scripts-tools/arxiv_scanner.py >> logs/cron.log 2>&1

# Domain Ranking - Weekly on Sunday at 05:00
0 5 * * 0 cd /path/to/workspace && py domain_ranker_v2.py --compare >> logs/cron.log 2>&1

# Session Cleanup - Daily at 03:00
0 3 * * * cd /path/to/workspace && py 30-scripts-tools/session_cleanup.py >> logs/cron.log 2>&1

# Daily Backup - Daily at 02:00
0 2 * * * cd /path/to/workspace && py 30-scripts-tools/auto_backup.py --daily >> logs/cron.log 2>&1

# Health Check - Every 4 hours
0 */4 * * * cd /path/to/workspace && py 30-scripts-tools/health_check.py >> logs/cron.log 2>&1
"""
        return script


logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) > 1:
        scheduler = CronScheduler()
        
        if sys.argv[1] == "--list":
            result = scheduler.list_tasks()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--add":
            if len(sys.argv) < 5:
                print("Usage: --add <task_id> <name> <schedule>")
                return 1
            task_id = sys.argv[2]
            name = sys.argv[3]
            schedule = sys.argv[4]
            command = sys.argv[5] if len(sys.argv) > 5 else f"py 30-scripts-tools/{task_id}.py"
            result = scheduler.add_task(task_id, name, schedule, command)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--remove":
            if len(sys.argv) < 3:
                print("Usage: --remove <task_id>")
                return 1
            result = scheduler.remove_task(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--run":
            if len(sys.argv) < 3:
                print("Usage: --run <task_id>")
                return 1
            result = scheduler.run_task(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--enable":
            if len(sys.argv) < 3:
                print("Usage: --enable <task_id>")
                return 1
            result = scheduler.enable_task(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--disable":
            if len(sys.argv) < 3:
                print("Usage: --disable <task_id>")
                return 1
            result = scheduler.disable_task(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--generate":
            print(scheduler.generate_cron_script())
            return 0
    
    print("CRON-001 Scheduler")
    print("Usage:")
    print("  py cron_001_scheduler.py --list              # List all tasks")
    print("  py cron_001_scheduler.py --add <id> <name> <schedule> <cmd>  # Add task")
    print("  py cron_001_scheduler.py --remove <id>       # Remove task")
    print("  py cron_001_scheduler.py --run <id>          # Run task now")
    print("  py cron_001_scheduler.py --enable <id>       # Enable task")
    print("  py cron_001_scheduler.py --disable <id>      # Disable task")
    print("  py cron_001_scheduler.py --generate          # Generate cron script")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())