#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Proactive Interaction System - 主动式交互系统

功能:
1. 主动提醒功能 (任务/日历/截止)
2. 智能建议生成 (基于上下文)
3. 预警系统 (异常/风险/机会)
4. 上下文感知交互
5. 用户行为学习

Usage:
    py proactive_agent.py --check              # 检查主动提醒
    py proactive_agent.py --suggest            # 生成智能建议
    py proactive_agent.py --alerts             # 查看预警
    py proactive_agent.py --context            # 显示上下文
    py proactive_agent.py --learn              # 学习用户行为
    py proactive_agent.py --status             # 查看状态
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
PROACTIVE_DIR = WORKSPACE / "proactive"
PROACTIVE_DB = PROACTIVE_DIR / "proactive-db.json"
PROACTIVE_CONFIG = PROACTIVE_DIR / "proactive-config.json"
USER_PATTERNS = PROACTIVE_DIR / "user-patterns.json"

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

# 提醒类型
class ReminderType:
    TASK = "task"           # 任务提醒
    DEADLINE = "deadline"   # 截止提醒
    CALENDAR = "calendar"   # 日历提醒
    HEARTBEAT = "heartbeat" # 心跳检查
    CUSTOM = "custom"       # 自定义提醒

# 预警级别
class AlertLevel:
    INFO = "info"           # 信息
    WARNING = "warning"     # 警告
    CRITICAL = "critical"   # 严重
    OPPORTUNITY = "opportunity"  # 机会

def init_proactive():
    """初始化主动交互系统"""
    PROACTIVE_DIR.mkdir(exist_ok=True)
    
    if not PROACTIVE_DB.exists():
        save_proactive_db({
            "reminders": [],
            "alerts": [],
            "suggestions": [],
            "next_id": 1
        })
    
    if not PROACTIVE_CONFIG.exists():
        save_config({
            "enabled": True,
            "check_interval_minutes": 30,
            "reminder_lead_time_minutes": 60,
            "enable_suggestions": True,
            "enable_alerts": True,
            "enable_context_awareness": True,
            "enable_learning": True,
            "quiet_hours": {
                "start": 23,
                "end": 8
            }
        })
    
    if not USER_PATTERNS.exists():
        save_patterns({
            "active_hours": [],
            "frequent_tasks": [],
            "preferred_priority": "important",
            "response_patterns": [],
            "learning_count": 0
        })

def save_proactive_db(db):
    """保存数据库"""
    with open(PROACTIVE_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def load_proactive_db():
    """加载数据库"""
    if not PROACTIVE_DB.exists():
        return {"reminders": [], "alerts": [], "suggestions": [], "next_id": 1}
    
    with open(PROACTIVE_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置"""
    with open(PROACTIVE_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_config():
    """加载配置"""
    if not PROACTIVE_CONFIG.exists():
        return {
            "enabled": True,
            "check_interval_minutes": 30,
            "reminder_lead_time_minutes": 60,
            "enable_suggestions": True,
            "enable_alerts": True,
            "enable_context_awareness": True,
            "enable_learning": True,
            "quiet_hours": {"start": 23, "end": 8}
        }
    
    with open(PROACTIVE_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_patterns(patterns):
    """保存用户模式"""
    with open(USER_PATTERNS, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)

def load_patterns():
    """加载用户模式"""
    if not USER_PATTERNS.exists():
        return {
            "active_hours": [],
            "frequent_tasks": [],
            "preferred_priority": "important",
            "response_patterns": [],
            "learning_count": 0
        }
    
    with open(USER_PATTERNS, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_id():
    """生成 ID"""
    db = load_proactive_db()
    item_id = db["next_id"]
    db["next_id"] += 1
    save_proactive_db(db)
    return f"PRO-{item_id:04d}"

def is_quiet_hours():
    """检查是否在安静时间"""
    config = load_config()
    quiet = config.get("quiet_hours", {"start": 23, "end": 8})
    current_hour = datetime.now().hour
    
    if quiet["start"] > quiet["end"]:  # 跨夜
        return current_hour >= quiet["start"] or current_hour < quiet["end"]
    else:
        return quiet["start"] <= current_hour < quiet["end"]

# ==================== 主动提醒功能 ====================

def add_reminder(content: str, reminder_type: str, scheduled_time: str = None, 
                 priority: str = "important", repeat: str = None) -> str:
    """添加主动提醒
    
    Args:
        content: 提醒内容
        reminder_type: 类型 (task/deadline/calendar/heartbeat/custom)
        scheduled_time: 计划时间 (ISO 格式)
        priority: 优先级 (urgent/important/normal/low)
        repeat: 重复规则 (daily/weekly/monthly)
    
    Returns:
        提醒 ID
    """
    init_proactive()
    
    reminder_id = generate_id()
    
    if not scheduled_time:
        scheduled_time = datetime.now().isoformat()
    
    reminder = {
        "id": reminder_id,
        "content": content,
        "type": reminder_type,
        "scheduled_time": scheduled_time,
        "priority": priority,
        "repeat": repeat,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "triggered_at": None,
        "dismissed": False,
        "context": {}
    }
    
    db = load_proactive_db()
    db["reminders"].append(reminder)
    save_proactive_db(db)
    
    print(f"{Colors.GREEN}✅ 提醒已添加{Colors.RESET}")
    print(f"   ID: {reminder_id}")
    print(f"   内容：{content}")
    print(f"   类型：{reminder_type}")
    print(f"   时间：{scheduled_time[:19]}")
    print(f"   优先级：{priority}")
    
    return reminder_id

def check_reminders() -> List[Dict]:
    """检查待触发的提醒"""
    init_proactive()
    db = load_proactive_db()
    config = load_config()
    
    if not config.get("enabled", True):
        return []
    
    if is_quiet_hours():
        print(f"{Colors.YELLOW}⚠️ 安静时间，跳过提醒检查{Colors.RESET}")
        return []
    
    now = datetime.now()
    lead_time = timedelta(minutes=config.get("reminder_lead_time_minutes", 60))
    
    triggered = []
    
    for reminder in db["reminders"]:
        if reminder["status"] != "pending" or reminder["dismissed"]:
            continue
        
        scheduled = datetime.fromisoformat(reminder["scheduled_time"])
        
        # 检查是否到达提醒时间
        if now >= scheduled - lead_time and now <= scheduled + lead_time:
            reminder["status"] = "triggered"
            reminder["triggered_at"] = now.isoformat()
            triggered.append(reminder)
            
            # 处理重复
            if reminder.get("repeat"):
                next_time = calculate_next_repeat(scheduled, reminder["repeat"])
                add_reminder(
                    reminder["content"],
                    reminder["type"],
                    next_time.isoformat(),
                    reminder["priority"],
                    reminder["repeat"]
                )
    
    save_proactive_db(db)
    
    return triggered

def calculate_next_repeat(current: datetime, repeat: str) -> datetime:
    """计算下次重复时间"""
    if repeat == "daily":
        return current + timedelta(days=1)
    elif repeat == "weekly":
        return current + timedelta(weeks=1)
    elif repeat == "monthly":
        return current + timedelta(days=30)
    return current

# ==================== 智能建议生成 ====================

def generate_suggestions(context: Dict = None) -> List[Dict]:
    """生成智能建议
    
    Args:
        context: 上下文信息 (当前任务、时间、状态等)
    
    Returns:
        建议列表
    """
    init_proactive()
    config = load_config()
    
    if not config.get("enable_suggestions", True):
        return []
    
    suggestions = []
    patterns = load_patterns()
    
    # 基于时间的建议
    hour = datetime.now().hour
    if 9 <= hour <= 11:
        suggestions.append({
            "id": generate_id(),
            "type": "productivity",
            "content": "上午是高效时间，建议处理重要且复杂的任务",
            "priority": "high",
            "context": "morning_focus"
        })
    elif 14 <= hour <= 15:
        suggestions.append({
            "id": generate_id(),
            "type": "break",
            "content": "午后容易疲劳，建议短暂休息或处理简单任务",
            "priority": "medium",
            "context": "afternoon_slump"
        })
    
    # 基于任务的建议
    if context:
        # 检查任务负载
        if context.get("task_count", 0) > 5:
            suggestions.append({
                "id": generate_id(),
                "type": "workload",
                "content": f"当前有{context['task_count']}个待办任务，建议优先处理高优先级任务",
                "priority": "high",
                "context": "high_workload"
            })
        
        # 检查任务停滞
        if context.get("stuck_task"):
            suggestions.append({
                "id": generate_id(),
                "type": "unblock",
                "content": f"任务'{context['stuck_task']}'已停滞，建议寻求帮助或调整方法",
                "priority": "high",
                "context": "task_stuck"
            })
    
    # 基于用户模式的建议
    if patterns.get("frequent_tasks"):
        top_task = patterns["frequent_tasks"][0] if patterns["frequent_tasks"] else None
        if top_task:
            suggestions.append({
                "id": generate_id(),
                "type": "habit",
                "content": f"您经常处理'{top_task}'相关任务，是否需要创建模板？",
                "priority": "low",
                "context": "pattern_learning"
            })
    
    # 保存建议
    db = load_proactive_db()
    for suggestion in suggestions:
        suggestion["created_at"] = datetime.now().isoformat()
        suggestion["dismissed"] = False
        db["suggestions"].append(suggestion)
    save_proactive_db(db)
    
    return suggestions

# ==================== 预警系统 ====================

def add_alert(content: str, level: str, category: str = "general", 
              auto_resolve: bool = False) -> str:
    """添加预警
    
    Args:
        content: 预警内容
        level: 级别 (info/warning/critical/opportunity)
        category: 类别 (task/system/resource/opportunity)
        auto_resolve: 是否自动解决
    
    Returns:
        预警 ID
    """
    init_proactive()
    
    alert_id = generate_id()
    
    # 预警级别颜色
    level_colors = {
        "info": Colors.BLUE,
        "warning": Colors.YELLOW,
        "critical": Colors.RED,
        "opportunity": Colors.GREEN
    }
    
    alert = {
        "id": alert_id,
        "content": content,
        "level": level,
        "category": category,
        "status": "active",
        "auto_resolve": auto_resolve,
        "created_at": datetime.now().isoformat(),
        "resolved_at": None,
        "acknowledged": False
    }
    
    db = load_proactive_db()
    db["alerts"].append(alert)
    save_proactive_db(db)
    
    color = level_colors.get(level, Colors.RESET)
    print(f"{color}🚨 预警已添加{Colors.RESET}")
    print(f"   ID: {alert_id}")
    print(f"   内容：{content}")
    print(f"   级别：{level}")
    print(f"   类别：{category}")
    
    return alert_id

def check_alerts(context: Dict = None) -> List[Dict]:
    """检查并生成预警"""
    init_proactive()
    config = load_config()
    
    if not config.get("enable_alerts", True):
        return []
    
    alerts = []
    
    # 系统预警
    if context:
        # 任务逾期预警
        if context.get("overdue_tasks", 0) > 0:
            alerts.append({
                "id": generate_id(),
                "content": f"有{context['overdue_tasks']}个任务已逾期",
                "level": AlertLevel.WARNING,
                "category": "task",
                "created_at": datetime.now().isoformat()
            })
        
        # 资源预警
        if context.get("high_memory_usage", False):
            alerts.append({
                "id": generate_id(),
                "content": "系统内存使用率过高，建议关闭不必要的应用",
                "level": AlertLevel.WARNING,
                "category": "resource",
                "created_at": datetime.now().isoformat()
            })
        
        # 机会预警
        if context.get("free_time_minutes", 0) > 30:
            alerts.append({
                "id": generate_id(),
                "content": f"检测到{context['free_time_minutes']}分钟空闲时间，可以处理小任务",
                "level": AlertLevel.OPPORTUNITY,
                "category": "opportunity",
                "created_at": datetime.now().isoformat()
            })
    
    # 保存预警
    db = load_proactive_db()
    for alert in alerts:
        alert["status"] = "active"
        alert["acknowledged"] = False
        db["alerts"].append(alert)
    save_proactive_db(db)
    
    return alerts

# ==================== 上下文感知交互 ====================

def get_context() -> Dict:
    """获取当前上下文"""
    init_proactive()
    
    # 从任务系统加载
    tasks_db_file = WORKSPACE / "tasks" / "tasks-db.json"
    tasks_context = {"task_count": 0, "overdue_tasks": 0}
    
    if tasks_db_file.exists():
        with open(tasks_db_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
            tasks = tasks_data.get("tasks", [])
            tasks_context["task_count"] = len([t for t in tasks if t["status"] == "pending"])
            tasks_context["in_progress"] = len([t for t in tasks if t["status"] == "in_progress"])
    
    # 从记忆系统加载
    memory_db_file = WORKSPACE / "13-memory" / "memory-db.json"
    memory_context = {"recent_memories": 0}
    
    if memory_db_file.exists():
        with open(memory_db_file, 'r', encoding='utf-8') as f:
            memory_data = json.load(f)
            memories = memory_data.get("memories", [])
            # 最近 24 小时的记忆
            recent = [m for m in memories if 
                     datetime.fromisoformat(m["created_at"]) > datetime.now() - timedelta(days=1)]
            memory_context["recent_memories"] = len(recent)
    
    # 时间上下文
    now = datetime.now()
    time_context = {
        "hour": now.hour,
        "day_of_week": now.strftime("%A"),
        "is_weekend": now.weekday() >= 5,
        "is_work_hours": 9 <= now.hour <= 18
    }
    
    # 合并上下文
    context = {
        **tasks_context,
        **memory_context,
        **time_context,
        "timestamp": now.isoformat()
    }
    
    return context

def context_aware_response(base_response: str, context: Dict = None) -> str:
    """基于上下文调整响应"""
    if not context:
        context = get_context()
    
    # 根据时间调整语气
    hour = context.get("hour", 12)
    if hour < 12:
        greeting = "早上好！"
    elif hour < 18:
        greeting = "下午好！"
    else:
        greeting = "晚上好！"
    
    # 根据任务负载调整
    task_count = context.get("task_count", 0)
    if task_count > 10:
        load_note = f" (您有{task_count}个待办任务，建议优先处理重要事项)"
    elif task_count > 5:
        load_note = f" (您有{task_count}个待办任务)"
    else:
        load_note = ""
    
    return f"{greeting}{load_note}\n\n{base_response}"

# ==================== 用户行为学习 ====================

def learn_user_action(action: str, context: Dict = None, outcome: str = "positive"):
    """学习用户行为
    
    Args:
        action: 用户行为
        context: 行为发生时的上下文
        outcome: 结果 (positive/negative/neutral)
    """
    init_proactive()
    patterns = load_patterns()
    
    # 记录活跃时间
    current_hour = datetime.now().hour
    if current_hour not in patterns["active_hours"]:
        patterns["active_hours"].append(current_hour)
        patterns["active_hours"].sort()
    
    # 记录频繁任务
    if context and context.get("task_type"):
        task_type = context["task_type"]
        if task_type not in patterns["frequent_tasks"]:
            patterns["frequent_tasks"].append(task_type)
    
    # 记录响应模式
    patterns["response_patterns"].append({
        "action": action,
        "context": context,
        "outcome": outcome,
        "timestamp": datetime.now().isoformat()
    })
    
    # 限制历史记录数量
    if len(patterns["response_patterns"]) > 100:
        patterns["response_patterns"] = patterns["response_patterns"][-100:]
    
    patterns["learning_count"] += 1
    
    save_patterns(patterns)
    
    print(f"{Colors.GREEN}✅ 已学习用户行为：{action}{Colors.RESET}")
    print(f"   学习次数：{patterns['learning_count']}")

# ==================== 状态显示 ====================

def show_status():
    """显示主动交互状态"""
    init_proactive()
    db = load_proactive_db()
    config = load_config()
    patterns = load_patterns()
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}主动交互系统状态{Colors.RESET}")
    print("=" * 70)
    
    # 系统状态
    enabled = config.get("enabled", True)
    status_color = Colors.GREEN if enabled else Colors.RED
    print(f"系统状态：{status_color}{'启用' if enabled else '禁用'}{Colors.RESET}")
    print(f"检查间隔：{config.get('check_interval_minutes', 30)}分钟")
    print(f"安静时间：{config.get('quiet_hours', {}).get('start', 23)}:00 - {config.get('quiet_hours', {}).get('end', 8)}:00")
    
    # 提醒统计
    reminders = db.get("reminders", [])
    pending = sum(1 for r in reminders if r["status"] == "pending")
    triggered = sum(1 for r in reminders if r["status"] == "triggered")
    print(f"\n提醒统计:")
    print(f"  待触发：{pending}个")
    print(f"  已触发：{triggered}个")
    
    # 预警统计
    alerts = db.get("alerts", [])
    active = sum(1 for a in alerts if a["status"] == "active")
    critical = sum(1 for a in alerts if a["level"] == "critical" and a["status"] == "active")
    print(f"\n预警统计:")
    print(f"  活跃预警：{active}个")
    print(f"  严重预警：{Colors.RED}{critical}{Colors.RESET}个")
    
    # 建议统计
    suggestions = db.get("suggestions", [])
    print(f"\n建议统计:")
    print(f"  历史建议：{len(suggestions)}条")
    
    # 用户模式
    print(f"\n用户模式学习:")
    print(f"  学习次数：{patterns.get('learning_count', 0)}")
    print(f"  活跃时段：{patterns.get('active_hours', [])}")
    print(f"  频繁任务：{patterns.get('frequent_tasks', [])[:3]}")
    
    print("=" * 70)

def check_all():
    """执行完整检查"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}主动交互检查{Colors.RESET}")
    print("=" * 70)
    
    # 1. 检查提醒
    print(f"\n{Colors.BOLD}1. 检查提醒:{Colors.RESET}")
    triggered = check_reminders()
    if triggered:
        for r in triggered:
            print(f"  🔔 {r['content']}")
    else:
        print(f"  {Colors.GREEN}✅ 无待触发提醒{Colors.RESET}")
    
    # 2. 生成建议
    print(f"\n{Colors.BOLD}2. 智能建议:{Colors.RESET}")
    context = get_context()
    suggestions = generate_suggestions(context)
    if suggestions:
        for s in suggestions:
            print(f"  💡 {s['content']}")
    else:
        print(f"  {Colors.GREEN}✅ 暂无建议{Colors.RESET}")
    
    # 3. 检查预警
    print(f"\n{Colors.BOLD}3. 系统预警:{Colors.RESET}")
    alerts = check_alerts(context)
    if alerts:
        for a in alerts:
            level_icon = {
                "info": "ℹ️",
                "warning": "⚠️",
                "critical": "🚨",
                "opportunity": "🌟"
            }.get(a["level"], "•")
            print(f"  {level_icon} {a['content']}")
    else:
        print(f"  {Colors.GREEN}✅ 无预警{Colors.RESET}")
    
    # 4. 上下文感知
    print(f"\n{Colors.BOLD}4. 上下文感知:{Colors.RESET}")
    print(f"  时间：{context['timestamp'][:19]}")
    print(f"  待办任务：{context.get('task_count', 0)}个")
    print(f"  进行中：{context.get('in_progress', 0)}个")
    print(f"  活跃时段：{'是' if context.get('is_work_hours') else '否'}")
    
    print("=" * 70)

def interactive_menu():
    """交互式菜单"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}主动交互系统菜单{Colors.RESET}")
        print("=" * 70)
        print("1. 执行完整检查")
        print("2. 添加提醒")
        print("3. 查看提醒")
        print("4. 生成建议")
        print("5. 添加预警")
        print("6. 查看预警")
        print("7. 查看上下文")
        print("8. 查看状态")
        print("9. 学习用户行为")
        print("10. 退出")
        print("=" * 70)
        
        choice = input("请选择 (1-10): ").strip()
        
        if choice == '1':
            check_all()
        elif choice == '2':
            content = input("提醒内容：").strip()
            rtype = input("类型 (task/deadline/calendar/custom): ").strip() or "custom"
            priority = input("优先级 (urgent/important/normal/low): ").strip() or "important"
            add_reminder(content, rtype, priority=priority)
        elif choice == '3':
            db = load_proactive_db()
            for r in db.get("reminders", [])[-5:]:
                print(f"  {r['id']}: {r['content'][:50]}... [{r['status']}]")
        elif choice == '4':
            suggestions = generate_suggestions(get_context())
            for s in suggestions:
                print(f"  💡 {s['content']}")
        elif choice == '5':
            content = input("预警内容：").strip()
            level = input("级别 (info/warning/critical): ").strip() or "warning"
            add_alert(content, level)
        elif choice == '6':
            db = load_proactive_db()
            for a in db.get("alerts", [])[-5:]:
                print(f"  {a['id']}: {a['content'][:50]}... [{a['level']}]")
        elif choice == '7':
            context = get_context()
            print(json.dumps(context, indent=2, ensure_ascii=False))
        elif choice == '8':
            show_status()
        elif choice == '9':
            action = input("行为描述：").strip()
            learn_user_action(action, get_context())
        elif choice == '10':
            print("退出")
            break
        else:
            print(f"{Colors.RED}❌ 无效选择{Colors.RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Proactive Interaction System - 主动式交互')
    parser.add_argument('--check', action='store_true', help='执行完整检查')
    parser.add_argument('--remind', type=str, help='添加提醒')
    parser.add_argument('--suggest', action='store_true', help='生成建议')
    parser.add_argument('--alert', type=str, help='添加预警')
    parser.add_argument('--alerts', action='store_true', help='查看预警')
    parser.add_argument('--context', action='store_true', help='查看上下文')
    parser.add_argument('--learn', type=str, help='学习用户行为')
    parser.add_argument('--status', action='store_true', help='查看状态')
    
    args = parser.parse_args()
    
    init_proactive()
    
    if args.check:
        check_all()
    elif args.remind:
        add_reminder(args.remind, "custom")
    elif args.suggest:
        suggestions = generate_suggestions(get_context())
        for s in suggestions:
            print(f"💡 {s['content']}")
    elif args.alert:
        add_alert(args.alert, "warning")
    elif args.alerts:
        db = load_proactive_db()
        for a in db.get("alerts", [])[-10:]:
            print(f"{a['id']}: {a['content'][:60]}... [{a['level']}]")
    elif args.context:
        context = get_context()
        print(json.dumps(context, indent=2, ensure_ascii=False))
    elif args.learn:
        learn_user_action(args.learn, get_context())
    elif args.status:
        show_status()
    else:
        interactive_menu()

if __name__ == '__main__':
    main()
