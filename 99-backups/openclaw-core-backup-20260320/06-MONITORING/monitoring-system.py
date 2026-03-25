#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitoring & Alerting System
监控与告警系统
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

class MonitoringSystem:
    """监控系统"""

    def __init__(self):
        self.workflows_dir = Path(r"str(Path(__file__).parent.parent)\workflows")
        self.logs_dir = Path(r"str(Path(__file__).parent.parent)\workflows\logs")
        self.metrics_file = Path(r"str(Path(__file__).parent.parent)\monitoring\metrics.json")
        self.alerts_file = Path(r"str(Path(__file__).parent.parent)\monitoring\alerts.json")

        # 告警阈值
        self.thresholds = {
            'processing_time_minutes': 30,
            'pass_rate': 0.80,
            'error_rate': 0.10
        }

    def collect_metrics(self) -> Dict:
        """收集指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'workflows': {},
            'quality_gates': [],
            'performance': {}
        }

        # 收集各工作流指标
        for workflow_dir in self.workflows_dir.iterdir():
            if workflow_dir.is_dir() and workflow_dir.name[0].isdigit():
                log_file = workflow_dir / 'logs' / f"{workflow_dir.name}.log"
                if log_file.exists():
                    workflow_metrics = self._parse_log(log_file)
                    metrics['workflows'][workflow_dir.name] = workflow_metrics

        # 计算性能指标
        metrics['performance'] = self._calculate_performance(metrics)

        return metrics

    def _parse_log(self, log_file: Path) -> Dict:
        """解析日志文件"""
        metrics = {
            'last_run': None,
            'processing_time': 0,
            'status': 'unknown',
            'errors': 0
        }

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

                # 查找最后运行时间
                for line in reversed(lines):
                    if 'COMPLETE' in line:
                        # 简单解析，实际应该更复杂
                        metrics['status'] = 'completed'
                        break
                    elif 'ERROR' in line or 'FAILED' in line:
                        metrics['status'] = 'failed'
                        metrics['errors'] += 1
        except Exception as e:
            metrics['status'] = 'error'

        return metrics

    def _calculate_performance(self, metrics: Dict) -> Dict:
        """计算性能指标"""
        performance = {
            'total_workflows': len(metrics['workflows']),
            'completed': sum(1 for w in metrics['workflows'].values() if w['status'] == 'completed'),
            'failed': sum(1 for w in metrics['workflows'].values() if w['status'] == 'failed'),
            'success_rate': 0
        }

        if performance['total_workflows'] > 0:
            performance['success_rate'] = performance['completed'] / performance['total_workflows']

        return performance

    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """检查告警"""
        alerts = []

        # 检查成功率
        if metrics['performance']['success_rate'] < self.thresholds['pass_rate']:
            alerts.append({
                'level': 'critical',
                'type': 'low_success_rate',
                'message': f"Success rate {metrics['performance']['success_rate']:.2%} < {self.thresholds['pass_rate']:.2%}",
                'timestamp': datetime.now().isoformat()
            })

        # 检查工作流失败
        for workflow_name, workflow_metrics in metrics['workflows'].items():
            if workflow_metrics['status'] == 'failed':
                alerts.append({
                    'level': 'error',
                    'type': 'workflow_failed',
                    'workflow': workflow_name,
                    'message': f"Workflow {workflow_name} failed",
                    'timestamp': datetime.now().isoformat()
                })

        return alerts

    def save_metrics(self, metrics: Dict):
        """保存指标"""
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

        # 保存历史指标
        history_file = self.metrics_file.parent / f"metrics_{datetime.now().strftime('%Y-%m-%d')}.json"

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        # 更新最新指标
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

    def save_alerts(self, alerts: List[Dict]):
        """保存告警"""
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'alerts': alerts,
                'total': len(alerts)
            }, f, indent=2, ensure_ascii=False)

    def send_notification(self, alerts: List[Dict]):
        """发送通知"""
        if not alerts:
            return

        # 打印告警
        print("\n" + "=" * 60)
        print("⚠️ ALERTS")
        print("=" * 60)

        for alert in alerts:
            print(f"[{alert['level'].upper()}] {alert['type']}: {alert['message']}")

        print("=" * 60)

        # TODO: 发送邮件/短信/Slack 等通知

    def run(self):
        """运行监控"""
        print("=" * 60)
        print("Monitoring & Alerting System")
        print("=" * 60)

        # 收集指标
        print(f"\n[1/4] Collecting metrics...")
        metrics = self.collect_metrics()
        print(f"  Collected metrics from {len(metrics['workflows'])} workflows")

        # 检查告警
        print(f"\n[2/4] Checking alerts...")
        alerts = self.check_alerts(metrics)
        print(f"  Found {len(alerts)} alerts")

        # 保存指标
        print(f"\n[3/4] Saving metrics...")
        self.save_metrics(metrics)
        print(f"  Saved to: {self.metrics_file}")

        # 保存告警并发送通知
        print(f"\n[4/4] Processing alerts...")
        self.save_alerts(alerts)
        if alerts:
            self.send_notification(alerts)
        else:
            print(f"  No alerts")

        print("\n" + "=" * 60)
        print("[COMPLETE]")
        print("=" * 60)

def demo():
    """演示使用"""
    monitor = MonitoringSystem()
    monitor.run()

if __name__ == "__main__":
    demo()
