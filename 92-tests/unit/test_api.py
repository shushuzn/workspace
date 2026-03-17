#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for API Gateway
API 网关单元测试
"""

import unittest
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestAPIGateway(unittest.TestCase):
    """API 网关测试"""
    
    def setUp(self):
        """设置测试环境"""
        from scripts.api.api_gateway import app
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.base_url = '/api/v1'
    
    def test_health_check(self):
        """测试健康检查"""
        response = self.app.get(f'{self.base_url}/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('version', data)
    
    def test_get_papers_no_date(self):
        """测试获取论文 (无日期)"""
        response = self.app.get(f'{self.base_url}/papers')
        # 应该返回 404 或空数据 (因为没有实际数据)
        self.assertIn(response.status_code, [200, 404])
    
    def test_get_papers_with_date(self):
        """测试获取论文 (有日期)"""
        response = self.app.get(f'{self.base_url}/papers?date=2026-03-05')
        # 应该返回 404 或空数据 (因为没有实际数据)
        self.assertIn(response.status_code, [200, 404])
    
    def test_get_trends(self):
        """测试获取趋势"""
        response = self.app.get(f'{self.base_url}/trends')
        self.assertIn(response.status_code, [200, 404])
    
    def test_get_clusters(self):
        """测试获取聚类"""
        response = self.app.get(f'{self.base_url}/clusters')
        self.assertIn(response.status_code, [200, 404])
    
    def test_get_knowledge_graph(self):
        """测试获取知识图谱"""
        response = self.app.get(f'{self.base_url}/graph')
        self.assertIn(response.status_code, [200, 404])
    
    def test_get_metrics(self):
        """测试获取监控指标"""
        response = self.app.get(f'{self.base_url}/metrics')
        self.assertIn(response.status_code, [200, 404])
    
    def test_get_alerts(self):
        """测试获取告警"""
        response = self.app.get(f'{self.base_url}/alerts')
        self.assertIn(response.status_code, [200, 404])
    
    def test_invalid_endpoint(self):
        """测试无效端点"""
        response = self.app.get(f'{self.base_url}/invalid')
        self.assertEqual(response.status_code, 404)
    
    def test_method_not_allowed(self):
        """测试方法不允许"""
        response = self.app.post(f'{self.base_url}/health')
        self.assertEqual(response.status_code, 405)

if __name__ == '__main__':
    unittest.main(verbosity=2)
