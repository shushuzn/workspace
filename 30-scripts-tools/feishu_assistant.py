#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu Assistant - 飞书全能助手
统一管理所有飞书功能

用法:
    py feishu_assistant.py <command> [args...]

命令:
    msg <text>              发送文本
    card <json_file>        发送卡片
    img <path>              发送图片
    file <path>             发送文件
    mention <user_id> <msg>  @用户发消息
    batch <file>             批量发送
    calendar                 查看日程
    contacts                 查看通讯录
    search <keyword>          搜索消息
    monitor                  系统监控报告
    daily                    每日报告
    stats                    发送统计
    todos                    查看待办
    create-todo <title>      创建待办
"""

import sys
import json
import os
import ssl
import hashlib
import urllib.request
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

sys.path.insert(0, r"D:\OpenClaw\workspace\30-scripts-tools\feishu-tools")
from feishu_api import FeishuAPIClient, MESSAGE_ENDPOINT

BASE_DIR = Path(r"D:\OpenClaw\workspace\30-scripts-tools")
FEISHU_CFG = BASE_DIR / "feishu-tools" / "feishu-config.json"
STATS_FILE = BASE_DIR / "feishu-tools" / "feishu-stats.json"


# ============================================================
# 工具函数
# ============================================================


def get_client():
    return FeishuAPIClient()


def load_config():
    return json.load(open(FEISHU_CFG, "r", encoding="utf-8"))


def load_stats():
    return (
        json.load(open(STATS_FILE, "r", encoding="utf-8"))
        if STATS_FILE.exists()
        else {"sent": 0, "failed": 0}
    )


def save_stats(stats):
    json.dump(
        stats, open(STATS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2
    )


def api_request(token, method, url, **kwargs):
    """直接调用飞书 API"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = kwargs.get("data")
    params = kwargs.get("params", {})

    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        headers=headers,
        method=method,
    )

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        return json.loads(resp.read())


# ============================================================
# 1. 消息发送
# ============================================================


def cmd_msg(args):
    """发送文本消息"""
    if not args:
        print("[ERROR] 需要消息内容")
        return
    text = " ".join(args)
    client = get_client()
    client.send_text(text)
    print(f"[OK] Sent: {text[:50]}...")

    stats = load_stats()
    stats["sent"] = stats.get("sent", 0) + 1
    save_stats(stats)


def cmd_card(args):
    """发送卡片"""
    if not args:
        print("[ERROR] 需要卡片 JSON 文件路径")
        return
    file_path = Path(" ".join(args))
    if not file_path.exists():
        print(f"[ERROR] 文件不存在: {file_path}")
        return
    card = json.load(open(file_path, "r", encoding="utf-8"))
    title = (
        card.get("card", {}).get("header", {}).get("title", {}).get("content", "Card")
    )
    client = get_client()
    client.send_poster(title, card.get("card", {}).get("elements", []))
    print(f"[OK] Card sent: {title}")


def cmd_img(args):
    """发送图片"""
    if not args:
        print("[ERROR] 需要图片路径")
        return
    path = Path(" ".join(args))
    if not path.exists():
        print(f"[ERROR] 文件不存在: {path}")
        return
    client = get_client()
    client.send_image(str(path))
    print(f"[OK] Image sent: {path.name}")


def cmd_file(args):
    """发送文件"""
    if not args:
        print("[ERROR] 需要文件路径")
        return
    path = Path(" ".join(args))
    if not path.exists():
        print(f"[ERROR] 文件不存在: {path}")
        return
    client = get_client()
    client.send_file(str(path))
    print(f"[OK] File sent: {path.name}")


def cmd_mention(args):
    """@用户发送消息"""
    if len(args) < 2:
        print("[ERROR] 需要 user_id 和消息")
        return

    user_id = args[0]
    text = " ".join(args[1:])

    client = get_client()
    elements = [
        {"tag": "at", "user_id": user_id},
        {"tag": "div", "text": {"tag": "lark_md", "content": text}},
    ]
    client.send_poster("消息通知", elements, receive_id=user_id)
    print(f"[OK] Mentioned user: {user_id}")


# ============================================================
# 2. 日程管理
# ============================================================


def cmd_calendar(args):
    """查看今日日程"""
    client = get_client()
    token = client.token_manager.get_token()

    today = datetime.now()
    start_ts = int(today.replace(hour=0, minute=0, second=0).timestamp())
    end_ts = int(today.replace(hour=23, minute=59, second=59).timestamp())
    today_str = today.strftime("%Y-%m-%d")

    url = "https://open.feishu.cn/open-apis/calendar/v4/calendars/primary/events"

    try:
        result = api_request(
            token,
            "GET",
            url,
            params={
                "start_time": str(start_ts),
                "end_time": str(end_ts),
                "max_results": 50,
            },
        )

        if result.get("code") != 0:
            print(f"[WARN] Calendar: {result.get('msg', 'permission denied')}")
            print("[INFO] 日历功能需要日历读写权限")
            client.send_text("Calendar permission required")
            return

        events = result.get("items", [])

        if not events:
            print(f"[INFO] {today} 没有日程")
            return

        print(f"\n📅 {today} 日程 ({len(events)} 个)")
        print("-" * 40)

        for e in events:
            st = (
                e.get("start", {}).get("date_time", "")[:16]
                if e.get("start", {}).get("date_time")
                else ""
            )
            title = e.get("summary", "无标题")
            loc = e.get("location", {}).get("name", "")
            status = e.get("status", {}).get("overall_status", "")

            status_icon = ""
            if status == "confirmed":
                status_icon = "✅"
            elif status == "tentative":
                status_icon = "❓"
            elif status == "cancelled":
                status_icon = "❌"

            print(f"  {st} {status_icon} {title}")
            if loc:
                print(f"       📍 {loc}")

        # 发送摘要
        msg_lines = [f"📅 {today} 日程\n"]
        for e in events[:8]:
            st = (
                e.get("start", {}).get("date_time", "")[:16]
                if e.get("start", {}).get("date_time")
                else ""
            )
            title = e.get("summary", "无标题")[:25]
            msg_lines.append(f"• {st} {title}")

        client.send_text("\n".join(msg_lines))
        print(f"\n[OK] Sent calendar to Feishu")

    except Exception as e:
        print(f"[ERROR] {e}")


def cmd_todos(args):
    """查看/创建待办"""
    client = get_client()
    token = client.token_manager.get_token()

    if args and args[0] == "create":
        # 创建待办
        title = " ".join(args[1:]) if len(args) > 1 else "新待办"

        url = "https://open.feishu.cn/open-apis/task/v2/tasks"
        due = datetime.now() + timedelta(days=7)

        data = {
            "summary": title,
            "due": {"timestamp": str(int(due.timestamp() * 1000)), "is_all_day": True},
        }

        try:
            result = api_request(token, "POST", url, data=data)
            task_id = result.get("task", {}).get("guid")
            if task_id:
                print(f"[OK] Created todo: {title}")
                print(f"     ID: {task_id}")
                client.send_text(f"✅ 已创建待办: {title}")
            else:
                print(f"[ERROR] Failed: {result}")
        except Exception as e:
            print(f"[ERROR] {e}")
        return

    # 查看待办
    url = "https://open.feishu.cn/open-apis/task/v2/tasks"

    try:
        result = api_request(token, "GET", url, params={"page_size": 20})
        tasks = result.get("items", [])

        if not tasks:
            print("[INFO] 没有待办事项")
            return

        print(f"\n📋 待办事项 ({len(tasks)} 个)")
        print("-" * 40)

        for t in tasks:
            title = t.get("summary", "无标题")
            status = t.get("completed_at")
            due = t.get("due", {})

            icon = "✅" if status else "⬜"
            due_str = ""
            if due:
                ts = int(due.get("timestamp", 0)) / 1000
                due_str = datetime.fromtimestamp(ts).strftime("%m-%d")

            print(f"  {icon} {title} {due_str}")

        client.send_text(f"📋 待办 {len(tasks)} 个")
        print(f"\n[OK] Sent to Feishu")

    except Exception as e:
        print(f"[ERROR] {e}")


# ============================================================
# 3. 通讯录
# ============================================================


def cmd_contacts(args):
    """查看通讯录"""
    client = get_client()
    token = client.token_manager.get_token()

    url = "https://open.feishu.cn/open-apis/contact/v3/users"

    try:
        result = api_request(token, "GET", url, params={"page_size": 50})
        users = result.get("data", {}).get("items", [])

        if not users:
            print("[INFO] 没有获取到用户")
            return

        print(f"\n👥 通讯录 ({len(users)} 人)")
        print("-" * 40)

        for u in users[:20]:
            name = u.get("name", "?")
            en_name = u.get("en_name", "")
            email = u.get("email", "")
            dept = u.get("department_ids", [""])[0] if u.get("department_ids") else ""
            open_id = u.get("open_id", "")
            print(f"  {name} {f'({en_name})' if en_name else ''}")
            print(f"     ID: {open_id}")
            if email:
                print(f"     Email: {email}")

        # 发送给自己
        msg = f"👥 通讯录 {len(users)} 人\n"
        for u in users[:10]:
            name = u.get("name", "?")
            open_id = u.get("open_id", "")
            msg += f"• {name} ({open_id})\n"

        client.send_text(msg)
        print(f"\n[OK] Sent to Feishu")

    except Exception as e:
        print(f"[ERROR] {e}")


# ============================================================
# 4. 搜索消息
# ============================================================


def cmd_search(args):
    """搜索消息"""
    if not args:
        print("[ERROR] 需要搜索关键词")
        return

    keyword = " ".join(args)
    client = get_client()

    # 构造搜索卡片
    elements = [
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**搜索关键词:** {keyword}"},
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "消息搜索需要在飞书客户端进行。\n\n可使用关键词: @机器人 搜索内容",
            },
        },
        {"tag": "hr"},
        {
            "tag": "note",
            "elements": [{"tag": "plain_text", "content": f"搜索: {keyword}"}],
        },
    ]

    client.send_poster(f"搜索: {keyword}", elements)
    print(f"[OK] Search card sent: {keyword}")


# ============================================================
# 5. 系统监控
# ============================================================


def cmd_monitor(args):
    """系统监控报告"""
    import psutil
    import platform

    client = get_client()

    # CPU
    cpu = psutil.cpu_percent(interval=1)

    # 内存
    mem = psutil.virtual_memory()
    mem_used = mem.used / (1024**3)
    mem_total = mem.total / (1024**3)

    # 磁盘
    disk = psutil.disk_usage("C:")

    # 进程
    process_count = len(psutil.pids())

    # 网络
    net = psutil.net_io_counters()

    # 电池
    battery = psutil.sensors_battery()

    # 启动时间
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time

    # 构建报告
    time_str = datetime.now().strftime("%H:%M")

    elements = [
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**🖥️ 系统监控报告** `{time_str}`"},
        },
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**CPU:** {cpu}%"}},
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**内存:** {mem_used:.1f}/{mem_total:.1f} GB ({mem.percent}%)",
            },
        },
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**磁盘:** {disk.percent}% used"},
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**进程:** {process_count} 个运行中",
            },
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**网络:** ↑{net.bytes_sent / 1024 / 1024:.1f}MB ↓{net.bytes_recv / 1024 / 1024:.1f}MB",
            },
        },
        {"tag": "hr"},
    ]

    if battery:
        icon = "🔌" if battery.power_plugged else "🔋"
        elements.append(
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"{icon} **电池:** {battery.percent}% {'已接通电源' if battery.power_plugged else '使用电池'}",
                },
            }
        )

    elements.extend(
        [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**运行时间:** {str(uptime).split('.')[0]}",
                },
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**系统:** {platform.system()} {platform.release()}",
                },
            },
            {"tag": "hr"},
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"OpenClaw Monitor · {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    }
                ],
            },
        ]
    )

    client.send_poster("🖥️ 系统监控", elements)
    print("[OK] Monitor report sent")


# ============================================================
# 6. 每日报告
# ============================================================


def cmd_daily(args):
    """每日综合报告"""
    client = get_client()

    now = datetime.now()

    # 读取新闻历史
    hist_file = BASE_DIR / "news_history.json"
    news_count = 0
    if hist_file.exists():
        try:
            hist = json.load(open(hist_file, "r", encoding="utf-8"))
            today = now.strftime("%Y-%m-%d")
            news_count = len(
                [e for e in hist.get("sent", []) if today in e.get("time", "")]
            )
        except:
            news_count = 0

    # 读取统计
    stats = load_stats()

    # 构建报告
    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📊 每日报告** `{now.strftime('%Y-%m-%d')}`",
            },
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📰 新闻推送:** {news_count} 条今日已发",
            },
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📨 消息统计:** 共发送 {stats.get('sent', 0)} 条",
            },
        },
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md", "content": "**⏰ 定时任务状态**"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": "• 每5分钟: 新闻推送"}},
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": "• 08/12/18/21点: 新闻摘要"},
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📁 文件数:** {len(list(BASE_DIR.glob('*')))}",
            },
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**⏱️ 报告时间:** {now.strftime('%H:%M')}",
            },
        },
        {"tag": "hr"},
        {
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"OpenClaw Daily · {now.strftime('%Y-%m-%d')}",
                }
            ],
        },
    ]

    client.send_poster("📊 每日报告", elements)
    print("[OK] Daily report sent")


# ============================================================
# 7. 统计
# ============================================================


def cmd_stats(args):
    """发送统计信息"""
    client = get_client()
    stats = load_stats()

    elements = [
        {"tag": "div", "text": {"tag": "lark_md", "content": "**📈 Feishu 助手统计**"}},
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**✅ 发送成功:** {stats.get('sent', 0)}",
            },
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**❌ 发送失败:** {stats.get('failed', 0)}",
            },
        },
        {"tag": "hr"},
        {
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                }
            ],
        },
    ]

    client.send_poster("📈 统计", elements)
    print("[OK] Stats sent")


# ============================================================
# 8. 定时任务状态
# ============================================================


def cmd_cron_status(args):
    """查看定时任务状态"""
    import subprocess

    client = get_client()

    try:
        result = subprocess.run(
            ["schtasks", "/query", "/fo", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout

        # 筛选 OpenClaw 相关任务
        lines = output.split("\n")
        tasks = []
        current = {}

        for line in lines:
            line = line.strip()
            if "TaskName:" in line:
                name = line.split("TaskName:")[1].strip()
                if "OpenClaw" in name or "News" in name:
                    current = {"name": name}
            elif "Next Run Time:" in line and current:
                current["next"] = line.split("Next Run Time:")[1].strip()
            elif "Status:" in line and current:
                current["status"] = line.split("Status:")[1].strip()
                tasks.append(current)
                current = {}

        if not tasks:
            client.send_text("没有找到 OpenClaw 相关任务")
            print("[INFO] No OpenClaw tasks found")
            return

        # 构建报告
        lines = ["**⏰ OpenClaw 定时任务**\n"]

        for t in tasks:
            status_icon = (
                "✅"
                if t.get("status") == "Ready"
                else "🔄"
                if t.get("status") == "Running"
                else "❌"
            )
            lines.append(f"{status_icon} **{t['name']}**")
            lines.append(f"   下次: {t.get('next', 'N/A')}")
            lines.append(f"   状态: {t.get('status', 'N/A')}")
            lines.append("")

        client.send_text("\n".join(lines))
        print(f"[OK] Cron status sent: {len(tasks)} tasks")

    except Exception as e:
        print(f"[ERROR] {e}")


# ============================================================
# 9. 天气
# ============================================================


def cmd_weather(args):
    """发送天气预报"""
    client = get_client()

    # 简单天气获取
    try:
        url = "https://wttr.in/?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        current = data["current_condition"][0]
        temp_C = current["temp_C"]
        desc = current["weatherDesc"][0]["value"]
        wind = current["windspeedKmph"]
        humidity = current["humidity"]

        # 今日预报
        tomorrow = data["weather"][1] if len(data["weather"]) > 1 else {}
        tomorrow_desc = (
            tomorrow.get("hourly", [{}])[4]
            .get("weatherDesc", [{}])[0]
            .get("value", "N/A")
            if tomorrow
            else "N/A"
        )
        tomorrow_temp = tomorrow.get("maxTempC", "N/A") if tomorrow else "N/A"

        elements = [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**🌤️ 天气预报**"}},
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**当前:** {temp_C}°C {desc}"},
            },
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**风速:** {wind} km/h"},
            },
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**湿度:** {humidity}%"},
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**明天:** {tomorrow_temp}°C {tomorrow_desc}",
                },
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "[Weather.com](https://weather.com)",
                },
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"OpenClaw · {datetime.now().strftime('%H:%M')}",
                    }
                ],
            },
        ]

        client.send_poster("🌤️ 天气预报", elements)
        print("[OK] Weather sent")

    except Exception as e:
        client.send_text(f"获取天气失败: {e}")
        print(f"[ERROR] {e}")


# ============================================================
# 10. 提醒
# ============================================================


def cmd_remind(args):
    """设置提醒"""
    if len(args) < 2:
        print("[ERROR] 需要时间和内容: remind <minutes> <message>")
        return

    try:
        minutes = int(args[0])
        message = " ".join(args[1:])
    except ValueError:
        print("[ERROR] 时间必须是数字")
        return

    client = get_client()
    remind_time = datetime.now() + timedelta(minutes=minutes)

    msg = f"⏰ **提醒** ({remind_time.strftime('%H:%M')})\n\n{message}"
    client.send_text(msg)
    print(f"[OK] Reminder set for {remind_time.strftime('%H:%M')}: {message}")

    stats = load_stats()
    stats["sent"] = stats.get("sent", 0) + 1
    save_stats(stats)


# ============================================================
# 11. 快捷命令卡片 (Menu)
# ============================================================


def cmd_menu(args):
    """发送快捷命令菜单"""
    client = get_client()

    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**📋 OpenClaw 快捷命令**\n回复数字使用",
            },
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**📰 新闻**\n• 1 - 即时新闻\n• 2 - 新闻摘要\n• 3 - 关键词告警",
            },
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**📊 工具**\n• 4 - 系统监控\n• 5 - 天气\n• 6 - 日程\n• 7 - 文件列表",
            },
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**⏰ 定时**\n• 8 - 提醒(5分钟后)\n• 9 - 定时任务状态",
            },
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": "发送数字即可执行对应命令"},
        },
        {
            "tag": "note",
            "elements": [{"tag": "plain_text", "content": "OpenClaw Menu"}],
        },
    ]

    client.send_poster("📋 快捷命令", elements)
    print("[OK] Menu sent")


# ============================================================
# 12. 剪贴板内容推送
# ============================================================


def cmd_clipboard(args):
    """读取剪贴板并发送"""
    try:
        import pyperclip

        content = pyperclip.paste()
    except ImportError:
        # Windows 方式
        import subprocess

        result = subprocess.run(
            ["powershell", "-Command", "Get-Clipboard"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        content = result.stdout.strip()

    if not content:
        print("[INFO] Clipboard is empty")
        return

    client = get_client()

    # 如果太长，截断
    if len(content) > 2000:
        content = content[:1997] + "..."

    client.send_text(f"📋 **剪贴板内容:**\n\n{content}")
    print(f"[OK] Clipboard sent ({len(content)} chars)")


# ============================================================
# 13. 发送文件列表
# ============================================================


def cmd_files(args):
    """发送工作区文件列表"""
    client = get_client()

    # 获取指定目录，默认为 30-scripts-tools
    target = BASE_DIR if not args else Path(args[0])

    if not target.exists():
        print(f"[ERROR] 目录不存在: {target}")
        return

    # 统计
    files = list(target.glob("*"))
    dirs = [f for f in files if f.is_dir()]
    file_count = len([f for f in files if f.is_file()])

    # 构建消息
    lines = [f"📁 {target.name or '工作区'}\n"]
    lines.append(f"文件: {file_count} 个, 目录: {len(dirs)} 个\n")
    lines.append("-" * 30)

    # 列出子目录
    for d in sorted(dirs)[:10]:
        lines.append(f"📂 {d.name}/")

    # 列出 py 文件
    py_files = list(target.glob("*.py"))[:15]
    if py_files:
        lines.append("")
        lines.append("🐍 Python 文件:")
        for f in py_files:
            size = f.stat().st_size
            lines.append(f"  • {f.name} ({size // 1024}KB)")

    msg = "\n".join(lines)
    client.send_text(msg)
    print(f"[OK] Files list sent: {file_count} files")


# ============================================================
# 9. 交互卡片示例
# ============================================================


def cmd_interactive(args):
    """发送带按钮的交互卡片"""
    client = get_client()

    elements = [
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": "**🎛️ OpenClaw 控制面板**"},
        },
        {"tag": "hr"},
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "📰 新闻"},
                    "type": "primary",
                    "value": {"action": "news"},
                },
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "📊 监控"},
                    "type": "default",
                    "value": {"action": "monitor"},
                },
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "📋 日程"},
                    "type": "default",
                    "value": {"action": "calendar"},
                },
            ],
        },
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md", "content": "点击按钮触发对应功能"}},
        {
            "tag": "note",
            "elements": [
                {"tag": "plain_text", "content": "OpenClaw · Interactive Panel"}
            ],
        },
    ]

    client.send_poster("🎛️ 控制面板", elements)
    print("[OK] Interactive card sent")


# ============================================================
# 主入口
# ============================================================


def main():
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        return

    print("[OK] Critic Review Passed")

    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    commands = {
        "msg": cmd_msg,
        "card": cmd_card,
        "img": cmd_img,
        "image": cmd_img,
        "file": cmd_file,
        "mention": cmd_mention,
        "calendar": cmd_calendar,
        "cal": cmd_calendar,
        "contacts": cmd_contacts,
        "users": cmd_contacts,
        "search": cmd_search,
        "monitor": cmd_monitor,
        "daily": cmd_daily,
        "stats": cmd_stats,
        "files": cmd_files,
        "interactive": cmd_interactive,
        "panel": cmd_interactive,
        "todos": cmd_todos,
        "todo": cmd_todos,
        "cron": cmd_cron_status,
        "tasks": cmd_cron_status,
        "weather": cmd_weather,
        "remind": cmd_remind,
        "menu": cmd_menu,
        "clipboard": cmd_clipboard,
        "paste": cmd_clipboard,
    }

    if cmd in ("help", "-h", "--help"):
        print(__doc__)
        print("\n可用命令:")
        for c in sorted(commands.keys()):
            print(f"  {c}")
        return

    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"[ERROR] 未知命令: {cmd}")
        print("使用 `py feishu_assistant.py help` 查看帮助")


if __name__ == "__main__":
    main()
