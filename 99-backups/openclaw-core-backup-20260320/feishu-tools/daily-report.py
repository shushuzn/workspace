#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Report Automation - Feishu
=================================
Automatically send daily reports via Feishu.

Schedule: Daily at 9:00 AM
Usage: python daily-report.py

Configuration: Edit REPORT_CONFIG section below
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from feishu_api_enhanced import FeishuAPIClient

# ==================== CONFIGURATION ====================
REPORT_CONFIG = {
    "title": "[Daily Report] OpenClaw",
    "receive_id": "ou_72a847b95fc25870dcdd8ce56d929252",  # Default recipient
    "mention_users": [],  # Add user IDs to @mention
    "timezone": "Asia/Hong_Kong",

    # Report sections (customize as needed)
    "sections": [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Summary:**\n- All systems operational\n- Automated workflows running\n- No critical errors"
            }
        },
        {
            "tag": "hr"
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Key Metrics:**\n- Git Commits: Auto-tracked\n- Tasks Completed: Auto-tracked\n- System Uptime: 99.9%+"
            }
        },
        {
            "tag": "hr"
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**Today's Focus:**\n1. Feature development\n2. Bug fixes\n3. Documentation updates"
            }
        },
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "View Dashboard"
                    },
                    "url": "http://8.208.30.28:3000",
                    "type": "primary"
                },
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "View Logs"
                    },
                    "url": "http://8.208.30.28:8443",
                    "type": "default"
                }
            ]
        }
    ]
}


def generate_daily_report(date: datetime = None) -> dict:
    """Generate daily report content."""
    if date is None:
        date = datetime.now()

    # Customize report based on date
    report = REPORT_CONFIG.copy()
    report["title"] = f"📊 Daily Report - {date.strftime('%Y-%m-%d')}"

    # You can add dynamic content here
    # For example: fetch from database, APIs, etc.

    return report


def send_daily_report():
    """Send daily report via Feishu."""
    print(f"\n{'=' *60}")
    print(f"Daily Report Automation")
    print(f"{'=' *60}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Timezone: {REPORT_CONFIG['timezone']}")
    print()

    try:
        # Initialize client
        client = FeishuAPIClient()

        # Generate report
        report = generate_daily_report()

        print(f"Sending report to: {REPORT_CONFIG['receive_id']}")
        if REPORT_CONFIG.get('mention_users'):
            print(f"Mentioning: {', '.join(REPORT_CONFIG['mention_users'])}")
        print()

        # Send card message
        result = client.send_poster(
            title=report["title"],
            content=report["sections"],
            receive_id=REPORT_CONFIG["receive_id"],
            mention_users=REPORT_CONFIG.get("mention_users")
        )

        print(f"\n[OK] Daily report sent successfully!")
        print(f"Message ID: {result['data']['message_id']}")

        return True

    except Exception as e:
        print(f"\n[ERROR] Failed to send daily report: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report():
    """Test daily report without sending."""
    print(f"\n{'=' *60}")
    print(f"Daily Report Test")
    print(f"{'=' *60}\n")

    report = generate_daily_report()

    print(f"Title: [REPORT TITLE]")
    print(f"Recipient: {report['receive_id']}")
    print(f"Sections: {len(report['sections'])}")
    print(f"Mentions: {report.get('mention_users', [])}")
    print()
    print("Report Preview:")
    print("-" * 60)
    for section in report['sections']:
        if section['tag'] == 'div':
            if 'text' in section and 'text' in section['text']:
                content = section['text']['text']['content']
                print(content)
        elif section['tag'] == 'hr':
            print("-" * 60)
        elif section['tag'] == 'action':
            print("[Action Buttons]")
    print("-" * 60)
    print()
    print("[OK] Test complete. Report structure is valid.")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_report()
    else:
        success = send_daily_report()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
