#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Task Decomposition System - 任务分解自动化系统

功能:
1. 复杂任务自动分解为子任务
2. 子任务依赖关系图
3. 执行优先级排序 (紧急/重要矩阵)
4. 进度追踪和汇报
5. 任务模板库

Usage:
    py task_decomposer.py --decompose "复杂任务描述"
    py task_decomposer.py --list [--status 状态]
    py task_decomposer.py --progress
    py task_decomposer.py --execute-next
    py task_decomposer.py --stats
    py task_decomposer.py --template "模板名"
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
TASKS_DIR = WORKSPACE / "tasks"
TASKS_DB = TASKS_DIR / "tasks-db.json"
TASKS_CONFIG = TASKS_DIR / "tasks-config.json"
TEMPLATES_DIR = TASKS_DIR / "templates"

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

# 优先级矩阵
class Priority:
    URGENT_IMPORTANT = "🔴 紧急重要"      # 立即执行
    IMPORTANT_NOT_URGENT = "🟡 重要不紧急"  # 计划执行
    URGENT_NOT_IMPORTANT = "🟠 紧急不重要"  # 委托/简化
    NOT_URGENT_NOT_IMPORTANT = "🟢 不紧急不重要"  # 可选

# 任务状态
class TaskStatus:
    PENDING = "pending"       # 待执行
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"   # 已完成
    BLOCKED = "blocked"       # 已阻塞
    CANCELLED = "cancelled"   # 已取消

def init_tasks():
    """初始化任务系统"""
    TASKS_DIR.mkdir(exist_ok=True)
    TEMPLATES_DIR.mkdir(exist_ok=True)
    
    if not TASKS_DB.exists():
        save_tasks_db({
            "tasks": [],
            "next_id": 1
        })
    
    if not TASKS_CONFIG.exists():
        save_config({
            "auto_decompose": True,
            "decompose_threshold": 3,  # 超过 3 个子任务自动分解
            "default_priority": "important",
            "enable_dependencies": True,
            "auto_progress_report": True
        })
    
    # 创建默认模板
    create_default_templates()

def save_tasks_db(db):
    """保存任务数据库"""
    with open(TASKS_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def load_tasks_db():
    """加载任务数据库"""
    if not TASKS_DB.exists():
        return {"tasks": [], "next_id": 1}
    
    with open(TASKS_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置"""
    with open(TASKS_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_config():
    """加载配置"""
    if not TASKS_CONFIG.exists():
        return {
            "auto_decompose": True,
            "decompose_threshold": 3,
            "default_priority": "important",
            "enable_dependencies": True,
            "auto_progress_report": True
        }
    
    with open(TASKS_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_task_id():
    """生成任务 ID"""
    db = load_tasks_db()
    task_id = db["next_id"]
    db["next_id"] += 1
    save_tasks_db(db)
    return f"TASK-{task_id:04d}"

def create_default_templates():
    """创建默认任务模板"""
    templates = {
        "research": {
            "name": "研究任务模板",
            "subtasks": [
                {"name": "文献调研", "estimated_hours": 2, "dependencies": []},
                {"name": "数据收集", "estimated_hours": 3, "dependencies": [1]},
                {"name": "数据分析", "estimated_hours": 4, "dependencies": [2]},
                {"name": "结果总结", "estimated_hours": 1, "dependencies": [3]}
            ]
        },
        "development": {
            "name": "开发任务模板",
            "subtasks": [
                {"name": "需求分析", "estimated_hours": 2, "dependencies": []},
                {"name": "设计架构", "estimated_hours": 3, "dependencies": [1]},
                {"name": "编码实现", "estimated_hours": 8, "dependencies": [2]},
                {"name": "测试验证", "estimated_hours": 4, "dependencies": [3]},
                {"name": "文档编写", "estimated_hours": 2, "dependencies": [3]}
            ]
        },
        "writing": {
            "name": "写作任务模板",
            "subtasks": [
                {"name": "大纲设计", "estimated_hours": 1, "dependencies": []},
                {"name": "初稿撰写", "estimated_hours": 4, "dependencies": [1]},
                {"name": "修改润色", "estimated_hours": 2, "dependencies": [2]},
                {"name": "最终审核", "estimated_hours": 1, "dependencies": [3]}
            ]
        }
    }
    
    for name, template in templates.items():
        template_file = TEMPLATES_DIR / f"{name}.json"
        if not template_file.exists():
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

def decompose_task(description: str, template: str = None, priority: str = "important") -> str:
    """分解任务
    
    Args:
        description: 任务描述
        template: 模板名 (research/development/writing)
        priority: 优先级 (urgent/important/normal/low)
    
    Returns:
        任务 ID
    """
    init_tasks()
    
    task_id = generate_task_id()
    
    # 确定优先级矩阵
    if priority == "urgent":
        priority_label = Priority.URGENT_IMPORTANT
    elif priority == "important":
        priority_label = Priority.IMPORTANT_NOT_URGENT
    elif priority == "normal":
        priority_label = Priority.URGENT_NOT_IMPORTANT
    else:
        priority_label = Priority.NOT_URGENT_NOT_IMPORTANT
    
    # 创建主任务
    main_task = {
        "id": task_id,
        "description": description,
        "status": TaskStatus.PENDING,
        "priority": priority,
        "priority_label": priority_label,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "subtasks": [],
        "dependencies": [],
        "estimated_hours": 0,
        "actual_hours": 0,
        "progress": 0,
        "parent_task": None,
        "tags": [],
        "notes": ""
    }
    
    # 使用模板分解
    if template:
        template_file = TEMPLATES_DIR / f"{template}.json"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            for i, subtask_template in enumerate(template_data["subtasks"], 1):
                subtask = {
                    "id": f"{task_id}-{i}",
                    "name": subtask_template["name"],
                    "description": f"{description} - {subtask_template['name']}",
                    "status": TaskStatus.PENDING,
                    "estimated_hours": subtask_template.get("estimated_hours", 1),
                    "dependencies": [f"{task_id}-{d}" for d in subtask_template.get("dependencies", [])],
                    "progress": 0,
                    "created_at": datetime.now().isoformat()
                }
                main_task["subtasks"].append(subtask)
                main_task["estimated_hours"] += subtask["estimated_hours"]
    
    # 保存任务
    db = load_tasks_db()
    db["tasks"].append(main_task)
    save_tasks_db(db)
    
    print(f"{Colors.GREEN}✅ 任务已分解{Colors.RESET}")
    print(f"   任务 ID: {task_id}")
    print(f"   描述：{description}")
    print(f"   优先级：{priority_label}")
    print(f"   子任务数：{len(main_task['subtasks'])}")
    print(f"   预估时间：{main_task['estimated_hours']}小时")
    
    # 显示子任务
    if main_task["subtasks"]:
        print(f"\n{Colors.BOLD}子任务列表:{Colors.RESET}")
        for i, subtask in enumerate(main_task["subtasks"], 1):
            deps = f" (依赖：{', '.join(subtask['dependencies'])})" if subtask['dependencies'] else ""
            print(f"   {i}. {subtask['name']} - {subtask['estimated_hours']}小时{deps}")
    
    return task_id

def list_tasks(status: str = None, limit: int = 20) -> List[Dict]:
    """列出任务
    
    Args:
        status: 状态过滤
        limit: 返回数量限制
    
    Returns:
        任务列表
    """
    init_tasks()
    db = load_tasks_db()
    
    tasks = db["tasks"]
    
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    
    # 按创建时间倒序
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    return tasks[:limit]

def get_task(task_id: str) -> Optional[Dict]:
    """获取任务详情"""
    init_tasks()
    db = load_tasks_db()
    
    # 查找主任务或子任务
    for task in db["tasks"]:
        if task["id"] == task_id:
            return task
        
        # 查找子任务
        for subtask in task.get("subtasks", []):
            if subtask["id"] == task_id:
                return subtask
    
    return None

def update_task_status(task_id: str, status: str, progress: int = None) -> bool:
    """更新任务状态"""
    init_tasks()
    db = load_tasks_db()
    
    for task in db["tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            task["updated_at"] = datetime.now().isoformat()
            
            if progress is not None:
                task["progress"] = progress
            
            if status == TaskStatus.IN_PROGRESS and not task["started_at"]:
                task["started_at"] = datetime.now().isoformat()
            
            if status == TaskStatus.COMPLETED:
                task["completed_at"] = datetime.now().isoformat()
                task["progress"] = 100
            
            save_tasks_db(db)
            print(f"{Colors.GREEN}✅ 任务状态已更新：{task_id} → {status}{Colors.RESET}")
            return True
        
        # 更新子任务
        for subtask in task.get("subtasks", []):
            if subtask["id"] == task_id:
                subtask["status"] = status
                if progress is not None:
                    subtask["progress"] = progress
                save_tasks_db(db)
                print(f"{Colors.GREEN}✅ 子任务状态已更新：{task_id} → {status}{Colors.RESET}")
                return True
    
    print(f"{Colors.RED}❌ 未找到任务：{task_id}{Colors.RESET}")
    return False

def get_next_task() -> Optional[Dict]:
    """获取下一个可执行任务
    
    基于依赖关系和优先级排序
    """
    init_tasks()
    db = load_tasks_db()
    
    # 找出所有待执行的任务
    pending_tasks = []
    
    for task in db["tasks"]:
        if task["status"] == TaskStatus.PENDING:
            # 检查依赖
            deps_satisfied = True
            for dep_id in task.get("dependencies", []):
                dep_task = get_task(dep_id)
                if dep_task and dep_task["status"] != TaskStatus.COMPLETED:
                    deps_satisfied = False
                    break
            
            if deps_satisfied:
                pending_tasks.append(task)
        
        # 检查子任务
        for subtask in task.get("subtasks", []):
            if subtask["status"] == TaskStatus.PENDING:
                # 检查子任务依赖
                deps_satisfied = True
                for dep_id in subtask.get("dependencies", []):
                    dep_task = get_task(dep_id)
                    if dep_task and dep_task["status"] != TaskStatus.COMPLETED:
                        deps_satisfied = False
                        break
                
                if deps_satisfied:
                    pending_tasks.append(subtask)
    
    if not pending_tasks:
        return None
    
    # 按优先级排序
    priority_order = {
        "urgent": 0,
        "important": 1,
        "normal": 2,
        "low": 3
    }
    
    pending_tasks.sort(key=lambda x: priority_order.get(x.get("priority", "normal"), 1))
    
    return pending_tasks[0]

def calculate_progress(task_id: str) -> int:
    """计算任务进度"""
    task = get_task(task_id)
    
    if not task:
        return 0
    
    # 如果有子任务，基于子任务计算
    if task.get("subtasks"):
        total = len(task["subtasks"])
        completed = sum(1 for s in task["subtasks"] if s["status"] == TaskStatus.COMPLETED)
        return int((completed / total) * 100) if total > 0 else 0
    
    return task.get("progress", 0)

def show_progress():
    """显示进度报告"""
    init_tasks()
    db = load_tasks_db()
    
    tasks = db["tasks"]
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}任务进度报告{Colors.RESET}")
    print("=" * 70)
    
    # 总体统计
    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == TaskStatus.COMPLETED)
    in_progress = sum(1 for t in tasks if t["status"] == TaskStatus.IN_PROGRESS)
    pending = sum(1 for t in tasks if t["status"] == TaskStatus.PENDING)
    
    print(f"总任务数：{total}")
    print(f"已完成：{Colors.GREEN}{completed}{Colors.RESET} ({completed/total*100:.1f}%)")
    print(f"进行中：{Colors.BLUE}{in_progress}{Colors.RESET}")
    print(f"待执行：{Colors.YELLOW}{pending}{Colors.RESET}")
    
    # 按优先级统计
    print(f"\n按优先级:")
    by_priority = {}
    for task in tasks:
        p = task.get("priority_label", "未知")
        by_priority[p] = by_priority.get(p, 0) + 1
    
    for priority, count in by_priority.items():
        print(f"  {priority}: {count}个")
    
    # 进行中的任务
    print(f"\n{Colors.BOLD}进行中的任务:{Colors.RESET}")
    for task in tasks:
        if task["status"] == TaskStatus.IN_PROGRESS:
            progress = calculate_progress(task["id"])
            bar = "█" * int(progress / 10)
            print(f"  {task['id']}: {task['description'][:40]}...")
            print(f"    [{bar:10}] {progress}%")
    
    # 下一个可执行任务
    next_task = get_next_task()
    if next_task:
        print(f"\n{Colors.BOLD}{Colors.GREEN}下一个可执行任务:{Colors.RESET}")
        print(f"  {next_task['id']}: {next_task['description'][:60]}")
        print(f"  优先级：{next_task.get('priority_label', '未知')}")
        print(f"  预估时间：{next_task.get('estimated_hours', 'N/A')}小时")
    
    print("=" * 70)

def show_stats():
    """显示统计"""
    init_tasks()
    db = load_tasks_db()
    
    tasks = db["tasks"]
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}任务系统统计{Colors.RESET}")
    print("=" * 70)
    
    # 总体统计
    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == TaskStatus.COMPLETED)
    
    print(f"总任务数：{total}")
    print(f"完成率：{Colors.GREEN}{completed/total*100 if total > 0 else 0:.1f}%{Colors.RESET}")
    
    # 时间统计
    total_estimated = sum(t.get("estimated_hours", 0) for t in tasks)
    total_actual = sum(t.get("actual_hours", 0) for t in tasks)
    
    print(f"预估时间：{total_estimated}小时")
    print(f"实际时间：{total_actual}小时")
    
    # 子任务统计
    total_subtasks = sum(len(t.get("subtasks", [])) for t in tasks)
    completed_subtasks = sum(
        sum(1 for s in t.get("subtasks", []) if s["status"] == TaskStatus.COMPLETED)
        for t in tasks
    )
    
    print(f"子任务总数：{total_subtasks}")
    print(f"子任务完成：{completed_subtasks}")
    
    # 模板统计
    templates = list(TEMPLATES_DIR.glob("*.json"))
    print(f"可用模板：{len(templates)}个")
    
    print("=" * 70)

def execute_next():
    """执行下一个任务"""
    next_task = get_next_task()
    
    if not next_task:
        print(f"{Colors.YELLOW}⚠️ 没有可执行的任务{Colors.RESET}")
        return None
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}开始执行任务:{Colors.RESET}")
    print(f"  ID: {next_task['id']}")
    print(f"  描述：{next_task['description']}")
    print(f"  优先级：{next_task.get('priority_label', '未知')}")
    print(f"  预估时间：{next_task.get('estimated_hours', 'N/A')}小时")
    
    # 更新状态为进行中
    update_task_status(next_task['id'], TaskStatus.IN_PROGRESS)
    
    return next_task['id']

def interactive_menu():
    """交互式菜单"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}任务分解系统菜单{Colors.RESET}")
        print("=" * 70)
        print("1. 分解新任务")
        print("2. 列出任务")
        print("3. 查看任务详情")
        print("4. 更新任务状态")
        print("5. 查看进度报告")
        print("6. 执行下一个任务")
        print("7. 查看统计")
        print("8. 使用模板")
        print("9. 退出")
        print("=" * 70)
        
        choice = input("请选择 (1-9): ").strip()
        
        if choice == '1':
            desc = input("任务描述：").strip()
            template = input("模板 (research/development/writing，回车跳过): ").strip() or None
            priority = input("优先级 (urgent/important/normal/low，默认 important): ").strip() or "important"
            decompose_task(desc, template, priority)
        
        elif choice == '2':
            status = input("状态过滤 (pending/in_progress/completed，回车显示全部): ").strip() or None
            tasks = list_tasks(status)
            for t in tasks:
                print(f"  {t['id']} [{t['status']}] {t['description'][:50]}...")
        
        elif choice == '3':
            task_id = input("任务 ID: ").strip()
            task = get_task(task_id)
            if task:
                print(f"\n任务详情：{task_id}")
                print(f"  描述：{task['description']}")
                print(f"  状态：{task['status']}")
                print(f"  优先级：{task.get('priority_label', '未知')}")
                print(f"  进度：{task.get('progress', 0)}%")
                print(f"  预估时间：{task.get('estimated_hours', 'N/A')}小时")
        
        elif choice == '4':
            task_id = input("任务 ID: ").strip()
            status = input("新状态 (pending/in_progress/completed/blocked): ").strip()
            progress = input("进度 (0-100，回车自动): ").strip()
            progress = int(progress) if progress.isdigit() else None
            update_task_status(task_id, status, progress)
        
        elif choice == '5':
            show_progress()
        
        elif choice == '6':
            execute_next()
        
        elif choice == '7':
            show_stats()
        
        elif choice == '8':
            template = input("模板名 (research/development/writing): ").strip()
            template_file = TEMPLATES_DIR / f"{template}.json"
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"\n模板：{data['name']}")
                for i, st in enumerate(data['subtasks'], 1):
                    deps = f" (依赖：{st.get('dependencies', [])})" if st.get('dependencies') else ""
                    print(f"  {i}. {st['name']} - {st.get('estimated_hours', 1)}小时{deps}")
            else:
                print(f"{Colors.RED}❌ 模板不存在{Colors.RESET}")
        
        elif choice == '9':
            print("退出")
            break
        
        else:
            print(f"{Colors.RED}❌ 无效选择{Colors.RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Task Decomposition System - 任务分解自动化')
    parser.add_argument('--decompose', type=str, help='分解任务')
    parser.add_argument('--template', type=str, help='使用模板')
    parser.add_argument('--priority', type=str, default='important', help='优先级')
    parser.add_argument('--list', action='store_true', help='列出任务')
    parser.add_argument('--status', type=str, help='状态过滤')
    parser.add_argument('--detail', type=str, help='查看任务详情')
    parser.add_argument('--update', type=str, help='更新任务状态')
    parser.add_argument('--progress', action='store_true', help='查看进度')
    parser.add_argument('--execute-next', action='store_true', help='执行下一个任务')
    parser.add_argument('--stats', action='store_true', help='查看统计')
    
    args = parser.parse_args()
    
    init_tasks()
    
    if args.decompose:
        decompose_task(args.decompose, args.template, args.priority)
    elif args.list:
        tasks = list_tasks(args.status)
        for t in tasks:
            print(f"  {t['id']} [{t['status']}] {t['description'][:50]}...")
    elif args.detail:
        task = get_task(args.detail)
        if task:
            print(f"任务详情：{task['id']}")
            print(f"  描述：{task['description']}")
            print(f"  状态：{task['status']}")
    elif args.update:
        status = input("新状态：").strip()
        update_task_status(args.update, status)
    elif args.progress:
        show_progress()
    elif args.execute_next:
        execute_next()
    elif args.stats:
        show_stats()
    else:
        interactive_menu()

if __name__ == '__main__':
    main()
