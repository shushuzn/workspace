#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenClaw + Cursor 协作模式
OpenClaw 分析 → Cursor 编辑
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(r"D:\OpenClaw\workspace")
TASKS_FILE = WORKSPACE / ".openclaw" / "cursor-tasks.json"

def create_task(description, files=None, instructions=None):
    """创建 Cursor 编辑任务"""
    tasks = load_tasks()

    task = {
        "id": len(tasks) + 1,
        "description": description,
        "files": files or [],
        "instructions": instructions or "",
        "status": "pending",
        "created": datetime.now().isoformat(),
        "completed": None
    }

    tasks.append(task)
    save_tasks(tasks)

    return task

def load_tasks():
    """加载任务列表"""
    if TASKS_FILE.exists():
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """保存任务列表"""
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def complete_task(task_id):
    """标记任务完成"""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completed"
            task["completed"] = datetime.now().isoformat()
    save_tasks(tasks)

def show_pending_tasks():
    """显示待办任务"""
    tasks = load_tasks()
    pending = [t for t in tasks if t["status"] == "pending"]

    if not pending:
        print("\n[OK] No pending tasks")
        return []

    print("\n" + "=" * 60)
    print("Cursor Editing Tasks (OpenClaw Analysis)")
    print("=" * 60)

    for i, task in enumerate(pending, 1):
        print(f"\n[{i}] Task #{task['id']}")
        print(f"    {task['description']}")
        if task['files']:
            print(f"    Files: {', '.join(task['files'])}")
        if task['instructions']:
            print(f"    Instructions:")
            for line in task['instructions'].split('\n'):
                print(f"      {line}")

    print("\n" + "=" * 60)
    return pending

def main():
    if len(sys.argv) < 2:
        # 显示帮助
        print("\nOpenClaw + Cursor Collaboration")
        print("=" * 40)
        print("\nUsage:")
        print("  py cursor_collab.py new <description> [files...]")
        print("  py cursor_collab.py list")
        print("  py cursor_collab.py done <task_id>")
        print("\nExample:")
        print('  py cursor_collab.py new "Add login function" auth.py login.html')
        return

    cmd = sys.argv[1]

    if cmd == "new":
        if len(sys.argv) < 3:
            print("Usage: py cursor_collab.py new <description> [files...]")
            return

        description = sys.argv[2]
        files = sys.argv[3:] if len(sys.argv) > 3 else []

        task = create_task(description, files)
        print(f"\n[OK] Created task #{task['id']}")
        print(f"     {task['description']}")
        if files:
            print(f"     Files: {', '.join(files)}")

    elif cmd == "list":
        show_pending_tasks()

    elif cmd == "done":
        if len(sys.argv) < 3:
            print("Usage: py cursor_collab.py done <task_id>")
            return

        task_id = int(sys.argv[2])
        complete_task(task_id)
        print(f"\n[OK] Task #{task_id} marked as completed")

    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
