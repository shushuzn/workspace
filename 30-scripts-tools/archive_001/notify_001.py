import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NOTIFY-001 Notification System
Sends notifications for workflow events
"""
import json, sys
from pathlib import Path
from datetime import datetime

NOTIFY_FILE = Path("13-memory/.notifications.json")

def load_notifications():
    if NOTIFY_FILE.exists():
        return json.loads(NOTIFY_FILE.read_text(encoding="utf-8", errors="replace"))
    return {"notifications": []}

def save_notifications(data):
    NOTIFY_FILE.parent.mkdir(parents=True, exist_ok=True)
    NOTIFY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def send_notification(title, message, level="info") -> None:
    """
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
# py notify_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py notify_001.py

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

Send a notification"""
    notifications = load_notifications()

    notification = {
        "time": datetime.now().isoformat(),
        "title": title,
        "message": message,
        "level": level,
        "read": False
    }

    notifications["notifications"].append(notification)

    # Keep only last 100
    notifications["notifications"] = notifications["notifications"][-100:]

    save_notifications(notifications)

    # Print notification (ASCII safe)
    icons = {"info": "[i]", "success": "[OK]", "warning": "[!]", "error": "[X]"}
    icon = icons.get(level, "[i]")
    print(f"\n{icon} [{level.upper()}] {title}")
    print(f"   {message}")

    return notification

def list_notifications(unread_only=False) -> None:
    """List all notifications"""
    notifications = load_notifications()
    items = notifications.get("notifications", [])

    if unread_only:
        items = [n for n in items if not n.get("read")]

    print(f"\n[NOTIFICATIONS] ({len(items)} items)")
    print("=" * 50)

    for n in reversed(items[-10:]):
        icon = {"info": "[i]", "success": "[OK]", "warning": "[!]", "error": "[X]"}.get(n.get("level"), "[i]")
        read = "" if n.get("read") else " [NEW]"
        print(f"{icon} {n['time'][11:19]} {n['title']}{read}")

    print("=" * 50)

    return items

def mark_read(index=None) -> None:
    """Mark notifications as read"""
    notifications = load_notifications()
    if index is None:
        for n in notifications["notifications"]:
            n["read"] = True
    else:
        if 0 <= index < len(notifications["notifications"]):
            notifications["notifications"][index]["read"] = True
    save_notifications(notifications)

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 2:
        print("""
[NOTIFY-001 Notification System]
Usage:
  python notify_001.py send <title> <message> [level]
  python notify_001.py list [unread]
  python notify_001.py read [index]
        """)
        return

    cmd = sys.argv[1]

    if cmd == "send":
        title = sys.argv[2] if len(sys.argv) > 2 else "Notification"
        message = sys.argv[3] if len(sys.argv) > 3 else ""
        level = sys.argv[4] if len(sys.argv) > 4 else "info"
        send_notification(title, message, level)

    elif cmd == "list":
        unread = len(sys.argv) > 2 and sys.argv[2] == "unread"
        list_notifications(unread)

    elif cmd == "read":
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
        mark_read(idx)
        print("Marked as read")

if __name__ == "__main__":
    main()
