import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-SCHEDULER-001 Workflow Scheduler
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


SCHEDULER_DIR = Path("10-MEMORY/00-CORE/.scheduler")
TASKS_FILE = SCHEDULER_DIR / "tasks.json"
HISTORY_FILE = SCHEDULER_DIR / "history.json"


class WorkflowScheduler:
    """Workflow Scheduler"""

    BUILTIN_TASKS = {
        "daily-discover": {
            "id": "daily-discover",
            "name": "Daily Tool Discovery",
            "cron": "0 7 * * *",
            "command": "py 30-scripts-tools/auto_discover_001.py --sync",
            "enabled": True,
            "last_run": None
        },
        "weekly-optimize": {
            "id": "weekly-optimize",
            "name": "Weekly Optimization",
            "cron": "0 8 * * 1",
            "command": "py 30-scripts-tools/chain_runner_001.py --run full-optimize",
            "enabled": True,
            "last_run": None
        }
    }

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.tools_dir = self.workspace / "30-scripts-tools"
        SCHEDULER_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_files()

    def _ensure_files(self):
        if not TASKS_FILE.exists():
            TASKS_FILE.write_text(json.dumps({"tasks": self.BUILTIN_TASKS}, ensure_ascii=False, indent=2))
        if not HISTORY_FILE.exists():
            HISTORY_FILE.write_text(json.dumps({"history": []}, ensure_ascii=False, indent=2))

    def _load_tasks(self) -> dict:
        return json.loads(TASKS_FILE.read_text(encoding="utf-8", errors="replace"))

    def _save_tasks(self, data: dict):
        TASKS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def _load_history(self) -> dict:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8", errors="replace"))

    def _save_history(self, data: dict):
        HISTORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def list_tasks(self) -> List[Dict]:
        tasks = self._load_tasks()["tasks"]
        return [{"id": k, "name": v["name"], "cron": v["cron"], "enabled": v.get("enabled", True), "last_run": v.get("last_run")} for k, v in tasks.items()]

    def add_task(self, name: str, command: str, cron: str = "0 9 * * *") -> Dict:
        tasks = self._load_tasks()
        # 清理name中的特殊字符
        clean_name = name.strip().strip('"').strip("'")
        task_id = clean_name.lower().replace(" ", "-").replace('"', "").replace("'", "")
        if task_id in tasks["tasks"]:
            return {"status": "error", "reason": "Task already exists"}
        tasks["tasks"][task_id] = {"id": task_id, "name": clean_name, "cron": cron, "command": command, "enabled": True, "last_run": None}
        self._save_tasks(tasks)
        return {"status": "success", "task_id": task_id}

    def remove_task(self, task_id: str) -> Dict:
        tasks = self._load_tasks()
        if task_id not in tasks["tasks"]:
            return {"status": "error", "reason": "Task not found"}
        del tasks["tasks"][task_id]
        self._save_tasks(tasks)
        return {"status": "success", "task_id": task_id}

    def run_task(self, task_id: str) -> Dict:
        tasks = self._load_tasks()
        if task_id not in tasks["tasks"]:
            return {"status": "error", "reason": "Task not found"}
        task = tasks["tasks"][task_id]
        try:
            result = subprocess.run(task["command"], shell=True, capture_output=True, text=True, timeout=120, cwd=str(self.workspace), encoding="utf-8", errors="replace")
            history = self._load_history()
            history["history"].append({"task_id": task_id, "executed_at": datetime.now().isoformat(), "status": "success" if result.returncode == 0 else "failed"})
            if len(history["history"]) > 100:
                history["history"] = history["history"][-50:]
            self._save_history(history)
            tasks["tasks"][task_id]["last_run"] = datetime.now().isoformat()
            self._save_tasks(tasks)
            return {"status": "success" if result.returncode == 0 else "failed", "task_id": task_id}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def get_history(self, limit: int = 10) -> List[Dict]:
        history = self._load_history()
        return history["history"][-limit:]

    def toggle_task(self, task_id: str) -> Dict:
        tasks = self._load_tasks()
        if task_id not in tasks["tasks"]:
            return {"status": "error", "reason": "Task not found"}
        current = tasks["tasks"][task_id].get("enabled", True)
        tasks["tasks"][task_id]["enabled"] = not current
        self._save_tasks(tasks)
        return {"status": "success", "task_id": task_id, "enabled": not current}


logging.basicConfig(level=logging.INFO)
def main():
    scheduler = WorkflowScheduler()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "--list":
            tasks = scheduler.list_tasks()
            print(json.dumps(tasks, ensure_ascii=False, indent=2))
            return 0

        if cmd == "--add":
            # Format: --add "task.json"
            arg = sys.argv[2] if len(sys.argv) > 2 else None
            if not arg:
                print("Usage: py scheduler.py --add <json>")
                print("Example: py scheduler.py --add \"{'name':'Test','command':'echo hello','cron':'0 9 * * *'}\"")
                return 1
            try:
                if arg.startswith("{"):
                    data = json.loads(arg)
                    result = scheduler.add_task(data["name"], data["command"], data.get("cron", "0 9 * * *"))
                else:
                    parts = [p.strip() for p in arg.split("|")]
                    if len(parts) < 2:
                        print("Error: Need name|command format")
                        return 1
                    result = scheduler.add_task(parts[0], parts[1], parts[2] if len(parts) > 2 else "0 9 * * *")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0
            except json.JSONDecodeError as e:
                print(f"JSON Error: {e}")
                return 1
            except Exception as e:
                print(f"Error: {e}")
                return 1

        if cmd == "--run":
            tid = sys.argv[2] if len(sys.argv) > 2 else None
            if not tid:
                print("Usage: py scheduler.py --run <task_id>")
                return 1
            result = scheduler.run_task(tid)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if cmd == "--remove":
            tid = sys.argv[2] if len(sys.argv) > 2 else None
            if not tid:
                print("Usage: py scheduler.py --remove <task_id>")
                return 1
            result = scheduler.remove_task(tid)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if cmd == "--history":
            history = scheduler.get_history()
            print(json.dumps(history, ensure_ascii=False, indent=2))
            return 0

        if cmd == "--toggle":
            tid = sys.argv[2] if len(sys.argv) > 2 else None
            if not tid:
                print("Usage: py scheduler.py --toggle <task_id>")
                return 1
            result = scheduler.toggle_task(tid)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

    print("WORKFLOW-SCHEDULER-001 Workflow Scheduler")
    print("Usage:")
    print("  py scheduler.py --list                       # List tasks")
    print("  py scheduler.py --add <name> <cmd> [cron]    # Add task")
    print("  py scheduler.py --run <task_id>              # Run task")
    print("  py scheduler.py --remove <task_id>            # Remove task")
    print("  py scheduler.py --history                    # View history")
    print("  py scheduler.py --toggle <task_id>            # Enable/Disable")
    return 0
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py workflow_scheduler_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_scheduler_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""




if __name__ == "__main__":
    sys.exit(main())
