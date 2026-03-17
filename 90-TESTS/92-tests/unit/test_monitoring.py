#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Enhanced Monitoring
增强监控系统单元测试
"""

import unittest
import sys
from pathlib import Path
import time

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.monitoring.enhanced_monitoring import MetricCollector, AlertManager, EnhancedMonitoringSystem

class TestMetricCollector(unittest.TestCase):
    """指标收集器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.collector = MetricCollector()
    
    def test_record_metric(self):
        """测试记录指标"""
        self.collector.record_metric('cpu_usage', 75.5)
        metrics = self.collector.get_metrics('cpu_usage')
        
        self.assertIn('cpu_usage', metrics)
        self.assertEqual(len(metrics['cpu_usage']), 1)
    
    def test_increment_counter(self):
        """测试增加计数器"""
        self.collector.increment_counter('api_requests')
        self.collector.increment_counter('api_requests', 5)
        
        counters = self.collector.counters
        self.assertEqual(counters['api_requests'], 6)
    
    def test_set_gauge(self):
        """测试设置仪表盘"""
        self.collector.set_gauge('memory_usage', 85.0)
        
        gauges = self.collector.gauges
        self.assertEqual(gauges['memory_usage'], 85.0)
    
    def test_get_stats(self):
        """测试获取统计"""
        # 记录一些指标
        self.collector.record_metric('response_time', 100)
        self.collector.record_metric('response_time', 150)
        self.collector.record_metric('response_time', 200)
        
        stats = self.collector.get_stats()
        
        self.assertIn('response_time', stats)
        self.assertEqual(stats['response_time']['count'], 3)
        self.assertEqual(stats['response_time']['min'], 100)
        self.assertEqual(stats['response_time']['max'], 200)
        self.assertEqual(stats['response_time']['avg'], 150)

class TestAlertManager(unittest.TestCase):
    """告警管理器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.manager = AlertManager()
    
    def test_add_rule(self):
        """测试添加告警规则"""
        self.manager.add_rule('high_cpu', 'cpu_usage', '>', 80.0, 'warning')
        
        self.assertEqual(len(self.manager.alert_rules), 1)
        self.assertEqual(self.manager.alert_rules[0]['name'], 'high_cpu')
    
    def test_check_alerts_triggered(self):
        """测试告警触发"""
        self.manager.add_rule('high_cpu', 'cpu_usage', '>', 80.0, 'warning')
        
        alerts = self.manager.check_alerts({'cpu_usage': 90.0})
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['name'], 'high_cpu')
    
    def test_check_alerts_not_triggered(self):
        """测试告警不触发"""
        self.manager.add_rule('high_cpu', 'cpu_usage', '>', 80.0, 'warning')
        
        alerts = self.manager.check_alerts({'cpu_usage': 70.0})
        
        self.assertEqual(len(alerts), 0)
    
    def test_get_alerts(self):
        """测试获取告警"""
        self.manager.add_rule('high_cpu', 'cpu_usage', '>', 80.0, 'warning')
        self.manager.check_alerts({'cpu_usage': 90.0})
        
        alerts = self.manager.get_alerts()
        
        self.assertEqual(len(alerts), 1)

class TestEnhancedMonitoringSystem(unittest.TestCase):
    """增强监控系统测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.system = EnhancedMonitoringSystem()
    
    def test_record_api_request(self):
        """测试记录 API 请求"""
        self.system.record_api_request('/api/v1/papers', 50.0, 200)
        
        counters = self.system.collector.counters
        self.assertEqual(counters['api_requests_total'], 1)
    
    def test_record_workflow_execution(self):
        """测试记录工作流执行"""
        self.system.record_workflow_execution('quality_control', 120.5, 'success')
        
        counters = self.system.collector.counters
        self.assertEqual(counters['workflow_quality_control_executions'], 1)
    
    def test_get_dashboard_data(self):
        """测试获取仪表板数据"""
        self.system.record_api_request('/api/v1/papers', 50.0, 200)
        
        dashboard = self.system.get_dashboard_data()
        
        self.assertIn('timestamp', dashboard)
        self.assertIn('metrics', dashboard)
        self.assertIn('counters', dashboard)
        self.assertIn('gauges', dashboard)
        self.assertIn('recent_alerts', dashboard)

if __name__ == '__main__':
    unittest.main(verbosity=2)
