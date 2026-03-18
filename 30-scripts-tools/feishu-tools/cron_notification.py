#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cron Task Notification Hook for Feishu

Usage:
    python cron_notification.py <task_name> <status> [message]
    
Examples:
    python cron_notification.py "7AM Risk Warning" "success" "All checks passed"
    python cron_notification.py "Memory Distillation" "failed" "Error: timeout"
"""

import sys
import json
import os
from datetime import datetime
from feishu_api import FeishuAPIClient

def get_task_emoji(status):
    """Get emoji based on task status"""
    emojis = {
        "success": "✅",
        "failed": "❌",
        "warning": "⚠️",
        "running": "⏳",
        "skipped": "⭕"
    }
    return emojis.get(status.lower(), "📋")

def create_notification_card(task_name, status, message, timestamp=None):
    """Create a formatted notification card"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    emoji = get_task_emoji(status)
    status_color = {
        "success": "green",
        "failed": "red",
        "warning": "orange",
        "running": "blue",
        "skipped": "gray"
    }.get(status.lower(), "gray")
    
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "template": status_color,
            "title": {
                "tag": "plain_text",
                "content": f"{emoji} 定时任务通知 | Cron Task Notification"
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**任务名称 | Task Name:**\n{task_name}"
                }
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**状态 | Status:**\n{emoji} {status.upper()}"
                }
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**执行时间 | Executed:**\n{timestamp}"
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**详情 | Details:**\n{message}"
                }
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "🐾 Claw AI Agent - OpenClaw Workspace"
                    }
                ]
            }
        ]
    }
    
    return card

def send_notification(task_name, status, message, config_file=None):
    """Send notification to Feishu"""
    # Load config
    if config_file is None:
        config_file = os.path.join(os.path.dirname(__file__), "feishu-config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Initialize client (loads config automatically)
    client = FeishuAPIClient(config_file=config_file)
    
    # Create card elements for send_poster
    card = create_notification_card(task_name, status, message)
    title = card['header']['title']['content']
    elements = card['elements']
    
    try:
        result = client.send_poster(
            title=title,
            content=elements,
            receive_id=config['default_receive_id']
        )
        
        print(f"[OK] Notification sent: {result.get('message_id', 'unknown')}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send notification: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print(f"\nCurrent args: {sys.argv}")
        sys.exit(1)
    
    task_name = sys.argv[1]
    status = sys.argv[2]
    message = sys.argv[3] if len(sys.argv) > 3 else "No additional details"
    
    success = send_notification(task_name, status, message)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
