#!/usr/bin/env python3
"""
Cron Notification Script - Feishu Integration

Send notifications for scheduled tasks

Usage:
    python cron-notify.py <task_name> <status> [message]
    
Example:
    python cron-notify.py "Memory Distillation" "success" "Completed, 5 insights added"
    python cron-notify.py "Server Check" "error" "SSH connection failed"
"""

import sys
import os
import json
from datetime import datetime

# Add tools path
sys.path.insert(0, r'D:\OpenClaw\workspace\30-scripts-tools\feishu-tools')

try:
    from feishu_api import send_text, send_card
except ImportError:
    print("Feishu tools not found, using fallback")
    def send_text(text):
        print(f"[FEISHU] {text}")
        return True

def send_cron_notification(task_name, status, message=""):
    """Send cron task notification"""
    
    # Status emoji
    status_emoji = {
        'success': '[OK]',
        'error': '[ERROR]',
        'warning': '[WARN]',
        'info': '[INFO]'
    }
    
    emoji = status_emoji.get(status.lower(), '[INFO]')
    
    # Format message
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text = f"{emoji} Cron Task Notification\n\n"
    text += f"Task: {task_name}\n"
    text += f"Status: {status.upper()}\n"
    text += f"Time: {timestamp}\n"
    
    if message:
        text += f"\nDetails: {message}"
    
    # Send notification
    print(f"Sending notification: {task_name} - {status}")
    result = send_text(text)
    
    if result:
        print("Notification sent successfully")
        return True
    else:
        print("Failed to send notification")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python cron-notify.py <task_name> <status> [message]")
        print("Status: success, error, warning, info")
        sys.exit(1)
    
    task_name = sys.argv[1]
    status = sys.argv[2]
    message = sys.argv[3] if len(sys.argv) > 3 else ""
    
    success = send_cron_notification(task_name, status, message)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
