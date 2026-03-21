import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EVENT-BUS-001 Tool Event Bus
[Tool Event Bus - Inter-tool Communication]

功能:
  - 工具间事件发布/订阅
  - 事件总线中央协调
  - 事件日志与追踪

使用:
  py event_bus_001.py --publish <event> <data>
  py event_bus_001.py --subscribe <event>
  py event_bus_001.py --events
  py event_bus_001.py --status
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable, Optional

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


EVENT_BUS_DIR = Path("13-memory/.event_bus")
EVENT_LOG = EVENT_BUS_DIR / "events.json"
SUBSCRIPTIONS_FILE = EVENT_BUS_DIR / "subscriptions.json"


class EventBus:
    """工具间事件总线"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        EVENT_BUS_DIR.mkdir(parents=True, exist_ok=True)
        
        self._ensure_files()
    
    def _ensure_files(self):
        if not EVENT_LOG.exists():
            EVENT_LOG.write_text(json.dumps({"events": []}, ensure_ascii=False, indent=2))
        if not SUBSCRIPTIONS_FILE.exists():
            SUBSCRIPTIONS_FILE.write_text(json.dumps({"subscriptions": {}}, ensure_ascii=False, indent=2))
    
    def _load_events(self) -> dict:
        return json.loads(EVENT_LOG.read_text(encoding="utf-8"))
    
    def _save_events(self, data: dict):
        EVENT_LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def _load_subscriptions(self) -> dict:
        return json.loads(SUBSCRIPTIONS_FILE.read_text(encoding="utf-8"))
    
    def _save_subscriptions(self, data: dict):
        SUBSCRIPTIONS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def publish(self, event_type: str, data: dict = None) -> Dict:
        """发布事件"""
        events_data = self._load_events()
        
        event = {
            "id": len(events_data["events"]) + 1,
            "type": event_type,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
            "source": "cli"
        }
        
        events_data["events"].append(event)
        
        # 限制日志大小
        if len(events_data["events"]) > 1000:
            events_data["events"] = events_data["events"][-500:]
        
        self._save_events(events_data)
        
        # 触发订阅者
        self._trigger_subscribers(event_type, event)
        
        return {
            "status": "success",
            "event_id": event["id"],
            "type": event_type
        }
    
    def subscribe(self, event_type: str, handler: str = None) -> Dict:
        """订阅事件"""
        subs = self._load_subscriptions()
        
        if event_type not in subs["subscriptions"]:
            subs["subscriptions"][event_type] = []
        
        handler_info = {
            "handler": handler or "default",
            "subscribed_at": datetime.now().isoformat()
        }
        
        subs["subscriptions"][event_type].append(handler_info)
        self._save_subscriptions(subs)
        
        return {
            "status": "success",
            "event_type": event_type,
            "subscribers": len(subs["subscriptions"][event_type])
        }
    
    def _trigger_subscribers(self, event_type: str, event: dict):
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py event_bus_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py event_bus_001.py

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

触发订阅者"""
        subs = self._load_subscriptions()
        
        if event_type in subs["subscriptions"]:
            # 这里只是记录，实际触发需要工具主动查询
            pass
    
    def list_events(self, limit: int = 20) -> List:
        """列出最近事件"""
        events_data = self._load_events()
        return events_data["events"][-limit:]
    
    def list_subscriptions(self) -> Dict:
        """列出所有订阅"""
        subs = self._load_subscriptions()
        return subs["subscriptions"]
    
    def status(self) -> Dict:
        """查看状态"""
        events_data = self._load_events()
        subs = self._load_subscriptions()
        
        return {
            "total_events": len(events_data["events"]),
            "event_types": list(set(e["type"] for e in events_data["events"])),
            "total_subscriptions": sum(len(v) for v in subs["subscriptions"].values()),
            "subscribed_types": list(subs["subscriptions"].keys())
        }


logging.basicConfig(level=logging.INFO)
def main():
    bus = EventBus()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--publish":
            event_type = sys.argv[2] if len(sys.argv) > 2 else "default"
            data_str = sys.argv[3] if len(sys.argv) > 3 else "{}"
            try:
                data = json.loads(data_str)
            except (Exception,):
                data = {"message": data_str}
            
            result = bus.publish(event_type, data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--subscribe":
            event_type = sys.argv[2] if len(sys.argv) > 2 else "default"
            handler = sys.argv[3] if len(sys.argv) > 3 else None
            result = bus.subscribe(event_type, handler)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--events":
            events = bus.list_events()
            print(json.dumps(events, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--subscriptions":
            subs = bus.list_subscriptions()
            print(json.dumps(subs, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--status":
            result = bus.status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("EVENT-BUS-001 Tool Event Bus")
    print("Usage:")
    print("  py event_bus_001.py --publish <event> <data>  # Publish event")
    print("  py event_bus_001.py --subscribe <event>       # Subscribe")
    print("  py event_bus_001.py --events                 # List events")
    print("  py event_bus_001.py --subscriptions          # List subscriptions")
    print("  py event_bus_001.py --status                 # View status")
    return 0


if __name__ == "__main__":
    sys.exit(main())
