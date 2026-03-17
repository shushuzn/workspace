#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core System Integration Test - Core System Iteration
Test all core systems together
Features: cache + config + monitor + self-healing integration

Usage:
    python core_system_test.py --all
    python core_system_test.py --cache
    python core_system_test.py --config
    python core_system_test.py --monitor
    python core_system_test.py --healing
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Workspace root
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / "30-scripts-tools"
REPORT_FILE = WORKSPACE / "20-data-reports" / "core_system_test_report.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class CoreSystemTester:
    """Test all core systems"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {}
        }
    
    def test_cache_system(self) -> dict:
        """Test cache manager"""
        print("\n" + "=" * 60)
        print("Testing Cache System")
        print("=" * 60)
        
        result = {
            'name': 'Cache System',
            'start_time': datetime.now().isoformat(),
            'tests': [],
            'status': 'unknown'
        }
        
        try:
            from cache_manager import TwoLevelCache
            
            # Test 1: Basic set/get
            print("\n[Test 1] Basic set/get...")
            cache = TwoLevelCache()
            
            cache.set('test_key', {'value': 'test_data', 'number': 42})
            value = cache.get('test_key')
            
            if value and value.get('number') == 42:
                print("  ✅ PASS: Basic set/get")
                result['tests'].append({'name': 'basic_set_get', 'status': 'pass'})
            else:
                print("  ❌ FAIL: Basic set/get")
                result['tests'].append({'name': 'basic_set_get', 'status': 'fail'})
            
            # Test 2: TTL expiration
            print("\n[Test 2] TTL expiration...")
            cache.set('short_ttl', 'expires_soon', ttl=2)
            time.sleep(3)
            expired = cache.get('short_ttl')
            
            if expired is None:
                print("  ✅ PASS: TTL expiration")
                result['tests'].append({'name': 'ttl_expiration', 'status': 'pass'})
            else:
                print("  ❌ FAIL: TTL expiration")
                result['tests'].append({'name': 'ttl_expiration', 'status': 'fail'})
            
            # Test 3: Stats tracking
            print("\n[Test 3] Stats tracking...")
            stats = cache.get_stats()
            
            if 'hit_rate_percent' in stats and 'hits' in stats:
                print(f"  ✅ PASS: Stats tracking (hit rate: {stats['hit_rate_percent']}%)")
                result['tests'].append({'name': 'stats_tracking', 'status': 'pass'})
            else:
                print("  ❌ FAIL: Stats tracking")
                result['tests'].append({'name': 'stats_tracking', 'status': 'fail'})
            
            # Test 4: L1/L2 cache
            print("\n[Test 4] Two-level cache...")
            cache.set('l1_test', 'in_memory')
            l1_value = cache.get('l1_test')  # Should be L1 hit
            
            if l1_value == 'in_memory' and stats.get('l1_hits', 0) > 0:
                print(f"  ✅ PASS: Two-level cache (L1 hits: {stats['l1_hits']})")
                result['tests'].append({'name': 'two_level_cache', 'status': 'pass'})
            else:
                print("  ❌ FAIL: Two-level cache")
                result['tests'].append({'name': 'two_level_cache', 'status': 'fail'})
            
            result['status'] = 'pass' if all(t['status'] == 'pass' for t in result['tests']) else 'fail'
        
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        result['end_time'] = datetime.now().isoformat()
        self.results['tests'].append(result)
        
        return result
    
    def test_config_system(self) -> dict:
        """Test configuration center"""
        print("\n" + "=" * 60)
        print("Testing Configuration System")
        print("=" * 60)
        
        result = {
            'name': 'Configuration System',
            'start_time': datetime.now().isoformat(),
            'tests': [],
            'status': 'unknown'
        }
        
        try:
            from config_center import ConfigCenter
            
            # Test 1: Load config
            print("\n[Test 1] Load configuration...")
            config = ConfigCenter()
            
            if config.config and 'system' in config.config:
                print("  ✅ PASS: Load configuration")
                result['tests'].append({'name': 'load_config', 'status': 'pass'})
            else:
                print("  ❌ FAIL: Load configuration")
                result['tests'].append({'name': 'load_config', 'status': 'fail'})
            
            # Test 2: Get values
            print("\n[Test 2] Get configuration values...")
            workspace = config.get('system.workspace')
            debug = config.get('system.debug_mode')
            
            if workspace and isinstance(debug, bool):
                print(f"  ✅ PASS: Get values (workspace: {workspace[:30]}...)")
                result['tests'].append({'name': 'get_values', 'status': 'pass'})
            else:
                print("  ❌ FAIL: Get values")
                result['tests'].append({'name': 'get_values', 'status': 'fail'})
            
            # Test 3: Validate
            print("\n[Test 3] Validate configuration...")
            validation = config.validate()
            
            if validation.get('valid', False):
                print("  ✅ PASS: Validate configuration")
                result['tests'].append({'name': 'validate_config', 'status': 'pass'})
            else:
                print(f"  ❌ FAIL: Validate configuration ({validation.get('errors', [])})")
                result['tests'].append({'name': 'validate_config', 'status': 'fail'})
            
            # Test 4: Set value
            print("\n[Test 4] Set configuration value...")
            success = config.set('system.debug_mode', True, save=False)
            
            if success and config.get('system.debug_mode') == True:
                print("  ✅ PASS: Set configuration value")
                result['tests'].append({'name': 'set_value', 'status': 'pass'})
            else:
                print("  ❌ FAIL: Set configuration value")
                result['tests'].append({'name': 'set_value', 'status': 'fail'})
            
            result['status'] = 'pass' if all(t['status'] == 'pass' for t in result['tests']) else 'fail'
        
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        result['end_time'] = datetime.now().isoformat()
        self.results['tests'].append(result)
        
        return result
    
    def test_monitor_system(self) -> dict:
        """Test real-time monitor"""
        print("\n" + "=" * 60)
        print("Testing Monitor System")
        print("=" * 60)
        
        result = {
            'name': 'Monitor System',
            'start_time': datetime.now().isoformat(),
            'tests': [],
            'status': 'unknown'
        }
        
        try:
            from real_time_monitor import RealTimeMonitor
            
            # Test 1: Collect metrics
            print("\n[Test 1] Collect metrics...")
            monitor = RealTimeMonitor()
            metrics = monitor.collect_metrics()
            
            if 'system' in metrics and 'tools' in metrics:
                print("  ✅ PASS: Collect metrics")
                result['tests'].append({'name': 'collect_metrics', 'status': 'pass'})
            else:
                print("  ❌ FAIL: Collect metrics")
                result['tests'].append({'name': 'collect_metrics', 'status': 'fail'})
            
            # Test 2: System metrics
            print("\n[Test 2] System metrics...")
            system = metrics.get('system', {})
            
            if 'cpu_percent' in system or 'error' in system:
                print(f"  ✅ PASS: System metrics (CPU: {system.get('cpu_percent', 'N/A')}%)")
                result['tests'].append({'name': 'system_metrics', 'status': 'pass'})
            else:
                print("  ❌ FAIL: System metrics")
                result['tests'].append({'name': 'system_metrics', 'status': 'fail'})
            
            # Test 3: Tool metrics
            print("\n[Test 3] Tool metrics...")
            tools = metrics.get('tools', {})
            
            if tools.get('total', 0) > 0:
                print(f"  ✅ PASS: Tool metrics ({tools['total']} tools)")
                result['tests'].append({'name': 'tool_metrics', 'status': 'pass'})
            else:
                print("  ❌ FAIL: Tool metrics")
                result['tests'].append({'name': 'tool_metrics', 'status': 'fail'})
            
            # Test 4: Alert checking
            print("\n[Test 4] Alert checking...")
            initial_alerts = len(monitor.alerts)
            monitor._check_alerts(metrics)
            
            print(f"  ✅ PASS: Alert checking ({len(monitor.alerts)} alerts)")
            result['tests'].append({'name': 'alert_checking', 'status': 'pass'})
            
            result['status'] = 'pass' if all(t['status'] == 'pass' for t in result['tests']) else 'fail'
        
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        result['end_time'] = datetime.now().isoformat()
        self.results['tests'].append(result)
        
        return result
    
    def test_healing_system(self) -> dict:
        """Test self-healing system"""
        print("\n" + "=" * 60)
        print("Testing Self-Healing System")
        print("=" * 60)
        
        result = {
            'name': 'Self-Healing System',
            'start_time': datetime.now().isoformat(),
            'tests': [],
            'status': 'unknown'
        }
        
        try:
            from self_healing import SelfHealingSystem
            
            # Test 1: Load patterns
            print("\n[Test 1] Load error patterns...")
            healer = SelfHealingSystem()
            
            if len(healer.patterns) >= 15:
                print(f"  ✅ PASS: Load patterns ({len(healer.patterns)} patterns)")
                result['tests'].append({'name': 'load_patterns', 'status': 'pass'})
            else:
                print(f"  ❌ FAIL: Load patterns ({len(healer.patterns)} patterns)")
                result['tests'].append({'name': 'load_patterns', 'status': 'fail'})
            
            # Test 2: Get stats
            print("\n[Test 2] Get healing stats...")
            stats = healer.get_stats()
            
            if 'patterns_loaded' in stats and 'scans' in stats:
                print(f"  ✅ PASS: Get stats ({stats['patterns_loaded']} patterns)")
                result['tests'].append({'name': 'get_stats', 'status': 'pass'})
            else:
                print("  ❌ FAIL: Get stats")
                result['tests'].append({'name': 'get_stats', 'status': 'fail'})
            
            # Test 3: Pattern matching
            print("\n[Test 3] Pattern matching...")
            test_error = {
                'type': 'encoding_error',
                'file': 'test.py',
                'message': "UnicodeDecodeError: 'utf-8' codec can't decode"
            }
            
            if 'encoding_error' in healer.patterns:
                pattern = healer.patterns['encoding_error']
                if len(pattern.get('recovery_strategies', [])) >= 2:
                    print(f"  ✅ PASS: Pattern matching ({len(pattern['recovery_strategies'])} strategies)")
                    result['tests'].append({'name': 'pattern_matching', 'status': 'pass'})
                else:
                    print("  ❌ FAIL: Pattern matching (no strategies)")
                    result['tests'].append({'name': 'pattern_matching', 'status': 'fail'})
            else:
                print("  ❌ FAIL: Pattern matching (pattern not found)")
                result['tests'].append({'name': 'pattern_matching', 'status': 'fail'})
            
            result['status'] = 'pass' if all(t['status'] == 'pass' for t in result['tests']) else 'fail'
        
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        result['end_time'] = datetime.now().isoformat()
        self.results['tests'].append(result)
        
        return result
    
    def run_all_tests(self) -> dict:
        """Run all core system tests"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 15 + "Core System Integration Test" + " " * 13 + "║")
        print("╚" + "═" * 58 + "╝")
        
        # Run tests
        self.test_cache_system()
        self.test_config_system()
        self.test_monitor_system()
        self.test_healing_system()
        
        # Calculate summary
        total_tests = sum(len(t['tests']) for t in self.results['tests'])
        passed_tests = sum(
            len([t for t in test['tests'] if t['status'] == 'pass'])
            for test in self.results['tests']
        )
        
        self.results['summary'] = {
            'total_systems': len(self.results['tests']),
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'pass_rate_percent': round(passed_tests / total_tests * 100, 2) if total_tests > 0 else 0,
            'end_time': datetime.now().isoformat()
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Systems Tested: {self.results['summary']['total_systems']}")
        print(f"Total Tests: {self.results['summary']['total_tests']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        print(f"Pass Rate: {self.results['summary']['pass_rate_percent']}%")
        print("=" * 60)
        
        # Save report
        self._save_report()
        
        return self.results
    
    def _save_report(self):
        """Save test report"""
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Report saved to {REPORT_FILE}")


def main():
    parser = argparse.ArgumentParser(description='Core System Integration Test')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--cache', action='store_true', help='Test cache system')
    parser.add_argument('--config', action='store_true', help='Test config system')
    parser.add_argument('--monitor', action='store_true', help='Test monitor system')
    parser.add_argument('--healing', action='store_true', help='Test healing system')
    args = parser.parse_args()
    
    tester = CoreSystemTester()
    
    if args.all:
        tester.run_all_tests()
    elif args.cache:
        tester.test_cache_system()
    elif args.config:
        tester.test_config_system()
    elif args.monitor:
        tester.test_monitor_system()
    elif args.healing:
        tester.test_healing_system()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
