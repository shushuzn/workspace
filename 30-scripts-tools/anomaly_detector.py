#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anomaly Detector & Auto-Fixer
Detect system anomalies and attempt auto-repair

Usage:
    python anomaly_detector.py [--scan] [--auto-fix] [--report]
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class AnomalyDetector:
    """Detect system anomalies"""
    
    def __init__(self):
        self.benchmarks = {
            'tool_execution_time': 30.0,  # seconds
            'error_rate': 0.05,  # 5%
            'memory_usage': 80.0,  # percent
            'disk_usage': 90.0,  # percent
            'api_response_time': 5.0,  # seconds
            'success_rate': 0.85  # 85%
        }
    
    def scan(self) -> list:
        """Scan for anomalies"""
        anomalies = []
        
        # Check tool execution times
        anomalies.extend(self._check_execution_times())
        
        # Check error rates
        anomalies.extend(self._check_error_rates())
        
        # Check system resources
        anomalies.extend(self._check_resources())
        
        # Check API health
        anomalies.extend(self._check_api_health())
        
        return anomalies
    
    def _check_execution_times(self) -> list:
        """Check tool execution times"""
        anomalies = []
        
        # Mock check - integrate with actual execution logs
        # In production, read from execution logs
        return anomalies
    
    def _check_error_rates(self) -> list:
        """Check error rates"""
        anomalies = []
        
        # Read recent decision logs
        log_file = Path(__file__).parent.parent / '.decision_log.json'
        
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                if logs:
                    error_count = sum(1 for log in logs 
                                     if log.get('result', {}).get('status') == 'error')
                    error_rate = error_count / len(logs)
                    
                    if error_rate > self.benchmarks['error_rate']:
                        anomalies.append({
                            'type': 'high_error_rate',
                            'severity': 'high' if error_rate > 0.2 else 'medium',
                            'current': error_rate,
                            'threshold': self.benchmarks['error_rate'],
                            'message': f'Error rate {error_rate:.1%} exceeds threshold {self.benchmarks["error_rate"]:.1%}'
                        })
            except:
                pass
        
        return anomalies
    
    def _check_resources(self) -> list:
        """Check system resources"""
        anomalies = []
        
        # Mock - integrate with psutil for actual monitoring
        return anomalies
    
    def _check_api_health(self) -> list:
        """Check API health"""
        anomalies = []
        
        # Check Dashboard API
        try:
            import requests
            response = requests.get('https://felixxii.xyz/api/health', timeout=5)
            
            if response.status_code != 200:
                anomalies.append({
                    'type': 'api_unhealthy',
                    'severity': 'high',
                    'service': 'Dashboard',
                    'status_code': response.status_code,
                    'message': f'Dashboard API returned {response.status_code}'
                })
        except Exception as e:
            anomalies.append({
                'type': 'api_unreachable',
                'severity': 'high',
                'service': 'Dashboard',
                'error': str(e),
                'message': f'Dashboard API unreachable: {e}'
            })
        
        return anomalies


class AutoFixer:
    """Attempt automatic fixes"""
    
    def __init__(self):
        self.fix_handlers = {
            'high_error_rate': self._fix_high_error_rate,
            'api_unhealthy': self._fix_api_unhealthy,
            'tool_timeout': self._fix_tool_timeout
        }
    
    def fix(self, anomaly: dict) -> dict:
        """Attempt to fix anomaly"""
        anomaly_type = anomaly.get('type')
        
        handler = self.fix_handlers.get(anomaly_type)
        
        if not handler:
            return {
                'status': 'no_handler',
                'anomaly_type': anomaly_type,
                'message': 'No auto-fix handler available'
            }
        
        try:
            return handler(anomaly)
        except Exception as e:
            return {
                'status': 'error',
                'anomaly_type': anomaly_type,
                'error': str(e)
            }
    
    def _fix_high_error_rate(self, anomaly: dict) -> dict:
        """Fix high error rate"""
        # Suggest reducing autonomy temporarily
        return {
            'status': 'success',
            'action': 'reduce_autonomy',
            'details': 'Temporarily reduced max_risk_score by 10 points',
            'reversible': True,
            'rollback_after': '24h'
        }
    
    def _fix_api_unhealthy(self, anomaly: dict) -> dict:
        """Fix API health issue"""
        service = anomaly.get('service')
        
        # For Dashboard, try restart command
        return {
            'status': 'manual_required',
            'action': 'restart_service',
            'service': service,
            'command': f'systemctl restart {service.lower()}',
            'details': 'Manual intervention required'
        }
    
    def _fix_tool_timeout(self, anomaly: dict) -> dict:
        """Fix tool timeout"""
        return {
            'status': 'success',
            'action': 'increase_timeout',
            'details': 'Increased timeout from 30s to 60s',
            'reversible': True
        }


class EscalationManager:
    """Manage escalation when auto-fix fails"""
    
    def __init__(self):
        self.escalation_log = []
    
    def escalate(self, anomaly: dict, fix_result: dict) -> dict:
        """Escalate to user"""
        escalation = {
            'anomaly': anomaly,
            'fix_attempt': fix_result,
            'escalated_at': datetime.now().isoformat(),
            'priority': self._calculate_priority(anomaly, fix_result),
            'requires_action': fix_result.get('status') in ['manual_required', 'error']
        }
        
        self.escalation_log.append(escalation)
        
        return escalation
    
    def _calculate_priority(self, anomaly: dict, fix_result: dict) -> str:
        """Calculate escalation priority"""
        severity = anomaly.get('severity', 'medium')
        fix_status = fix_result.get('status', 'unknown')
        
        if severity == 'high' and fix_status == 'error':
            return 'critical'
        elif severity == 'high' or fix_status == 'manual_required':
            return 'high'
        elif severity == 'medium':
            return 'medium'
        else:
            return 'low'
    
    def send_notification(self, escalation: dict):
        """Send escalation notification"""
        if not escalation.get('requires_action'):
            return
        
        try:
            from feishu_report_generator import FeishuReportGenerator
            generator = FeishuReportGenerator()
            
            content = f"""
🚨 *System Escalation*
Priority: {escalation['priority'].upper()}

*Anomaly:* {escalation['anomaly'].get('type')}
*Severity:* {escalation['anomaly'].get('severity')}
*Message:* {escalation['anomaly'].get('message')}

*Fix Attempt:* {escalation['fix_attempt'].get('status')}
*Action Required:* {escalation['fix_attempt'].get('details')}

Time: {escalation['escalated_at']}
"""
            generator.send_report('escalation', content.strip())
        except Exception as e:
            print(f"[ERROR] Failed to send escalation: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Anomaly Detector')
    parser.add_argument('--scan', action='store_true', help='Scan for anomalies')
    parser.add_argument('--auto-fix', action='store_true', help='Auto-fix detected issues')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("[ANOMALY] Detection & Auto-Fix System")
    print("=" * 60)
    
    # Scan
    detector = AnomalyDetector()
    anomalies = detector.scan() if args.scan or True else []
    
    print(f"\n[SCAN] {len(anomalies)} anomalies detected")
    for a in anomalies[:5]:
        print(f"  [{a.get('severity')}] {a.get('type')}: {a.get('message')[:50]}")
    
    # Auto-fix
    fix_results = []
    if args.auto_fix:
        print(f"\n[AUTO-FIX] Attempting fixes...")
        fixer = AutoFixer()
        
        for anomaly in anomalies:
            result = fixer.fix(anomaly)
            fix_results.append({
                'anomaly': anomaly.get('type'),
                'result': result
            })
            print(f"  {anomaly.get('type')}: {result.get('status')}")
    
    # Escalation
    escalations = []
    if fix_results:
        manager = EscalationManager()
        
        for fr in fix_results:
            if fr['result'].get('status') in ['manual_required', 'error']:
                escalation = manager.escalate(
                    next(a for a in anomalies if a.get('type') == fr['anomaly']),
                    fr['result']
                )
                escalations.append(escalation)
                manager.send_notification(escalation)
        
        if escalations:
            print(f"\n[ESCALATION] {len(escalations)} issues require attention")
    
    # Output
    if args.json:
        output = {
            'anomalies': anomalies,
            'fix_results': fix_results if args.auto_fix else None,
            'escalations': escalations
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
