#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for API
API 集成测试
"""

import unittest
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestAPIIntegration(unittest.TestCase):
    """API 集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 启动测试服务器
        from scripts.api.api_gateway import app
        app.config['TESTING'] = True
        cls.app = app.test_client()
        cls.base_url = '/api/v1'
    
    def test_health_check(self):
        """测试健康检查"""
        response = self.app.get(f'{self.base_url}/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('version', data)
    
    def test_papers_endpoint(self):
        """测试论文端点"""
        response = self.app.get(f'{self.base_url}/papers')
        # 应该返回 404 (因为没有数据)
        self.assertIn(response.status_code, [200, 404])
    
    def test_trends_endpoint(self):
        """测试趋势端点"""
        response = self.app.get(f'{self.base_url}/trends')
        self.assertIn(response.status_code, [200, 404])
    
    def test_clusters_endpoint(self):
        """测试聚类端点"""
        response = self.app.get(f'{self.base_url}/clusters')
        self.assertIn(response.status_code, [200, 404])
    
    def test_graph_endpoint(self):
        """测试图谱端点"""
        response = self.app.get(f'{self.base_url}/graph')
        self.assertIn(response.status_code, [200, 404])
    
    def test_metrics_endpoint(self):
        """测试指标端点"""
        response = self.app.get(f'{self.base_url}/metrics')
        self.assertIn(response.status_code, [200, 404])
    
    def test_alerts_endpoint(self):
        """测试告警端点"""
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
