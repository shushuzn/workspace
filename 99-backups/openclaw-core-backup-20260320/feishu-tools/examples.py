#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu API Examples - OpenClaw Integration
===========================================
Demonstrates common use cases for the Feishu API client.

Run examples:
    python examples.py all         # Run all examples
    python examples.py text        # Text message only
    python examples.py card        # Card message only
    python examples.py token       # Token info only
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from feishu_api import FeishuAPIClient


def example_text_message():
    """Example: Send simple text message."""
    print("\n" + "=" *50)
    print("Example 1: Text Message")
    print("=" *50)

    client = FeishuAPIClient()

    # Simple text
    client.send_text("🐾 Hello from OpenClaw!\n\nThis is an automated test message.")

    # Text with formatting (Feishu supports markdown-like syntax)
    client.send_text("""**Bold Text**
*Italic Text*
- List item 1
- List item 2
- List item 3

[Link](https://open.feishu.cn/)
""")


def example_card_message():
    """Example: Send interactive card message."""
    print("\n" + "=" *50)
    print("Example 2: Card Message")
    print("=" *50)

    client = FeishuAPIClient()

    # Task completion notification
    title = "✅ Task Completed"
    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Task:** Data Processing\n**Status:** Success\n**Duration:** 5 minutes"
            }
        },
        {
            "tag": "hr"
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Session ID:** 6d929252\n**Files Processed:** 10\n**Errors:** 0"
            }
        },
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "View Details"
                    },
                    "url": "http://8.208.30.28:3000",
                    "type": "primary"
                }
            ]
        }
    ]

    client.send_poster(title, elements)


def example_alert_message():
    """Example: Send alert/warning message."""
    print("\n" + "=" *50)
    print("Example 3: Alert Message")
    print("=" *50)

    client = FeishuAPIClient()

    title = "⚠️ System Alert"
    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Alert Type:** High CPU Usage\n**Server:** OpenClaw-fipq\n**Current:** 85%\n**Threshold:** 80%"
            }
        },
        {
            "tag": "hr"
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Recommended Action:**\n1. Check running processes\n2. Review recent deployments\n3. Scale if necessary"
            }
        },
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "View Metrics"
                    },
                    "url": "http://8.208.30.28:8443",
                    "type": "danger"
                },
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "Dismiss"
                    },
                    "type": "default"
                }
            ]
        }
    ]

    client.send_poster(title, elements)


def example_daily_report():
    """Example: Send daily report."""
    print("\n" + "=" *50)
    print("Example 4: Daily Report")
    print("=" *50)

    client = FeishuAPIClient()

    title = "📊 Daily Report - 2026-03-14"
    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Summary:**\n✅ All systems operational\n✅ 20+ tasks completed\n✅ 0 critical errors"
            }
        },
        {
            "tag": "hr"
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Metrics:**\n- Git Commits: 20+\n- Files Created: 100+\n- API Calls: 50+\n- Uptime: 99.9%"
            }
        },
        {
            "tag": "hr"
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Next Steps:**\n1. Memory distillation (5AM)\n2. Web console enhancement\n3. Performance optimization"
            }
        }
    ]

    client.send_poster(title, elements)


def example_token_management():
    """Example: Token management."""
    print("\n" + "=" *50)
    print("Example 5: Token Management")
    print("=" *50)

    client = FeishuAPIClient()

    # Get token info
    info = client.get_token_info()

    print("\nToken Information:")
    print(f"  Status: {info['status']}")
    if info['status'] != 'no_token':
        print(f"  Token: {info['token_preview']}")
        print(f"  Expires: {info['expires_at']}")
        print(f"  Time Left: {info['time_left_formatted']}")
    print()


def example_batch_messages():
    """Example: Send batch messages to multiple users."""
    print("\n" + "=" *50)
    print("Example 6: Batch Messages")
    print("=" *50)

    client = FeishuAPIClient()

    # Multiple recipients (example - use real user IDs)
    recipients = [
        "ou_72a847b95fc25870dcdd8ce56d929252",
        # Add more user IDs here
    ]

    message = "📢 Broadcast: System maintenance scheduled for 2026-03-15 02:00-04:00"

    for user_id in recipients:
        try:
            client.send_text(message, receive_id=user_id)
            print(f"✓ Sent to {user_id}")
        except Exception as e:
            print(f"✗ Failed for {user_id}: {e}")


def main():
    """Run examples based on command line argument."""
    if len(sys.argv) < 2:
        print("Usage: python examples.py <example_name>")
        print("Examples: all, text, card, alert, report, token, batch")
        sys.exit(1)

    example_name = sys.argv[1].lower()

    examples = {
        'all': [
            example_token_management,
            example_text_message,
            example_card_message,
            example_alert_message,
            example_daily_report,
        ],
        'text': [example_text_message],
        'card': [example_card_message],
        'alert': [example_alert_message],
        'report': [example_daily_report],
        'token': [example_token_management],
        'batch': [example_batch_messages],
    }

    if example_name not in examples:
        print(f"Unknown example: {example_name}")
        print(f"Available: {', '.join(examples.keys())}")
        sys.exit(1)

    print("\n" + "=" *50)
    print("Feishu API Examples - OpenClaw")
    print("=" *50)

    selected_examples = examples[example_name]

    for example_func in selected_examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n[✗] Example failed: {e}")
            print("Continue with next example...\n")

    print("\n" + "=" *50)
    print("Examples Complete!")
    print("=" *50 + "\n")


if __name__ == "__main__":
    main()
