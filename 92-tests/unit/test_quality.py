#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Quality Controller
质量控制单元测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

# 动态导入 (因为文件夹名有连字符)
import importlib.util
spec = importlib.util.spec_from_file_location("quality_controller", Path(__file__).parent.parent.parent / 'scripts' / 'level-0' / 'quality-controller.py')
quality_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality_module)
QualityController = quality_module.QualityController

class TestQualityController(unittest.TestCase):
    """质量控制器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.controller = QualityController()
    
    def test_validate_arxiv_id_valid(self):
        """测试 arXiv ID 验证 (有效)"""
        valid_ids = ['2603.00267', 'arXiv:2603.00267', '2401.00001', '9999.99999']
        for arxiv_id in valid_ids:
            result = self.controller._validate_arxiv_id(arxiv_id)
            self.assertTrue(result, f"{arxiv_id} should be valid")
    
    def test_validate_arxiv_id_invalid(self):
        """测试 arXiv ID 验证 (无效)"""
        invalid_ids = ['invalid', '2603.267', 'arXiv:invalid', '', '123', 'abc.def']
        for arxiv_id in invalid_ids:
            result = self.controller._validate_arxiv_id(arxiv_id)
            self.assertFalse(result, f"{arxiv_id} should be invalid")
    
    def test_validate_papers_required_fields(self):
        """测试必填字段验证"""
        # 有效论文
        valid_paper = {
            'arxiv_id': '2603.00267',
            'title': 'Test Paper Title',
            'abstract': 'This is a test abstract with sufficient length for validation'
        }
        
        valid, invalid = self.controller.validate_papers([valid_paper])
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(invalid), 0)
    
    def test_validate_papers_missing_fields(self):
        """测试缺失字段验证"""
        # 缺失 arxiv_id
        paper1 = {'title': 'Test', 'abstract': 'Test abstract'}
        # 缺失 title
        paper2 = {'arxiv_id': '2603.00267', 'abstract': 'Test'}
        # 缺失 abstract
        paper3 = {'arxiv_id': '2603.00267', 'title': 'Test'}
        
        valid, invalid = self.controller.validate_papers([paper1, paper2, paper3])
        self.assertEqual(len(valid), 0)
        self.assertEqual(len(invalid), 3)
    
    def test_validate_papers_title_length(self):
        """测试标题长度验证"""
        # 标题太短
        short_paper = {
            'arxiv_id': '2603.00267',
            'title': 'Short',  # < 10 字符
            'abstract': 'This is a test abstract with sufficient length'
        }
        
        valid, invalid = self.controller.validate_papers([short_paper])
        self.assertEqual(len(invalid), 1)
        self.assertIn('Title too short', invalid[0].get('validation_issues', []))
    
    def test_validate_papers_abstract_length(self):
        """测试摘要长度验证"""
        # 摘要太短
        short_abstract_paper = {
            'arxiv_id': '2603.00267',
            'title': 'Test Paper Title',
            'abstract': 'Short'  # < 50 字符
        }
        
        valid, invalid = self.controller.validate_papers([short_abstract_paper])
        self.assertEqual(len(invalid), 1)
        self.assertIn('Abstract too short', invalid[0].get('validation_issues', []))
    
    def test_validate_papers_duplicate(self):
        """测试重复论文检测"""
        paper1 = {
            'arxiv_id': '2603.00267',
            'title': 'Test Paper Title That Is Long Enough',
            'abstract': 'This is a test abstract with sufficient length for validation purposes'
        }
        paper2 = {
            'arxiv_id': '2603.00267',  # 重复
            'title': 'Duplicate Paper Title That Is Long Enough',
            'abstract': 'This is a duplicate abstract with sufficient length for validation'
        }
        
        valid, invalid = self.controller.validate_papers([paper1, paper2])
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(invalid), 1)
        self.assertIn('Duplicate paper', invalid[0].get('validation_issues', []))
    
    def test_quality_score_perfect(self):
        """测试完美质量评分"""
        score = self.controller.calculate_quality_score(
            valid=100,
            invalid=0,
            anomalies=0
        )
        self.assertEqual(score['level'], 'A')
        self.assertGreaterEqual(score['score'], 0.95)
    
    def test_quality_score_good(self):
        """测试良好质量评分"""
        score = self.controller.calculate_quality_score(
            valid=95,
            invalid=5,
            anomalies=3
        )
        self.assertIn(score['level'], ['A', 'B'])
        self.assertGreater(score['score'], 0.80)
    
    def test_quality_score_poor(self):
        """测试差质量评分"""
        score = self.controller.calculate_quality_score(
            valid=50,
            invalid=50,
            anomalies=20
        )
        self.assertIn(score['level'], ['D', 'F'])
        self.assertLess(score['score'], 0.70)
    
    def test_quality_score_fail(self):
        """测试失败质量评分"""
        score = self.controller.calculate_quality_score(
            valid=20,
            invalid=80,
            anomalies=50
        )
        self.assertEqual(score['level'], 'F')
        self.assertLess(score['score'], 0.70)
    
    def test_clean_data_whitespace(self):
        """测试数据清洗 (空白字符)"""
        dirty_paper = {
            'arxiv_id': '  2603.00267  ',
            'title': '  Test Title  ',
            'abstract': '  Test Abstract  '
        }
        
        cleaned = self.controller.clean_data([dirty_paper])
        self.assertEqual(cleaned[0]['arxiv_id'], '2603.00267')
        self.assertEqual(cleaned[0]['title'], 'Test Title')
    
    def test_clean_data_categories(self):
        """测试数据清洗 (类别标准化)"""
        paper_with_string_category = {
            'arxiv_id': '2603.00267',
            'title': 'Test',
            'abstract': 'Test',
            'categories': 'cs.AI'  # 字符串而非列表
        }
        
        cleaned = self.controller.clean_data([paper_with_string_category])
        self.assertIsInstance(cleaned[0]['categories'], list)
        self.assertEqual(cleaned[0]['categories'], ['cs.AI'])
    
    def test_clean_data_timestamp(self):
        """测试数据清洗 (时间戳)"""
        paper = {
            'arxiv_id': '2603.00267',
            'title': 'Test',
            'abstract': 'Test'
        }
        
        cleaned = self.controller.clean_data([paper])
        self.assertIn('processed_at', cleaned[0])
    
    def test_add_metadata(self):
        """测试元数据添加"""
        data = {'test': 'data'}
        result = self.controller.add_metadata(data, 'test-source', '1.0')
        
        self.assertIn('metadata', result)
        self.assertIn('data', result)
        self.assertEqual(result['metadata']['source'], 'test-source')
        self.assertEqual(result['metadata']['version'], '1.0')
        self.assertIn('processed_at', result['metadata'])
        self.assertIn('checksum', result['metadata'])

class TestAnomalyDetection(unittest.TestCase):
    """异常检测测试"""
    
    def setUp(self):
        self.controller = QualityController()
    
    def test_detect_anomalies_title_length(self):
        """测试标题长度异常检测"""
        papers = [
            {'arxiv_id': f'2603.00{i:03d}', 'title': 'Normal Paper Title', 'abstract': 'Test'}
            for i in range(20)
        ]
        
        # 添加一个异常标题 (特别长)
        papers.append({
            'arxiv_id': '2603.00999',
            'title': 'A' * 500,  # 异常长的标题
            'abstract': 'Test'
        })
        
        anomalies = self.controller.detect_anomalies(papers)
        self.assertGreater(len(anomalies), 0)
        self.assertTrue(any(a['type'] == 'abnormal_title_length' for a in anomalies))

if __name__ == '__main__':
    unittest.main(verbosity=2)
