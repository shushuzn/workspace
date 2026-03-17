#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Feishu Notification Smart Router
Intelligent notification routing with priority queue

Usage:
    python notification_router.py [--send MESSAGE] [--priority PRIORITY] [--queue]
"""

import sys
import json
from datetime import datetime, time
from pathlib import Path
from collections import deque

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class NotificationRouter:
    """Route notifications intelligently"""
    
    def __init__(self, config_file: str = None):
        self.config_file = Path(config_file) if config_file else Path(__file__).parent / 'notification_config.json'
        self.config = self._load_config()
        self.queue = PriorityNotificationQueue()
    
    def _load_config(self) -> dict:
        """Load configuration"""
        default_config = {
            'routing_rules': {
                'critical': {'immediate': True, 'channels': ['feishu', 'email']},
                'high': {'immediate': True, 'channels': ['feishu']},
                'medium': {'immediate': False, 'channels': ['feishu'], 'batch': True},
                'low': {'immediate': False, 'channels': ['feishu'], 'batch': True, 'digest': True}
            },
            'dnd': {
                'enabled': False,
                'start': '23:00',
                'end': '07:00',
                'allow_critical': True
            },
            'rate_limit': {
                'max_per_hour': 20,
                'max_per_day': 100
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config
    
    def route(self, message: str, priority: str = 'medium', 
              category: str = None) -> dict:
        """Route notification"""
        # Check DND
        if self._is_dnd() and priority != 'critical':
            return {
                'status': 'queued_dnd',
                'message': 'In Do Not Disturb period',
                'will_send_at': self._dnd_end_time()
            }
        
        # Check rate limit
        if not self._check_rate_limit(priority):
            return {
                'status': 'rate_limited',
                'message': 'Rate limit exceeded',
                'retry_after': '1h'
            }
        
        # Get routing rules
        rules = self.config['routing_rules'].get(priority, {})
        
        if rules.get('immediate'):
            return self._send_immediate(message, priority, rules.get('channels', []))
        elif rules.get('batch'):
            return self._queue_for_batch(message, priority)
        else:
            return self._send_immediate(message, priority, ['feishu'])
    
    def _is_dnd(self) -> bool:
        """Check if in DND period"""
        dnd = self.config.get('dnd', {})
        
        if not dnd.get('enabled'):
            return False
        
        now = datetime.now().time()
        start = datetime.strptime(dnd['start'], '%H:%M').time()
        end = datetime.strptime(dnd['end'], '%H:%M').time()
        
        return now >= start or now <= end
    
    def _dnd_end_time(self) -> str:
        """Get DND end time"""
        dnd = self.config.get('dnd', {})
        return dnd.get('end', '07:00')
    
    def _check_rate_limit(self, priority: str) -> bool:
        """Check rate limit"""
        # Mock - implement with actual tracking
        return True
    
    def _send_immediate(self, message: str, priority: str, channels: list) -> dict:
        """Send immediate notification"""
        try:
            from feishu_api import FeishuNotifier
            notifier = FeishuNotifier()
            
            # Format message with priority
            priority_emoji = {
                'critical': '🚨',
                'high': '[WARN]',
                'medium': '📢',
                'low': 'ℹ️'
            }
            
            formatted = f"{priority_emoji.get(priority, 'ℹ️')} *[{priority.upper()}]*\n{message}"
            
            result = notifier.send_text(formatted)
            
            return {
                'status': 'sent',
                'channels': channels,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _queue_for_batch(self, message: str, priority: str) -> dict:
        """Queue for batch sending"""
        self.queue.add(message, priority)
        
        return {
            'status': 'queued',
            'queue_size': self.queue.size(),
            'will_send_at': 'next_batch'
        }


class PriorityNotificationQueue:
    """Priority queue for notifications"""
    
    def __init__(self):
        self.queues = {
            'critical': deque(),
            'high': deque(),
            'medium': deque(),
            'low': deque()
        }
    
    def add(self, message: str, priority: str = 'medium'):
        """Add to queue"""
        if priority not in self.queues:
            priority = 'medium'
        
        self.queues[priority].append({
            'message': message,
            'priority': priority,
            'queued_at': datetime.now().isoformat()
        })
    
    def size(self) -> int:
        """Get total queue size"""
        return sum(len(q) for q in self.queues.values())
    
    def get_batch(self, max_size: int = 10) -> list:
        """Get batch of notifications"""
        batch = []
        
        # Priority order: critical > high > medium > low
        for priority in ['critical', 'high', 'medium', 'low']:
            queue = self.queues[priority]
            
            while queue and len(batch) < max_size:
                batch.append(queue.popleft())
        
        return batch
    
    def clear(self):
        """Clear all queues"""
        for queue in self.queues.values():
            queue.clear()


class DNDManager:
    """Manage Do Not Disturb settings"""
    
    def __init__(self, config_file: str = None):
        self.config_file = Path(config_file) if config_file else Path(__file__).parent / 'notification_config.json'
    
    def set_dnd(self, enabled: bool, start: str = None, end: str = None):
        """Set DND settings"""
        config = self._load_config()
        
        config['dnd']['enabled'] = enabled
        if start:
            config['dnd']['start'] = start
        if end:
            config['dnd']['end'] = end
        
        self._save_config(config)
        
        return {'status': 'success', 'dnd': config['dnd']}
    
    def _load_config(self) -> dict:
        """Load config"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'dnd': {'enabled': False, 'start': '23:00', 'end': '07:00'}}
    
    def _save_config(self, config: dict):
        """Save config"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Notification Router')
    parser.add_argument('--send', type=str, help='Send message')
    parser.add_argument('--priority', type=str, default='medium',
                       choices=['critical', 'high', 'medium', 'low'],
                       help='Priority level')
    parser.add_argument('--queue', action='store_true', help='Show queue status')
    parser.add_argument('--dnd', action='store_true', help='Set DND')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    router = NotificationRouter()
    
    # Send
    if args.send:
        result = router.route(args.send, args.priority)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"[{result['status'].upper()}] {result.get('message', result.get('status'))}")
    
    # Queue status
    elif args.queue:
        status = {
            'queue_size': router.queue.size(),
            'dnd_active': router._is_dnd()
        }
        
        if args.json:
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print(f"[QUEUE] Size: {status['queue_size']}")
            print(f"[DND] Active: {status['dnd_active']}")
    
    # DND
    elif args.dnd:
        dnd = DNDManager()
        result = dnd.set_dnd(True)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"[DND] Enabled until {result['dnd']['end']}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
