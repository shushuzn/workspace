#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notification Center - Unified Notification Management
Features: Multi-channel (Feishu/Email/Console), templates, scheduling, priority

Usage:
    python notification_center.py --send "Task completed" --channel feishu
    python notification_center.py --template daily_brief
    python notification_center.py --schedule
    python notification_center.py --history
"""

import os
import sys
import json
import smtplib
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class Notification:
    """Notification record"""
    id: str
    channel: str  # feishu/email/console
    priority: str  # critical/high/normal/low
    title: str
    content: str
    sent_at: str
    status: str  # sent/failed/pending
    recipient: Optional[str] = None


@dataclass
class NotificationTemplate:
    """Notification template"""
    id: str
    name: str
    channel: str
    title_template: str
    content_template: str
    default_priority: str


class NotificationCenter:
    """Unified notification management"""
    
    def __init__(self):
        self.config_file = WORKSPACE / "30-scripts-tools" / "notification_config.json"
        self.history_file = WORKSPACE / "20-data-reports" / "notification_history.json"
        self.templates_dir = WORKSPACE / "30-scripts-tools" / "notification_templates"
        
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
        self.history = []
        self.templates = {}
        
        self.load_state()
        self._load_templates()
    
    def _load_config(self) -> Dict:
        """Load notification config"""
        default_config = {
            'feishu': {
                'enabled': True,
                'app_id': os.getenv('FEISHU_APP_ID', ''),
                'app_secret': os.getenv('FEISHU_APP_SECRET', ''),
                'webhook_url': os.getenv('FEISHU_WEBHOOK', ''),
            },
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': os.getenv('EMAIL_USERNAME', ''),
                'password': os.getenv('EMAIL_PASSWORD', ''),
                'from_address': '',
                'to_addresses': [],
            },
            'console': {
                'enabled': True,
                'color': True,
            },
            'defaults': {
                'channel': 'console',
                'priority': 'normal',
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key not in saved_config:
                        saved_config[key] = default_config[key]
                return saved_config
        
        return default_config
    
    def load_state(self):
        """Load notification history"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.history = data.get('history', [])
    
    def save_state(self):
        """Save notification history"""
        # Keep last 500 notifications
        self.history = self.history[-500:]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump({
                'history': self.history,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def _load_templates(self):
        """Load notification templates"""
        # Built-in templates
        self.templates = {
            'task_complete': NotificationTemplate(
                id='task_complete',
                name='Task Complete',
                channel='feishu',
                title_template='✅ Task Completed: {task_name}',
                content_template='Task **{task_name}** completed successfully.\n\nDuration: {duration}\nStatus: {status}',
                default_priority='normal'
            ),
            'task_failed': NotificationTemplate(
                id='task_failed',
                name='Task Failed',
                channel='feishu',
                title_template='❌ Task Failed: {task_name}',
                content_template='Task **{task_name}** failed.\n\nError: {error}\nTime: {time}',
                default_priority='high'
            ),
            'daily_brief': NotificationTemplate(
                id='daily_brief',
                name='Daily Brief',
                channel='feishu',
                title_template='📊 Daily Brief - {date}',
                content_template='**Daily Summary**\n\n'
                               '• Papers collected: {papers}\n'
                               '• Code analyzed: {code_files}\n'
                               '• Issues found: {issues}\n'
                               '• Optimizations: {optimizations}\n\n'
                               'Full report: {report_url}',
                default_priority='normal'
            ),
            'security_alert': NotificationTemplate(
                id='security_alert',
                name='Security Alert',
                channel='feishu',
                title_template='🚨 Security Alert',
                content_template='**Security Issue Detected**\n\n'
                               'Severity: {severity}\n'
                               'Type: {type}\n'
                               'Location: {location}\n\n'
                               'Action required: {action}',
                default_priority='critical'
            ),
            'system_health': NotificationTemplate(
                id='system_health',
                name='System Health',
                channel='console',
                title_template='💚 System Health: {status}',
                content_template='Health Score: {score}/100\n'
                               'Systems: {healthy}/{total} healthy\n'
                               'Alerts: {alerts}',
                default_priority='normal'
            ),
        }
        
        # Load custom templates from files
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    template = NotificationTemplate(**data)
                    self.templates[template.id] = template
            except:
                pass
    
    def send_feishu(self, title: str, content: str, priority: str = 'normal') -> bool:
        """Send Feishu notification"""
        if not self.config['feishu']['enabled']:
            print("⚠️  Feishu notifications disabled")
            return False
        
        try:
            # Import feishu tools
            feishu_tools_dir = WORKSPACE / "30-scripts-tools" / "feishu-tools"
            if feishu_tools_dir.exists():
                sys.path.insert(0, str(feishu_tools_dir))
                
                try:
                    from feishu_api import FeishuAPI
                    
                    api = FeishuAPI()
                    
                    # Replace emoji for console compatibility
                    console_title = title
                    console_content = content
                    
                    # Send
                    result = api.send_text(f"{console_title}\n\n{console_content}")
                    
                    if result:
                        print(f"✅ Feishu notification sent")
                        return True
                    else:
                        print(f"❌ Feishu notification failed")
                        return False
                
                except ImportError:
                    print("⚠️  Feishu API not available")
                    return False
            
            print("⚠️  Feishu tools directory not found")
            return False
        
        except Exception as e:
            print(f"❌ Feishu error: {e}")
            return False
    
    def send_email(self, title: str, content: str, priority: str = 'normal',
                   to_addresses: List[str] = None) -> bool:
        """Send email notification"""
        if not self.config['email']['enabled']:
            print("⚠️  Email notifications disabled")
            return False
        
        try:
            if not to_addresses:
                to_addresses = self.config['email'].get('to_addresses', [])
            
            if not to_addresses:
                print("❌ No recipient addresses configured")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['from_address']
            msg['To'] = ', '.join(to_addresses)
            msg['Subject'] = f"[{priority.upper()}] {title}"
            
            # Add priority header
            if priority == 'critical':
                msg['X-Priority'] = '1'
            elif priority == 'high':
                msg['X-Priority'] = '2'
            
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # Send
            server = smtplib.SMTP(
                self.config['email']['smtp_server'],
                self.config['email']['smtp_port']
            )
            server.starttls()
            server.login(
                self.config['email']['username'],
                self.config['email']['password']
            )
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent to {len(to_addresses)} recipients")
            return True
        
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
    
    def send_console(self, title: str, content: str, priority: str = 'normal'):
        """Send console notification"""
        if not self.config['console']['enabled']:
            return
        
        # Color codes
        colors = {
            'critical': '\033[91m',  # Red
            'high': '\033[93m',      # Yellow
            'normal': '\033[94m',    # Blue
            'low': '\033[92m',       # Green
        }
        reset = '\033[0m'
        
        if self.config['console']['color']:
            color = colors.get(priority, '')
            print(f"\n{color}{'='*60}")
            print(f" {title}")
            print(f"{'='*60}{reset}")
            print(f" {content}\n")
        else:
            print(f"\n{'='*60}")
            print(f" {title}")
            print(f"{'='*60}")
            print(f" {content}\n")
    
    def send(self, title: str, content: str, channel: str = None,
             priority: str = None, recipient: str = None) -> Notification:
        """Send notification through specified channel"""
        
        # Use defaults if not specified
        if not channel:
            channel = self.config['defaults']['channel']
        if not priority:
            priority = self.config['defaults']['priority']
        
        # Generate ID
        notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(title.encode()).hexdigest()[:8]}"
        
        # Create notification record
        notification = Notification(
            id=notification_id,
            channel=channel,
            priority=priority,
            title=title,
            content=content,
            sent_at=datetime.now().isoformat(),
            status='pending',
            recipient=recipient
        )
        
        # Send through channel
        success = False
        
        if channel == 'feishu':
            success = self.send_feishu(title, content, priority)
        elif channel == 'email':
            success = self.send_email(title, content, priority, [recipient] if recipient else None)
        elif channel == 'console':
            self.send_console(title, content, priority)
            success = True
        else:
            print(f"⚠️  Unknown channel: {channel}")
        
        # Update status
        notification.status = 'sent' if success else 'failed'
        
        # Record to history
        self.history.append(asdict(notification))
        self.save_state()
        
        return notification
    
    def send_from_template(self, template_id: str, **kwargs) -> Notification:
        """Send notification from template"""
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self.templates[template_id]
        
        # Render templates
        title = template.title_template.format(**kwargs)
        content = template.content_template.format(**kwargs)
        
        return self.send(
            title=title,
            content=content,
            channel=template.channel,
            priority=template.default_priority
        )
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get notification history"""
        return self.history[-limit:]
    
    def get_statistics(self) -> Dict:
        """Get notification statistics"""
        by_channel = {}
        by_priority = {}
        by_status = {}
        
        for notif in self.history:
            channel = notif['channel']
            priority = notif['priority']
            status = notif['status']
            
            by_channel[channel] = by_channel.get(channel, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            'total': len(self.history),
            'by_channel': by_channel,
            'by_priority': by_priority,
            'by_status': by_status,
            'success_rate': by_status.get('sent', 0) / len(self.history) * 100 if self.history else 0
        }
    
    def list_templates(self) -> List[Dict]:
        """List available templates"""
        return [
            {
                'id': t.id,
                'name': t.name,
                'channel': t.channel,
                'priority': t.default_priority
            }
            for t in self.templates.values()
        ]
    
    def save_template(self, template: NotificationTemplate):
        """Save custom template"""
        filepath = self.templates_dir / f"{template.id}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(template), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Template saved: {filepath}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Notification Center')
    parser.add_argument('--send', type=str, help='Send notification')
    parser.add_argument('--channel', type=str, choices=['feishu', 'email', 'console'],
                       help='Notification channel')
    parser.add_argument('--priority', type=str, choices=['critical', 'high', 'normal', 'low'],
                       help='Notification priority')
    parser.add_argument('--template', type=str, help='Send from template')
    parser.add_argument('--template-var', nargs='+', help='Template variables (key=value)')
    parser.add_argument('--history', action='store_true', help='Show history')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--templates', action='store_true', help='List templates')
    args = parser.parse_args()
    
    center = NotificationCenter()
    
    if args.send:
        # Parse template variables
        kwargs = {}
        if args.template_var:
            for var in args.template_var:
                if '=' in var:
                    key, value = var.split('=', 1)
                    kwargs[key] = value
        
        if args.template:
            notification = center.send_from_template(args.template, **kwargs)
        else:
            notification = center.send(
                title='Notification',
                content=args.send,
                channel=args.channel,
                priority=args.priority
            )
        
        print(f"\nNotification sent: {notification.status}")
    
    elif args.history:
        history = center.get_history()
        print("\nNotification History:\n")
        for notif in history[-10:][::-1]:
            print(f"  [{notif['status']}] {notif['title']}")
            print(f"    Channel: {notif['channel']} | Priority: {notif['priority']}")
            print(f"    Time: {notif['sent_at'][:19]}\n")
    
    elif args.stats:
        stats = center.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.templates:
        templates = center.list_templates()
        print("\nAvailable Templates:\n")
        for t in templates:
            print(f"  • {t['id']}: {t['name']}")
            print(f"    Channel: {t['channel']} | Priority: {t['priority']}\n")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
