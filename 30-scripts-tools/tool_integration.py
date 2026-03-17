#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Integration Layer - Phase 4 Deep Iteration
Connects all Phase 4 tools into unified workflow
Features: event bus, tool chaining, auto-trigger, result aggregation

Usage:
    python tool_integration.py --demo
    python tool_integration.py --chain review,notify,log
    python tool_integration.py --status
    python tool_integration.py --trigger code_change
"""

import os
import sys
import json
import time
import argparse
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable, Any
from queue import Queue, Empty

# Workspace root
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / "30-scripts-tools"
INTEGRATION_CONFIG = TOOLS_DIR / "integration-config.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class EventBus:
    """Simple event bus for tool communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue = Queue()
        self.running = False
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        print(f"[SUBSCRIBE] {event_type} -> {callback.__name__}")
    
    def publish(self, event_type: str, data: Any = None):
        """Publish an event"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.event_queue.put(event)
        print(f"[PUBLISH] {event_type}")
    
    def process_events(self, timeout: float = 0.1):
        """Process events from queue"""
        try:
            event = self.event_queue.get(timeout=timeout)
            
            event_type = event['type']
            if event_type in self.subscribers:
                for callback in self.subscribers[event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        print(f"[ERROR] Callback {callback.__name__}: {e}")
            
            return True
        except Empty:
            return False
    
    def start(self):
        """Start event processing loop"""
        self.running = True
        
        def process_loop():
            while self.running:
                self.process_events()
        
        thread = threading.Thread(target=process_loop, daemon=True)
        thread.start()
        print("[EVENT BUS] Started")
    
    def stop(self):
        """Stop event processing"""
        self.running = False
        print("[EVENT BUS] Stopped")


class ToolIntegrationLayer:
    """Integrate all Phase 4 tools"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.tools = self._discover_tools()
        self.chains = self._load_chains()
        self._setup_default_subscriptions()
    
    def _discover_tools(self) -> Dict:
        """Discover available tools"""
        tools = {
            'code_reviewer': {
                'path': 'code_quality_reviewer.py',
                'triggers': ['code_change', 'pre_commit'],
                'outputs': ['review_result']
            },
            'test_generator': {
                'path': 'auto_test_generator.py',
                'triggers': ['new_code', 'code_change'],
                'outputs': ['test_files']
            },
            'doc_generator': {
                'path': 'smart_doc_generator.py',
                'triggers': ['code_change', 'new_feature'],
                'outputs': ['documentation']
            },
            'health_checker': {
                'path': 'system_health_checker.py',
                'triggers': ['scheduled', 'on_demand'],
                'outputs': ['health_report']
            },
            'notifier': {
                'path': 'smart_notification.py',
                'triggers': ['review_complete', 'test_complete', 'error_detected'],
                'outputs': ['notification_sent']
            },
            'cache_manager': {
                'path': 'cache_manager.py',
                'triggers': ['scheduled', 'cache_miss'],
                'outputs': ['cache_stats']
            },
            'knowledge_updater': {
                'path': 'knowledge_graph_builder.py',
                'triggers': ['new_lesson', 'daily'],
                'outputs': ['knowledge_updated']
            },
            'error_analyzer': {
                'path': 'error_analyzer.py',
                'triggers': ['error_detected', 'scheduled'],
                'outputs': ['error_report']
            }
        }
        return tools
    
    def _load_chains(self) -> Dict:
        """Load predefined tool chains"""
        chains = {
            'code_review': {
                'description': 'Automatic code review workflow',
                'steps': [
                    {'tool': 'code_reviewer', 'action': 'review'},
                    {'tool': 'test_generator', 'action': 'generate'},
                    {'tool': 'notifier', 'action': 'notify_result'}
                ]
            },
            'health_monitor': {
                'description': 'System health monitoring',
                'steps': [
                    {'tool': 'health_checker', 'action': 'check'},
                    {'tool': 'cache_manager', 'action': 'stats'},
                    {'tool': 'notifier', 'action': 'notify_if_warning'}
                ]
            },
            'documentation': {
                'description': 'Auto-documentation workflow',
                'steps': [
                    {'tool': 'doc_generator', 'action': 'generate'},
                    {'tool': 'knowledge_updater', 'action': 'update'}
                ]
            },
            'error_handling': {
                'description': 'Error detection and response',
                'steps': [
                    {'tool': 'error_analyzer', 'action': 'analyze'},
                    {'tool': 'notifier', 'action': 'notify_urgent'},
                    {'tool': 'health_checker', 'action': 'check_impact'}
                ]
            }
        }
        return chains
    
    def _setup_default_subscriptions(self):
        """Setup default event subscriptions"""
        # Code change events
        self.event_bus.subscribe('code_change', self._on_code_change)
        self.event_bus.subscribe('review_complete', self._on_review_complete)
        self.event_bus.subscribe('error_detected', self._on_error_detected)
        self.event_bus.subscribe('scheduled', self._on_scheduled)
    
    def _on_code_change(self, event: Dict):
        """Handle code change event"""
        print(f"[INTEGRATION] Code change detected: {event.get('data', {})}")
        
        # Trigger code review chain
        self.run_chain('code_review', event.get('data'))
    
    def _on_review_complete(self, event: Dict):
        """Handle review complete event"""
        print(f"[INTEGRATION] Review complete: {event.get('data', {})}")
        
        # Notify if issues found
        review_data = event.get('data', {})
        if review_data.get('issues_found', 0) > 0:
            self.event_bus.publish('notify_developer', {
                'type': 'code_review_issues',
                'count': review_data['issues_found']
            })
    
    def _on_error_detected(self, event: Dict):
        """Handle error detection event"""
        print(f"[INTEGRATION] Error detected: {event.get('data', {})}")
        
        # Trigger error handling chain
        self.run_chain('error_handling', event.get('data'))
    
    def _on_scheduled(self, event: Dict):
        """Handle scheduled event"""
        print(f"[INTEGRATION] Scheduled task: {event.get('type', 'unknown')}")
        
        # Run health monitoring
        self.run_chain('health_monitor')
    
    def run_chain(self, chain_name: str, data: Dict = None) -> Dict:
        """Run a tool chain"""
        if chain_name not in self.chains:
            print(f"[ERROR] Unknown chain: {chain_name}")
            return {'error': f'Unknown chain: {chain_name}'}
        
        chain = self.chains[chain_name]
        print(f"\n[RUN CHAIN] {chain_name}: {chain['description']}")
        print("=" * 60)
        
        results = []
        
        for step in chain['steps']:
            tool_name = step['tool']
            action = step['action']
            
            print(f"\n[STEP] {tool_name}.{action}()")
            
            # Simulate tool execution
            result = self._simulate_tool_execution(tool_name, action, data)
            results.append(result)
            
            print(f"[RESULT] {result.get('status', 'unknown')} - {result.get('message', '')}")
            
            # Pass result to next step
            if result.get('status') == 'success':
                data = {**(data or {}), **result.get('output', {})}
            else:
                print(f"[WARN] Chain stopped at {tool_name}")
                break
        
        print("=" * 60)
        print(f"[CHAIN COMPLETE] {chain_name}")
        
        return {
            'chain': chain_name,
            'steps_completed': len(results),
            'results': results,
            'status': 'success' if all(r.get('status') == 'success' for r in results) else 'partial'
        }
    
    def _simulate_tool_execution(self, tool_name: str, action: str, data: Dict = None) -> Dict:
        """Simulate tool execution (would call actual tool in production)"""
        # In production, this would actually call the tool
        # For now, simulate success
        
        time.sleep(0.1)  # Simulate processing
        
        return {
            'tool': tool_name,
            'action': action,
            'status': 'success',
            'message': f'{tool_name}.{action}() completed',
            'output': {
                'timestamp': datetime.now().isoformat(),
                'tool': tool_name
            }
        }
    
    def show_status(self):
        """Show integration status"""
        print("\n" + "=" * 60)
        print("Tool Integration Layer Status")
        print("=" * 60)
        
        print(f"\n📦 Discovered Tools: {len(self.tools)}")
        for tool_name, tool_info in self.tools.items():
            print(f"   • {tool_name}: {tool_info['path']}")
        
        print(f"\n🔗 Available Chains: {len(self.chains)}")
        for chain_name, chain_info in self.chains.items():
            print(f"   • {chain_name}: {chain_info['description']}")
        
        print(f"\n📡 Event Subscriptions: {len(self.event_bus.subscribers)}")
        for event_type, callbacks in self.event_bus.subscribers.items():
            callback_names = [cb.__name__ for cb in callbacks]
            print(f"   • {event_type}: {', '.join(callback_names)}")
        
        print("=" * 60)
    
    def demo(self):
        """Run integration demo"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 15 + "Tool Integration Demo" + " " * 20 + "║")
        print("╚" + "═" * 58 + "╝")
        
        # Start event bus
        self.event_bus.start()
        
        # Demo: Code change workflow
        print("\n[DEMO] Simulating code change...")
        self.event_bus.publish('code_change', {
            'file': 'example.py',
            'changes': 'new feature'
        })
        
        # Wait for processing
        time.sleep(0.5)
        
        # Demo: Health check
        print("\n[DEMO] Running scheduled health check...")
        self.event_bus.publish('scheduled', {'type': 'health_check'})
        
        # Wait for processing
        time.sleep(0.5)
        
        # Show status
        self.show_status()
        
        # Stop event bus
        self.event_bus.stop()
        
        print("\n[DEMO COMPLETE]")


def main():
    parser = argparse.ArgumentParser(description='Tool Integration Layer')
    parser.add_argument('--demo', action='store_true', help='Run integration demo')
    parser.add_argument('--chain', type=str, help='Run a tool chain')
    parser.add_argument('--status', action='store_true', help='Show integration status')
    parser.add_argument('--trigger', type=str, help='Trigger an event')
    args = parser.parse_args()
    
    integration = ToolIntegrationLayer()
    
    if args.demo:
        integration.demo()
    
    if args.chain:
        chain_name = args.chain
        result = integration.run_chain(chain_name)
        print(f"\nResult: {json.dumps(result, indent=2)}")
    
    if args.status:
        integration.show_status()
    
    if args.trigger:
        event_type = args.trigger
        integration.event_bus.publish(event_type, {'source': 'manual'})
        time.sleep(0.2)
        print(f"[OK] Event {event_type} triggered")
    
    if not any([args.demo, args.chain, args.status, args.trigger]):
        parser.print_help()


if __name__ == "__main__":
    main()
