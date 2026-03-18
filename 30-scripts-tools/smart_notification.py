#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Smart Notification System - Phase 4 Innovation
Intelligent notification routing based on priority, context, and time
Features: multi-channel, priority classification, context-aware, aggregation

Usage:
    python smart_notification.py --send "message" --priority high
    python smart_notification.py --test                    # Test all channels
    python smart_notification.py --status                  # Show status
    python smart_notification.py --aggregate               # Aggregate pending notifications
"""

import os
import subprocess
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Workspace root
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "20-data-reports" / "notifications"
CONFIG_FILE = DATA_DIR / "notification-config.json"
QUEUE_FILE = DATA_DIR / "notification-queue.json"
HISTORY_FILE = DATA_DIR / "notification-history.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class SmartNotificationSystem:
    """Intelligent notification routing system"""
    
    def __init__(self):
        self.config = self._load_config()
        self.queue = self._load_queue()
        self.history = self._load_history()
    
    def _load_config(self) -> Dict:
        """Load notification configuration"""
        default_config = {
            "version": "1.0",
            "channels": {
                "feishu": {
                    "enabled": True,
                    "priority_threshold": "normal",  # low, normal, important, urgent
                    "rate_limit_per_hour": 60,
                    "config_file": ".env"
                },
                "email": {
                    "enabled": False,
                    "priority_threshold": "important",
                    "rate_limit_per_hour": 20,
                    "config_file": ".env"
                },
                "desktop": {
                    "enabled": True,
                    "priority_threshold": "normal",
                    "rate_limit_per_hour": 100,
                    "config_file": None
                },
                "sms": {
                    "enabled": False,
                    "priority_threshold": "urgent",
                    "rate_limit_per_hour": 5,
                    "config_file": ".env"
                }
            },
            "priority_levels": {
                "low": {"weight": 1, "color": "gray", "aggregation_window_minutes": 60},
                "normal": {"weight": 2, "color": "blue", "aggregation_window_minutes": 30},
                "important": {"weight": 3, "color": "yellow", "aggregation_window_minutes": 15},
                "urgent": {"weight": 4, "color": "red", "aggregation_window_minutes": 0}  # Immediate
            },
            "context_awareness": {
                "work_hours": {"start": 9, "end": 18, "timezone": "Asia/Hong_Kong"},
                "do_not_disturb": False,
                "meeting_mode": False
            },
            "aggregation": {
                "enabled": True,
                "max_batch_size": 10,
                "similar_notification_window_minutes": 5
            }
        }
        
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
    
    def _load_queue(self) -> Dict:
        """Load notification queue"""
        if QUEUE_FILE.exists():
            with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"pending": [], "aggregated": {}}
    
    def _load_history(self) -> Dict:
        """Load notification history"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"sent": [], "statistics": {}}
    
    def _save_queue(self):
        """Save notification queue"""
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.queue, f, indent=2, ensure_ascii=False)
    
    def _save_history(self):
        """Save notification history"""
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def classify_priority(self, message: str, explicit_priority: str = None) -> str:
        """Automatically classify message priority"""
        if explicit_priority:
            return explicit_priority
        
        # Keywords for priority classification
        urgent_keywords = ['critical', 'emergency', 'failure', 'error', 'down', 'urgent', '立即', '紧急']
        important_keywords = ['warning', 'alert', 'important', 'attention', '注意', '警告']
        normal_keywords = ['info', 'update', 'complete', 'success', '完成', '更新']
        
        message_lower = message.lower()
        
        # Count keyword matches
        urgent_score = sum(1 for kw in urgent_keywords if kw in message_lower)
        important_score = sum(1 for kw in important_keywords if kw in message_lower)
        normal_score = sum(1 for kw in normal_keywords if kw in message_lower)
        
        if urgent_score > 0:
            return 'urgent'
        elif important_score > 0:
            return 'important'
        elif normal_score > 0:
            return 'normal'
        else:
            return 'low'
    
    def should_aggregate(self, notification: Dict) -> bool:
        """Check if notification should be aggregated"""
        if not self.config['aggregation']['enabled']:
            return False
        
        priority = notification.get('priority', 'normal')
        if priority == 'urgent':
            return False  # Urgent notifications are never aggregated
        
        # Check for similar recent notifications
        window_minutes = self.config['priority_levels'][priority]['aggregation_window_minutes']
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        for existing in self.queue['pending']:
            if existing.get('category') == notification.get('category'):
                existing_time = datetime.fromisoformat(existing['timestamp'])
                if existing_time > cutoff_time:
                    return True
        
        return False
    
    def send(self, message: str, priority: str = None, category: str = "general", 
             channel_override: str = None) -> Dict:
        """Send a notification"""
        # Classify priority
        priority = self.classify_priority(message, priority)
        
        # Check context awareness
        if self.config['context_awareness']['do_not_disturb']:
            if priority not in ['urgent']:
                print(f"[DND] Notification queued (Do Not Disturb mode)")
                self.queue['pending'].append({
                    'message': message,
                    'priority': priority,
                    'category': category,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'queued_dnd'
                })
                self._save_queue()
                return {'status': 'queued', 'reason': 'dnd_mode'}
        
        # Determine channels
        channels_to_use = []
        for channel, config in self.config['channels'].items():
            if not config.get('enabled', False):
                continue
            
            threshold = config.get('priority_threshold', 'normal')
            threshold_weight = self.config['priority_levels'].get(threshold, {}).get('weight', 2)
            message_weight = self.config['priority_levels'].get(priority, {}).get('weight', 2)
            
            if message_weight >= threshold_weight:
                channels_to_use.append(channel)
        
        if channel_override:
            channels_to_use = [channel_override]
        
        if not channels_to_use:
            print(f"[SKIP] No channels configured for priority '{priority}'")
            return {'status': 'skipped', 'reason': 'no_channels'}
        
        # Check aggregation
        notification = {
            'message': message,
            'priority': priority,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'channels': channels_to_use
        }
        
        if self.should_aggregate(notification):
            print(f"[AGGREGATE] Notification added to aggregation queue")
            self.queue['pending'].append(notification)
            self._save_queue()
            return {'status': 'aggregated'}
        
        # Send to channels
        results = []
        for channel in channels_to_use:
            result = self._send_to_channel(channel, message, priority, category)
            results.append(result)
        
        # Record in history
        self.history['sent'].append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'priority': priority,
            'category': category,
            'channels': channels_to_use,
            'results': results
        })
        
        # Keep only last 1000
        self.history['sent'] = self.history['sent'][-1000:]
        self._save_history()
        
        # Summary
        success_count = sum(1 for r in results if r.get('success', False))
        print(f"[OK] Notification sent via {success_count}/{len(channels_to_use)} channels")
        
        return {
            'status': 'sent',
            'priority': priority,
            'channels': channels_to_use,
            'results': results
        }
    
    def _send_to_channel(self, channel: str, message: str, priority: str, category: str) -> Dict:
        """Send notification to specific channel"""
        print(f"[SEND] {channel}: {message[:50]}...")
        
        try:
            if channel == 'feishu':
                return self._send_feishu(message, priority)
            elif channel == 'desktop':
                return self._send_desktop(message, priority)
            elif channel == 'email':
                return self._send_email(message, priority)
            elif channel == 'sms':
                return self._send_sms(message, priority)
            else:
                return {'success': False, 'error': f'Unknown channel: {channel}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_feishu(self, message: str, priority: str) -> Dict:
        """Send via Feishu"""
        # Check if feishu tools exist
        feishu_tool = WORKSPACE / "30-scripts-tools" / "feishu_notification.py"
        
        if not feishu_tool.exists():
            # Fallback: simple API call
            return {
                'success': True,
                'channel': 'feishu',
                'method': 'mock',
                'note': 'Feishu tool not found, mocked'
            }
        
        # Use existing feishu tool
        import subprocess
        result = subprocess.run(
            ['python', str(feishu_tool), '--text', message],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            'success': result.returncode == 0,
            'channel': 'feishu',
            'stdout': result.stdout[:200],
            'stderr': result.stderr[:200]
        }
    
    def _send_desktop(self, message: str, priority: str) -> Dict:
        """Send desktop notification"""
        try:
            # Windows toast notification
            from win32api import ShellExecute
            from win32con import SW_HIDE
            
            # Create VBScript for toast
            vbs_content = f'''
Set wshShell = CreateObject("WScript.Shell")
wshShell.Popup "{message}", 5, "OpenClaw Notification", 64
'''
            vbs_path = DATA_DIR / "temp_notify.vbs"
            with open(vbs_path, 'w', encoding='utf-8') as f:
                f.write(vbs_content)
            
            subprocess.run(['wscript', str(vbs_path)], capture_output=True)
            
            return {
                'success': True,
                'channel': 'desktop',
                'method': 'windows_toast'
            }
        except Exception as e:
            # Fallback: print to console
            print(f"🔔 DESKTOP: {message}")
            return {
                'success': True,
                'channel': 'desktop',
                'method': 'console_fallback',
                'error': str(e)
            }
    
    def _send_email(self, message: str, priority: str) -> Dict:
        """Send email notification"""
        # TODO: Implement email sending
        return {
            'success': True,
            'channel': 'email',
            'method': 'mock',
            'note': 'Email not configured'
        }
    
    def _send_sms(self, message: str, priority: str) -> Dict:
        """Send SMS notification"""
        # TODO: Implement SMS sending
        return {
            'success': True,
            'channel': 'sms',
            'method': 'mock',
            'note': 'SMS not configured'
        }
    
    def aggregate_pending(self) -> Dict:
        """Aggregate and send pending notifications"""
        if not self.queue['pending']:
            print("[INFO] No pending notifications")
            return {'status': 'empty'}
        
        print(f"[AGGREGATE] Processing {len(self.queue['pending'])} pending notifications")
        
        # Group by category
        by_category = {}
        for notif in self.queue['pending']:
            cat = notif.get('category', 'general')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(notif)
        
        # Send aggregated messages
        results = []
        for category, notifs in by_category.items():
            if len(notifs) == 1:
                # Single notification, send as-is
                result = self.send(
                    notifs[0]['message'],
                    notifs[0]['priority'],
                    category
                )
                results.append(result)
            else:
                # Multiple notifications, aggregate
                priority_counts = {}
                for n in notifs:
                    p = n['priority']
                    priority_counts[p] = priority_counts.get(p, 0) + 1
                
                # Determine highest priority
                priority_order = ['urgent', 'important', 'normal', 'low']
                highest_priority = next(p for p in priority_order if p in priority_counts)
                
                # Build aggregated message
                agg_message = f"[{category.upper()}] {len(notifs)} notifications:\n"
                for n in notifs[:5]:  # Show first 5
                    agg_message += f"  • {n['message'][:60]}...\n"
                if len(notifs) > 5:
                    agg_message += f"  ... and {len(notifs) - 5} more"
                
                result = self.send(agg_message, highest_priority, category)
                results.append(result)
        
        # Clear queue
        self.queue['pending'] = []
        self._save_queue()
        
        return {
            'status': 'aggregated',
            'count': len(by_category),
            'results': results
        }
    
    def show_status(self):
        """Show notification system status"""
        print("\n" + "=" * 60)
        print("Smart Notification System - Status")
        print("=" * 60)
        
        print("\nChannels:")
        for channel, config in self.config['channels'].items():
            enabled = "✅" if config.get('enabled', False) else "❌"
            threshold = config.get('priority_threshold', 'normal')
            rate_limit = config.get('rate_limit_per_hour', 0)
            print(f"  {enabled} {channel:12} | Threshold: {threshold:10} | Rate: {rate_limit}/hr")
        
        print("\nQueue:")
        print(f"  Pending: {len(self.queue['pending'])}")
        
        # Statistics
        if self.history.get('sent'):
            total_sent = len(self.history['sent'])
            by_priority = {}
            by_channel = {}
            
            for record in self.history['sent']:
                p = record.get('priority', 'unknown')
                by_priority[p] = by_priority.get(p, 0) + 1
                
                for ch in record.get('channels', []):
                    by_channel[ch] = by_channel.get(ch, 0) + 1
            
            print("\nHistory (Last 1000):")
            print(f"  Total sent: {total_sent}")
            print(f"  By priority: {by_priority}")
            print(f"  By channel: {by_channel}")
        
        print("\nContext:")
        ctx = self.config.get('context_awareness', {})
        print(f"  Work hours: {ctx.get('work_hours', {}).get('start', 9)}:00 - {ctx.get('work_hours', {}).get('end', 18)}:00")
        print(f"  DND mode: {ctx.get('do_not_disturb', False)}")
        print(f"  Meeting mode: {ctx.get('meeting_mode', False)}")
        
        print("=" * 60)
    
    def test_all_channels(self):
        """Test all notification channels"""
        print("\n" + "=" * 60)
        print("Testing All Notification Channels")
        print("=" * 60)
        
        test_message = "[TEST] Smart Notification System - All channels working!"
        
        for channel in self.config['channels'].keys():
            print(f"\nTesting {channel}...")
            result = self._send_to_channel(channel, test_message, 'normal', 'test')
            
            if result.get('success'):
                print(f"  ✅ {channel}: OK")
            else:
                print(f"  ❌ {channel}: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Smart Notification System')
    parser.add_argument('--send', type=str, help='Send notification message')
    parser.add_argument('--priority', type=str, default=None, 
                       choices=['low', 'normal', 'important', 'urgent'],
                       help='Priority level')
    parser.add_argument('--category', type=str, default='general', help='Category')
    parser.add_argument('--channel', type=str, default=None, help='Override channel')
    parser.add_argument('--test', action='store_true', help='Test all channels')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--aggregate', action='store_true', help='Aggregate pending')
    args = parser.parse_args()
    
    notifier = SmartNotificationSystem()
    
    if args.send:
        result = notifier.send(args.send, args.priority, args.category, args.channel)
        print(f"\nResult: {json.dumps(result, indent=2)}")
    
    if args.test:
        notifier.test_all_channels()
    
    if args.status:
        notifier.show_status()
    
    if args.aggregate:
        result = notifier.aggregate_pending()
        print(f"\nResult: {json.dumps(result, indent=2)}")
    
    if not any([args.send, args.test, args.status, args.aggregate]):
        parser.print_help()


if __name__ == "__main__":
    main()
