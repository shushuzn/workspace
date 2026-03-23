#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Monitoring System
增强监控系统
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitoring-enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MetricCollector:
    """指标收集器"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)

    def record_metric(self, name: str, value: float, tags: Dict = None):
        """记录指标"""
        self.metrics[name].append({
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'tags': tags or {}
        })

    def increment_counter(self, name: str, value: int = 1):
        """增加计数器"""
        self.counters[name] += value

    def set_gauge(self, name: str, value: float):
        """设置仪表盘"""
        self.gauges[name] = value

    def get_metrics(self, name: str = None, start_time: datetime = None) -> Dict:
        """获取指标"""
        if name:
            metrics = self.metrics.get(name, [])
            if start_time:
                metrics = [
                    m for m in metrics
                    if datetime.fromisoformat(m['timestamp']) > start_time
                ]
            return {name: metrics}

        return {
            'metrics': dict(self.metrics),
            'counters': dict(self.counters),
            'gauges': dict(self.gauges)
        }

    def get_stats(self) -> Dict:
        """获取统计"""
        stats = {}

        for name, values in self.metrics.items():
            if values:
                numeric_values = [v['value'] for v in values if isinstance(v['value'], (int, float))]
                if numeric_values:
                    stats[name] = {
                        'count': len(values),
                        'min': min(numeric_values),
                        'max': max(numeric_values),
                        'avg': sum(numeric_values) / len(numeric_values),
                        'latest': values[-1]['value']
                    }

        return stats

    def clear_old(self, max_age_hours: int = 24):
        """清理旧指标"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)

        for name in list(self.metrics.keys()):
            self.metrics[name] = [
                m for m in self.metrics[name]
                if datetime.fromisoformat(m['timestamp']) > cutoff
            ]
            if not self.metrics[name]:
                del self.metrics[name]

class AlertManager:
    """告警管理器"""

    def __init__(self):
        self.alerts = []
        self.alert_rules = []

    def add_rule(self, name: str, metric: str, condition: str, threshold: float, severity: str = 'warning'):
        """添加告警规则"""
        self.alert_rules.append({
            'name': name,
            'metric': metric,
            'condition': condition,  # '>', '<', '==', '>=', '<='
            'threshold': threshold,
            'severity': severity
        })

    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """检查告警"""
        new_alerts = []

        for rule in self.alert_rules:
            metric_name = rule['metric']
            if metric_name in metrics:
                metric_value = metrics[metric_name]

                triggered = False
                if rule['condition'] == '>' and metric_value > rule['threshold']:
                    triggered = True
                elif rule['condition'] == '<' and metric_value < rule['threshold']:
                    triggered = True
                elif rule['condition'] == '==' and metric_value == rule['threshold']:
                    triggered = True
                elif rule['condition'] == '>=' and metric_value >= rule['threshold']:
                    triggered = True
                elif rule['condition'] == '<=' and metric_value <= rule['threshold']:
                    triggered = True

                if triggered:
                    alert = {
                        'name': rule['name'],
                        'metric': metric_name,
                        'value': metric_value,
                        'threshold': rule['threshold'],
                        'condition': rule['condition'],
                        'severity': rule['severity'],
                        'timestamp': datetime.now().isoformat()
                    }
                    new_alerts.append(alert)

        self.alerts.extend(new_alerts)
        return new_alerts

    def get_alerts(self, severity: str = None, limit: int = 100) -> List[Dict]:
        """获取告警"""
        alerts = self.alerts[-limit:]

        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]

        return alerts

    def clear_alerts(self):
        """清空告警"""
        self.alerts = []

class EnhancedMonitoringSystem:
    """增强监控系统"""

    def __init__(self, config_file: str = None):
        """
        初始化监控系统
        
        Args:
            config_file: 配置文件路径
        """
        self.collector = MetricCollector()
        self.alert_manager = AlertManager()
        self.config_file = config_file
        self.running = False

        # 加载配置
        if config_file and Path(config_file).exists():
            self.load_config(config_file)

        # 设置默认告警规则
        self._setup_default_alerts()

    def load_config(self, config_file: str):
        """加载配置"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # 加载告警规则
            for rule in config.get('alert_rules', []):
                self.alert_manager.add_rule(**rule)

            logger.info(f"Loaded config from {config_file}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def _setup_default_alerts(self):
        """设置默认告警规则"""
        self.alert_manager.add_rule(
            name='high_cpu',
            metric='cpu_usage',
            condition='>',
            threshold=80.0,
            severity='warning'
        )

        self.alert_manager.add_rule(
            name='high_memory',
            metric='memory_usage',
            condition='>',
            threshold=90.0,
            severity='critical'
        )

        self.alert_manager.add_rule(
            name='high_error_rate',
            metric='error_rate',
            condition='>',
            threshold=5.0,
            severity='critical'
        )

    def record_api_request(self, endpoint: str, duration_ms: float, status_code: int):
        """记录 API 请求"""
        self.collector.increment_counter('api_requests_total')
        self.collector.record_metric('api_request_duration', duration_ms, {'endpoint': endpoint})

        if status_code >= 400:
            self.collector.increment_counter('api_errors_total')

    def record_workflow_execution(self, workflow_name: str, duration_seconds: float, status: str):
        """记录工作流执行"""
        self.collector.increment_counter(f'workflow_{workflow_name}_executions')
        self.collector.record_metric(
            f'workflow_{workflow_name}_duration',
            duration_seconds,
            {'status': status}
        )

    def collect_system_metrics(self):
        """收集系统指标"""
        try:
            import psutil

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.collector.set_gauge('cpu_usage', cpu_percent)

            # 内存
            memory = psutil.virtual_memory()
            self.collector.set_gauge('memory_usage', memory.percent)

            # 磁盘
            disk = psutil.disk_usage('/')
            self.collector.set_gauge('disk_usage', disk.percent)

        except ImportError:
            logger.warning("psutil not installed, skipping system metrics")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    def check_and_alert(self) -> List[Dict]:
        """检查并触发告警"""
        # 收集系统指标
        self.collect_system_metrics()

        # 获取当前指标
        stats = self.collector.get_stats()

        # 计算错误率
        api_requests = self.collector.counters.get('api_requests_total', 0)
        api_errors = self.collector.counters.get('api_errors_total', 0)
        error_rate = (api_errors / api_requests * 100) if api_requests > 0 else 0
        self.collector.set_gauge('error_rate', error_rate)

        # 检查告警
        alerts = self.alert_manager.check_alerts({
            'cpu_usage': self.collector.gauges.get('cpu_usage', 0),
            'memory_usage': self.collector.gauges.get('memory_usage', 0),
            'error_rate': error_rate
        })

        # 记录告警
        for alert in alerts:
            logger.warning(f"Alert triggered: {alert['name']} - {alert['metric']}={alert['value']}")

        return alerts

    def get_dashboard_data(self) -> Dict:
        """获取仪表板数据"""
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.collector.get_stats(),
            'counters': dict(self.collector.counters),
            'gauges': dict(self.collector.gauges),
            'recent_alerts': self.alert_manager.get_alerts(limit=10)
        }

    def export_metrics(self, output_file: str):
        """导出指标"""
        data = self.get_dashboard_data()

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported metrics to {output_file}")

    def run(self, interval_seconds: int = 60):
        """运行监控"""
        self.running = True
        logger.info(f"Starting monitoring (interval: {interval_seconds}s)")

        try:
            while self.running:
                self.check_and_alert()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped")
        finally:
            self.running = False

    def stop(self):
        """停止监控"""
        self.running = False

if __name__ == "__main__":
    # 测试监控系统
    monitor = EnhancedMonitoringSystem()

    # 模拟 API 请求
    for i in range(10):
        monitor.record_api_request('/api/v1/papers', 50 + i * 10, 200 if i < 8 else 500)

    # 检查工作流
    monitor.record_workflow_execution('quality_control', 120.5, 'success')
    monitor.record_workflow_execution('analysis', 300.2, 'success')

    # 检查告警
    alerts = monitor.check_and_alert()
    print(f"Alerts: {alerts}")

    # 获取仪表板数据
    dashboard = monitor.get_dashboard_data()
    print(f"Dashboard: {json.dumps(dashboard, indent=2)}")
