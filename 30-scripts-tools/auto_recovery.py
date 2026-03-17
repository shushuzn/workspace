#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Recovery - Automatic error recovery system

Features:
- Automated recovery strategies
- Retry with exponential backoff
- Fallback mechanisms
- State preservation
- Recovery logging
- Self-healing workflows
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from collections import defaultdict
import traceback

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / 'data' / 'auto_recovery'
DATA_DIR.mkdir(parents=True, exist_ok=True)

RECOVERY_LOG = DATA_DIR / 'recovery_log.json'
RECOVERY_STATE = DATA_DIR / 'recovery_state.json'

class RecoveryStrategy:
    """Base recovery strategy"""
    
    def __init__(self, name: str):
        self.name = name
    
    def can_handle(self, error_type: str, context: Dict) -> bool:
        """Check if this strategy can handle the error"""
        raise NotImplementedError
    
    def execute(self, context: Dict) -> Dict:
        """Execute recovery"""
        raise NotImplementedError


class RetryStrategy(RecoveryStrategy):
    """Retry with exponential backoff"""
    
    def __init__(self):
        super().__init__('retry')
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 60.0
        self.exponential_base = 2
    
    def can_handle(self, error_type: str, context: Dict) -> bool:
        """Handle transient errors"""
        transient_errors = [
            'timeout', 'connection', 'rate_limit',
            'temporary', 'unavailable', 'busy',
        ]
        return any(e in error_type.lower() for e in transient_errors)
    
    def execute(self, context: Dict) -> Dict:
        """Execute retry with backoff"""
        retries = context.get('retries', 0)
        
        if retries >= self.max_retries:
            return {
                'success': False,
                'reason': 'max_retries_exceeded',
                'retries_attempted': retries,
            }
        
        # Calculate delay
        delay = min(
            self.base_delay * (self.exponential_base ** retries),
            self.max_delay
        )
        
        # Add jitter
        delay = delay * (0.5 + random.random())
        
        return {
            'success': True,
            'action': 'retry',
            'delay': delay,
            'retry_count': retries + 1,
            'message': f'Retrying in {delay:.2f}s (attempt {retries + 1}/{self.max_retries})',
        }


class FallbackStrategy(RecoveryStrategy):
    """Use fallback alternative"""
    
    def __init__(self):
        super().__init__('fallback')
        self.fallbacks = {
            'api_error': 'use_cached_data',
            'file_not_found': 'use_default_file',
            'database_error': 'use_local_cache',
            'network_error': 'use_offline_mode',
        }
    
    def can_handle(self, error_type: str, context: Dict) -> bool:
        """Handle errors with known fallbacks"""
        return error_type.lower() in self.fallbacks
    
    def execute(self, context: Dict) -> Dict:
        """Execute fallback"""
        error_type = context.get('error_type', 'unknown')
        fallback_action = self.fallbacks.get(error_type.lower(), 'unknown')
        
        return {
            'success': True,
            'action': 'fallback',
            'fallback_to': fallback_action,
            'message': f'Using fallback: {fallback_action}',
            'data_loss': fallback_action in ['use_offline_mode', 'use_default_file'],
        }


class BypassStrategy(RecoveryStrategy):
    """Bypass failed step"""
    
    def __init__(self):
        super().__init__('bypass')
    
    def can_handle(self, error_type: str, context: Dict) -> bool:
        """Handle non-critical errors"""
        non_critical = ['warning', 'optional', 'non_essential']
        severity = context.get('severity', 'medium')
        return severity in non_critical or any(nc in error_type.lower() for nc in non_critical)
    
    def execute(self, context: Dict) -> Dict:
        """Execute bypass"""
        return {
            'success': True,
            'action': 'bypass',
            'message': 'Bypassing failed step',
            'impact': 'Some functionality may be limited',
        }


class RestartStrategy(RecoveryStrategy):
    """Restart component/service"""
    
    def __init__(self):
        super().__init__('restart')
    
    def can_handle(self, error_type: str, context: Dict) -> bool:
        """Handle stuck/deadlock situations"""
        critical_errors = ['deadlock', 'hang', 'frozen', 'unresponsive']
        return any(e in error_type.lower() for e in critical_errors)
    
    def execute(self, context: Dict) -> Dict:
        """Execute restart"""
        component = context.get('component', 'service')
        
        return {
            'success': True,
            'action': 'restart',
            'component': component,
            'message': f'Restarting {component}',
            'downtime': '5-10 seconds',
        }


class RollbackStrategy(RecoveryStrategy):
    """Rollback to previous state"""
    
    def __init__(self):
        super().__init__('rollback')
    
    def can_handle(self, error_type: str, context: Dict) -> bool:
        """Handle state corruption errors"""
        state_errors = ['corruption', 'invalid_state', 'inconsistent', 'failed_transaction']
        return any(e in error_type.lower() for e in state_errors)
    
    def execute(self, context: Dict) -> Dict:
        """Execute rollback"""
        checkpoint = context.get('last_checkpoint')
        
        if not checkpoint:
            return {
                'success': False,
                'reason': 'no_checkpoint_available',
                'message': 'No checkpoint available for rollback',
            }
        
        return {
            'success': True,
            'action': 'rollback',
            'to_checkpoint': checkpoint,
            'message': f'Rolling back to checkpoint: {checkpoint}',
            'data_loss': 'Changes after checkpoint will be lost',
        }


class RecoveryEngine:
    """Recovery execution engine"""
    
    def __init__(self):
        self.strategies = [
            RetryStrategy(),
            FallbackStrategy(),
            BypassStrategy(),
            RestartStrategy(),
            RollbackStrategy(),
        ]
        self.recovery_history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load recovery history"""
        if RECOVERY_LOG.exists():
            with open(RECOVERY_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'recoveries': [], 'success_rate': 0.0}
    
    def select_strategy(self, error_type: str, context: Dict) -> Optional[RecoveryStrategy]:
        """Select best recovery strategy"""
        for strategy in self.strategies:
            if strategy.can_handle(error_type, context):
                return strategy
        return None
    
    def execute_recovery(self, error_type: str, context: Dict) -> Dict:
        """Execute recovery"""
        # Select strategy
        strategy = self.select_strategy(error_type, context)
        
        if not strategy:
            return {
                'success': False,
                'reason': 'no_suitable_strategy',
                'error_type': error_type,
                'message': 'No recovery strategy available for this error',
            }
        
        # Execute strategy
        result = strategy.execute(context)
        
        # Log recovery
        self._log_recovery(error_type, context, strategy.name, result)
        
        return {
            'success': result.get('success', False),
            'strategy': strategy.name,
            'action': result.get('action', 'unknown'),
            'message': result.get('message', ''),
            'details': result,
        }
    
    def _log_recovery(self, error_type: str, context: Dict, strategy: str, result: Dict):
        """Log recovery attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'strategy': strategy,
            'success': result.get('success', False),
            'tool': context.get('tool', 'unknown'),
        }
        
        self.recovery_history['recoveries'].append(log_entry)
        
        # Keep last 1000 entries
        if len(self.recovery_history['recoveries']) > 1000:
            self.recovery_history['recoveries'] = self.recovery_history['recoveries'][-1000:]
        
        # Update success rate
        recent = self.recovery_history['recoveries'][-100:]
        successes = sum(1 for r in recent if r['success'])
        self.recovery_history['success_rate'] = successes / len(recent) if recent else 0.0
        
        # Save
        with open(RECOVERY_LOG, 'w', encoding='utf-8') as f:
            json.dump(self.recovery_history, f, indent=2)


class StateManager:
    """Manage recovery state"""
    
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load state"""
        if RECOVERY_STATE.exists():
            with open(RECOVERY_STATE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'checkpoints': {}, 'retries': {}}
    
    def save_checkpoint(self, workflow_id: str, checkpoint_data: Dict) -> str:
        """Save checkpoint"""
        checkpoint_id = f"{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.state['checkpoints'][checkpoint_id] = {
            'data': checkpoint_data,
            'created_at': datetime.now().isoformat(),
            'workflow_id': workflow_id,
        }
        
        self._save_state()
        
        return checkpoint_id
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Get checkpoint"""
        return self.state['checkpoints'].get(checkpoint_id)
    
    def get_last_checkpoint(self, workflow_id: str) -> Optional[Dict]:
        """Get last checkpoint for workflow"""
        workflow_checkpoints = [
            (cid, data)
            for cid, data in self.state['checkpoints'].items()
            if data['workflow_id'] == workflow_id
        ]
        
        if not workflow_checkpoints:
            return None
        
        # Sort by creation time
        workflow_checkpoints.sort(key=lambda x: x[1]['created_at'], reverse=True)
        
        return workflow_checkpoints[0][1]
    
    def increment_retry(self, key: str) -> int:
        """Increment retry count"""
        current = self.state['retries'].get(key, 0)
        self.state['retries'][key] = current + 1
        self._save_state()
        return current + 1
    
    def reset_retry(self, key: str):
        """Reset retry count"""
        if key in self.state['retries']:
            del self.state['retries'][key]
            self._save_state()
    
    def _save_state(self):
        """Save state"""
        with open(RECOVERY_STATE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)


class AutoRecovery:
    """
    Automatic error recovery system
    
    Features:
    - Automated recovery strategies
    - Retry with exponential backoff
    - Fallback mechanisms
    - State preservation
    - Recovery logging
    - Self-healing workflows
    """
    
    def __init__(self):
        self.engine = RecoveryEngine()
        self.state_manager = StateManager()
    
    def recover(self, error_type: str, context: Dict) -> Dict:
        """Attempt automatic recovery"""
        # Add retry count to context
        retry_key = f"{context.get('tool', 'unknown')}_{context.get('operation', 'unknown')}"
        context['retries'] = self.state_manager.state['retries'].get(retry_key, 0)
        
        # Execute recovery
        result = self.engine.execute_recovery(error_type, context)
        
        # Update retry count if retrying
        if result.get('strategy') == 'retry' and result.get('success'):
            self.state_manager.increment_retry(retry_key)
        else:
            self.state_manager.reset_retry(retry_key)
        
        return result
    
    def save_checkpoint(self, workflow_id: str, data: Dict) -> str:
        """Save workflow checkpoint"""
        return self.state_manager.save_checkpoint(workflow_id, data)
    
    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Restore from checkpoint"""
        checkpoint = self.state_manager.get_checkpoint(checkpoint_id)
        if checkpoint:
            return checkpoint['data']
        return None
    
    def get_recovery_stats(self) -> Dict:
        """Get recovery statistics"""
        history = self.engine.recovery_history
        
        # Calculate stats
        total = len(history['recoveries'])
        recent = history['recoveries'][-100:]
        
        strategy_counts = defaultdict(int)
        for recovery in history['recoveries']:
            strategy_counts[recovery['strategy']] += 1
        
        return {
            'total_recoveries': total,
            'recent_success_rate': history['success_rate'],
            'strategy_distribution': dict(strategy_counts),
            'most_common_strategy': max(strategy_counts, key=strategy_counts.get) if strategy_counts else None,
        }
    
    def print_recovery(self, result: Dict):
        """Print recovery result"""
        print("\n" + "=" * 60)
        print("🔄 AUTO RECOVERY")
        print("=" * 60)
        
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"\nStatus: {status}")
        
        if result['success']:
            print(f"Strategy: {result['strategy']}")
            print(f"Action: {result['action']}")
            print(f"Message: {result['message']}")
            
            if 'details' in result:
                details = result['details']
                if 'delay' in details:
                    print(f"Delay: {details['delay']:.2f}s")
                if 'retry_count' in details:
                    print(f"Retry: {details['retry_count']}")
                if 'fallback_to' in details:
                    print(f"Fallback: {details['fallback_to']}")
        else:
            print(f"Reason: {result.get('reason', 'unknown')}")
            print(f"Message: {result.get('message', 'No recovery possible')}")
        
        print("\n" + "=" * 60)
    
    def print_stats(self):
        """Print recovery statistics"""
        stats = self.get_recovery_stats()
        
        print("\n" + "=" * 60)
        print("📊 RECOVERY STATISTICS")
        print("=" * 60)
        
        print(f"\nTotal Recoveries: {stats['total_recoveries']}")
        print(f"Recent Success Rate: {stats['recent_success_rate']:.1%}")
        print(f"Most Common Strategy: {stats['most_common_strategy']}")
        
        print(f"\nStrategy Distribution:")
        for strategy, count in stats['strategy_distribution'].items():
            bar = '█' * min(count, 20)
            print(f"   {strategy:15} {bar:20} {count}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Auto Recovery")
    parser.add_argument('--recover', action='store_true', help='Demo recovery')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--test', action='store_true', help='Test strategies')
    args = parser.parse_args()
    
    recovery = AutoRecovery()
    
    if args.recover:
        # Demo recovery scenarios
        scenarios = [
            ('connection_timeout', {'tool': 'api_caller.py', 'operation': 'fetch_data'}),
            ('file_not_found', {'tool': 'data_loader.py', 'file': 'config.json'}),
            ('rate_limit', {'tool': 'web_scraper.py', 'url': 'https://api.example.com'}),
        ]
        
        for error_type, context in scenarios:
            print(f"\n🔧 Testing: {error_type}")
            result = recovery.recover(error_type, context)
            recovery.print_recovery(result)
    
    elif args.stats:
        recovery.print_stats()
    
    elif args.test:
        print("\n🧪 Testing Recovery Strategies\n")
        
        # Test each strategy
        test_cases = [
            ('timeout', {'tool': 'test', 'operation': 'test'}),
            ('file_not_found', {'tool': 'test'}),
            ('deadlock', {'component': 'worker'}),
            ('corruption', {'last_checkpoint': 'chk_001'}),
        ]
        
        for error_type, context in test_cases:
            result = recovery.recover(error_type, context)
            status = "✅" if result['success'] else "❌"
            print(f"{status} {error_type:20} → {result.get('strategy', 'none'):15} ({result.get('action', 'none')})")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
